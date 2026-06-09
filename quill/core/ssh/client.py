"""SFTP file service for edit-over-SSH (issue #139).

:class:`SftpFileService` wraps an SFTP handle (paramiko's ``SFTPClient`` or any
object exposing the same ``listdir_attr``/``open``/``stat``/``rename`` methods)
so the browse + read + write-with-backup logic can be unit-tested with a fake,
no network or ``paramiko`` required.

:func:`connect` builds a real connection via ``paramiko`` and raises a plain,
actionable message when the optional dependency is not installed.
"""

from __future__ import annotations

import stat as stat_module
from dataclasses import dataclass

from quill.core.ssh.sites import AUTH_AGENT, AUTH_KEY, DEFAULT_PORT
from quill.core.ssh.transfer import backup_name

_INSTALL_HINT = (
    "Editing files over SSH needs the 'paramiko' package, which is not installed. "
    "Install it with: pip install paramiko"
)


class SshDependencyError(RuntimeError):
    """Raised when an SSH action is requested but ``paramiko`` is unavailable."""


@dataclass(slots=True)
class RemoteEntry:
    """One entry in a remote directory listing."""

    name: str
    is_dir: bool
    size: int
    mtime: float


class SftpFileService:
    """Browse and transfer files over an established SFTP handle."""

    def __init__(self, sftp: object) -> None:
        self._sftp = sftp

    def list_dir(self, path: str) -> list[RemoteEntry]:
        """List ``path``, directories first then files, each alphabetical."""
        entries: list[RemoteEntry] = []
        for attr in self._sftp.listdir_attr(path):  # type: ignore[attr-defined]
            mode = int(getattr(attr, "st_mode", 0) or 0)
            entries.append(
                RemoteEntry(
                    name=attr.filename,
                    is_dir=stat_module.S_ISDIR(mode),
                    size=int(getattr(attr, "st_size", 0) or 0),
                    mtime=float(getattr(attr, "st_mtime", 0) or 0),
                )
            )
        return sorted(entries, key=lambda entry: (not entry.is_dir, entry.name.lower()))

    def read_file(self, path: str) -> bytes:
        with self._sftp.open(path, "rb") as handle:  # type: ignore[attr-defined]
            return handle.read()

    def write_file(self, path: str, data: bytes, *, make_backup: bool = True) -> str | None:
        """Write ``data`` to ``path``, backing up any existing file as ``path~``.

        Returns the backup path when one was made, else ``None``. The backup is
        created by renaming the original (the conventional editor behaviour), so
        ``test.txt`` becomes ``test.txt~`` before the new content is written.
        """
        backup: str | None = None
        if make_backup and self._exists(path):
            backup = backup_name(path)
            self._replace(path, backup)
        with self._sftp.open(path, "wb") as handle:  # type: ignore[attr-defined]
            handle.write(data)
        return backup

    def _exists(self, path: str) -> bool:
        try:
            self._sftp.stat(path)  # type: ignore[attr-defined]
        except OSError:
            return False
        return True

    def _replace(self, src: str, dst: str) -> None:
        # POSIX rename overwrites an existing destination atomically; fall back to
        # remove-then-rename for servers without the posix-rename extension.
        posix_rename = getattr(self._sftp, "posix_rename", None)
        if callable(posix_rename):
            posix_rename(src, dst)
            return
        try:
            self._sftp.remove(dst)  # type: ignore[attr-defined]
        except OSError:
            pass
        self._sftp.rename(src, dst)  # type: ignore[attr-defined]


class SftpConnection:
    """An open SSH connection and its SFTP channel; a file-service factory."""

    def __init__(self, client: object, sftp: object) -> None:
        self._client = client
        self.service = SftpFileService(sftp)

    def close(self) -> None:
        for target in (getattr(self, "_client", None),):
            try:
                if target is not None:
                    target.close()
            except Exception:  # noqa: BLE001 - closing must never raise
                pass

    def __enter__(self) -> SftpConnection:
        return self

    def __exit__(self, *_exc: object) -> None:
        self.close()


def _import_paramiko():
    try:
        import paramiko  # type: ignore[import-not-found]
    except Exception as exc:  # noqa: BLE001
        raise SshDependencyError(_INSTALL_HINT) from exc
    return paramiko


def connect(
    host: str,
    *,
    port: int = DEFAULT_PORT,
    username: str = "",
    password: str | None = None,
    auth: str = "password",
    key_path: str = "",
    key_passphrase: str | None = None,
    timeout: float = 15.0,
) -> SftpConnection:
    """Open an SSH/SFTP connection. Requires the optional ``paramiko`` package."""
    paramiko = _import_paramiko()
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    # Accept and cache unknown host keys (PuTTY-style first-connect behaviour). A
    # future pass can surface a host-key confirmation prompt in the UI.
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    pkey = None
    if auth == AUTH_KEY and key_path:
        from quill.core.ssh.keys import load_private_key

        pkey = load_private_key(key_path, key_passphrase)

    client.connect(
        hostname=host,
        port=port,
        username=username or None,
        password=password if auth == "password" else None,
        pkey=pkey,
        timeout=timeout,
        allow_agent=(auth == AUTH_AGENT),
        look_for_keys=(auth in (AUTH_AGENT, AUTH_KEY)),
    )
    return SftpConnection(client, client.open_sftp())
