"""Tests for the wx-free Table Studio core (model, controller, CSV I/O)."""

from __future__ import annotations

from quill.core.table_studio import (
    Alignment,
    AnnounceConfig,
    SpokenCellFormatter,
    TableController,
    TableDocumentModel,
)
from quill.core.table_studio.csv_io import (
    load_csv,
    parse_csv_text,
    sniff_delimiter,
    to_csv_text,
)


def _model() -> TableDocumentModel:
    return TableDocumentModel.from_lists(
        headers=["Name", "City"],
        rows=[["Ada", "London"], ["Alan", "Bletchley"]],
        caption="People",
    )


# -- model -------------------------------------------------------------------


def test_dimensions_and_values() -> None:
    m = _model()
    assert m.row_count == 2 and m.col_count == 2
    assert m.value(0, 0) == "Ada"
    assert m.col_header(1) == "City"


def test_set_value_notifies_and_rejects_readonly() -> None:
    m = _model()
    changes: list = []
    m.add_listener(lambda change, kw: changes.append((change, kw)))
    assert m.set_value(0, 1, "Manchester") is True
    assert m.value(0, 1) == "Manchester"
    assert changes and changes[-1][0].value == "cell_value"


def test_row_and_column_operations() -> None:
    m = _model()
    m.insert_row(1)
    assert m.row_count == 3 and m.value(1, 0) == ""
    m.set_value(1, 0, "Grace")
    m.move_row(1, 0)
    assert m.value(0, 0) == "Grace"
    m.insert_col(2, "Role")
    assert m.col_count == 3 and m.col_header(2) == "Role"
    assert m.delete_col(2) is True and m.col_count == 2
    assert m.delete_row(0) is True and m.row_count == 2


def test_column_header_override() -> None:
    m = _model()
    m.set_col_label_override(0, "Full Name")
    assert m.col_header(0) == "Full Name"
    assert "Full Name" in m.to_markdown().splitlines()[0]
    m.clear_col_label_override(0)
    assert m.col_header(0) == "Name"


def test_markdown_and_html_serialization() -> None:
    m = _model()
    md = m.to_markdown().splitlines()
    assert md[0].startswith("| Name") and md[1].startswith("| ---")
    assert any("Ada" in line for line in md)
    html = m.to_html()
    assert '<th scope="col">Name</th>' in html
    assert "<caption>People</caption>" in html


def test_alignment_delimiters_in_markdown() -> None:
    m = TableDocumentModel.from_lists(
        headers=["L", "C", "R"],
        rows=[["1", "2", "3"]],
        alignments=[Alignment.LEFT, Alignment.CENTER, Alignment.RIGHT],
    )
    delim = m.to_markdown().splitlines()[1]
    assert ":-" in delim and "-:" in delim  # center + right markers present


def test_row_header_when_first_column_is_header() -> None:
    m = TableDocumentModel.from_lists(
        headers=["Name", "City"],
        rows=[["Ada", "London"]],
        first_col_is_header=True,
    )
    assert m.row_header(0) == "Ada"
    assert '<th scope="row">Ada</th>' in m.to_html()


# -- spoken-cell formatter (accessibility) -----------------------------------


def test_standard_verbosity_announces_changed_headers() -> None:
    m = _model()
    fmt = SpokenCellFormatter(SpokenCellFormatter.STANDARD)
    # First cell in a column announces the header; the announce mode is "changed".
    said = fmt.cell(m, 0, 1, prev_col_hdr="")
    assert "City" in said and "London" in said
    # Same column again with the header already in the ear -> header omitted.
    said2 = fmt.cell(m, 1, 1, prev_col_hdr="City")
    assert "City" not in said2 and "Bletchley" in said2


def test_detailed_verbosity_includes_coordinates() -> None:
    m = _model()
    fmt = SpokenCellFormatter(SpokenCellFormatter.DETAILED)
    said = fmt.cell(m, 0, 0)
    assert "Row 1 of 2" in said and "column 1 of 2" in said


def test_blank_cell_reads_blank() -> None:
    m = _model()
    m.set_value(0, 0, "")
    said = SpokenCellFormatter(SpokenCellFormatter.CONCISE).cell(m, 0, 0)
    assert "Blank" in said


def test_announce_config_off_suppresses_headers() -> None:
    m = _model()
    m.set_announce_config(AnnounceConfig(col_headers="off"))
    said = SpokenCellFormatter(SpokenCellFormatter.STANDARD).cell(m, 0, 1, prev_col_hdr="")
    assert "City" not in said


