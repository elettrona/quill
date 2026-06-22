from __future__ import annotations

from quill.core.features import FEATURE_DEFINITIONS, FeatureManager, feature_for_command


def test_publishing_commands_map_to_publishing_feature() -> None:
    publishing_commands = [
        "publishing.connections",
        "publishing.verify_connection",
        "publishing.create_draft",
        "publishing.publish_current",
        "publishing.create_page_draft",
        "publishing.publish_current_page",
        "publishing.browse_content",
        "publishing.open_remote_item",
        "publishing.update_remote_item",
        "publishing.publish_remote_item",
        "publishing.schedule_publish",
        "publishing.compare_remote_item",
    ]

    for command_id in publishing_commands:
        assert feature_for_command(command_id) == "future.publishing"


def test_publishing_command_ids_stay_provider_neutral() -> None:
    publishing_commands = [
        "publishing.connections",
        "publishing.verify_connection",
        "publishing.create_draft",
        "publishing.publish_current",
        "publishing.create_page_draft",
        "publishing.publish_current_page",
        "publishing.browse_content",
        "publishing.open_remote_item",
        "publishing.update_remote_item",
        "publishing.publish_remote_item",
        "publishing.schedule_publish",
        "publishing.compare_remote_item",
    ]

    assert all(command_id.startswith("publishing.") for command_id in publishing_commands)
    assert all("wordpress" not in command_id for command_id in publishing_commands)


def test_publishing_feature_is_locked_off_pending_review() -> None:
    # The publishing-providers-framework branch is locked off so it never
    # ships in a public release until this gate is deliberately lifted.
    definition = FEATURE_DEFINITIONS["future.publishing"]
    assert definition.locked_off is True


def test_publishing_disabled_in_default_build() -> None:
    manager = FeatureManager.load(persistent=False)
    assert manager.is_enabled("future.publishing") is False
    assert manager.is_visible("future.publishing") is False
