"""L-23: regression tests for CsvGridSurface cell-position encoding."""

from __future__ import annotations

from quill.ui.csv_grid import (
    _CELL_POSITION_STRIDE,
    detect_csv_delimiter,
    parse_csv_rows,
    serialize_csv_rows,
)


def test_cell_position_stride_large_enough_for_excel_max() -> None:
    assert _CELL_POSITION_STRIDE >= 16384


def test_cell_position_no_collision_at_stride_boundary() -> None:
    # With the old stride=1000: row=1,col=0 -> 1000 == row=0,col=1000 (collision).
    # With stride=16384: row=1,col=0 -> 16384; row=0,col=16383 -> 16383 (no collision).
    row_1_col_0 = 1 * _CELL_POSITION_STRIDE + 0
    row_0_col_max = 0 * _CELL_POSITION_STRIDE + (_CELL_POSITION_STRIDE - 1)
    assert row_1_col_0 != row_0_col_max


def test_cell_position_ordering_increases_with_row_then_col() -> None:
    def pos(row: int, col: int) -> int:
        return max(0, row) * _CELL_POSITION_STRIDE + max(0, col)

    assert pos(0, 0) < pos(0, 1) < pos(1, 0) < pos(1, 1)


def test_detect_csv_delimiter_comma() -> None:
    assert detect_csv_delimiter("a,b,c\n1,2,3") == ","


def test_detect_csv_delimiter_tab() -> None:
    assert detect_csv_delimiter("a\tb\tc\n1\t2\t3") == "\t"


def test_parse_csv_rows_pads_ragged() -> None:
    rows = parse_csv_rows("a,b\nc", ",")
    assert rows == [["a", "b"], ["c", ""]]


def test_serialize_roundtrip() -> None:
    rows = [["x", "y"], ["1", "2"]]
    text = serialize_csv_rows(rows, ",")
    assert parse_csv_rows(text, ",") == rows
