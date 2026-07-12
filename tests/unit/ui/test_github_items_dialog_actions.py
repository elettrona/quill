"""Tests for GitHubItemsDialog's write actions: new issue/PR, merge, delete
branch, re-run workflow, and comment reply/edit/delete.

Constructed with a real wx.App/Frame (matching test_status_dialog.py's
precedent — this dialog builds real wx controls in __init__ and there is no
wx-free seam to fake around that). Per-test, ``_show_modal`` is monkeypatched
to short-circuit dialog confirmation, ``_selected_indices`` is monkeypatched
to avoid driving real wx.ListCtrl selection state, and ``_provider`` is a
lightweight fake recording calls -- mirroring the level of faking already
used for the batch-operations code path this mirrors.
"""

from __future__ import annotations

from typing import Any

import pytest
import wx

from quill.core.github.items_provider import GitHubItem, GitHubItemsError
from quill.ui.github_items_dialog import GitHubItemsDialog


class _FakeProvider:
    def __init__(self, *, authenticated: bool = True, token: str = "tok") -> None:
        self._authenticated = authenticated
        self._token = token
        self.created_issues: list[tuple[str, str, str]] = []
        self.created_pulls: list[tuple[str, str, str, str, str]] = []
        self.merged: list[tuple[str, int]] = []
        self.reran: list[tuple[str, int]] = []
        self.posted_comments: list[tuple[str, int, str]] = []
        self.edited_comments: list[tuple[str, int, str]] = []
        self.deleted_comments: list[tuple[str, int]] = []
        self.merge_result = "merged-sha-1234567"
        self.raise_on_merge: Exception | None = None

    @property
    def is_authenticated(self) -> bool:
        return self._authenticated

    @property
    def token(self) -> str:
        return self._token

    def create_issue(self, repo: str, title: str, body: str) -> GitHubItem:
        self.created_issues.append((repo, title, body))
        return GitHubItem(number=101, title=title, state="open", url="", is_pr=False)

    def create_pull_request(
        self, repo: str, title: str, body: str, head: str, base: str
    ) -> GitHubItem:
        self.created_pulls.append((repo, title, body, head, base))
        return GitHubItem(number=102, title=title, state="open", url="", is_pr=True)

    def merge_pull_request(self, repo: str, number: int, **_kw: Any) -> str:
        if self.raise_on_merge:
            raise self.raise_on_merge
        self.merged.append((repo, number))
        return self.merge_result

    def rerun_workflow_run(self, repo: str, run_id: int) -> None:
        self.reran.append((repo, run_id))

    def create_comment(self, repo: str, number: int, body: str) -> dict:
        self.posted_comments.append((repo, number, body))
        return {"id": "1", "author": "me", "created_at": "", "body": body}

    def edit_comment(self, repo: str, comment_id: int, body: str) -> dict:
        self.edited_comments.append((repo, comment_id, body))
        return {"id": str(comment_id), "author": "me", "created_at": "", "body": body}

    def delete_comment(self, repo: str, comment_id: int) -> None:
        self.deleted_comments.append((repo, comment_id))

    def fetch_issue_comments(self, repo: str, number: int) -> list[dict]:
        return []


@pytest.fixture(scope="module")
def wx_app():
    app = wx.App()
    yield app
    app.Destroy()


class _SyncThread:
    """Stands in for threading.Thread: runs target() immediately on .start(),
    so the write actions' worker/CallAfter round trip is deterministic in a
    test with no real wx event loop pumping CallAfter's queue."""

    def __init__(self, target=None, daemon=None, **_kw: Any) -> None:
        self._target = target

    def start(self) -> None:
        if self._target is not None:
            self._target()


