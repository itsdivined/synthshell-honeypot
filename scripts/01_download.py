"""Download the Magazov et al. Zenodo deposit and write data/MANIFEST.txt."""

from __future__ import annotations

import hashlib
import json
import sys
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.config import ZENODO_API_URL, ZENODO_DOI_URL, ZENODO_FILE_URL
from src.corpus import ZIP_PATH, count_commands

MANIFEST = ROOT / "data" / "MANIFEST.txt"


def main() -> int:
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    ZIP_PATH.parent.mkdir(parents=True, exist_ok=True)
    meta, meta_error = _fetch_metadata()
    file_url = ZENODO_FILE_URL
    expected_md5 = ""
    expected_size = None
    licence_id = "cc-by-4.0"
    if meta:
        files = meta.get("files") or []
        if files:
            file_url = (files[0].get("links") or {}).get("self") or file_url
            checksum = str(files[0].get("checksum") or "")
            expected_md5 = checksum.split(":", 1)[-1]
            expected_size = files[0].get("size")
        licence = (meta.get("metadata") or {}).get("license") or {}
        if isinstance(licence, dict) and licence.get("id"):
            licence_id = str(licence["id"])

    download_error = ""
    if not _valid_local(ZIP_PATH, expected_md5):
        try:
            _download(file_url, ZIP_PATH)
        except Exception as exc:  # noqa: BLE001
            download_error = f"{type(exc).__name__}: {exc}"

    if not ZIP_PATH.is_file():
        _write_manifest(
            status="DOWNLOAD_FAILED",
            file_url=file_url,
            licence_id=licence_id,
            error=download_error or meta_error or "The zip file is not on disk.",
            byte_size="",
            md5_actual="",
            md5_expected=expected_md5,
            counts=None,
        )
        print("DOWNLOAD FAILED")
        print(f"DOI URL: {ZENODO_DOI_URL}")
        print(f"File URL: {file_url}")
        print(f"Detail: {download_error or meta_error}")
        print(f"Manifest draft: {MANIFEST}")
        return 2

    md5_actual = _md5(ZIP_PATH)
    byte_size = ZIP_PATH.stat().st_size
    md5_ok = (not expected_md5) or md5_actual == expected_md5
    size_ok = expected_size is None or int(expected_size) == byte_size
    try:
        counts = count_commands(ZIP_PATH)
    except Exception as exc:  # noqa: BLE001
        counts = None
        download_error = download_error or f"Could not read command tables: {type(exc).__name__}"

    status = "OK" if md5_ok and size_ok and counts else "CHECK_FAILED"
    _write_manifest(
        status=status,
        file_url=file_url,
        licence_id=licence_id,
        error=download_error or meta_error,
        byte_size=str(byte_size),
        md5_actual=md5_actual,
        md5_expected=expected_md5,
        counts=counts,
    )
    print(f"status: {status}")
    print(f"bytes: {byte_size}")
    print(f"md5: {md5_actual}")
    if counts:
        print(f"command_rows: {counts['command_row_count']}")
        print(f"command_files: {counts['command_file_count']}")
        print(f"distinct_session_ids: {counts['distinct_session_ids']}")
    print(f"manifest: {MANIFEST}")
    return 0 if status == "OK" else 2


def _fetch_metadata() -> tuple[dict | None, str]:
    request = urllib.request.Request(ZENODO_API_URL, headers={"User-Agent": "synthshell-honeypot"})
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            return json.loads(response.read().decode("utf-8")), ""
    except Exception as exc:  # noqa: BLE001
        return None, f"Zenodo API was not reachable ({type(exc).__name__})."


def _valid_local(path: Path, expected_md5: str) -> bool:
    if not path.is_file() or path.stat().st_size == 0:
        return False
    if not expected_md5:
        return True
    return _md5(path) == expected_md5


def _download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    temporary = dest.with_suffix(dest.suffix + ".part")
    request = urllib.request.Request(url, headers={"User-Agent": "synthshell-honeypot"})
    try:
        with urllib.request.urlopen(request, timeout=120) as response, temporary.open("wb") as handle:
            while True:
                chunk = response.read(1024 * 256)
                if not chunk:
                    break
                handle.write(chunk)
        temporary.replace(dest)
    except Exception:
        if temporary.exists():
            temporary.unlink()
        raise


def _md5(path: Path) -> str:
    digest = hashlib.md5()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 256), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _write_manifest(
    *,
    status: str,
    file_url: str,
    licence_id: str,
    error: str,
    byte_size: str,
    md5_actual: str,
    md5_expected: str,
    counts: dict | None,
) -> None:
    lines = [
        f"status: {status}",
        "source: Magazov, R., Abeshev, K., Shamuratov, Y., Uralova, F. and Aksholak, G. (2026) De-identified SSH honeypot attacker corpus. Zenodo.",
        "doi: 10.5281/zenodo.20816078",
        f"source_url: {ZENODO_DOI_URL}",
        f"api_url: {ZENODO_API_URL}",
        f"download_url: {file_url}",
        f"zenodo_licence_id: {licence_id}",
        "licence_data_and_results: CC BY 4.0",
        "licence_code_and_prompts_inside_zip: MIT",
        "filename: zenodo_deposit.zip",
        f"byte_size: {byte_size}",
        f"md5_expected: {md5_expected}",
        f"md5_actual: {md5_actual}",
        f"md5_ok: {str(bool(md5_expected) and md5_actual == md5_expected).lower()}",
        f"accessed: {date.today().isoformat()}",
        "stored_at: data/raw/zenodo_deposit.zip",
        "git: the zip is gitignored and is not committed",
        "plan_figure: about 12900 de-identified commands",
    ]
    if counts:
        lines.append(f"command_file_count: {counts['command_file_count']}")
        lines.append(f"command_row_count: {counts['command_row_count']}")
        lines.append(f"distinct_session_ids_in_command_tables: {counts['distinct_session_ids']}")
        lines.append("per_file_rows:")
        for file_rows, name in counts.get("per_file") or []:
            lines.append(f"  {file_rows} {name}")
    else:
        lines.append("command_row_count: ")
    if error:
        lines.append(f"error: {error}")
    lines.append(
        "note: Author code and prompts stay inside the zip. This project does not copy them into the source tree."
    )
    MANIFEST.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except urllib.error.URLError as exc:
        print(f"DOWNLOAD FAILED: {exc}")
        print(f"DOI URL: {ZENODO_DOI_URL}")
        raise SystemExit(2)
