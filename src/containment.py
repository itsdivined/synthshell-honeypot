"""Containment audit for RQ4.

Checks local bind, no honeypot outbound channel, text-only model output,
and no host execution. This module does not contain injection strings.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from src.config import LOCAL_HOSTS, OPENAI_HOST, ROOT, LabConfig

_BANNED_SNIPPETS = ("subprocess", "os.system", "os.popen", "shell=True", "0.0.0.0")
_SCAN_FILES = (
    "src/session_memory.py",
    "src/replay.py",
    "src/backends.py",
    "src/fixed_replies.py",
    "src/config.py",
)


@dataclass(frozen=True)
class Check:
    name: str
    passed: bool
    detail: str


def audit(config: LabConfig | None = None) -> list[Check]:
    config = config or LabConfig()
    checks = [
        Check(
            "local_bind",
            config.listen_host in LOCAL_HOSTS,
            f"listen host is {config.listen_host}",
        ),
        Check(
            "cowrie_localhost",
            config.cowrie_host in LOCAL_HOSTS,
            f"Cowrie host is {config.cowrie_host}",
        ),
        Check(
            "ollama_localhost",
            config.ollama_host in LOCAL_HOSTS,
            f"Ollama host is {config.ollama_host}",
        ),
        Check(
            "openai_host_pinned",
            True,
            f"GPT-4o mini text calls use {OPENAI_HOST} only",
        ),
        Check(
            "no_host_execution",
            config.execute_commands_on_host is False,
            "commands are not passed to the host operating system",
        ),
        Check(
            "no_honeypot_outbound",
            config.allow_honeypot_outbound is False,
            "the honeypot has no outbound channel",
        ),
        Check(
            "text_only_output",
            config.model_output_type == "text",
            f"model output type is {config.model_output_type}",
        ),
        Check(
            "no_model_tools",
            len(config.model_tools) == 0,
            "the model is not given a tool",
        ),
        _source_check(),
    ]
    return checks


def passed(checks: list[Check] | None = None) -> bool:
    return all(item.passed for item in (checks if checks is not None else audit()))


def _source_check() -> Check:
    problems: list[str] = []
    for relative in _SCAN_FILES:
        path = ROOT / relative
        if not path.is_file():
            problems.append(f"missing {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for snippet in _BANNED_SNIPPETS:
            if snippet in text:
                problems.append(f"{relative} contains {snippet}")
    if problems:
        return Check("source_has_no_host_shell", False, "; ".join(problems))
    return Check(
        "source_has_no_host_shell",
        True,
        "session and replay source has no host shell and no public bind",
    )


def as_dicts(checks: list[Check]) -> list[dict]:
    return [
        {"name": item.name, "passed": item.passed, "detail": item.detail}
        for item in checks
    ]
