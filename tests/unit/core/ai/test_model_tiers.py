"""Tests for mid-task model speed/cost tiers (AI-22)."""

from __future__ import annotations

from pathlib import Path

import pytest

from quill.core.ai import model_tiers
from quill.core.ai.model_tiers import (
    TIER_FAST,
    TIER_STRONG,
    active_tier,
    active_tier_id,
    announce_tier_change,
    assign_model_to_tier,
    describe_tier,
    load_tiers,
    resolve_tier_spec,
    set_active_tier,
)


@pytest.fixture(autouse=True)
def data_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setenv("QUILL_DATA_DIR", str(tmp_path))
    return tmp_path


def test_defaults_fast_and_strong() -> None:
    tiers = load_tiers()
    assert [t.tier_id for t in tiers] == [TIER_FAST, TIER_STRONG]
    fast, strong = tiers
    assert fast.model_id == "llama-3.2-1b"
    assert strong.model_id == "phi-4-mini"
    assert active_tier_id() == TIER_STRONG


def test_switch_active_tier_persists() -> None:
    set_active_tier(TIER_FAST)
    assert active_tier_id() == TIER_FAST
    assert active_tier().tier_id == TIER_FAST


def test_assign_model_to_tier() -> None:
    tier = assign_model_to_tier(TIER_FAST, "phi-4-mini")
    assert tier.model_id == "phi-4-mini"
    # Persisted independently of the active tier.
    fast = next(t for t in load_tiers() if t.tier_id == TIER_FAST)
    assert fast.model_id == "phi-4-mini"


def test_assign_auto_is_allowed() -> None:
    tier = assign_model_to_tier(TIER_STRONG, "auto")
    assert tier.is_auto is True


def test_unknown_tier_rejected() -> None:
    with pytest.raises(ValueError):
        set_active_tier("turbo")
    with pytest.raises(ValueError):
        assign_model_to_tier("turbo", "phi-4-mini")


def test_unknown_model_rejected() -> None:
    with pytest.raises(ValueError):
        assign_model_to_tier(TIER_FAST, "gpt-9")


def test_resolve_tier_spec_uses_model_manager(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(model_tiers.model_manager, "recommended_id", lambda: "llama-3.2-1b")
    assign_model_to_tier(TIER_STRONG, "auto")
    spec = resolve_tier_spec(next(t for t in load_tiers() if t.tier_id == TIER_STRONG))
    assert spec.id == "llama-3.2-1b"


def test_describe_and_announce_are_spoken() -> None:
    fast = next(t for t in load_tiers() if t.tier_id == TIER_FAST)
    strong = next(t for t in load_tiers() if t.tier_id == TIER_STRONG)

    assert describe_tier(fast).startswith("Fast tier for quick edits:")

    message = announce_tier_change(strong, fast)
    assert message.startswith("Switched to the Fast tier")
    assert "quick edits" in message

    same = announce_tier_change(fast, fast)
    assert same.startswith("Staying on the Fast tier")
