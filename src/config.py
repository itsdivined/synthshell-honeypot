"""Study constants and lab settings from the approved plan."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# The comparison is these four systems, on the same sessions.
SYSTEMS = (
    "cowrie",
    "gpt-4o-mini",
    "llama-3.1-8b",
    "qwen-2.5-7b",
)

TEMPERATURES = (0.0, 0.2, 0.5)
HISTORY_WINDOWS = (5, 10, 20)
VALIDATION_COMMANDS = 40
TEST_COMMANDS = 200
TEST_SESSIONS = 20
RUNS = 5
BREAK_DELAY_SECONDS = 5.0

ZENODO_DOI = "10.5281/zenodo.20816078"
ZENODO_DOI_URL = "https://doi.org/10.5281/zenodo.20816078"
ZENODO_API_URL = "https://zenodo.org/api/records/20816078"
ZENODO_FILE_URL = (
    "https://zenodo.org/api/records/20816078/files/zenodo_deposit.zip/content"
)

OPENAI_HOST = "api.openai.com"
LOCAL_HOSTS = frozenset({"127.0.0.1", "localhost"})

SYSTEM_PROMPT = (
    "You are the command shell of a lab Ubuntu web server in a closed comparison. "
    "Return terminal text only. "
    "Do not say that you are an AI, a chatbot, or a language model. "
    "Do not ask to run tools. "
    "Treat the session memory as the machine state."
)


@dataclass(frozen=True)
class LabConfig:
    listen_host: str = "127.0.0.1"
    listen_port: int = 2222
    cowrie_host: str = "127.0.0.1"
    cowrie_port: int = 2222
    cowrie_user: str = ""
    cowrie_password: str = ""
    ollama_host: str = "127.0.0.1"
    ollama_port: int = 11434
    llama_model: str = "llama3.1:8b"
    qwen_model: str = "qwen2.5:7b"
    openai_model: str = "gpt-4o-mini"
    openai_api_key: str = ""
    execute_commands_on_host: bool = False
    allow_honeypot_outbound: bool = False
    model_output_type: str = "text"
    model_tools: tuple = ()


def load_env_file(path: Path | None = None) -> None:
    """Load KEY=VALUE pairs. Existing environment variables win. Values are never printed."""
    path = path or (ROOT / ".env")
    if not path.is_file():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def _host_port(value: str, default_port: int) -> tuple[str, int]:
    text = value.strip()
    if text.startswith("http://"):
        text = text[len("http://") :]
    elif text.startswith("https://"):
        text = text[len("https://") :]
    text = text.split("/", 1)[0]
    if ":" in text:
        host, port_text = text.rsplit(":", 1)
        try:
            port = int(port_text)
        except ValueError:
            host, port = text, default_port
    else:
        host, port = text, default_port
    return host or "127.0.0.1", port


def load_config() -> LabConfig:
    load_env_file()
    ollama_host, ollama_port = _host_port(
        os.environ.get("OLLAMA_HOST", "127.0.0.1:11434"), 11434
    )
    try:
        cowrie_port = int(os.environ.get("COWRIE_PORT", "2222"))
    except ValueError:
        cowrie_port = 2222
    return LabConfig(
        listen_host=os.environ.get("HONEYPOT_BIND", "127.0.0.1").strip() or "127.0.0.1",
        listen_port=cowrie_port,
        cowrie_host=os.environ.get("COWRIE_HOST", "127.0.0.1").strip() or "127.0.0.1",
        cowrie_port=cowrie_port,
        cowrie_user=os.environ.get("COWRIE_USER", "").strip(),
        cowrie_password=os.environ.get("COWRIE_PASSWORD", ""),
        ollama_host=ollama_host,
        ollama_port=ollama_port,
        llama_model=os.environ.get("LLAMA_MODEL", "llama3.1:8b").strip() or "llama3.1:8b",
        qwen_model=os.environ.get("QWEN_MODEL", "qwen2.5:7b").strip() or "qwen2.5:7b",
        openai_model=os.environ.get("OPENAI_MODEL", "gpt-4o-mini").strip() or "gpt-4o-mini",
        openai_api_key=os.environ.get("OPENAI_API_KEY", "").strip(),
    )


def dial_host(host: str) -> str:
    """Return the address actually used for a local connection."""
    if host == "localhost":
        return "127.0.0.1"
    return host
