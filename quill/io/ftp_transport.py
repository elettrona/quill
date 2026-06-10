"""FTP transport (issue #154).

Thin wrapper around :mod:`ftplib` that conforms to :class:`RemoteTransport`.

Design notes
------------

* The transport is intentionally dumb: it understands listing directories and
  moving bytes. It does not know about formats, encodings, or the editor.
* We do not attempt FTPS here. QUILL has no out-of-the-box certificate store
  for FTPS, and silently sending passwords in cleartext is a footgun the
  docs will be very loud about. If a user needs FTPS they should pick SFTP
  (File > Open from Remote) or an SSH tunnel (File > SSH).
* Active mode is not used; we ask :mod:`ftplib` for a passive-mode data
  channel. This matches the way most consumer routers expect the connection
  to behave.
* The session is kept open for the duration of the transport (one transport
  per ``Open from Remote`` invocation). Callers that want to keep the
  connection alive across dialog opens can keep the :class:`FtpTransport`
  alive, but the dialog UI does not do this today.
"""

from __future__ import annotations

import ftplib
import io
import socket
import time
from typing import IO

from quill.core.remote_sites import RemoteSite
from quill.io.remote_transport import (
    DownloadResult,
    ProgressCallback,
    RemoteAuthError,
    RemoteEntry,
    RemoteNotFoundError,
    RemoteTransport,
    RemoteTransportError,
    chunked_copy,
    merge_headers,
)

_LIST_LINE = "-rw-r--r--   1 quill   quill        1234 Jan 01 12:00 name.txt"


class _ListingParser:
    """Translate the FTP ``LIST`` output to a list of :class:`RemoteEntry`.

    :mod:`ftplib` exposes :func:`parsecols` and :func:`MLSD` but neither is
    universally available; parsing the ``LIST`` text is the lowest common
    denominator that works with every conformant FTP server.
    """

    _SKIP_NAMES = frozenset({".", ".."})

    @classmethod
    def parse(cls, payload: str) -> list[RemoteEntry]:
        entries: list[RemoteEntry] = []
        for raw in payload.splitlines():
            if not raw.strip():
                continue
            entry = cls._parse_line(raw)
            if entry is None or entry.name in cls._SKIP_NAMES:
                continue
            entries.append(entry)
        return entries

    @classmethod
    def _parse_line(cls, line: str) -> RemoteEntry | None:
        # Modern FTP servers emit a "total N" header line on directory lists.
        if line.startswith("total "):
            return None
        # We only need name, dir flag, size, and a best-effort mtime. The
        # ``ls -l``-style format is the standard; fall back to the
        # MS-DOS-style "MM-DD-YY HH:MM[AP]M NAME" variant by checking the
        # first token.
        parts = line.split(None, 8)
        if len(parts) < 9:
            return None
        perms = parts[0]
        if not perms or perms[0] not in "-dldcbps":
            return None
        is_dir = perms[0] == "d"
        try:
            size = int(parts[4])
        except ValueError:
            size = 0
        name = parts[8]
        if name in cls._SKIP_NAMES:
            return None
        mtime = _parse_mlsd_time(parts[5], parts[6], parts[7])
        return RemoteEntry(name=name, is_dir=is_dir, size=size, modified=mtime)


def _parse_mlsd_time(month: str, day: str, year_or_time: str) -> float:
    """Return a POSIX timestamp from the standard ``ls -l`` time triplet."""

    months = {
        "Jan": 1,
        "Feb": 2,
        "Mar": 3,
        "Apr": 4,
        "May": 5,
        "Jun": 6,
        "Jul": 7,
        "Aug": 8,
        "Sep": 9,
        "Oct": 10,
        "Nov": 11,
        "Dec": 12,
    }
    month_num = months.get(month, 0)
    try:
        day_num = int(day.rstrip(","))
    except ValueError:
        day_num = 0
    if ":" in year_or_time:
        current_year = time.gmtime().tm_year
        hour_str, minute_str = year_or_time.split(":", 1)
        try:
            hour = int(hour_str)
            minute = int(minute_str)
        except ValueError:
            return 0.0
        return time.mktime((current_year, month_num, day_num, hour, minute, 0, 0, 0, -1))
    try:
        year = int(year_or_time)
    except ValueError:
        return 0.0
    return time.mktime((year, month_num, day_num, 0, 0, 0, 0, 0, -1))


