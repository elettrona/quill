from __future__ import annotations

from pathlib import Path


def _source() -> str:
    return (Path(__file__).resolve().parents[3] / "quill" / "ui" / "main_frame.py").read_text(
        encoding="utf-8"
    )


def test_share_export_dialog_uses_accessible_controls_and_helper() -> None:
    source = _source()
    assert "def open_share_export_dialog(self) -> None:" in source
    assert 'title="Export and Back Up"' in source
    assert "gather_export_offers(self.settings, self.features)" in source
    assert "build_export_document(" in source
    assert "write_export(document, target)" in source
    assert "apply_modal_ids(dialog, affirmative_id=wx.ID_OK, escape_id=wx.ID_CANCEL)" in source
    # Privacy: profile mode disables and unchecks any private section.
    assert "if offer.private:" in source


def test_share_import_dialog_previews_and_applies_with_rollback() -> None:
    source = _source()
    assert "def open_share_import_dialog(self) -> None:" in source
    assert 'title="Import and Restore"' in source
    assert "read_import(source)" in source
    assert "package_summary(package)" in source
    assert "importable_sections(package)" in source
    assert "apply_import(package, selected_ids, self.settings, self.features)" in source
    # Imported settings go through the shared persist-and-refresh path.
    assert "self._settings_dialog_apply_refresh(" in source


def test_share_dialogs_registered_and_wired_in_menu() -> None:
    source = _source()
    assert '"tools.share_export"' in source
    assert '"tools.share_import"' in source
    assert "self._id_share_export = wx.NewIdRef()" in source
    assert "self._id_share_import = wx.NewIdRef()" in source
    assert 'customize_menu.Append(self._id_share_export, "&Export and Back Up...")' in source
    assert 'customize_menu.Append(self._id_share_import, "&Import or Restore...")' in source