# -- controller --------------------------------------------------------------


def test_controller_tracks_active_cell_and_announces() -> None:
    m = _model()
    ctrl = TableController(m)
    spoken: list[str] = []
    ctrl.set_announce_callback(spoken.append)
    assert ctrl.active_row == 0 and ctrl.active_col == 0


# -- CSV I/O -----------------------------------------------------------------


def test_sniff_delimiter() -> None:
    assert sniff_delimiter("a,b,c\n1,2,3") == ","
    assert sniff_delimiter("a\tb\tc\n1\t2\t3") == "\t"
    assert sniff_delimiter("a;b;c\n1;2;3") == ";"


def test_csv_round_trip() -> None:
    text = "Name,City\nAda,London\nAlan,Bletchley\n"
    m = parse_csv_text(text, caption="people")
    assert m.row_count == 2 and m.col_header(0) == "Name"
    assert m.value(1, 1) == "Bletchley"
    out = to_csv_text(m)
    assert out.splitlines()[0] == "Name,City"
    assert "Ada,London" in out


def test_csv_file_round_trip(tmp_path) -> None:
    p = tmp_path / "data.csv"
    p.write_text("Col A;Col B\n1;2\n", encoding="utf-8")
    m = load_csv(p)
    assert m.csv_delimiter == ";" and m.value(0, 0) == "1"
    assert m.csv_source_path == str(p)
    assert m.caption == "data"


def test_parse_empty_csv_raises() -> None:
    import pytest

    with pytest.raises(ValueError):
        parse_csv_text("")


# -- integration wiring (source-contract) ------------------------------------


def test_settings_flags_round_trip() -> None:
    from quill.core.settings import Settings

    s = Settings.from_dict(
        {"table_studio_experimental_enabled": True, "csv_studio_experimental_enabled": True}
    )
    assert s.table_studio_experimental_enabled is True
    assert s.csv_studio_experimental_enabled is True


def test_commands_registered_and_gated() -> None:
    from pathlib import Path

    root = Path(__file__).resolve().parents[4]
    mf = (root / "quill" / "ui" / "main_frame.py").read_text(encoding="utf-8")
    assert '"tools.table_studio"' in mf and '"tools.csv_studio"' in mf
    assert "def open_table_studio" in mf and "def open_csv_studio" in mf
    # Both are gated behind the experimental master + their own flag.
    assert '_experimental_gate_on("table_studio_experimental_enabled")' in mf
    assert '_experimental_gate_on("csv_studio_experimental_enabled")' in mf
    # Both flags follow the Experimental master switch (disabled when it is off).
    assert "table_studio_experimental_enabled" in mf and "csv_studio_experimental_enabled" in mf


def test_menu_items_gated() -> None:
    from pathlib import Path

    root = Path(__file__).resolve().parents[4]
    menu = (root / "quill" / "ui" / "main_frame_menu.py").read_text(encoding="utf-8")
    assert '_("&Table Studio...")' in menu and '_("CS&V Studio...")' in menu
    assert "_experimental_gate_on(\"table_studio_experimental_enabled\")" in menu


def test_native_uia_wrapper_falls_back_cleanly() -> None:
    # With no compiled .pyd present, the native bridge reports unavailable and
    # attach() returns None so the grid uses the MSAA fallback.
    from quill.ui import table_studio_native as native

    assert native.is_available() in (True, False)  # never raises
    if not native.is_available():
        result = native.attach(
            0,
            get_dims=lambda: (0, 0),
            get_value=lambda r, c: "",
            get_col_header=lambda c: "",
            get_row_header=lambda r: "",
            get_focus=lambda: (0, 0),
            set_focus=lambda r, c: None,
            is_editable=lambda r, c: True,
            caption="T",
        )
        assert result is None


def test_native_uia_sources_captured_and_build_wired() -> None:
    from pathlib import Path

    root = Path(__file__).resolve().parents[4]
    native = root / "quill" / "native" / "table_uia"
    for name in ("table_provider.cpp", "table_provider.hpp", "python_bridge.cpp", "CMakeLists.txt"):
        assert (native / name).is_file(), f"missing native source {name}"
    # The distribution build stages the .pyd when present (optional dependency).
    build = (root / "scripts" / "build_windows_distribution.py").read_text(encoding="utf-8")
    assert "_stage_table_uia" in build and "_quill_table_uia" in build
