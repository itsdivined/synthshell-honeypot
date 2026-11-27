"""Session memory for the text-only honeypot.

State changes come from structured records. This module does not start a shell
and does not read or write the host filesystem.
"""

from __future__ import annotations

import json
import re

_USER_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_-]{0,31}$")
_SHELL_META = set(";&|`$()<>\n")
_EVENT_TYPES = frozenset(
    {"set_cwd", "file_created", "file_changed", "file_deleted", "user_added"}
)
_REJECTED_KEYS = frozenset(
    {"command", "exec", "tool", "shell", "payload", "argv"}
)


def normalise_abs(path: str) -> str:
    """Lexical absolute path. `..` is collapsed in memory only."""
    if not isinstance(path, str) or "\x00" in path:
        raise ValueError("path must be a string")
    if not path.startswith("/"):
        raise ValueError("path must be absolute")
    parts: list[str] = []
    for part in path.split("/"):
        if part in ("", "."):
            continue
        if part == "..":
            if parts:
                parts.pop()
            continue
        parts.append(part)
    return "/" + "/".join(parts)


def resolve_path(cwd: str, path: str) -> str:
    if not isinstance(path, str) or not path.strip():
        raise ValueError("path must be a string")
    text = path.strip()
    if text.startswith("/") or text.startswith("~"):
        return resolve_cwd(cwd, text)
    return resolve_cwd(cwd, text)


def resolve_cwd(current: str, value: str) -> str:
    """Apply a dataset cwd string onto the simulated working directory."""
    if not isinstance(value, str):
        return current
    text = value.strip()
    if not text:
        return current
    if text == "~":
        return "/home/ubuntu"
    if text.startswith("~/"):
        text = "/home/ubuntu/" + text[2:]
    try:
        if text.startswith("/"):
            return normalise_abs(text)
        base = current if current.endswith("/") else current + "/"
        return normalise_abs(base + text)
    except ValueError:
        return current


class SessionMemory:
    def __init__(self, cwd: str = "/home/ubuntu") -> None:
        self.cwd = normalise_abs(cwd)
        self.files_created: list[str] = []
        self.files_changed: list[str] = []
        self.files_deleted: list[str] = []
        self.users_added: list[str] = []

    def apply(self, record: dict) -> None:
        if not isinstance(record, dict):
            raise ValueError("memory record must be an object")
        extra = _REJECTED_KEYS.intersection(record)
        if extra:
            raise ValueError(
                "session memory accepts structured events only, not commands or tools"
            )
        kind = record.get("type")
        if kind not in _EVENT_TYPES:
            raise ValueError(f"unsupported memory event type: {kind!r}")
        if kind == "set_cwd":
            self.cwd = normalise_abs(str(record.get("path", "")))
            return
        if kind == "user_added":
            name = str(record.get("name", ""))
            if not _USER_NAME.match(name):
                raise ValueError("user name is not a plain account token")
            if name not in self.users_added:
                self.users_added.append(name)
            return
        path = resolve_path(self.cwd, str(record.get("path", "")))
        if kind == "file_created":
            _drop(self.files_deleted, path)
            _add(self.files_created, path)
        elif kind == "file_changed":
            if path in self.files_deleted:
                raise ValueError("file was already deleted in this session")
            _add(self.files_changed, path)
        elif kind == "file_deleted":
            _drop(self.files_created, path)
            _drop(self.files_changed, path)
            _add(self.files_deleted, path)

    def apply_text(self, line: str) -> None:
        record = json.loads(line)
        self.apply(record)

    def apply_cwd_text(self, value: str) -> None:
        self.cwd = resolve_cwd(self.cwd, value)

    def note_simple_command(self, command: str) -> None:
        """Update simulated state from one simple command.

        Commands that contain shell metacharacters are ignored. Nothing is run
        on the host.
        """
        if not isinstance(command, str) or any(char in command for char in _SHELL_META):
            return
        parts = command.split()
        if len(parts) != 2:
            return
        verb, argument = parts
        try:
            if verb == "cd":
                self.apply_cwd_text(argument)
            elif verb in {"mkdir", "touch"}:
                self.apply({"type": "file_created", "path": argument})
            elif verb == "rm":
                self.apply({"type": "file_deleted", "path": argument})
            elif verb == "useradd":
                self.apply({"type": "user_added", "name": argument})
        except ValueError:
            return

    def render(self) -> str:
        return "\n".join(
            [
                f"cwd: {self.cwd}",
                f"files_created: {_show(self.files_created)}",
                f"files_changed: {_show(self.files_changed)}",
                f"files_deleted: {_show(self.files_deleted)}",
                f"users_added: {_show(self.users_added)}",
            ]
        )


def render_context(memory: SessionMemory, history: list[dict], window: int) -> str:
    if window < 1:
        raise ValueError("history window must be positive")
    shown = history[-window:]
    lines = ["Session memory:", memory.render(), "", "Recent turns:"]
    if not shown:
        lines.append("(none)")
    else:
        for turn in shown:
            lines.append("$ " + str(turn.get("command", "")))
            lines.append(str(turn.get("reply", "")))
    return "\n".join(lines)


def _add(items: list[str], value: str) -> None:
    if value not in items:
        items.append(value)


def _drop(items: list[str], value: str) -> None:
    if value in items:
        items.remove(value)


def _show(items: list[str]) -> str:
    return "(none)" if not items else ", ".join(items)
