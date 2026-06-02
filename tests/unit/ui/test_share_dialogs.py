from __future__ import annotations

import pytest

from quill.core.features import FeatureManager
from quill.core.settings import Settings
from quill.core.share_package import (
    KIND_BACKUP,
    KIND_PROFILE,
    SECTION_FEATURES,
    SECTION_SETTINGS,
    PrivacyError,
    private_fields_present,
    read_package,
)
from quill.ui.share_dialogs import (
    SectionOffer,
    apply_import,
    build_export_document,
    gather_export_offers,
    importable_sections,
    read_import,
    write_export,
)


@pytest.fixture(autouse=True)
def _redirect_app_data(tmp_path, monkeypatch):
    monkeypatch.setenv("QUILL_DATA_DIR", str(tmp_path / "appdata"))


def _features() -> FeatureManager:
    return FeatureManager()


def test_gather_offers_lists_settings_and_features() -> None:
    offers = gather_export_offers(Settings(), _features())
    ids = {offer.id for offer in offers}
    assert ids == {SECTION_SETTINGS, SECTION_FEATURES}
    assert all(not offer.private for offer in offers)


def test_build_export_requires_a_section() -> None:
    offers = gather_export_offers(Settings(), _features())
    with pytest.raises(ValueError):
        build_export_document(
            kind=KIND_BACKUP,
            name="x",
            source_version="0.1.5",
            selected_ids=[],
            offers=offers,
        )


def test_profile_export_is_privacy_clean() -> None:
    settings = Settings(theme="dark", watch_folder_path=r"D:\watch")
    offers = gather_export_offers(settings, _features())
    document = build_export_document(
        kind=KIND_PROFILE,
        name="Share me",
        source_version="0.1.5",
        selected_ids=[SECTION_SETTINGS, SECTION_FEATURES],
        offers=offers,
    )
    assert private_fields_present(document) == []
    inner = document["sections"][SECTION_SETTINGS]["settings"]  # type: ignore[index]
    assert "watch_folder_path" not in inner
    assert inner["theme"] == "dark"


def test_round_trip_apply_restores_settings_and_features(tmp_path) -> None:
    source_settings = Settings(theme="dark", read_aloud_rate=275)
    source_features = _features()
    source_features.import_profile_data(
        {"schema_version": 1, "active_profile_id": "writer", "overrides": {}}
    )
    offers = gather_export_offers(source_settings, source_features)
    document = build_export_document(
        kind=KIND_BACKUP,
        name="Everything",
        source_version="0.1.5",
        selected_ids=[SECTION_SETTINGS, SECTION_FEATURES],
        offers=offers,
    )
    path = tmp_path / "backup.quillbackup"
    write_export(document, path)

    package = read_import(path)
    rows = {row[0] for row in importable_sections(package)}
    assert rows == {SECTION_SETTINGS, SECTION_FEATURES}

    target_settings = Settings()
    target_features = _features()
    outcome = apply_import(
        package, [SECTION_SETTINGS, SECTION_FEATURES], target_settings, target_features
    )
    assert outcome.settings is not None
    assert outcome.settings.theme == "dark"
    assert outcome.settings.read_aloud_rate == 275
    assert target_features.active_profile_id == "writer"
    assert len(outcome.applied) == 2


def test_apply_only_selected_sections() -> None:
    offers = gather_export_offers(Settings(theme="dark"), _features())
    document = build_export_document(
        kind=KIND_BACKUP,
        name="x",
        source_version="0.1.5",
        selected_ids=[SECTION_SETTINGS, SECTION_FEATURES],
        offers=offers,
    )
    package = read_package(document)
    target_features = _features()
    outcome = apply_import(package, [SECTION_SETTINGS], Settings(), target_features)
    assert outcome.settings is not None
    assert outcome.applied == ["Settings"]


def test_apply_rolls_back_features_on_failure() -> None:
    offers = gather_export_offers(Settings(), _features())
    document = build_export_document(
        kind=KIND_BACKUP,
        name="x",
        source_version="0.1.5",
        selected_ids=[SECTION_FEATURES],
        offers=offers,
    )
    package = read_package(document)
    package.sections[SECTION_FEATURES] = {"schema_version": 999}  # unsupported

    target_features = _features()
    target_features.import_profile_data(
        {"schema_version": 1, "active_profile_id": "writer", "overrides": {}}
    )
    before = target_features.active_profile_id
    with pytest.raises(ValueError):
        apply_import(package, [SECTION_FEATURES], Settings(), target_features)
    assert target_features.active_profile_id == before  # rolled back


def test_profile_refuses_private_section_via_helper() -> None:
    from quill.core.share_package import SECTION_SECRETS

    offers = [SectionOffer(SECTION_SECRETS, "Secrets", "Credentials.", True, {"k": "v"})]
    with pytest.raises(PrivacyError):
        build_export_document(
            kind=KIND_PROFILE,
            name="leak",
            source_version="0.1.5",
            selected_ids=[SECTION_SECRETS],
            offers=offers,
        )
