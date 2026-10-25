"""Four text backends. A missing backend records a skip and stays in the study."""

from __future__ import annotations

import json
import socket
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field

from src.config import OPENAI_HOST, SYSTEM_PROMPT, LabConfig, dial_host
from src.fixed_replies import fixed_reply

MAX_OUTPUT_TOKENS = 400


@dataclass
class Reply:
    text: str = ""
    delay_seconds: float = 0.0
    token_count: int | None = None
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    status: str = "ok"
    skip_reason: str = ""
    response_source: str = "model"


@dataclass
class Backend:
    system: str
    disabled: str = ""
    settings_extra: dict = field(default_factory=dict)

    def prepare(self) -> str | None:
        return None

    def reply(
        self,
        *,
        command: str,
        memory_text: str,
        history: list[dict],
        settings: dict,
        session_id: str,
    ) -> Reply:
        raise NotImplementedError

    def close(self) -> None:
        return None


def build_user_content(
    memory_text: str, history: list[dict], command: str, window: int
) -> str:
    shown = history[-window:] if window > 0 else []
    lines = ["Session memory:", memory_text, "", "Recent turns:"]
    if not shown:
        lines.append("(none)")
    else:
        for turn in shown:
            lines.append("$ " + str(turn.get("command", "")))
            lines.append(str(turn.get("reply", "")))
    lines.extend(["", "Command:", command, "", "Reply with terminal text only."])
    return "\n".join(lines)


def build_openai_body(model: str, temperature: float, content: str) -> dict:
    """Text chat request. There is no tool field."""
    return {
        "model": model,
        "temperature": temperature,
        "max_tokens": MAX_OUTPUT_TOKENS,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": content},
        ],
    }


class CowrieBackend(Backend):
    def __init__(self, config: LabConfig) -> None:
        super().__init__(system="cowrie")
        self.config = config
        self._client = None
        self._channel = None
        self._session_id = ""

    def prepare(self) -> str | None:
        if self.config.cowrie_host not in {"127.0.0.1", "localhost"}:
            return "Cowrie host is not local. Cowrie stays in the study and this run records a skip."
        if not self.config.cowrie_user or not self.config.cowrie_password:
            return (
                "COWRIE_USER or COWRIE_PASSWORD is empty. Cowrie remains the baseline. "
                "This run records a skip."
            )
        try:
            import paramiko  # noqa: F401
        except ImportError:
            return (
                "The paramiko package is not installed. Cowrie remains the baseline. "
                "This run records a skip."
            )
        host = dial_host(self.config.cowrie_host)
        try:
            sock = socket.create_connection((host, self.config.cowrie_port), timeout=2)
            sock.close()
        except OSError:
            return (
                "Cowrie is not accepting connections on 127.0.0.1:"
                f"{self.config.cowrie_port}. Cowrie remains the baseline. "
                "This run records a skip."
            )
        return None

    def reply(self, *, command, memory_text, history, settings, session_id) -> Reply:
        if self.disabled:
            return Reply(status="skipped", skip_reason=self.disabled, response_source="cowrie")
        start = time.perf_counter()
        try:
            self._ensure_channel(session_id)
            assert self._channel is not None
            self._channel.send(command + "\n")
            text = _read_channel(self._channel, 3.0)
        except Exception:
            self.disabled = "Cowrie session failed. Later commands in this run record a skip."
            self.close()
            return Reply(
                delay_seconds=time.perf_counter() - start,
                status="error",
                skip_reason=self.disabled,
                response_source="cowrie",
            )
        return Reply(
            text=text,
            delay_seconds=time.perf_counter() - start,
            status="ok",
            response_source="cowrie",
        )

    def close(self) -> None:
        if self._channel is not None:
            try:
                self._channel.close()
            except Exception:
                pass
            self._channel = None
        if self._client is not None:
            try:
                self._client.close()
            except Exception:
                pass
            self._client = None
        self._session_id = ""

    def _ensure_channel(self, session_id: str) -> None:
        if self._channel is not None and self._session_id == session_id:
            return
        self.close()
        if self.config.cowrie_host not in {"127.0.0.1", "localhost"}:
            raise RuntimeError("refusing a Cowrie host that is not local")
        import paramiko

        host = dial_host(self.config.cowrie_host)
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(
            hostname=host,
            port=self.config.cowrie_port,
            username=self.config.cowrie_user,
            password=self.config.cowrie_password,
            timeout=3,
            allow_agent=False,
            look_for_keys=False,
            banner_timeout=3,
            auth_timeout=3,
        )
        channel = client.invoke_shell(width=120, height=40)
        _read_channel(channel, 1.0)
        self._client = client
        self._channel = channel
        self._session_id = session_id


