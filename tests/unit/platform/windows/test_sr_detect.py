import subprocess

import pytest

from quill.platform.windows import sr_detect
from quill.platform.windows.sr_detect import detect_screen_reader


def test_detect_screen_reader_nvda() -> None:
    snapshot = '"nvda.exe","1234","Console","1","10,000 K"\n'
    result = detect_screen_reader(snapshot)
    assert result.detected is True
    assert result.name == "NVDA"


def test_detect_screen_reader_jaws() -> None:
    snapshot = '"jfw.exe","4321","Console","1","20,000 K"\n'
    result = detect_screen_reader(snapshot)
    assert result.detected is True
    assert result.name == "JAWS"


def test_tasklist_snapshot_creates_no_console_window(monkeypatch: pytest.MonkeyPatch) -> None:
    """The tasklist probe must not flash a console window a screen reader can see."""
    captured: dict[str, object] = {}

    class _Result:
        stdout = '"jfw.exe","1","Console","1","1 K"\n'

    def fake_run(cmd: object, **kwargs: object) -> _Result:
        captured["cmd"] = cmd
        captured["kwargs"] = kwargs
        return _Result()

    monkeypatch.setattr(sr_detect.subprocess, "run", fake_run)
    out = sr_detect._tasklist_snapshot()

    assert "jfw.exe" in out
    assert list(captured["cmd"])[0] == "tasklist"  # type: ignore[arg-type]
    expected = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    assert captured["kwargs"]["creationflags"] == expected  # type: ignore[index]


def test_detect_screen_reader_none() -> None:
    snapshot = '"explorer.exe","111","Console","1","10,000 K"\n'
    result = detect_screen_reader(snapshot)
    assert result.detected is False
    assert result.name == "none"
