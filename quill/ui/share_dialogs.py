"""Portable profile / backup export and import helpers (SHARE-1, SHARE-2).

This module lives in the UI layer because it composes user-facing export and
import flows, but it imports only :mod:`quill.core` and never ``wx`` so the
whole export/import pipeline stays unit-testable without a display.  The
wxPython dialogs in :mod:`quill.ui.main_frame` are thin shells over the
functions defined here.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from quill.core.features import FeatureManager
from quill.core.settings import Settings
from quill.core.settings_registry import export_settings, import_settings
from quill.core.share_package import (
    SECTION_FEATURES,
    SECTION_SETTINGS,
    Package,
    SectionSpec,
    build_package,
    read_package_file,
    section_spec,
    write_package_file,
)


def _spec(section_id: str) -> SectionSpec:
    spec = section_spec(section_id)
    if spec is None:  # pragma: no cover - section ids are module constants
        raise KeyError(section_id)
    return spec


@dataclass(frozen=True, slots=True)
class SectionOffer:
    """A section the user may include when exporting."""

    id: str
    title: str
    summary: str
    private: bool
    payload: object


@dataclass(slots=True)
class ImportOutcome:
    """The result of applying selected sections from a package."""

    settings: Settings | None = None
    warnings: list[str] = field(default_factory=list)
    applied: list[str] = field(default_factory=list)


def gather_export_offers(settings: Settings, features: FeatureManager) -> list[SectionOffer]:
    """Collect the sections currently available to export.

    Only the sections QUILL can faithfully serialize today are offered
    (settings and the feature profile).  The package format itself supports
    more sections, which can be wired in here as their serializers land.
    """
    offers: list[SectionOffer] = []
    for section_id, payload in (
        (SECTION_SETTINGS, export_settings(settings)),
        (SECTION_FEATURES, features.export_profile_data()),
    ):
        spec = _spec(section_id)
        offers.append(
            SectionOffer(
                id=spec.id,
                title=spec.title,
                summary=spec.summary,
                private=spec.private,
                payload=payload,
            )
        )
    return offers


def build_export_document(
    *,
    kind: str,
    name: str,
    source_version: str,
    selected_ids: list[str] | set[str],
    offers: list[SectionOffer],
) -> dict[str, object]:
    """Build a package document from the chosen offers."""
    chosen = set(selected_ids)
    sections = {offer.id: offer.payload for offer in offers if offer.id in chosen}
    if not sections:
        raise ValueError("Choose at least one section to include.")
    return build_package(
        kind=kind,
        name=name,
        source_version=source_version,
        sections=sections,
    )


def write_export(document: dict[str, object], path: str | Path) -> None:
    """Write a built package document to disk."""
    write_package_file(document, Path(path))


def read_import(path: str | Path) -> Package:
    """Read and validate a package from disk."""
    return read_package_file(Path(path))


def importable_sections(package: Package) -> list[tuple[str, str, str]]:
    """Return ``(id, title, summary)`` for every section QUILL can apply."""
    rows: list[tuple[str, str, str]] = []
    for section_id in package.sections:
        if section_id not in _APPLIERS:
            continue
        spec = _spec(section_id)
        rows.append((spec.id, spec.title, spec.summary))
    return rows


def apply_import(
    package: Package,
    selected_ids: list[str] | set[str],
    settings: Settings,
    features: FeatureManager,
) -> ImportOutcome:
    """Apply the selected sections, rolling back features on any failure.

    A snapshot of the feature state is taken before any change so a partial
    failure leaves the manager untouched.  Settings are returned as a new
    :class:`Settings` rather than mutated, so the caller controls persistence.
    """
    chosen = set(selected_ids)
    outcome = ImportOutcome(settings=None)
    feature_snapshot = features.export_profile_data()
    try:
        for section_id in package.sections:
            if section_id not in chosen or section_id not in _APPLIERS:
                continue
            _APPLIERS[section_id](package, settings, features, outcome)
    except Exception:
        # Restore the feature manager to its pre-import state.
        features.import_profile_data(feature_snapshot)
        raise
    return outcome


def _apply_settings(
    package: Package,
    _settings: Settings,
    _features: FeatureManager,
    outcome: ImportOutcome,
) -> None:
    payload = package.sections[SECTION_SETTINGS]
    outcome.settings = import_settings(payload)
    outcome.applied.append(_spec(SECTION_SETTINGS).title)


def _apply_features(
    package: Package,
    _settings: Settings,
    features: FeatureManager,
    outcome: ImportOutcome,
) -> None:
    payload = package.sections[SECTION_FEATURES]
    outcome.warnings.extend(features.import_profile_data(payload))
    outcome.applied.append(_spec(SECTION_FEATURES).title)


_APPLIERS = {
    SECTION_SETTINGS: _apply_settings,
    SECTION_FEATURES: _apply_features,
}
