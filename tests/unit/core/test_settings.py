from __future__ import annotations

from pathlib import Path

import pytest

from quill.core.settings import STATUS_BAR_ITEMS, Settings, load_settings, save_settings


def test_settings_round_trip(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("QUILL_DATA_DIR", str(tmp_path))
    save_settings(
        Settings(
            theme="dark",
            keyboard_pack="VS Code",
            soft_wrap=False,
            wrap_find=False,
            browse_mode_wrap=False,
            browse_mode_feedback="both",
            browse_mode_preload_cache=False,
            csv_open_mode="grid",
            word_open_mode="structured",
            indent_with_tabs=True,
            indent_size=2,
            auto_check_updates=True,
            recent_files_limit=7,
            tray_enabled=True,
            persistent_undo=True,
            spellcheck_as_you_type=True,
            intellisense_as_you_type=True,
            preview_browser="edge",
            title_bar_path_mode="full_path",
            dirty_title_style="asterisk_text",
            announcement_backend="prism",
            announcement_trace_enabled=True,
            assistant_enabled=True,
            assistant_prompt_style="technical",
            bw_speech_selection_mode="manual",
            bw_speech_model_id="whisper-small",
            bw_provider_id="openai_whisper",
            bw_provider_mode="cloud_first",
            bw_show_cloud_providers=False,
            bw_auto_open_status_page_on_download_start=True,
            bw_safe_mode_lock=True,
            status_page_refresh_announcement_cadence="verbose",
            watch_folder_enabled=True,
            watch_folder_path="C:\\incoming-audio",
            watch_folder_include_subfolders=True,
            watch_folder_process_existing=True,
            watch_folder_auto_start=True,
            watch_folder_poll_interval_seconds=12,
            status_bar_order=["line_column", "mode", "message", "file_path", "selection"],
            status_bar_hidden=["selection"],
        )
    )
    loaded = load_settings()
    assert loaded.theme == "dark"
    assert loaded.keyboard_pack == "VS Code"
    assert loaded.soft_wrap is False
    assert loaded.wrap_find is False
    assert loaded.browse_mode_wrap is False
    assert loaded.browse_mode_feedback == "both"
    assert loaded.browse_mode_preload_cache is False
    assert loaded.csv_open_mode == "grid"
    assert loaded.word_open_mode == "structured"
    assert loaded.indent_with_tabs is True
    assert loaded.indent_size == 2
    assert loaded.auto_check_updates is True
    assert loaded.recent_files_limit == 7
    assert loaded.tray_enabled is True
    assert loaded.persistent_undo is True
    assert loaded.spellcheck_as_you_type is True
    assert loaded.intellisense_as_you_type is True
    assert loaded.preview_browser == "edge"
    assert loaded.snippet_trigger_expansion is True
    assert loaded.title_bar_path_mode == "full_path"
    assert loaded.dirty_title_style == "asterisk_text"
    assert loaded.announcement_backend == "prism"
    assert loaded.announcement_trace_enabled is True
    assert loaded.assistant_enabled is True
    assert loaded.assistant_prompt_style == "technical"
    assert loaded.bw_speech_selection_mode == "manual"
    assert loaded.bw_speech_model_id == "whisper-small"
    assert loaded.bw_provider_id == "openai_whisper"
    assert loaded.bw_provider_mode == "cloud_first"
    assert loaded.bw_show_cloud_providers is False
    assert loaded.bw_auto_open_status_page_on_download_start is True
    assert loaded.bw_safe_mode_lock is True
    assert loaded.status_page_refresh_announcement_cadence == "verbose"
    assert loaded.watch_folder_enabled is True
    assert loaded.watch_folder_path == "C:\\incoming-audio"
    assert loaded.watch_folder_include_subfolders is True
    assert loaded.watch_folder_process_existing is True
    assert loaded.watch_folder_auto_start is True
    assert loaded.watch_folder_poll_interval_seconds == 12
    assert loaded.show_tab_control is False
    expected_order = list(
        dict.fromkeys([
            "line_column",
            "mode",
            "message",
            "file_path",
            "selection",
            *STATUS_BAR_ITEMS,
        ])
    )
    assert loaded.status_bar_order == expected_order
    assert loaded.status_bar_hidden == ["selection"]


def test_settings_default_dictation_policy(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("QUILL_DATA_DIR", str(tmp_path))
    loaded = load_settings()
    assert loaded.dictation_max_locked_seconds == 300.0
    assert loaded.dictation_stop_on_focus_loss is True
    assert loaded.dictation_intelligent_spacing is True
    assert loaded.dictation_min_hold_seconds == 0.0


def test_settings_dictation_policy_round_trip(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("QUILL_DATA_DIR", str(tmp_path))
    save_settings(
        Settings(
            dictation_max_locked_seconds=120.0,
            dictation_stop_on_focus_loss=False,
            dictation_intelligent_spacing=False,
            dictation_min_hold_seconds=0.25,
        )
    )
    loaded = load_settings()
    assert loaded.dictation_max_locked_seconds == 120.0
    assert loaded.dictation_stop_on_focus_loss is False
    assert loaded.dictation_intelligent_spacing is False
    assert loaded.dictation_min_hold_seconds == 0.25


def test_settings_clamp_negative_dictation_durations(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("QUILL_DATA_DIR", str(tmp_path))
    (tmp_path / "settings.json").write_text(
        '{"dictation_max_locked_seconds":-5,"dictation_min_hold_seconds":"oops"}',
        encoding="utf-8",
    )
    loaded = load_settings()
    assert loaded.dictation_max_locked_seconds == 0.0  # negative clamped to 0
    assert loaded.dictation_min_hold_seconds == 0.0  # malformed falls back to default


def test_settings_persists_list_studio_settings(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("QUILL_DATA_DIR", str(tmp_path))
    save_settings(Settings(list_studio_settings={"verbosity": "detailed", "markdown_loose": True}))
    loaded = load_settings()
    assert loaded.list_studio_settings == {"verbosity": "detailed", "markdown_loose": True}


def test_settings_list_studio_settings_defaults_empty_and_ignores_garbage(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("QUILL_DATA_DIR", str(tmp_path))
    (tmp_path / "settings.json").write_text(
        '{"list_studio_settings": "not-a-dict"}', encoding="utf-8"
    )
    assert load_settings().list_studio_settings == {}


def test_settings_persists_tts_normalization(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("QUILL_DATA_DIR", str(tmp_path))
    save_settings(
        Settings(tts_normalization_enabled=False, tts_normalization={"dash_mode": "hyphen"})
    )
    loaded = load_settings()
    assert loaded.tts_normalization_enabled is False
    assert loaded.tts_normalization == {"dash_mode": "hyphen"}


def test_settings_clamps_recent_file_limit(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("QUILL_DATA_DIR", str(tmp_path))
    save_settings(Settings(recent_files_limit=1000))
    loaded = load_settings()
    assert loaded.recent_files_limit == 50


def test_settings_clamps_indent_size(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("QUILL_DATA_DIR", str(tmp_path))
    (tmp_path / "settings.json").write_text(
        '{"indent_size":0,"indent_with_tabs":1}',
        encoding="utf-8",
    )
    loaded = load_settings()
    assert loaded.indent_size == 1
    assert loaded.indent_with_tabs is True


def test_settings_normalize_status_bar_layout(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("QUILL_DATA_DIR", str(tmp_path))
    (tmp_path / "settings.json").write_text(
        (
            '{"status_bar_order":["line_column","line_column","unknown"],'
            '"status_bar_hidden":["line_column","missing"]}'
        ),
        encoding="utf-8",
    )
    loaded = load_settings()
    expected_order = list(dict.fromkeys(["line_column", *STATUS_BAR_ITEMS]))
    assert loaded.status_bar_order == expected_order
    assert loaded.status_bar_hidden == ["line_column"]


def test_settings_normalize_announcement_backend(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("QUILL_DATA_DIR", str(tmp_path))
    (tmp_path / "settings.json").write_text(
        '{"announcement_backend":"not-real","announcement_trace_enabled":1}',
        encoding="utf-8",
    )

    loaded = load_settings()

    assert loaded.announcement_backend == "auto"
    assert loaded.announcement_trace_enabled is True


def test_settings_defaults_snippet_trigger_expansion_to_true(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("QUILL_DATA_DIR", str(tmp_path))
    (tmp_path / "settings.json").write_text("{}", encoding="utf-8")
    loaded = load_settings()
    assert loaded.snippet_trigger_expansion is True


def test_settings_defaults_intellisense_to_false(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("QUILL_DATA_DIR", str(tmp_path))
    loaded = load_settings()
    assert loaded.intellisense_as_you_type is False


def test_settings_defaults_preview_browser_to_system(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("QUILL_DATA_DIR", str(tmp_path))
    loaded = load_settings()
    assert loaded.preview_browser == "system"


def test_settings_defaults_browse_mode_to_enabled_wrap_and_speech(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("QUILL_DATA_DIR", str(tmp_path))
    loaded = load_settings()
    assert loaded.browse_mode_wrap is True
    assert loaded.browse_mode_feedback == "speech"
    assert loaded.browse_mode_preload_cache is True


def test_settings_normalize_invalid_browse_mode_feedback(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("QUILL_DATA_DIR", str(tmp_path))
    (tmp_path / "settings.json").write_text(
        '{"browse_mode_feedback":"loud"}',
        encoding="utf-8",
    )
    loaded = load_settings()
    assert loaded.browse_mode_feedback == "speech"


def test_settings_defaults_csv_open_mode_to_prompt(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("QUILL_DATA_DIR", str(tmp_path))
    loaded = load_settings()
    assert loaded.csv_open_mode == "prompt"


def test_settings_normalize_invalid_csv_open_mode(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("QUILL_DATA_DIR", str(tmp_path))
    (tmp_path / "settings.json").write_text('{"csv_open_mode":"nope"}', encoding="utf-8")
    loaded = load_settings()
    assert loaded.csv_open_mode == "prompt"


def test_settings_defaults_word_open_mode_to_prompt(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("QUILL_DATA_DIR", str(tmp_path))
    loaded = load_settings()
    assert loaded.word_open_mode == "prompt"


def test_settings_normalize_invalid_word_open_mode(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("QUILL_DATA_DIR", str(tmp_path))
    (tmp_path / "settings.json").write_text('{"word_open_mode":"nope"}', encoding="utf-8")
    loaded = load_settings()
    assert loaded.word_open_mode == "prompt"


def test_settings_default_hides_tab_control(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("QUILL_DATA_DIR", str(tmp_path))
    loaded = load_settings()
    assert loaded.show_tab_control is False


def test_settings_defaults_assistant_to_disabled(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("QUILL_DATA_DIR", str(tmp_path))
    loaded = load_settings()
    assert loaded.assistant_enabled is False
    assert loaded.assistant_prompt_style == "balanced"


def test_settings_glow_engine_on_by_default_network_features_off(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("QUILL_DATA_DIR", str(tmp_path))
    loaded = load_settings()
    # GLOW engine is enabled by default; optional networked features stay off.
    assert loaded.glow_enabled is True
    assert loaded.glow_ai_alt_text_consent is False
    assert loaded.glow_pii_redaction_consent is False
    assert loaded.glow_language_processing_consent is False


def test_settings_glow_consent_round_trips(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("QUILL_DATA_DIR", str(tmp_path))
    (tmp_path / "settings.json").write_text(
        '{"glow_enabled":false,"glow_ai_alt_text_consent":true,'
        '"glow_pii_redaction_consent":true,"glow_language_processing_consent":true}',
        encoding="utf-8",
    )
    loaded = load_settings()
    assert loaded.glow_enabled is False
    assert loaded.glow_ai_alt_text_consent is True
    assert loaded.glow_pii_redaction_consent is True
    assert loaded.glow_language_processing_consent is True


def test_settings_indent_tone_scale_round_trips(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("QUILL_DATA_DIR", str(tmp_path))
    (tmp_path / "settings.json").write_text(
        '{"indent_tone_scale":"pentatonic"}',
        encoding="utf-8",
    )
    loaded = load_settings()
    assert loaded.indent_tone_scale == "pentatonic"


def test_settings_rejects_unknown_indent_tone_scale(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("QUILL_DATA_DIR", str(tmp_path))
    (tmp_path / "settings.json").write_text(
        '{"indent_tone_scale":"bogus"}',
        encoding="utf-8",
    )
    loaded = load_settings()
    # Unknown scales fall back to off rather than loading a missing pack.
    assert loaded.indent_tone_scale == ""


def test_settings_clamps_watch_folder_poll_interval(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("QUILL_DATA_DIR", str(tmp_path))
    (tmp_path / "settings.json").write_text(
        '{"watch_folder_poll_interval_seconds":0}',
        encoding="utf-8",
    )
    loaded = load_settings()
    assert loaded.watch_folder_poll_interval_seconds == 2


def test_settings_normalize_bw_speech_selection_mode(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("QUILL_DATA_DIR", str(tmp_path))
    (tmp_path / "settings.json").write_text(
        '{"bw_speech_selection_mode":"invalid"}',
        encoding="utf-8",
    )
    loaded = load_settings()
    assert loaded.bw_speech_selection_mode == "recommended"


def test_settings_normalize_bw_provider_mode(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("QUILL_DATA_DIR", str(tmp_path))
    (tmp_path / "settings.json").write_text(
        '{"bw_provider_mode":"invalid"}',
        encoding="utf-8",
    )
    loaded = load_settings()
    assert loaded.bw_provider_mode == "local_first"


def test_settings_normalize_status_page_refresh_announcement_cadence(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("QUILL_DATA_DIR", str(tmp_path))
    (tmp_path / "settings.json").write_text(
        '{"status_page_refresh_announcement_cadence":"invalid"}',
        encoding="utf-8",
    )
    loaded = load_settings()
    assert loaded.status_page_refresh_announcement_cadence == "quiet"


def test_shell_verb_settings_round_trip(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("QUILL_DATA_DIR", str(tmp_path))
    save_settings(
        Settings(
            shell_integration_enabled=True,
            shell_verb_ocr=False,
            shell_verb_ocr_structured=True,
            shell_verb_open=False,
            shell_verb_read=True,
            shell_file_types="images",
        )
    )
    loaded = load_settings()
    assert loaded.shell_integration_enabled is True
    assert loaded.shell_verb_ocr is False
    assert loaded.shell_verb_ocr_structured is True
    assert loaded.shell_verb_open is False
    assert loaded.shell_verb_read is True
    assert loaded.shell_file_types == "images"


def test_settings_normalize_invalid_shell_file_types(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("QUILL_DATA_DIR", str(tmp_path))
    (tmp_path / "settings.json").write_text(
        '{"shell_file_types":"nonsense"}',
        encoding="utf-8",
    )
    loaded = load_settings()
    assert loaded.shell_file_types == "images_pdf"


def test_settings_defaults_announcement_startup_tips_to_off(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("QUILL_DATA_DIR", str(tmp_path))
    loaded = load_settings()
    assert loaded.announcement_startup_tips_enabled is False


def test_settings_round_trip_announcement_startup_tips(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("QUILL_DATA_DIR", str(tmp_path))
    save_settings(Settings(announcement_startup_tips_enabled=True))
    loaded = load_settings()
    assert loaded.announcement_startup_tips_enabled is True


def test_announcement_startup_tips_setting_is_registered() -> None:
    from quill.core.settings_registry import find_spec

    spec = find_spec("announcement_startup_tips_enabled")
    assert spec is not None
    assert spec.kind == "bool"
    assert spec.group == "accessibility"
    assert "announcement" in spec.keywords


def test_settings_defaults_verbosity_speech_to_on(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("QUILL_DATA_DIR", str(tmp_path))
    loaded = load_settings()
    assert loaded.verbosity_speech_enabled is True


def test_settings_round_trip_verbosity_speech(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("QUILL_DATA_DIR", str(tmp_path))
    save_settings(Settings(verbosity_speech_enabled=False))
    loaded = load_settings()
    assert loaded.verbosity_speech_enabled is False


def test_settings_defaults_announce_screen_reader_detected_to_off(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("QUILL_DATA_DIR", str(tmp_path))
    loaded = load_settings()
    assert loaded.announce_screen_reader_detected is False


def test_settings_round_trip_announce_screen_reader_detected(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("QUILL_DATA_DIR", str(tmp_path))
    save_settings(Settings(announce_screen_reader_detected=True))
    loaded = load_settings()
    assert loaded.announce_screen_reader_detected is True


def test_verbosity_speech_setting_is_registered() -> None:
    from quill.core.settings_registry import find_spec

    spec = find_spec("verbosity_speech_enabled")
    assert spec is not None
    assert spec.kind == "bool"
    assert spec.group == "accessibility"


def test_announce_screen_reader_detected_setting_is_registered() -> None:
    from quill.core.settings_registry import find_spec

    spec = find_spec("announce_screen_reader_detected")
    assert spec is not None
    assert spec.kind == "bool"
    assert spec.group == "accessibility"


# --- #269: setup-wizard intent + extras fields ---------------------------


def test_settings_wizard_intent_fields_have_defaults() -> None:
    # #269: the wizard dialog writes setup_wizard_intent and the three
    # setup_wizard_wants_* flags onto the Settings object on Finish. The
    # dataclass uses slots=True, so any field that is not declared raises
    # AttributeError on assignment. The defaults below also match the
    # getattr fallbacks that main_frame.run_startup_wizard historically used
    # when these fields were not persisted.
    settings = Settings()
    assert settings.setup_wizard_intent == ""
    assert settings.setup_wizard_wants_ai is False
    assert settings.setup_wizard_wants_braille is False
    assert settings.setup_wizard_wants_automation is False


def test_settings_wizard_intent_round_trip(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    # #269: ensure the wizard's choice survives a save/reload cycle so the
    # next launch applies the same Quillin profile the user originally picked.
    monkeypatch.setenv("QUILL_DATA_DIR", str(tmp_path))
    save_settings(
        Settings(
            setup_wizard_completed=True,
            setup_wizard_intent="writer",
            setup_wizard_wants_ai=True,
            setup_wizard_wants_braille=False,
            setup_wizard_wants_automation=True,
        )
    )
    loaded = load_settings()
    assert loaded.setup_wizard_completed is True
    assert loaded.setup_wizard_intent == "writer"
    assert loaded.setup_wizard_wants_ai is True
    assert loaded.setup_wizard_wants_braille is False
    assert loaded.setup_wizard_wants_automation is True


def test_settings_wizard_intent_rejects_non_string_payload() -> None:
    # #269: a legacy settings.json containing a non-string intent value
    # (e.g. an int left over from an earlier schema draft) must be coerced
    # to a string rather than crashing the wizard on the next launch.
    settings = Settings.from_dict({"setup_wizard_intent": 42})
    assert settings.setup_wizard_intent == "42"
