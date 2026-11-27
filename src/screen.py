"""IP screen for the downloaded corpus. Command text is not written out."""

from __future__ import annotations

import ipaddress
import json
import re
import zipfile
from pathlib import Path

_IPV4 = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")


def classify(address: str) -> str:
    try:
        ip = ipaddress.ip_address(address)
    except ValueError:
        return "invalid"
    if not isinstance(ip, ipaddress.IPv4Address):
        return "other"
    if ip in ipaddress.ip_network("198.51.100.0/24"):
        return "author_placeholder"
    if (
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_reserved
        or ip.is_multicast
        or ip.is_unspecified
        or ip in ipaddress.ip_network("192.0.2.0/24")
        or ip in ipaddress.ip_network("203.0.113.0/24")
        or ip in ipaddress.ip_network("100.64.0.0/10")
    ):
        return "reserved_or_private"
    return "needs_review"


def scan_text(text: str) -> dict[str, set[str]]:
    found: dict[str, set[str]] = {
        "author_placeholder": set(),
        "reserved_or_private": set(),
        "needs_review": set(),
    }
    for match in _IPV4.findall(text):
        kind = classify(match)
        if kind in found:
            found[kind].add(match)
    return found


def scan_zip(zip_path: Path) -> dict[str, set[str]]:
    totals: dict[str, set[str]] = {
        "author_placeholder": set(),
        "reserved_or_private": set(),
        "needs_review": set(),
    }
    with zipfile.ZipFile(zip_path) as zf:
        for name in zf.namelist():
            if not name.endswith(".jsonl") and not name.endswith(".json") and not name.endswith(".txt"):
                continue
            if name.startswith("prompts/") or name.startswith("code/"):
                continue
            with zf.open(name) as handle:
                for raw in handle:
                    try:
                        text = raw.decode("utf-8", errors="ignore")
                    except Exception:
                        continue
                    # Keep the match local to the line. Do not store the line.
                    for kind, addresses in scan_text(text).items():
                        totals[kind].update(addresses)
                    # Avoid holding a parsed command in a longer-lived object.
                    del text
    return totals


def summary_counts(found: dict[str, set[str]]) -> dict[str, int]:
    return {key: len(values) for key, values in found.items()}
