"""Build the comparison tables, bootstrap intervals, Wilcoxon tests, and RQ4 audit."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.analyse import load_ground_truth, load_log, render_markdown, summarise

LOG = ROOT / "data" / "logs" / "replay.jsonl"
TRUTH = ROOT / "data" / "test_set" / "ground_truth.jsonl"
SUMMARY = ROOT / "results" / "summary.json"
TABLES = ROOT / "results" / "tables.md"
AUDIT = ROOT / "results" / "rq4_containment.json"


def main() -> int:
    if not LOG.is_file():
        print("No replay log at data/logs/replay.jsonl.")
        print("Run python scripts/04_replay.py --smoke or a study replay first.")
        return 2
    rows = load_log(LOG)
    command_rows = [row for row in rows if row.get("record_type") == "command"]
    if not command_rows:
        print("The log has no command rows.")
        return 2
    truth = load_ground_truth(TRUTH if TRUTH.is_file() else None)
    summary = summarise(rows, truth)
    SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    TABLES.write_text(render_markdown(summary), encoding="utf-8")
    AUDIT.write_text(
        json.dumps(summary["rq4_containment"], indent=2) + "\n", encoding="utf-8"
    )
    print(render_markdown(summary))
    print(f"Wrote {TABLES}")
    print(f"Wrote {SUMMARY}")
    print(f"Wrote {AUDIT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
