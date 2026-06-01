from __future__ import annotations

from quill.tools.network_egress_audit import (
    _REVIEWED_EGRESS,
    discover_egress_sites,
    find_unreviewed_egress,
)


def test_no_unreviewed_network_egress() -> None:
    unreviewed, stale = find_unreviewed_egress()
    assert not unreviewed, (
        "New outbound network call(s) found that are not in the reviewed "
        "egress inventory. Add each to _REVIEWED_EGRESS in "
        "quill/tools/network_egress_audit.py with a note on what user action "
        "or explicit consent triggers it: " + ", ".join(sorted(unreviewed))
    )
    assert not stale, (
        "Reviewed egress entries no longer match any call site (remove them): "
        + ", ".join(sorted(stale))
    )


def test_every_reviewed_site_has_a_rationale() -> None:
    for site, reason in _REVIEWED_EGRESS.items():
        assert reason.strip(), f"{site} has an empty rationale"


def test_discovered_sites_are_all_inside_the_quill_package() -> None:
    # The audit must scan only our package, never vendored copies in .venv or
    # the portable distribution (which would create false positives).
    for site in discover_egress_sites():
        assert not site.startswith(".."), site
        assert "site-packages" not in site, site
