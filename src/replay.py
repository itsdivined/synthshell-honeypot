"""Replay one saved session list through every configured system."""

from __future__ import annotations

import json
import time
from pathlib import Path

from src.backends import build_backends
from src.config import BREAK_DELAY_SECONDS, BASE_SYSTEMS, LabConfig, active_systems
from src.containment import audit, passed
from src.session_memory import SessionMemory


def _safe_exception_reason(exc: BaseException, *, limit: int = 240) -> str:
    """Short type+message for JSONL; no traceback, truncated if long."""
    text = f"{type(exc).__name__}: {exc}".replace("\r", " ").replace("\n", " ").strip()
    if not text:
        return type(exc).__name__
    if len(text) > limit:
        return text[: limit - 3] + "..."
    return text


def load_session_file(path: Path) -> list[dict]:
    records = []
    for line_number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not raw.strip():
            continue
        row = json.loads(raw)
        if "session_id" not in row or "command" not in row:
            raise ValueError(f"{path} line {line_number} needs session_id and command")
        records.append(
            {
                "session_id": str(row["session_id"]),
                "step": int(row.get("step") or line_number),
                "command": str(row["command"]),
                "cwd": str(row.get("cwd") or ""),
                "events": list(row.get("events") or []),
                "technique_label": str(row.get("technique_label") or ""),
            }
        )
    return records


def break_reason(status: str, reply: str, delay: float) -> str | None:
    if status != "ok":
        return None
    if not reply.strip():
        return "empty_reply"
    lowered = reply.lower()
    if "as an ai" in lowered or "language model" in lowered or "i am an ai" in lowered:
        return "ai_self_disclosure"
    if delay > BREAK_DELAY_SECONDS:
        return "delay_over_5s"
    return None


