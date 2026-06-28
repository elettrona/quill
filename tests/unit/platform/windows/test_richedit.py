"""Guards for the RichEdit margin tweak (braille cell-two experiment 1)."""

from __future__ import annotations

from quill.platform.windows import richedit


def test_zero_margins_rejects_falsy_handle() -> None:
    # No HWND -> safe no-op, never raises.
    assert richedit.zero_richedit_margins(0) is False
    assert richedit.zero_richedit_margins(None) is False


def test_em_setmargins_constants() -> None:
    # winuser.h values: EM_SETMARGINS=0x00D3, left=0x0001, right=0x0002.
    assert richedit._EM_SETMARGINS == 0x00D3
    assert richedit._EC_LEFTMARGIN | richedit._EC_RIGHTMARGIN == 0x0003


def test_settings_round_trip_braille_editor_flags() -> None:
    from quill.core.settings import Settings

    raw = {"editor_zero_richedit_margins": False, "editor_use_legacy_richedit": True}
    loaded = Settings.from_dict(raw) if hasattr(Settings, "from_dict") else None
    if loaded is None:
        import pytest

        pytest.skip("Settings.from_dict unavailable in this build")
    assert loaded.editor_zero_richedit_margins is False
    assert loaded.editor_use_legacy_richedit is True
    # Defaults: margin-zero on, legacy engine off.
    defaults = Settings()
    assert defaults.editor_zero_richedit_margins is True
    assert defaults.editor_use_legacy_richedit is False
