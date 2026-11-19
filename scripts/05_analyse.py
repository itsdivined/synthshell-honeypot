"""Build the comparison tables, bootstrap intervals, Wilcoxon tests, and RQ4 audit."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.analyse import load_ground_truth, load_log, render_markdown, summarise

DEFAULT_LOG = ROOT / "data" / "logs" / "replay.jsonl"
DEFAULT_TRUTH = ROOT / "data" / "test_set" / "ground_truth.jsonl"
DEFAULT_OUT = ROOT / "results"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Score a replay JSONL log into comparison tables and RQ4 audit."
    )
    parser.add_argument(
        "--log",
        type=Path,
        default=DEFAULT_LOG,
        help="Replay JSONL path (default: data/logs/replay.jsonl).",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=DEFAULT_OUT,
        help="Directory for tables.md, summary.json, rq4_containment.json (default: results/).",
    )
    parser.add_argument(
        "--truth",
        type=Path,
        default=DEFAULT_TRUTH,
        help="Optional ground-truth JSONL (default: data/test_set/ground_truth.jsonl).",
    )
    args = parser.parse_args(argv)

    log_path = args.log if args.log.is_absolute() else ROOT / args.log
    out_dir = args.out_dir if args.out_dir.is_absolute() else ROOT / args.out_dir
    truth_path = args.truth if args.truth.is_absolute() else ROOT / args.truth

    if not log_path.is_file():
        print(f"No replay log at {log_path}.")
        print("Run python scripts/04_replay.py --smoke or a study replay first.")
        return 2
    rows = load_log(log_path)
    command_rows = [row for row in rows if row.get("record_type") == "command"]
    if not command_rows:
        print("The log has no command rows.")
        return 2
    truth = load_ground_truth(truth_path if truth_path.is_file() else None)
    summary = summarise(rows, truth)
    out_dir.mkdir(parents=True, exist_ok=True)
    summary_path = out_dir / "summary.json"
    tables_path = out_dir / "tables.md"
    audit_path = out_dir / "rq4_containment.json"
    source_path = out_dir / "SOURCE.txt"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    tables_path.write_text(render_markdown(summary), encoding="utf-8")
    audit_path.write_text(
        json.dumps(summary["rq4_containment"], indent=2) + "\n", encoding="utf-8"
    )
    source_path.write_text(
        "\n".join(
            [
                f"Source log: {log_path.resolve()}",
                "Script: scripts/05_analyse.py --log <path> --out-dir <dir>",
                f"Ground truth present: {truth_path.is_file()}",
                f"Command rows scored: {len(command_rows)}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    print(render_markdown(summary))
    print(f"Wrote {tables_path}")
    print(f"Wrote {summary_path}")
    print(f"Wrote {audit_path}")
    print(f"Wrote {source_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
