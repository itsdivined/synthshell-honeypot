"""Screen the corpus for IP addresses. Command lines are not stored."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.corpus import ZIP_PATH
from src.screen import scan_zip, summary_counts

SUMMARY = ROOT / "data" / "screen_summary.txt"
DETAIL = ROOT / "data" / "screen_report.txt"


def main() -> int:
    if not ZIP_PATH.is_file():
        print("Corpus zip is missing.")
        print("Run: python scripts/01_download.py")
        print("DOI URL: https://doi.org/10.5281/zenodo.20816078")
        return 2
    found = scan_zip(ZIP_PATH)
    counts = summary_counts(found)
    summary = "\n".join(
        [
            "IP screen counts only. Command text is not included.",
            f"author_placeholder_addresses: {counts['author_placeholder']}",
            f"reserved_or_private_addresses: {counts['reserved_or_private']}",
            f"public_addresses_needing_review: {counts['needs_review']}",
            "Username review is a manual read of the de-identified tables.",
            "This script does not guess usernames from command text.",
            "",
        ]
    )
    SUMMARY.write_text(summary, encoding="utf-8")
    review = sorted(found["needs_review"])
    detail_lines = ["Public addresses that are outside the authors' placeholder range:"]
    detail_lines.extend(review or ["(none)"])
    DETAIL.write_text("\n".join(detail_lines) + "\n", encoding="utf-8")
    print(summary)
    if review:
        print("Review addresses were written to data/screen_report.txt (gitignored).")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
