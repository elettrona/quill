from __future__ import annotations

from quill.core import settings_registry as registry
from quill.core.settings import Settings
from quill.ui.main_frame import MainFrame


class _Frame:
    pass


def _build_frame() -> MainFrame:
    """Build a bare MainFrame with the side-effect methods stubbed out.

    The tabbed Settings dialog funnels OK, Import, and Reset through
    ``_settings_dialog_apply_refresh``; these tests exercise that shared path
    and the registry round-trip without constructing real wx widgets.
    """
    frame = MainFrame.__new__(MainFrame)
    frame.frame = _Frame()
    frame.settings = Settings()
    frame._status_message = ""
    frame._refresh_calls = []  # type: ignore[attr-defined]

    frame._set_status = lambda message: setattr(frame, "_status_message", message)
    # Record every side effect the apply path is expected to run.
    for name in (
        "set_theme",
        "_set_spellcheck_mode",
        "_apply_ai_menu_enabled",
        "_refresh_ai_status",
        "_apply_soft_wrap_setting",
        "_rebuild_tab_host",
        "_build_menu",
        "_apply_dirty_title_style_setting",
        "_refresh_title",
        "_refresh_view_menu_checks",
        "_clear_navigation_issue_state",
    ):
        setattr(
            frame,
            name,
            (lambda _n: lambda *a, **k: frame._refresh_calls.append(_n))(name),
        )
    return frame


def test_apply_refresh_saves_and_runs_side_effects(monkeypatch) -> None:
    frame = _build_frame()
    saved: list[Settings] = []
    monkeypatch.setattr("quill.ui.main_frame.save_settings", lambda s: saved.append(s))

    frame._settings_dialog_apply_refresh("Updated settings")

    assert saved == [frame.settings]
    assert frame._status_message == "Updated settings"
    # The headline refreshers must all fire so the UI stays consistent.
    for expected in ("set_theme", "_build_menu", "_rebuild_tab_host", "_refresh_title"):
        assert expected in frame._refresh_calls


def test_reset_all_returns_factory_defaults() -> None:
    frame = _build_frame()
    frame.settings = registry.set_value(frame.settings, "soft_wrap", not Settings().soft_wrap)

    frame.settings = registry.reset_all()

    assert frame.settings == Settings()


def test_set_value_round_trip_normalizes() -> None:
    settings = Settings()
    # recent_files_limit clamps to its 1..50 range via Settings.from_dict.
    updated = registry.set_value(settings, "recent_files_limit", 9999)

    assert updated.recent_files_limit <= 50


def test_export_import_settings_round_trip() -> None:
    settings = registry.set_value(Settings(), "theme", "dark")
    exported = registry.export_settings(settings)

    restored = registry.import_settings(exported)

    assert restored.theme == "dark"
    assert exported["schema_version"] == registry.SCHEMA_VERSION
