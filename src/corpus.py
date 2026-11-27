"""Read the Magazov command tables from the Zenodo zip. Values are not printed."""

from __future__ import annotations

import json
import zipfile
from pathlib import Path

from src.config import ROOT

ZIP_PATH = ROOT / "data" / "raw" / "zenodo_deposit.zip"


def command_members(zf: zipfile.ZipFile) -> list[str]:
    names = [
        name
        for name in zf.namelist()
        if name.endswith(".jsonl") and Path(name).name.startswith("commands-")
    ]
    return sorted(names)


def iter_command_rows(zip_path: Path = ZIP_PATH):
    with zipfile.ZipFile(zip_path) as zf:
        for name in command_members(zf):
            with zf.open(name) as handle:
                for raw in handle:
                    line = raw.strip()
                    if not line:
                        continue
                    row = json.loads(line)
                    command = row.get("command")
                    if not isinstance(command, str) or not command.strip():
                        continue
                    cwd = row.get("cwd") if isinstance(row.get("cwd"), str) else ""
                    yield {
                        "session_id": str(row.get("session_id") or "unknown"),
                        "command": command,
                        "cwd": cwd,
                        "ts": str(row.get("ts") or ""),
                        "technique_label": _label(row.get("tactic_mapping")),
                        "source_file": name,
                    }


def count_commands(zip_path: Path = ZIP_PATH) -> dict:
    files = 0
    rows = 0
    sessions: set[str] = set()
    per_file: list[tuple[int, str]] = []
    with zipfile.ZipFile(zip_path) as zf:
        members = command_members(zf)
        files = len(members)
        for name in members:
            file_rows = 0
            with zf.open(name) as handle:
                for raw in handle:
                    if not raw.strip():
                        continue
                    file_rows += 1
                    rows += 1
                    try:
                        row = json.loads(raw)
                    except json.JSONDecodeError:
                        continue
                    sessions.add(str(row.get("session_id") or ""))
            per_file.append((file_rows, name))
    return {
        "command_file_count": files,
        "command_row_count": rows,
        "distinct_session_ids": len(sessions),
        "per_file": per_file,
    }


def load_sessions(
    zip_path: Path = ZIP_PATH,
    max_sessions: int | None = None,
    max_commands_per_session: int | None = None,
) -> list[dict]:
    """Group archive rows into one shared session list. Archive order is kept."""
    groups: dict[str, list[dict]] = {}
    order: list[str] = []
    for row in iter_command_rows(zip_path):
        sid = row["session_id"]
        if sid not in groups:
            if max_sessions is not None and len(groups) >= max_sessions:
                continue
            groups[sid] = []
            order.append(sid)
        bucket = groups[sid]
        if (
            max_commands_per_session is not None
            and len(bucket) >= max_commands_per_session
        ):
            continue
        bucket.append(row)
    records: list[dict] = []
    for sid in order:
        rows = sorted(groups[sid], key=lambda item: item["ts"])
        for step, row in enumerate(rows, start=1):
            records.append(
                {
                    "session_id": sid,
                    "step": step,
                    "command": row["command"],
                    "cwd": row["cwd"],
                    "events": [],
                    "technique_label": row["technique_label"],
                }
            )
    return records


def _label(value) -> str:
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, list):
        parts = [item.strip() for item in value if isinstance(item, str) and item.strip()]
        return "; ".join(parts)
    return ""
