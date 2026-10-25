"""Replay one shared session list on Cowrie and the three LLM backends."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.config import HISTORY_WINDOWS, RUNS, TEMPERATURES, load_config
from src.corpus import ZIP_PATH, load_sessions
from src.replay import load_session_file, run_replay

FIXTURE = ROOT / "data" / "fixtures" / "pipeline_check.jsonl"
TEST_SET = ROOT / "data" / "test_set" / "sessions.jsonl"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Replay the same saved sessions on all four systems."
    )
    parser.add_argument("--smoke", action="store_true", help="Use the benign pipeline-check fixture.")
    parser.add_argument("--source", choices=("test-set", "magazov"), default="test-set")
    parser.add_argument("--sessions", type=Path)
    parser.add_argument("--max-sessions", type=int)
    parser.add_argument("--max-commands-per-session", type=int)
    parser.add_argument("--full", action="store_true")
    parser.add_argument("--runs", type=int, default=1)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--history-window", type=int, default=10)
    parser.add_argument("--log", type=Path, default=ROOT / "data" / "logs" / "replay.jsonl")
    args = parser.parse_args(argv)

    if args.runs < 1:
        print("runs must be at least 1. The study setting is 5.")
        return 2
    if args.history_window < 1:
        print("history window must be positive.")
        return 2
    if args.history_window not in HISTORY_WINDOWS:
        print(f"Planned history windows are {HISTORY_WINDOWS}. This run uses {args.history_window}.")
    if args.temperature not in TEMPERATURES:
        print(f"Planned temperatures are {TEMPERATURES}. This run uses {args.temperature}.")

    try:
        records, source_name = _load(args)
    except (FileNotFoundError, ValueError) as exc:
        print(exc)
        return 2

    config = load_config()
    try:
        summary = run_replay(
            records,
            config=config,
            log_path=args.log,
            runs=args.runs,
            temperature=args.temperature,
            history_window=args.history_window,
            source_name=source_name,
        )
    except RuntimeError as exc:
        print(exc)
        return 2

    print("Containment: pass")
    print(f"Source: {source_name}")
    print(f"Commands in the shared list: {summary['command_count']}")
    print(f"Runs: {summary['runs']}")
    print("The same list was used for every system.")
    for name in summary["systems"]:
        counts = summary["counts"][name]
        reason = summary["skip_reasons"].get(name, "")
        print(
            f"{name}: ok={counts['ok']} skipped={counts['skipped']} error={counts['error']}"
            + (f" | {reason}" if reason else "")
        )
    print(f"Log: {summary['log_path']}")
    if summary["study_complete"]:
        print("Study complete for this log: all four systems returned replies.")
        return 0
    print("Study incomplete: at least one of the four systems was skipped or returned an error.")
    print("The skipped system remains in the comparison. Configure it and replay the same sessions.")
    print(f"Full study runs before the freeze: --runs {RUNS}")
    return 0


def _load(args) -> tuple[list[dict], str]:
    if args.smoke:
        if not FIXTURE.is_file():
            raise FileNotFoundError(f"Missing fixture: {FIXTURE}")
        return load_session_file(FIXTURE), "pipeline-check"
    if args.source == "test-set":
        path = args.sessions or TEST_SET
        if not path.is_file():
            raise FileNotFoundError(
                "TEST SET MISSING. Capture it in the Ubuntu container, or run "
                "python scripts/04_replay.py --smoke for the pipeline check, or "
                "python scripts/04_replay.py --source magazov --max-sessions 20"
            )
        return load_session_file(path), "test-set"
    if not ZIP_PATH.is_file():
        raise FileNotFoundError(
            "Corpus zip is missing. Run python scripts/01_download.py. "
            "DOI URL: https://doi.org/10.5281/zenodo.20816078"
        )
    if not args.full and args.max_sessions is None:
        raise ValueError(
            "Refusing to send the whole corpus until you choose a slice. "
            "Use --max-sessions 20 for the first paired replay, or --full for every command row."
        )
    limit = None if args.full else args.max_sessions
    records = load_sessions(
        ZIP_PATH,
        max_sessions=limit,
        max_commands_per_session=args.max_commands_per_session,
    )
    if not records:
        raise ValueError("The corpus zip has no command rows.")
    return records, "magazov"


if __name__ == "__main__":
    raise SystemExit(main())
