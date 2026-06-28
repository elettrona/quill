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

    loaded = Settings.from_dict(
        {"editor_zero_richedit_margins": False, "editor_control_kind": "plain"}
    )
    assert loaded.editor_zero_richedit_margins is False
    assert loaded.editor_control_kind == "plain"
    # Defaults: margin-zero on, RichEdit 3.0.
    defaults = Settings()
    assert defaults.editor_zero_richedit_margins is True
    assert defaults.editor_control_kind == "rich2"


def test_editor_control_kind_validates_and_is_back_compatible() -> None:
    from quill.core.settings import Settings

    # Unknown values fall back to the default.
    assert Settings.from_dict({"editor_control_kind": "bogus"}).editor_control_kind == "rich2"
    # The retired editor_use_legacy_richedit bool maps to "rich".
    assert Settings.from_dict({"editor_use_legacy_richedit": True}).editor_control_kind == "rich"
    assert Settings.from_dict({"editor_use_legacy_richedit": False}).editor_control_kind == "rich2"