def run_replay(
    records: list[dict],
    *,
    config: LabConfig,
    log_path: Path,
    runs: int,
    temperature: float,
    history_window: int,
    source_name: str,
) -> dict:
    checks = audit(config)
    if not passed(checks):
        failed = [item.name for item in checks if not item.passed]
        raise RuntimeError("containment audit failed: " + ", ".join(failed))
    if not records:
        raise ValueError("session list is empty")

    backends = build_backends(config)
    names = [backend.system for backend in backends]
    expected = active_systems(config)
    if tuple(names) != expected:
        raise RuntimeError(
            "replay backends do not match the configured study systems: "
            f"got {tuple(names)}, expected {expected}"
        )
    if tuple(names[: len(BASE_SYSTEMS)]) != BASE_SYSTEMS:
        raise RuntimeError("replay must keep the default four systems as the first rows")

    log_path.parent.mkdir(parents=True, exist_ok=True)
    settings = {"temperature": temperature, "history_window": history_window}
    counts = {name: {"ok": 0, "skipped": 0, "error": 0} for name in names}
    reasons: dict[str, str] = {}

    with log_path.open("w", encoding="utf-8") as handle:
        meta = {
            "record_type": "run",
            "source": source_name,
            "systems": list(names),
            "runs": runs,
            "session_ids": sorted({row["session_id"] for row in records}),
            "command_count": len(records),
            "model_settings": settings,
            "containment_pass": True,
        }
        handle.write(json.dumps(meta) + "\n")
        handle.flush()
        print(
            f"Replay started: {len(records)} commands × {runs} run(s) × {len(names)} systems",
            flush=True,
        )
        try:
            for run_number in range(1, runs + 1):
                for backend in backends:
                    print(f"  [{backend.system}] starting (run {run_number})...", flush=True)
                    skip = backend.prepare()
                    if skip:
                        reasons[backend.system] = skip
                        print(f"  [{backend.system}] skip: {skip}", flush=True)
                    history: dict[str, list[dict]] = {}
                    memory_by_session: dict[str, SessionMemory] = {}
                    for row in records:
                        sid = row["session_id"]
                        if skip or backend.disabled:
                            _write_row(
                                handle,
                                backend=backend.system,
                                run_number=run_number,
                                row=row,
                                reply="",
                                delay=0.0,
                                status="skipped",
                                reason=skip or backend.disabled,
                                settings=settings,
                                result_tokens=(None, None, None),
                                response_source="skipped",
                                memory_text="",
                                break_reason_value=None,
                            )
                            counts[backend.system]["skipped"] += 1
                            continue
                        call_started: float | None = None
                        try:
                            memory = memory_by_session.setdefault(sid, SessionMemory())
                            if row["cwd"]:
                                memory.apply_cwd_text(row["cwd"])
                            for event in row["events"]:
                                memory.apply(event)
                            memory_text = memory.render()
                            call_started = time.perf_counter()
                            result = backend.reply(
                                command=row["command"],
                                memory_text=memory_text,
                                history=history.get(sid, []),
                                settings=settings,
                                session_id=sid,
                            )
                        except Exception as exc:
                            delay = (
                                time.perf_counter() - call_started
                                if call_started is not None
                                else 0.0
                            )
                            _write_row(
                                handle,
                                backend=backend.system,
                                run_number=run_number,
                                row=row,
                                reply="",
                                delay=delay,
                                status="error",
                                reason=_safe_exception_reason(exc),
                                settings=settings,
                                result_tokens=(None, None, None),
                                response_source="error",
                                memory_text="",
                                break_reason_value=None,
                            )
                            counts[backend.system]["error"] += 1
                            continue
                        reason = break_reason(
                            result.status, result.text, result.delay_seconds
                        )
                        _write_row(
                            handle,
                            backend=backend.system,
                            run_number=run_number,
                            row=row,
                            reply=result.text,
                            delay=result.delay_seconds,
                            status=result.status,
                            reason=result.skip_reason,
                            settings=settings,
                            result_tokens=(
                                result.token_count,
                                result.prompt_tokens,
                                result.completion_tokens,
                            ),
                            response_source=result.response_source,
                            memory_text=memory_text,
                            break_reason_value=reason,
                        )
                        counts[backend.system][result.status] += 1
                        handle.flush()
                        if result.status == "ok":
                            memory.note_simple_command(row["command"])
                            turns = history.setdefault(sid, [])
                            turns.append({"command": row["command"], "reply": result.text})
                            if len(turns) > history_window:
                                del turns[:-history_window]
                        if backend.disabled and backend.system not in reasons:
                            reasons[backend.system] = backend.disabled
                    print(
                        f"  [{backend.system}] done "
                        f"ok={counts[backend.system]['ok']} "
                        f"skipped={counts[backend.system]['skipped']} "
                        f"error={counts[backend.system]['error']}",
                        flush=True,
                    )
        finally:
            for backend in backends:
                backend.close()
            print("Replay finished writing log.", flush=True)

    study_complete = all(
        counts[name]["ok"] > 0 and counts[name]["skipped"] == 0 and counts[name]["error"] == 0
        for name in names
    )
    return {
        "log_path": str(log_path),
        "counts": counts,
        "skip_reasons": reasons,
        "command_count": len(records),
        "runs": runs,
        "systems": list(names),
        "study_complete": study_complete,
    }


def _write_row(
    handle,
    *,
    backend: str,
    run_number: int,
    row: dict,
    reply: str,
    delay: float,
    status: str,
    reason: str,
    settings: dict,
    result_tokens: tuple,
    response_source: str,
    memory_text: str,
    break_reason_value: str | None,
) -> None:
    token_count, prompt_tokens, completion_tokens = result_tokens
    record = {
        "record_type": "command",
        "system": backend,
        "run_number": run_number,
        "session_id": row["session_id"],
        "step": row["step"],
        "command": row["command"],
        "reply": reply,
        "delay_seconds": round(float(delay), 4),
        "token_count": token_count,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "model_settings": {**settings, "response_source": response_source},
        "status": status,
        "skip_reason": reason,
        "break_reason": break_reason_value,
        "technique_label": row.get("technique_label") or "",
        "memory": memory_text,
    }
    handle.write(json.dumps(record, ensure_ascii=True) + "\n")
