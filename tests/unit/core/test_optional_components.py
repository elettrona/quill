from __future__ import annotations

import quill.core.optional_components as oc
from quill.core.optional_components import gather_optional_components


def test_gather_includes_the_core_optional_components() -> None:
    ids = {c.component_id for c in gather_optional_components()}
    assert {
        "whispercpp",
        "vosk",
        "kokoro",
        "espeak",
        "dectalk",
        "ffmpeg",
        "libmpv",
        "mathcat",
    }.issubset(ids)


def test_status_reflects_detectors(monkeypatch) -> None:
    monkeypatch.setattr(oc, "_whisper_installed", lambda: True)
    monkeypatch.setattr(oc, "_kokoro_installed", lambda: False)
    monkeypatch.setattr(oc, "_espeak_installed", lambda: False)
    monkeypatch.setattr(oc, "_dectalk_installed", lambda: False)
    monkeypatch.setattr(oc, "_ffmpeg_installed", lambda: False)
    by_id = {c.component_id: c for c in gather_optional_components()}
    assert by_id["whispercpp"].installed is True
    assert by_id["whispercpp"].status_label == "Installed"
    assert by_id["kokoro"].installed is False
    assert by_id["kokoro"].status_label == "Available to download"


def test_a_broken_detector_never_crashes_the_list(monkeypatch) -> None:
    def boom() -> bool:
        raise RuntimeError("detector exploded")

    monkeypatch.setattr(oc, "_whisper_installed", boom)
    comps = gather_optional_components()  # must not raise
    whisper = next(c for c in comps if c.component_id == "whispercpp")
    assert whisper.installed is False


def test_dictionary_components_use_spellcheck_state(monkeypatch) -> None:
    from quill.core import spellcheck

    monkeypatch.setattr(spellcheck, "installed_languages", lambda: ["en_US", "fr_FR"])
    monkeypatch.setattr(spellcheck, "installable_languages", lambda: ["es_ES"])
    by_id = {c.component_id: c for c in gather_optional_components()}
    # en_US is bundled in pyenchant, so it is never listed as a separate download.
    assert "spell-en_US" not in by_id
    assert by_id["spell-fr_FR"].installed is True
    assert by_id["spell-es_ES"].installed is False
    assert by_id["spell-fr_FR"].category == oc.DICTIONARY


def test_size_hints_present_for_large_components() -> None:
    by_id = {c.component_id: c for c in gather_optional_components()}
    assert by_id["kokoro"].size_hint  # non-empty
    assert by_id["whispercpp"].size_hint


def test_libmpv_detector_checks_the_engine_pack(tmp_path, monkeypatch) -> None:
    import quill.core.speech.engine_install as ei

    monkeypatch.setattr(ei, "engine_packs_dir", lambda: tmp_path)
    assert oc._libmpv_installed() is False
    (tmp_path / "mpv").mkdir()
    (tmp_path / "mpv" / "libmpv-2.dll").write_bytes(b"MZ")
    assert oc._libmpv_installed() is True


def test_mathcat_detector_checks_the_engine_pack(tmp_path, monkeypatch) -> None:
    from quill.core.math import mathcat_engine

    monkeypatch.setattr(mathcat_engine, "pack_dir", lambda: tmp_path / "mathcat")
    assert oc._mathcat_installed() is False
    (tmp_path / "mathcat" / "Rules").mkdir(parents=True)
    (tmp_path / "mathcat" / "libmathcat_c.dll").write_bytes(b"MZ")
    assert oc._mathcat_installed() is True


def test_gather_includes_piper_and_node() -> None:
    """Piper and Node.js are downloadable, so they must have a touch point in the
    dialog (they were missing before the catalog-completeness pass)."""
    ids = {c.component_id for c in gather_optional_components()}
    assert "piper" in ids
    assert "node" in ids


def test_components_are_ordered_by_importance() -> None:
    comps = gather_optional_components()
    ids = [c.component_id for c in comps]
    # Pandoc leads, braille second (the user-facing importance order).
    assert ids[0] == "pandoc"
    assert ids[1] == "braille"
    # Spell-check dictionaries are grouped last.
    spell_positions = [i for i, cid in enumerate(ids) if cid.startswith("spell-")]
    non_spell_positions = [i for i, cid in enumerate(ids) if not cid.startswith("spell-")]
    if spell_positions and non_spell_positions:
        assert min(spell_positions) > max(non_spell_positions)


def test_every_component_row_states_a_size() -> None:
    # Every row (dictionaries included, which were blank before) shows a size.
    for c in gather_optional_components():
        assert c.size_hint, f"{c.component_id} has no size_hint"


def test_describe_component_reports_state_and_size() -> None:
    from quill.core.optional_components import OptionalComponent, describe_component

    installed = OptionalComponent(
        "pandoc", "Pandoc", "Converts documents.", oc.TOOL, True, "~45 MB"
    )
    text = describe_component(installed)
    assert "Pandoc" in text and "~45 MB" in text and "Installed" in text and "Remove" in text

    missing = OptionalComponent(
        "kokoro", "Kokoro neural voices", "Neural voices.", oc.VOICES, False, "~120 MB"
    )
    text2 = describe_component(missing)
    assert "Not installed" in text2 and "~120 MB" in text2 and "Download" in text2


def test_every_hosted_release_asset_is_catalogued() -> None:
    """A component QUILL can fetch from its own release must appear in the dialog,
    so a future downloadable component can't silently miss it. Spell-check assets
    map to the dynamic spell-<lang> rows and are checked separately."""
    from quill.core.release_assets import ASSETS

    ids = {c.component_id for c in gather_optional_components()}
    for key in ASSETS:
        if key.startswith("spell-"):
            continue
        assert key in ids, f"release_assets component {key!r} is not in the download dialog"
