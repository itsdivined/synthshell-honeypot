"""Scores for RQ1-RQ3 and the RQ4 containment audit."""

from __future__ import annotations

import json
import os
import random
from collections import defaultdict
from pathlib import Path

from src.config import SYSTEMS
from src.containment import as_dicts, audit, passed


def load_log(path: Path) -> list[dict]:
    rows = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        if raw.strip():
            rows.append(json.loads(raw))
    return rows


def bootstrap_ci(values: list[float], n_resamples: int = 1000, seed: int = 25) -> dict | None:
    if not values:
        return None
    rng = random.Random(seed)
    means = []
    size = len(values)
    for _ in range(n_resamples):
        sample = [values[rng.randrange(size)] for _ in range(size)]
        means.append(sum(sample) / size)
    means.sort()
    low_index = int(0.025 * (n_resamples - 1))
    high_index = int(0.975 * (n_resamples - 1))
    return {
        "mean": sum(values) / size,
        "low": means[low_index],
        "high": means[high_index],
        "n": size,
    }


def commands_completed(rows: list[dict]) -> int | None:
    if not rows or all(row.get("status") == "skipped" for row in rows):
        return None
    completed = 0
    for row in rows:
        if row.get("status") != "ok":
            continue
        if row.get("break_reason"):
            break
        completed += 1
    return completed


def _rates() -> tuple[float | None, float | None]:
    def parse(name: str) -> float | None:
        raw = os.environ.get(name, "").strip()
        if not raw:
            return None
        try:
            return float(raw)
        except ValueError:
            return None

    return parse("GPT4O_MINI_INPUT_PER_MILLION"), parse("GPT4O_MINI_OUTPUT_PER_MILLION")


def _cost(row: dict, rates: tuple[float | None, float | None]) -> float | None:
    system = row.get("system")
    if row.get("status") != "ok":
        return None
    if system in {"cowrie", "llama-3.1-8b", "qwen-2.5-7b"}:
        return 0.0
    input_rate, output_rate = rates
    if input_rate is None or output_rate is None:
        return None
    prompt = row.get("prompt_tokens")
    completion = row.get("completion_tokens")
    if prompt is None or completion is None:
        return None
    return (float(prompt) / 1_000_000) * input_rate + (float(completion) / 1_000_000) * output_rate


def _fidelity(rows: list[dict], truth: dict[tuple, str]) -> dict:
    if not truth:
        return {
            "fidelity": None,
            "invented_content": None,
            "note": "Ground-truth file is not present yet. RQ1 fidelity waits for the Ubuntu capture.",
        }
    compared = 0
    exact = 0
    invented = 0
    for row in rows:
        if row.get("status") != "ok":
            continue
        key = (str(row.get("session_id")), int(row.get("step") or 0))
        if key not in truth:
            continue
        compared += 1
        reply = str(row.get("reply") or "").strip()
        expected = truth[key].strip()
        if reply == expected:
            exact += 1
        reply_tokens = set(reply.split())
        expected_tokens = set(expected.split())
        if reply_tokens - expected_tokens:
            invented += 1
    if compared == 0:
        return {
            "fidelity": None,
            "invented_content": None,
            "note": "No ok replies joined to ground truth.",
        }
    return {
        "fidelity": exact / compared,
        "invented_content": invented / compared,
        "compared": compared,
        "note": "",
    }


def _consistency(rows: list[dict]) -> float | None:
    groups: dict[tuple, list[str]] = defaultdict(list)
    for row in rows:
        if row.get("status") != "ok":
            continue
        key = (row.get("run_number"), row.get("session_id"), row.get("command"))
        groups[key].append(str(row.get("reply") or ""))
    checked = 0
    agreed = 0
    for replies in groups.values():
        if len(replies) < 2:
            continue
        checked += 1
        if all(item == replies[0] for item in replies[1:]):
            agreed += 1
    if checked == 0:
        return None
    return agreed / checked


def _wilcoxon(pairs: list[tuple[float, float]]) -> dict:
    if len(pairs) < 5:
        return {
            "statistic": None,
            "p_value": None,
            "n_pairs": len(pairs),
            "note": "Fewer than 5 paired sessions. Wilcoxon waits for a larger shared run.",
        }
    try:
        from scipy.stats import wilcoxon
    except ImportError:
        return {
            "statistic": None,
            "p_value": None,
            "n_pairs": len(pairs),
            "note": "scipy is not installed. Run pip install -r requirements.txt.",
        }
    first = [item[0] for item in pairs]
    second = [item[1] for item in pairs]
    if all(a == b for a, b in pairs):
        return {
            "statistic": None,
            "p_value": None,
            "n_pairs": len(pairs),
            "note": "All paired differences are zero.",
        }
    try:
        result = wilcoxon(first, second)
    except ValueError as exc:
        return {
            "statistic": None,
            "p_value": None,
            "n_pairs": len(pairs),
            "note": str(exc),
        }
    return {
        "statistic": float(result.statistic),
        "p_value": float(result.pvalue),
        "n_pairs": len(pairs),
        "note": "",
    }


def load_ground_truth(path: Path | None) -> dict[tuple, str]:
    if path is None or not path.is_file():
        return {}
    truth = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        if not raw.strip():
            continue
        row = json.loads(raw)
        truth[(str(row["session_id"]), int(row["step"]))] = str(row.get("stdout") or "")
    return truth


