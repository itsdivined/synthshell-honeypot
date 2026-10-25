"""Check the Ubuntu test-set scaffold. This script does not invent commands."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.config import TEST_COMMANDS, TEST_SESSIONS, VALIDATION_COMMANDS

TEMPLATES = ROOT / "data" / "templates"
TEST_SET = ROOT / "data" / "test_set" / "sessions.jsonl"
GROUND_TRUTH = ROOT / "data" / "test_set" / "ground_truth.jsonl"
FIXTURE = ROOT / "data" / "fixtures" / "pipeline_check.jsonl"


def main() -> int:
    missing = [path for path in TEMPLATES.glob("*.json") if not path.is_file()]
    schemas = list(TEMPLATES.glob("*.json"))
    if not schemas:
        print("Template schemas are missing from data/templates.")
        return 2
    for path in schemas:
        json.loads(path.read_text(encoding="utf-8"))
    if not FIXTURE.is_file():
        print("Pipeline-check fixture is missing.")
        return 2
    _validate_rows(FIXTURE)
    print("Scaffold schemas and the pipeline-check fixture are valid.")
    print(
        f"The study set is about {TEST_COMMANDS} commands in about {TEST_SESSIONS} sessions."
    )
    print(
        f"Keep about {VALIDATION_COMMANDS} validation commands separate from that test set."
    )
    print("Capture ground truth in a clean container with no network:")
    print("docker run --rm -it --network none ubuntu:24.04")
    print(f"Write sessions to {TEST_SET}")
    print(f"Write ground truth to {GROUND_TRUTH}")
    if not TEST_SET.is_file() or not GROUND_TRUTH.is_file():
        print("TEST SET MISSING")
        print("The Ubuntu capture is still to do. The pipeline check can run with:")
        print("python scripts/04_replay.py --smoke")
        return 2
    sessions = _validate_rows(TEST_SET)
    truth = _validate_rows(GROUND_TRUTH)
    print(f"sessions: {len(sessions)}")
    print(f"ground_truth_rows: {len(truth)}")
    return 0


def _validate_rows(path: Path) -> list[dict]:
    rows = []
    for line_number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not raw.strip():
            continue
        row = json.loads(raw)
        if "session_id" not in row:
            raise ValueError(f"{path} line {line_number} needs session_id")
        rows.append(row)
    return rows


if __name__ == "__main__":
    raise SystemExit(main())