class FtpTransport(RemoteTransport):
    """Plain (unencrypted) FTP transport."""

    def __init__(self, site: RemoteSite, *, password: str, timeout: float = 30.0) -> None:
        self._site = site
        self._password = password
        self._timeout = timeout
        self._conn: ftplib.FTP | None = None

    # --- lifecycle -----------------------------------------------------------

    def _connect(self) -> ftplib.FTP:
        if self._conn is not None:
            return self._conn
        host = self._site.host
        port = self._site.port or 21
        try:
            conn = ftplib.FTP()
            conn.connect(host, port, timeout=self._timeout)
            conn.login(self._site.username or "anonymous", self._password or "anonymous@")
        except ftplib.error_perm as exc:
            raise RemoteAuthError(str(exc).strip() or "FTP login failed") from exc
        except (TimeoutError, socket.gaierror, OSError) as exc:
            raise RemoteTransportError(f"Could not connect to {host}: {exc}") from exc
        self._conn = conn
        return conn

    def close(self) -> None:
        if self._conn is not None:
            try:
                self._conn.quit()
            except (ftplib.Error, OSError):
                try:
                    self._conn.close()
                except (ftplib.Error, OSError):
                    pass
            self._conn = None

    # --- public API ----------------------------------------------------------

    def list_dir(self, path: str) -> list[RemoteEntry]:
        conn = self._connect()
        target = path or self._site.root_dir or "/"
        buf: list[str] = []
        try:
            conn.retrlines(f"LIST {target}", buf.append)
        except ftplib.error_perm as exc:
            message = str(exc).strip()
            if message.startswith("550"):
                raise RemoteNotFoundError(message) from exc
            raise RemoteTransportError(message or "FTP LIST failed") from exc
        return _ListingParser.parse("\n".join(buf))

    def download(
        self,
        remote_path: str,
        local_path: str,
        *,
        progress: ProgressCallback | None = None,
    ) -> DownloadResult:
        conn = self._connect()
        start = time.monotonic()
        total: int | None = None
        try:
            size = conn.size(remote_path)
            total = int(str(size)) if size is not None else None
        except ftplib.error_perm:
            total = None
        with open(local_path, "wb") as dest:
            source = io.BytesIO()
            try:
                conn.retrbinary(f"RETR {remote_path}", source.write, blocksize=64 * 1024)
            except ftplib.error_perm as exc:
                message = str(exc).strip()
                if message.startswith("550"):
                    raise RemoteNotFoundError(message) from exc
                raise RemoteTransportError(message or "FTP RETR failed") from exc
            source.seek(0)
            written = chunked_copy(source, dest, total=total, progress=progress)
        return DownloadResult(
            path=local_path,
            size=written,
            mime_type="",
            elapsed_ms=int((time.monotonic() - start) * 1000),
            headers=merge_headers([]),
        )

    def upload(
        self,
        local_path: str,
        remote_path: str,
        *,
        progress: ProgressCallback | None = None,
    ) -> DownloadResult:
        conn = self._connect()
        start = time.monotonic()
        with open(local_path, "rb") as source:
            total = _file_size(source)
            dest = io.BytesIO()
            chunked_copy(source, dest, total=total, progress=progress)
            data = dest.getvalue()
        try:
            conn.storbinary(f"STOR {remote_path}", io.BytesIO(data))
        except ftplib.error_perm as exc:
            message = str(exc).strip()
            if message.startswith("550"):
                raise RemoteNotFoundError(message) from exc
            raise RemoteTransportError(message or "FTP STOR failed") from exc
        return DownloadResult(
            path=local_path,
            size=len(data),
            mime_type="",
            elapsed_ms=int((time.monotonic() - start) * 1000),
            headers=merge_headers([]),
        )


def _file_size(handle: IO[bytes]) -> int:
    current = handle.tell()
    handle.seek(0, io.SEEK_END)
    size = handle.tell()
    handle.seek(current)
    return size
