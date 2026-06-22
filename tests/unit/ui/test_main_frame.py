"""Tests for MainFrame dialog contract helpers (M-28: crash recovery focus)."""

from __future__ import annotations

from pathlib import Path

SOURCE = (Path(__file__).resolve().parents[3] / "quill" / "ui" / "main_frame.py").read_text(
    encoding="utf-8"
)


def test_show_modal_dialog_has_restore_editor_focus_param() -> None:
    # M-28: _show_modal_dialog must accept restore_editor_focus to prevent
    # focus-racing in loops that re-show the same dialog.
    assert "restore_editor_focus: bool = True" in SOURCE


def test_crash_recovery_loop_does_not_steal_focus() -> None:
    # M-28: The crash-recovery re-show loop must pass restore_editor_focus=False
    # so editor.SetFocus is not called between loop iterations, which would race
    # with the dialog's own focus management.
    assert "restore_editor_focus=False" in SOURCE
    # The _show_modal_dialog call for Crash Recovery must carry the flag.
    crash_call = (
        "_show_modal_dialog(\n"
        '                    dialog, "Crash Recovery", restore_editor_focus=False\n'
        "                )"
    )
    assert crash_call in SOURCE


def test_remote_publishing_open_records_explicit_representation_metadata() -> None:
    # Publishing content now chooses a Quill authoring surface at open time.
    # Metadata should continue to record that choice explicitly so later update
    # flows do not have to guess.
    assert '"source_kind": "publishing_remote"' in SOURCE
    assert '"publishing_authoring_surface": prepared_content.authoring_surface' in SOURCE
    assert '"publishing_open_representation": prepared_content.open_representation' in SOURCE
    assert '"display_name": remote_document.title' in SOURCE
    assert '"source_label": "from publishing"' in SOURCE
    assert '"publishing_remote_title": remote_document.title' in SOURCE


def test_remote_publishing_tabs_use_metadata_identity() -> None:
    assert (
        'tab.source_label = str(document.source_metadata.get("source_label", "")).strip()' in SOURCE
    )


def test_browse_publishing_content_dialog_receives_task_manager() -> None:
    assert "BrowsePublishingContentDialog(\n            self.frame, self._task_manager," in SOURCE
    assert "self.notebook.AddPage(panel, document.name, select=select)" in SOURCE


def test_remote_publishing_update_uses_saved_authoring_surface_metadata() -> None:
    assert '"publishing.update_remote_item"' in SOURCE
    assert '"publishing.publish_remote_item"' in SOURCE
    assert "def _publish_open_remote_item(self) -> None:" in SOURCE
    assert "def _send_publishing_remote_item(self, *, status: str | None) -> None:" in SOURCE
    assert (
        'authoring_surface = str(metadata.get("publishing_authoring_surface", "")).strip().lower()'
        in SOURCE
    )
    assert "document_text=self.editor.GetValue()" in SOURCE
    assert 'authoring_surface=authoring_surface or "markdown"' in SOURCE
    assert (
        'dialog_title = "Publish Open Remote Content" if is_publish else "Update Remote Content"'
        in SOURCE
    )
    assert "status=status" in SOURCE


def test_publishing_create_draft_commands_stay_command_registered_and_metadata_backed() -> None:
    assert '"publishing.create_draft"' in SOURCE
    assert '"publishing.publish_current"' in SOURCE
    assert '"publishing.create_page_draft"' in SOURCE
    assert '"publishing.publish_current_page"' in SOURCE
    assert "def _create_publishing_draft(self) -> None:" in SOURCE
    assert "def _publish_current_document(self) -> None:" in SOURCE
    assert "def _create_publishing_page_draft(self) -> None:" in SOURCE
    assert "def _publish_current_page(self) -> None:" in SOURCE
    assert "status=publishing_status" in SOURCE
    assert '"publishing_remote_id": remote_document.remote_id' in SOURCE
    assert '"publishing_content_kind": remote_document.content_kind' in SOURCE
    assert '"display_name": remote_document.title' in SOURCE
    assert '"publishing_remote_title": remote_document.title' in SOURCE


def test_publishing_publish_now_uses_existing_confirmation_path() -> None:
    assert '"Publish Current Document"' in SOURCE
    assert 'if publishing_status == "publish"\n            else "Create Publishing Draft"' in SOURCE
    assert '"Publish current document cancelled"' in SOURCE
    assert (
        'f"Choose Yes to send the current document text and {action_label.lower()} it."' in SOURCE
    )


def test_publishing_send_results_use_explicit_confirmation_formatter() -> None:
    assert 'publishing_result_message("updated", remote_document)' in SOURCE
    assert 'publishing_result_message("created", remote_document)' in SOURCE
    assert "result_message.splitlines()[0]" in SOURCE


def test_write_document_to_disk_syncs_publishing_linkage_after_save() -> None:
    # The save chokepoint persists/refreshes the durable linkage registry so
    # Compare/Update survive a close-and-reopen cycle (#publishing-linkage).
    assert (
        "write_document_as(document, target, plain_text_link_style=link_style)"
        "  # type: ignore[arg-type]\n        self._sync_publishing_linkage_for_document(document)"
        in SOURCE
    )
    assert "def _sync_publishing_linkage_for_document(self, document: Document) -> None:" in SOURCE


def test_sync_publishing_linkage_excludes_structured_surfaces() -> None:
    # Compare/Update only ever read self.editor.GetValue() as markdown/HTML
    # text, a shape CSV grid and Word structured surfaces were never designed
    # to produce, so linkage is never persisted for them.
    assert (
        'isinstance(getattr(self, "editor", None), (CsvGridSurface, WordDocumentSurface)):'
        in SOURCE
    )
    assert "entry = publishing_linkage_from_source_metadata(metadata)" in SOURCE
    assert "upsert_publishing_linkage(path, entry)" in SOURCE


def test_finish_open_document_restores_publishing_linkage_from_registry() -> None:
    # Reopening a previously-linked, previously-saved file restores its
    # publishing linkage before either tab branch (new tab or refresh) runs.
    assert (
        "linkage_entry = get_publishing_linkage(selected_path)\n"
        "        if linkage_entry is not None:\n"
        "            apply_publishing_linkage_to_source_metadata("
        "loaded.source_metadata, linkage_entry)" in SOURCE
    )


def test_send_and_schedule_publishing_handlers_resync_linkage_after_success() -> None:
    # _send_publishing_remote_item, the schedule-publish handler, and the
    # create-draft/publish-now handler all refresh the registry's cached
    # remote state immediately after self.document.mark_saved().
    assert SOURCE.count("self._sync_publishing_linkage_for_document(self.document)") == 3
