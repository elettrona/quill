from quill.io.rtf_safety import scan_rtf_safety


def test_clean_rtf_is_safe() -> None:
    rtf = r"{\rtf1\ansi\pard Hello {\b world}\par}"
    report = scan_rtf_safety(rtf)
    assert report.safe is True
    assert report.blocked == []
    assert report.sanitized_rtf == rtf


def test_embedded_object_is_blocked_and_stripped() -> None:
    rtf = r"{\rtf1\ansi {\object\objemb {\*\objdata 0105badbeef}}\pard text\par}"
    report = scan_rtf_safety(rtf)
    assert report.safe is False
    assert "embedded OLE object" in report.blocked
    assert "objdata" not in report.sanitized_rtf
    assert "badbeef" not in report.sanitized_rtf
    # Surrounding legitimate content survives.
    assert "text" in report.sanitized_rtf


def test_ignorable_objdata_destination_is_stripped() -> None:
    rtf = r"{\rtf1\ansi {\*\objdata deadbeef} keep}"
    report = scan_rtf_safety(rtf)
    assert "deadbeef" not in report.sanitized_rtf
    assert "keep" in report.sanitized_rtf


def test_remote_field_is_flagged_not_blocked() -> None:
    rtf = r'{\rtf1\ansi {\field{\*\fldinst INCLUDEPICTURE "http://x/y.png"}}}'
    report = scan_rtf_safety(rtf)
    assert "remote content references" in report.warnings


def test_binary_payload_is_neutralized() -> None:
    rtf = r"{\rtf1\ansi \bin8 \x00\x01 trailing}"
    report = scan_rtf_safety(rtf)
    assert "binary data" in report.warnings
    assert "\\bin8" not in report.sanitized_rtf


def test_nested_object_group_skipped_entirely() -> None:
    rtf = r"{\rtf1 {\object {\inner nested} more} after}"
    report = scan_rtf_safety(rtf)
    assert "nested" not in report.sanitized_rtf
    assert "after" in report.sanitized_rtf


def test_autotext_not_flagged_as_remote() -> None:
    # M-12: AUTOTEXT is a benign boilerplate-insert control word, not a
    # remote-fetch instruction; it must not trigger the remote-content warning.
    rtf = r'{\rtf1\ansi {\field{\*\fldinst AUTOTEXT "Yours sincerely"}}}'
    report = scan_rtf_safety(rtf)
    assert "remote content references" not in report.warnings