class OpenAIBackend(Backend):
    def __init__(self, config: LabConfig) -> None:
        super().__init__(system="gpt-4o-mini")
        self.config = config

    def prepare(self) -> str | None:
        if not self.config.openai_api_key:
            return (
                "OPENAI_API_KEY is not set. GPT-4o mini remains part of the four-system study. "
                "This run records a skip."
            )
        return None

    def reply(self, *, command, memory_text, history, settings, session_id) -> Reply:
        if self.disabled:
            return Reply(status="skipped", skip_reason=self.disabled, response_source="model")
        denial = fixed_reply(command)
        if denial is not None:
            return Reply(text=denial, status="ok", response_source="fixed_denial")
        content = build_user_content(
            memory_text, history, command, int(settings.get("history_window", 10))
        )
        body = build_openai_body(
            self.config.openai_model,
            float(settings.get("temperature", 0)),
            content,
        )
        request = urllib.request.Request(
            f"https://{OPENAI_HOST}/v1/chat/completions",
            data=json.dumps(body).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.config.openai_api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        start = time.perf_counter()
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            reason = f"GPT-4o mini returned HTTP {exc.code}. Later commands in this run record a skip."
            if exc.code in {401, 403}:
                self.disabled = reason
            return Reply(
                delay_seconds=time.perf_counter() - start,
                status="error",
                skip_reason=reason,
                response_source="model",
            )
        except urllib.error.URLError:
            self.disabled = "GPT-4o mini could not be reached. Later commands in this run record a skip."
            return Reply(
                delay_seconds=time.perf_counter() - start,
                status="error",
                skip_reason=self.disabled,
                response_source="model",
            )
        text = ""
        choices = payload.get("choices") or []
        if choices:
            text = str((choices[0].get("message") or {}).get("content") or "")
        usage = payload.get("usage") or {}
        prompt_tokens = usage.get("prompt_tokens")
        completion_tokens = usage.get("completion_tokens")
        total = usage.get("total_tokens")
        if total is None and prompt_tokens is not None and completion_tokens is not None:
            total = int(prompt_tokens) + int(completion_tokens)
        return Reply(
            text=text,
            delay_seconds=time.perf_counter() - start,
            token_count=total,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            status="ok",
            response_source="model",
        )


class OllamaBackend(Backend):
    def __init__(self, config: LabConfig, system: str, model: str) -> None:
        super().__init__(system=system)
        self.config = config
        self.model = model
        self._names: set[str] | None = None

    def prepare(self) -> str | None:
        if self.config.ollama_host not in {"127.0.0.1", "localhost"}:
            return (
                f"{self.model} would use a non-local host. The model remains in the study. "
                "This run records a skip."
            )
        url = (
            f"http://{dial_host(self.config.ollama_host)}:{self.config.ollama_port}/api/tags"
        )
        try:
            with urllib.request.urlopen(url, timeout=2) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError):
            return (
                f"Ollama is not reachable on 127.0.0.1:{self.config.ollama_port}. "
                f"{self.model} remains part of the four-system study. This run records a skip."
            )
        names = set()
        for item in payload.get("models") or []:
            name = str(item.get("name") or "")
            if name:
                names.add(name)
                names.add(name.split(":", 1)[0])
        self._names = names
        if self.model not in names and self.model.split(":", 1)[0] not in names:
            return (
                f"{self.model} is not installed in local Ollama. "
                "The model remains part of the four-system study. This run records a skip."
            )
        return None

    def reply(self, *, command, memory_text, history, settings, session_id) -> Reply:
        if self.disabled:
            return Reply(status="skipped", skip_reason=self.disabled, response_source="model")
        denial = fixed_reply(command)
        if denial is not None:
            return Reply(text=denial, status="ok", response_source="fixed_denial")
        content = build_user_content(
            memory_text, history, command, int(settings.get("history_window", 10))
        )
        body = {
            "model": self.model,
            "stream": False,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": content},
            ],
            "options": {
                "temperature": float(settings.get("temperature", 0)),
                "num_predict": MAX_OUTPUT_TOKENS,
            },
        }
        url = (
            f"http://{dial_host(self.config.ollama_host)}:{self.config.ollama_port}/api/chat"
        )
        request = urllib.request.Request(
            url,
            data=json.dumps(body).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        start = time.perf_counter()
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except urllib.error.URLError:
            self.disabled = (
                f"{self.model} stopped responding on localhost. "
                "Later commands in this run record a skip."
            )
            return Reply(
                delay_seconds=time.perf_counter() - start,
                status="error",
                skip_reason=self.disabled,
                response_source="model",
            )
        message = payload.get("message") or {}
        text = str(message.get("content") or "")
        prompt_tokens = payload.get("prompt_eval_count")
        completion_tokens = payload.get("eval_count")
        total = None
        if prompt_tokens is not None or completion_tokens is not None:
            total = int(prompt_tokens or 0) + int(completion_tokens or 0)
        return Reply(
            text=text,
            delay_seconds=time.perf_counter() - start,
            token_count=total,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            status="ok",
            response_source="model",
        )


def build_backends(config: LabConfig) -> list[Backend]:
    return [
        CowrieBackend(config),
        OpenAIBackend(config),
        OllamaBackend(config, "llama-3.1-8b", config.llama_model),
        OllamaBackend(config, "qwen-2.5-7b", config.qwen_model),
    ]


def _read_channel(channel, seconds: float) -> str:
    channel.settimeout(0.2)
    end = time.perf_counter() + seconds
    chunks: list[bytes] = []
    while time.perf_counter() < end:
        try:
            data = channel.recv(4096)
        except socket.timeout:
            if chunks:
                break
            continue
        except Exception:
            break
        if not data:
            break
        chunks.append(data)
    return b"".join(chunks).decode("utf-8", errors="replace").strip()
