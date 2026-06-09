"""Newline-safe transfer between a remote file and the local editor (issue #139).

A config file edited on a Linux server uses LF; a script from an old Mac may use
CR; a file authored on Windows uses CRLF. When Quill downloads a remote file to
edit it, the editor works in normalised LF text; on save we must write the file
back in *its own* original newline style so a round trip never silently rewrites
every line ending (which would wreck diffs and, for some tools, break the file).

These functions are pure so they can be unit-tested without a network. Bytes are
decoded/encoded with ``surrogateescape`` so non-UTF-8 content round-trips
losslessly.
"""

from __future__ import annotations

NEWLINE_LF = "lf"
NEWLINE_CRLF = "crlf"
NEWLINE_CR = "cr"

_NEWLINE_BYTES = {
    NEWLINE_LF: b"\n",
    NEWLINE_CRLF: b"\r\n",
    NEWLINE_CR: b"\r",
}


def detect_newline(data: bytes) -> str:
    """Return the dominant newline style of ``data`` (defaults to LF).

    CRLF is checked before CR so a ``\\r\\n`` file is not misread as CR.
    """
    if b"\r\n" in data:
        return NEWLINE_CRLF
    if b"\r" in data:
        return NEWLINE_CR
    return NEWLINE_LF


def remote_to_editor(data: bytes) -> tuple[str, str]:
    """Decode remote bytes for editing.

    Returns ``(text, newline)`` where ``text`` is normalised to LF for the editor
    and ``newline`` records the file's original style so :func:`editor_to_remote`
    can restore it on save.
    """
    newline = detect_newline(data)
    text = data.decode("utf-8", errors="surrogateescape")
    normalised = text.replace("\r\n", "\n").replace("\r", "\n")
    return normalised, newline


def editor_to_remote(text: str, newline: str) -> bytes:
    """Re-apply the file's original ``newline`` style and encode for upload.

    ``text`` is the editor buffer (any newline convention); it is normalised to
    LF first so re-applying the target style cannot produce doubled ``\\r``.
    """
    normalised = text.replace("\r\n", "\n").replace("\r", "\n")
    line_ending = _NEWLINE_BYTES.get(newline, b"\n").decode("ascii")
    if line_ending != "\n":
        normalised = normalised.replace("\n", line_ending)
    return normalised.encode("utf-8", errors="surrogateescape")


def backup_name(remote_path: str) -> str:
    """Return the tilde backup name for ``remote_path`` (``test.txt`` -> ``test.txt~``).

    Operates on the POSIX-style remote path string; the trailing ``~`` is the
    conventional Unix backup suffix used by editors such as vi and emacs.
    """
    return f"{remote_path}~"
