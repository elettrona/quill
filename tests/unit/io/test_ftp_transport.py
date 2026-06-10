"""Unit tests for the FTP transport's listing parser (issue #154).

We exercise the transport's public-facing logic without touching the network:
the ``_ListingParser`` translates the standard ``LIST`` text into
:class:`RemoteEntry` rows, and ``_parse_mlsd_time`` resolves the
``ls -l``-style time triplet into a POSIX timestamp. Both helpers are pure
functions and are the highest-value coverage for the unit suite.
"""

from __future__ import annotations

import time

from quill.io import ftp_transport
from quill.io.ftp_transport import _ListingParser, _parse_mlsd_time


def test_listing_parser_handles_ls_long_format() -> None:
    payload = "\n".join([
        "total 12",
        "-rw-r--r--   1 quill   quill        1234 Jan 01 12:00 name.txt",
        "drwxr-xr-x   2 quill   quill        4096 Feb 02 13:00 sub",
        "-rw-r--r--   1 quill   quill         500 Mar 03 14:30 notes.md",
        # Symlinks are not specially handled by the parser; the trailing "->"
        # is part of the name. This is the documented behaviour and matches
        # what the remote dialog shows the user.
        "lrwxrwxrwx   1 quill   quill           9 Apr 04 15:00 link -> name.txt",
    ])
    entries = _ListingParser.parse(payload)
    assert len(entries) == 4
    assert {entry.name for entry in entries} == {
        "name.txt",
        "sub",
        "notes.md",
        "link -> name.txt",
    }
    dirs = [entry for entry in entries if entry.is_dir]
    assert len(dirs) == 1
    assert dirs[0].name == "sub"
    files = [entry for entry in entries if entry.name == "name.txt"]
    assert files[0].size == 1234


def test_listing_parser_skips_dot_and_dotdot() -> None:
    payload = "\n".join([
        "drwxr-xr-x   2 quill   quill        4096 Jan 01 12:00 .",
        "drwxr-xr-x   2 quill   quill        4096 Jan 01 12:00 ..",
        "-rw-r--r--   1 quill   quill          10 Jan 01 12:00 visible.txt",
    ])
    entries = _ListingParser.parse(payload)
    assert [entry.name for entry in entries] == ["visible.txt"]


def test_listing_parser_handles_blank_lines() -> None:
    payload = "\n\n-rw-r--r--   1 quill   quill          1 Jan 01 12:00 only.txt\n\n"
    entries = _ListingParser.parse(payload)
    assert [entry.name for entry in entries] == ["only.txt"]


def test_listing_parser_ignores_short_lines() -> None:
    payload = "-rw-r--r-- only_three_columns"
    assert _ListingParser.parse(payload) == []


def test_listing_parser_ignores_unrecognised_permissions() -> None:
    payload = "?rw-r--r--  1 quill  quill  0 Jan 01 12:00 weird.txt"
    assert _ListingParser.parse(payload) == []


def test_parse_mlsd_time_handles_year_form() -> None:
    ts = _parse_mlsd_time("Jan", "01,", "2024")
    expected = time.mktime((2024, 1, 1, 0, 0, 0, 0, 0, -1))
    assert ts == expected


def test_parse_mlsd_time_handles_time_form() -> None:
    ts = _parse_mlsd_time("Feb", "02", "12:34")
    # Local-time stamp, so just assert it parses to a non-zero value in the
    # current year.
    assert ts > 0
    parsed = time.localtime(ts)
    assert parsed.tm_hour == 12
    assert parsed.tm_min == 34


def test_parse_mlsd_time_handles_unknown_month_gracefully() -> None:
    # Unknown months get mapped to 0; the rest of the function still uses
    # day/year and produces a valid epoch. We assert the function does not
    # raise rather than locking the exact epoch (which is timezone-sensitive).
    ts = _parse_mlsd_time("Foo", "01", "2024")
    assert ts > 0


def test_parse_mlsd_time_returns_zero_for_bad_time() -> None:
    # Non-time strings return 0.0; the implementation also yields 0.0 for the
    # day/empty-time combination.
    assert _parse_mlsd_time("Mar", "03", "not-a-time") == 0.0


def test_parse_mlsd_time_handles_bad_day_gracefully() -> None:
    # A non-numeric day does not raise; the implementation falls through to
    # the time branch, which yields a valid epoch. We assert it does not
    # raise rather than locking the exact epoch.
    ts = _parse_mlsd_time("Mar", "not-a-day", "12:34")
    assert ts > 0


def test_file_size_seeks_back_to_original_position() -> None:
    from io import BytesIO

    handle = BytesIO(b"abcdefghij")
    handle.seek(4)
    size = ftp_transport._file_size(handle)
    assert size == 10
    assert handle.tell() == 4
