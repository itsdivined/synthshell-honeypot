"""Fixed replies for two safety-critical categories named in the plan.

The caller passes a command string. This module does not run it.
"""

from __future__ import annotations

_PASSWORD_MARKERS = ("/etc/shadow", "/etc/passwd", "/etc/security/opasswd")


def fixed_reply(command: str) -> str | None:
    text = command.strip()
    if not text:
        return None
    first = text.split()[0]
    if first == "sudo":
        return "sudo: permission denied"
    lowered = text.lower()
    if any(marker in lowered for marker in _PASSWORD_MARKERS):
        return "permission denied"
    return None