def summarise(rows: list[dict], truth: dict[tuple, str] | None = None) -> dict:
    truth = truth or {}
    command_rows = [row for row in rows if row.get("record_type") == "command"]
    rates = _rates()
    by_system: dict[str, list[dict]] = {name: [] for name in SYSTEMS}
    for row in command_rows:
        system = row.get("system")
        if system in by_system:
            by_system[system].append(row)

    session_scores: dict[str, dict[tuple, int | None]] = {}
    systems_out = []
    for name in SYSTEMS:
        group = by_system[name]
        ok_rows = [row for row in group if row.get("status") == "ok"]
        delays = [float(row["delay_seconds"]) for row in ok_rows]
        costs = [_cost(row, rates) for row in ok_rows]
        known_costs = [item for item in costs if item is not None]
        sessions: dict[tuple, list[dict]] = defaultdict(list)
        for row in group:
            sessions[(row.get("run_number"), row.get("session_id"))].append(row)
        completed_values = []
        completed_map = {}
        for key, session_rows in sessions.items():
            score = commands_completed(session_rows)
            completed_map[key] = score
            if score is not None:
                completed_values.append(float(score))
        session_scores[name] = completed_map
        labels = sorted({row.get("technique_label") for row in group if row.get("technique_label")})
        status = "ok" if ok_rows and not any(row.get("status") == "skipped" for row in group) else (
            "skipped" if group and all(row.get("status") == "skipped" for row in group) else "partial"
        )
        if not group:
            status = "missing"
        fidelity = _fidelity(group, truth)
        systems_out.append(
            {
                "system": name,
                "status": status,
                "commands_logged": len(group),
                "replies_ok": len(ok_rows),
                "skipped": sum(1 for row in group if row.get("status") == "skipped"),
                "errors": sum(1 for row in group if row.get("status") == "error"),
                "delay_seconds": bootstrap_ci(delays),
                "commands_completed": bootstrap_ci(completed_values),
                "consistency": _consistency(group),
                "fidelity": fidelity["fidelity"],
                "invented_content": fidelity["invented_content"],
                "fidelity_note": fidelity["note"],
                "cost_usd": sum(known_costs) if known_costs else None,
                "technique_label_count": len(labels),
                "technique_labels": labels,
            }
        )

    tests = []
    baseline = session_scores["cowrie"]
    for name in SYSTEMS:
        if name == "cowrie":
            continue
        pairs = []
        other = session_scores[name]
        for key, base_score in baseline.items():
            if base_score is None or other.get(key) is None:
                continue
            pairs.append((float(base_score), float(other[key])))
        result = _wilcoxon(pairs)
        result["comparison"] = f"cowrie vs {name}"
        result["measure"] = "commands_completed"
        tests.append(result)

    checks = audit()
    return {
        "systems": systems_out,
        "wilcoxon": tests,
        "rq4_containment": {
            "passed": passed(checks),
            "checks": as_dicts(checks),
            "note": "Containment audit only. Injection wording is not stored in this repository.",
        },
        "study_complete": all(item["status"] == "ok" for item in systems_out),
    }


def render_markdown(summary: dict) -> str:
    lines = [
        "# Comparison tables",
        "",
        "All four systems stay in the table. A skip is a missing run, not a removed system.",
        "",
        "| System | Status | Logged | OK replies | Skipped | Mean delay (s) | Delay 95% CI | Mean commands completed | Fidelity | Consistency | Invented content | Cost USD | Technique labels |",
        "| --- | --- | ---: | ---: | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for item in summary["systems"]:
        delay = item["delay_seconds"]
        completed = item["commands_completed"]
        lines.append(
            "| {system} | {status} | {commands_logged} | {replies_ok} | {skipped} | {delay} | {ci} | {done} | {fidelity} | {consistency} | {invented} | {cost} | {labels} |".format(
                system=item["system"],
                status=item["status"],
                commands_logged=item["commands_logged"],
                replies_ok=item["replies_ok"],
                skipped=item["skipped"],
                delay=_num(None if delay is None else delay["mean"]),
                ci=_ci(delay),
                done=_num(None if completed is None else completed["mean"]),
                fidelity=_num(item["fidelity"]),
                consistency=_num(item["consistency"]),
                invented=_num(item["invented_content"]),
                cost=_num(item["cost_usd"]),
                labels=item["technique_label_count"],
            )
        )
    lines.extend(["", "## Wilcoxon signed-rank", ""])
    for test in summary["wilcoxon"]:
        lines.append(
            f"- {test['comparison']} on {test['measure']}: n={test['n_pairs']}, "
            f"statistic={test['statistic']}, p={test['p_value']}. {test['note']}".rstrip()
        )
    lines.extend(["", "## RQ4 containment", ""])
    audit_result = summary["rq4_containment"]
    lines.append("Passed." if audit_result["passed"] else "Failed.")
    for check in audit_result["checks"]:
        mark = "pass" if check["passed"] else "fail"
        lines.append(f"- {check['name']}: {mark}. {check['detail']}")
    lines.append("")
    lines.append(audit_result["note"])
    lines.append("")
    if summary["study_complete"]:
        lines.append("Study status: all four systems returned replies for this log.")
    else:
        lines.append(
            "Study status: the four-system comparison is not complete in this log. "
            "Skipped systems remain part of the design."
        )
    lines.append("")
    return "\n".join(lines)


def _num(value) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.4f}"
    return str(value)


def _ci(stats: dict | None) -> str:
    if not stats:
        return ""
    return f"[{stats['low']:.4f}, {stats['high']:.4f}]"
