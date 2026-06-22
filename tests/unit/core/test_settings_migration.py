from __future__ import annotations

from dataclasses import asdict

from quill.core.settings import Settings
from quill.core.settings_migration import (
    SETTINGS_SCHEMA_VERSION,
    UNGROUPED_KEY,
    from_versioned,
    migrate,
    to_versioned,
)


def test_versioned_document_is_nested_and_versioned() -> None:
    doc = to_versioned(Settings())
    assert doc["schema_version"] == SETTINGS_SCHEMA_VERSION
    assert isinstance(doc["groups"], dict)
    # A registry-backed field lands under its group, not the ungrouped bucket.
    assert "theme" in doc["groups"].get("general", {})


def test_round_trip_is_lossless() -> None:
    original = Settings(
        theme="dark",
        read_aloud_rate=275,
        autosave_interval_seconds=120,
        announce_wrap=False,
        status_bar_hidden=["encoding", "selection"],
    )
    restored = from_versioned(to_versioned(original))
    assert restored == original


def test_every_field_is_serialized_somewhere() -> None:
    doc = to_versioned(Settings())
    serialized: set[str] = set()
    for bucket in doc["groups"].values():
        serialized.update(bucket)
    assert serialized == set(asdict(Settings()).keys())


def test_legacy_flat_document_migrates() -> None:
    legacy = {"theme": "dark", "read_aloud_rate": 300, "soft_wrap": False}
    settings = from_versioned(legacy)
    assert settings.theme == "dark"
    assert settings.read_aloud_rate == 300
    assert settings.soft_wrap is False


def test_corrupt_value_recovers_without_losing_siblings() -> None:
    doc = to_versioned(Settings(theme="dark"))
    # Corrupt one value inside a group; siblings must survive.
    doc["groups"]["read_aloud"]["read_aloud_rate"] = "not-a-number"
    settings = from_versioned(doc)
    assert settings.theme == "dark"  # preserved
    assert settings.read_aloud_rate == Settings().read_aloud_rate  # defaulted


def test_migrate_handles_junk() -> None:
    assert migrate(None) == {}
    assert migrate(42) == {}
    assert migrate({"groups": "broken"}) == {}


def test_unspecced_fields_go_to_ungrouped() -> None:
    doc = to_versioned(Settings())
    # status_bar_order has no registry spec; it must still be serialized.
    assert "status_bar_order" in doc["groups"].get(UNGROUPED_KEY, {})


def test_dictation_engine_legacy_values_migrate_to_offline() -> None:
    # The legacy local-recognizer values never actually ran; preserve the user's
    # local/offline intent by mapping them to "offline" (Speech wave S0, #617).
    assert Settings.from_dict({"dictation_engine": "vosk"}).dictation_engine == "offline"
    assert Settings.from_dict({"dictation_engine": "whisper"}).dictation_engine == "offline"


def test_dictation_engine_unknown_defaults_to_windows() -> None:
    assert Settings.from_dict({"dictation_engine": "bogus"}).dictation_engine == "windows"
    # Windows dictation is the only functional engine today, so it is the default.
    assert Settings.from_dict({}).dictation_engine == "windows"


def test_dictation_engine_valid_values_pass_through() -> None:
    for value in ("offline", "windows", "cloud"):
        assert Settings.from_dict({"dictation_engine": value}).dictation_engine == value
