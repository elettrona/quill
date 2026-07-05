"""A compact Auphonic post-production client (upload, poll, fetch results).

Auphonic (auphonic.com) is an audio post-production service podcasters and
audiobook narrators use for leveling, noise reduction, and encoding. QUILL's
client covers the practical loop through Auphonic's "simple API": list the
account's presets, upload a finished master and start a production, poll until
it is done, and download the results.

Privacy/consent: everything requires the user's own API token (stored in the
Windows Credential Manager under :data:`CREDENTIAL_TARGET`, never in settings)
and runs only from the explicit publish dialog, which names the service and is
absent in Safe Mode. All calls funnel through the two reviewed egress sites
below (HTTPS-only, verified TLS, bounded timeouts) — see
``quill/tools/network_egress_audit.py``. wx-free, strict-typed.
"""

from __future__ import annotations

import json
import ssl
import urllib.error
import urllib.request
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

from quill import __version__

API_BASE = "https://auphonic.com/api"
#: Windows Credential Manager target for the user's Auphonic API token.
CREDENTIAL_TARGET = "quill:publish:auphonic"
_USER_AGENT = f"QUILL/{__version__} (https://github.com/Community-Access/quill)"
_TIMEOUT_SECONDS = 60.0
#: Production statuses that mean "finished" (3 = Done per Auphonic's API docs).
DONE_STATUS = 3
ERROR_STATUS = 2


class AuphonicError(RuntimeError):
    """An Auphonic call failed; the message is speakable."""


@dataclass(slots=True)
class Preset:
    """One saved Auphonic preset."""

    uuid: str
    name: str


@dataclass(slots=True)
class ProductionStatus:
    """A production's progress snapshot."""

    uuid: str
    status: int
    status_string: str
    output_files: list[dict[str, object]] = field(default_factory=list)

    @property
    def done(self) -> bool:
        return self.status == DONE_STATUS

    @property
    def failed(self) -> bool:
        return self.status == ERROR_STATUS


def _request(url: str, token: str, *, data: bytes | None = None, content_type: str = "") -> bytes:
    """One authenticated HTTPS exchange — the reviewed JSON egress site."""
    if not url.startswith("https://"):
        raise AuphonicError("Refusing a non-HTTPS Auphonic request.")
    headers = {"User-Agent": _USER_AGENT, "Authorization": f"Bearer {token}"}
    if content_type:
        headers["Content-Type"] = content_type
    request = urllib.request.Request(url, data=data, headers=headers)
    context = ssl.create_default_context()
    try:
        with urllib.request.urlopen(request, timeout=_TIMEOUT_SECONDS, context=context) as resp:
            return bytes(resp.read())
    except urllib.error.HTTPError as error:
        detail = ""
        try:
            body = json.loads(error.read().decode("utf-8"))
            detail = str(body.get("error_message", "")) if isinstance(body, dict) else ""
        except Exception:  # noqa: BLE001
            pass
        raise AuphonicError(detail or f"Auphonic said {error.code}: {error.reason}") from error
    except (urllib.error.URLError, TimeoutError, ssl.SSLError) as error:
        raise AuphonicError(f"Could not reach Auphonic: {error}") from error


def _json(
    url: str, token: str, *, data: bytes | None = None, content_type: str = ""
) -> dict[str, object]:
    payload = _request(url, token, data=data, content_type=content_type)
    try:
        parsed = json.loads(payload.decode("utf-8"))
    except ValueError as error:
        raise AuphonicError("Auphonic returned an unexpected response.") from error
    return parsed if isinstance(parsed, dict) else {}


def list_presets(token: str) -> list[Preset]:
    """The account's saved presets (name + uuid)."""
    data = _json(f"{API_BASE}/presets.json", token)
    presets: list[Preset] = []
    entries = data.get("data")
    for entry in entries if isinstance(entries, list) else []:
        if isinstance(entry, dict) and entry.get("uuid"):
            presets.append(Preset(uuid=str(entry["uuid"]), name=str(entry.get("preset_name", ""))))
    return presets


def _multipart(fields: dict[str, str], file_field: str, path: Path) -> tuple[bytes, str]:
    """Encode *fields* + one file as multipart/form-data (pure; unit-tested)."""
    boundary = f"----quill-{uuid.uuid4().hex}"
    lines: list[bytes] = []
    for key, value in fields.items():
        lines.append(f"--{boundary}\r\n".encode())
        lines.append(f'Content-Disposition: form-data; name="{key}"\r\n\r\n'.encode())
        lines.append(f"{value}\r\n".encode())
    lines.append(f"--{boundary}\r\n".encode())
    lines.append(
        f'Content-Disposition: form-data; name="{file_field}"; '
        f'filename="{path.name}"\r\n'
        "Content-Type: application/octet-stream\r\n\r\n".encode()
    )
    lines.append(path.read_bytes())
    lines.append(f"\r\n--{boundary}--\r\n".encode())
    return b"".join(lines), f"multipart/form-data; boundary={boundary}"


def start_production(
    token: str,
    path: Path,
    *,
    title: str = "",
    preset_uuid: str = "",
    on_progress: Callable[[str], None] | None = None,
) -> str:
    """Upload *path* and start a production via the simple API; returns its uuid."""
    fields: dict[str, str] = {"action": "start", "title": title or path.stem}
    if preset_uuid:
        fields["preset"] = preset_uuid
    if on_progress is not None:
        on_progress(f"Uploading {path.name} to Auphonic...")
    body, content_type = _multipart(fields, "input_file", path)
    data = _json(f"{API_BASE}/simple/productions.json", token, data=body, content_type=content_type)
    production = data.get("data")
    if not isinstance(production, dict) or not production.get("uuid"):
        raise AuphonicError("Auphonic did not accept the upload.")
    return str(production["uuid"])


def production_status(token: str, production_uuid: str) -> ProductionStatus:
    """The current status of a production."""
    data = _json(f"{API_BASE}/production/{production_uuid}.json", token)
    production = data.get("data")
    if not isinstance(production, dict):
        raise AuphonicError("Auphonic returned an unexpected response.")
    outputs = production.get("output_files")
    return ProductionStatus(
        uuid=production_uuid,
        status=int(production.get("status", -1) or -1),
        status_string=str(production.get("status_string", "")),
        output_files=[o for o in outputs if isinstance(o, dict)]
        if isinstance(outputs, list)
        else [],
    )


def download_results(
    token: str,
    status: ProductionStatus,
    out_dir: Path,
    *,
    on_progress: Callable[[str], None] | None = None,
) -> list[Path]:
    """Download a finished production's output files into *out_dir*."""
    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for output in status.output_files:
        url = str(output.get("download_url", ""))
        filename = str(output.get("filename", "")) or url.rsplit("/", 1)[-1]
        if not url or not filename:
            continue
        if on_progress is not None:
            on_progress(f"Downloading {filename}...")
        payload = _request(url, token)
        target = out_dir / filename
        target.write_bytes(payload)
        written.append(target)
    return written