@pytest.fixture
def dlg(wx_app, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr("quill.ui.github_items_dialog.threading.Thread", _SyncThread)
    monkeypatch.setattr(wx, "CallAfter", lambda fn, *a, **k: fn(*a, **k))
    frame = wx.Frame(None)
    provider = _FakeProvider()
    dialog = GitHubItemsDialog(frame, provider, initial_repo="owner/repo")
    dialog._repo = "owner/repo"
    statuses: list[str] = []
    announcements: list[str] = []
    dialog._set_status = lambda message: statuses.append(message) or announcements.append(message)
    dialog._announce = lambda message: announcements.append(message)
    dialog._reload = lambda: None
    dialog._show_modal = lambda _dlg, _title: wx.ID_OK
    dialog.statuses = statuses
    dialog.announcements = announcements
    return dialog


# ---------------------------------------------------------------------------
# Actions menu gating
# ---------------------------------------------------------------------------


def test_actions_menu_requires_a_loaded_repo(dlg) -> None:
    dlg._repo = ""
    dlg._on_actions_menu(None)
    assert "Load a repository" in dlg.announcements[-1]


def test_actions_menu_requires_authentication(dlg) -> None:
    dlg._provider = _FakeProvider(authenticated=False)
    dlg._on_actions_menu(None)
    assert "signed-in" in dlg.announcements[-1]


# ---------------------------------------------------------------------------
# New issue / new pull request
# ---------------------------------------------------------------------------


def test_new_issue_creates_via_provider(dlg, monkeypatch: pytest.MonkeyPatch) -> None:
    values = iter(["Bug title", "steps to repro"])
    monkeypatch.setattr(wx, "TextEntryDialog", lambda *a, **k: _FakeTextEntry(next(values, "")))
    dlg._new_issue()
    assert dlg._provider.created_issues == [("owner/repo", "Bug title", "steps to repro")]
    assert "Created ISSUE #101" in dlg.statuses[-1]


def test_new_issue_cancelled_at_title_does_nothing(dlg, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(wx, "TextEntryDialog", lambda *a, **k: _FakeTextEntry("", ok=False))
    dlg._new_issue()
    assert dlg._provider.created_issues == []


def test_new_pull_request_requires_head_and_base(dlg, monkeypatch: pytest.MonkeyPatch) -> None:
    # title, body, head="", base -> head blank should abort before creating.
    values = iter(["PR title", "body", ""])
    monkeypatch.setattr(wx, "TextEntryDialog", lambda *a, **k: _FakeTextEntry(next(values, "main")))
    dlg._new_pull_request()
    assert dlg._provider.created_pulls == []


def test_new_pull_request_creates_via_provider(dlg, monkeypatch: pytest.MonkeyPatch) -> None:
    values = iter(["PR title", "body", "feature", "main"])
    monkeypatch.setattr(wx, "TextEntryDialog", lambda *a, **k: _FakeTextEntry(next(values, "")))
    dlg._new_pull_request()
    assert dlg._provider.created_pulls == [("owner/repo", "PR title", "body", "feature", "main")]


# ---------------------------------------------------------------------------
# Merge
# ---------------------------------------------------------------------------


def test_merge_selected_pr_confirms_and_merges(dlg, monkeypatch: pytest.MonkeyPatch) -> None:
    pr = GitHubItem(number=5, title="Fix it", state="open", url="", is_pr=True, base_branch="main")
    dlg._rows = [pr]
    dlg._selected_indices = lambda: [0]
    monkeypatch.setattr(
        "quill.ui.github_repo_admin_dialogs.TypedConfirmDialog",
        lambda *a, **k: _FakeTypedConfirm(True),
    )
    dlg._merge_selected_pr()
    assert dlg._provider.merged == [("owner/repo", 5)]
    assert "Merged #5" in dlg.statuses[-1]


def test_merge_selected_pr_declined_confirmation(dlg, monkeypatch: pytest.MonkeyPatch) -> None:
    pr = GitHubItem(number=5, title="Fix it", state="open", url="", is_pr=True)
    dlg._rows = [pr]
    dlg._selected_indices = lambda: [0]
    monkeypatch.setattr(
        "quill.ui.github_repo_admin_dialogs.TypedConfirmDialog",
        lambda *a, **k: _FakeTypedConfirm(False),
    )
    dlg._merge_selected_pr()
    assert dlg._provider.merged == []


def test_merge_surfaces_provider_error(dlg, monkeypatch: pytest.MonkeyPatch) -> None:
    pr = GitHubItem(number=5, title="Fix it", state="open", url="", is_pr=True)
    dlg._rows = [pr]
    dlg._selected_indices = lambda: [0]
    dlg._provider.raise_on_merge = GitHubItemsError("not mergeable")
    monkeypatch.setattr(
        "quill.ui.github_repo_admin_dialogs.TypedConfirmDialog",
        lambda *a, **k: _FakeTypedConfirm(True),
    )
    dlg._merge_selected_pr()
    assert any("not mergeable" in s for s in dlg.statuses)


# ---------------------------------------------------------------------------
# Delete branch
# ---------------------------------------------------------------------------


def test_delete_selected_branch(dlg, monkeypatch: pytest.MonkeyPatch) -> None:
    from quill.core.github.items_provider import GitHubBranch

    branch = GitHubBranch(name="stale", commit_sha="abc")
    dlg._rows = [branch]
    dlg._selected_indices = lambda: [0]
    monkeypatch.setattr(
        "quill.ui.github_repo_admin_dialogs.TypedConfirmDialog",
        lambda *a, **k: _FakeTypedConfirm(True),
    )
    deleted: list[tuple[str, str]] = []
    monkeypatch.setattr(
        "quill.core.github.repo_admin.GitHubRepoAdminProvider",
        lambda token: _FakeRepoAdmin(deleted),
    )
    dlg._delete_selected_branch()
    assert deleted == [("owner/repo", "stale")]
    assert "Deleted branch stale" in dlg.statuses[-1]


# ---------------------------------------------------------------------------
# Re-run workflow
# ---------------------------------------------------------------------------


def test_rerun_selected_workflow(dlg) -> None:
    from quill.core.github.items_provider import GitHubWorkflowRun

    run = GitHubWorkflowRun(name="CI", status="completed", run_number=7)
    dlg._rows = [run]
    dlg._selected_indices = lambda: [0]
    dlg._confirm_action = lambda message, title: True
    dlg._rerun_selected_workflow()
    assert dlg._provider.reran == [("owner/repo", 7)]


def test_rerun_declined(dlg) -> None:
    from quill.core.github.items_provider import GitHubWorkflowRun

    run = GitHubWorkflowRun(name="CI", status="completed", run_number=7)
    dlg._rows = [run]
    dlg._selected_indices = lambda: [0]
    dlg._confirm_action = lambda message, title: False
    dlg._rerun_selected_workflow()
    assert dlg._provider.reran == []


# ---------------------------------------------------------------------------
# Comment reply / edit / delete
# ---------------------------------------------------------------------------


def test_reply_to_thread(dlg, monkeypatch: pytest.MonkeyPatch) -> None:
    dlg._comment_target = ("owner/repo", 9)
    monkeypatch.setattr(wx, "TextEntryDialog", lambda *a, **k: _FakeTextEntry("thanks!"))
    dlg._reply_to_thread()
    assert dlg._provider.posted_comments == [("owner/repo", 9, "thanks!")]


def test_reply_without_a_loaded_thread(dlg) -> None:
    dlg._comment_target = None
    dlg._reply_to_thread()
    assert dlg._provider.posted_comments == []
    assert "Select an issue" in dlg.announcements[-1]


def test_edit_current_comment(dlg, monkeypatch: pytest.MonkeyPatch) -> None:
    dlg._comments = [{"id": "42", "author": "me", "body": "typo hree"}]
    dlg._current_comment = 0
    monkeypatch.setattr(wx, "TextEntryDialog", lambda *a, **k: _FakeTextEntry("typo here"))
    dlg._edit_current_comment()
    assert dlg._provider.edited_comments == [("owner/repo", 42, "typo here")]


def test_edit_without_a_navigated_comment(dlg) -> None:
    dlg._comments = []
    dlg._current_comment = -1
    dlg._edit_current_comment()
    assert dlg._provider.edited_comments == []
    assert "Navigate to a comment" in dlg.announcements[-1]


def test_delete_current_comment(dlg, monkeypatch: pytest.MonkeyPatch) -> None:
    dlg._comments = [{"id": "42", "author": "me", "body": "oops"}]
    dlg._current_comment = 0
    monkeypatch.setattr(
        "quill.ui.github_repo_admin_dialogs.TypedConfirmDialog",
        lambda *a, **k: _FakeTypedConfirm(True),
    )
    dlg._delete_current_comment()
    assert dlg._provider.deleted_comments == [("owner/repo", 42)]


def test_delete_current_comment_declined(dlg, monkeypatch: pytest.MonkeyPatch) -> None:
    dlg._comments = [{"id": "42", "author": "me", "body": "oops"}]
    dlg._current_comment = 0
    monkeypatch.setattr(
        "quill.ui.github_repo_admin_dialogs.TypedConfirmDialog",
        lambda *a, **k: _FakeTypedConfirm(False),
    )
    dlg._delete_current_comment()
    assert dlg._provider.deleted_comments == []


# ---------------------------------------------------------------------------
# Fakes
# ---------------------------------------------------------------------------


class _FakeTextEntry:
    def __init__(self, value: str, *, ok: bool = True) -> None:
        self._value = value
        self._ok = ok

    def GetValue(self) -> str:
        return self._value

    def __enter__(self) -> _FakeTextEntry:
        return self

    def __exit__(self, *exc: object) -> None:
        return None


class _FakeTypedConfirm:
    def __init__(self, result: bool) -> None:
        self._result = result

    def show(self) -> bool:
        return self._result


class _FakeRepoAdmin:
    def __init__(self, sink: list[tuple[str, str]]) -> None:
        self._sink = sink

    def delete_branch(self, repo: str, branch: str) -> None:
        self._sink.append((repo, branch))

    def close(self) -> None:
        pass
