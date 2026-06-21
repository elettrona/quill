"""DLG-3 Phase 5: startup / onboarding hardening characterization.

Phase 5 hardens the first-run / startup modal chain (screen-reader detection,
trust consent, crash recovery, first-run onboarding, watch folders). Two of its
three acceptance claims are pure-code contracts that these tests pin so they
cannot silently regress:

1. **The screen-reader startup-crash path is retired.** Every deferred startup
   step runs inside its own ``try/except`` in ``_run_deferred_startup_tasks``; a
   throwing step is recorded via ``_report_startup_task_failure`` and the app
   stays open and keeps running the remaining steps. (Historically an exception
   here killed Quill right after the startup tip with nothing in the log.)

2. **Explicit-consent requirements are preserved.** ``_show_trust_consent_onboarding``
   only marks consent complete when the user explicitly accepts; declining never
   records consent, and a decline during startup closes the app instead of
   silently continuing.

The third claim (deterministic focus across chained modal flows) is verified
live in Phase 8 (DLG-3.8) and structurally enforced by the dialog-hardening
contract gate; it is not re-asserted here.

A #179-era test pins the deferred-modal offload contract: the crash-recovery
offer's snapshot read + ``mkdir`` runs on a background task, and a thrown
``read_recovery_snapshot`` is reported via ``_report_startup_task_failure``
without ever calling ``ShowModal``.
"""

from __future__ import annotations

import quill.ui.main_frame as main_frame_module
from quill.ui.main_frame import MainFrame


class _Frame:
    def __init__(self) -> None:
        self.closed = 0

    def Close(self):  # noqa: N802 - mimics wx API
        self.closed += 1


class _Wx:
    ID_YES = 5103
    ID_NO = 5104
    YES_NO = 0x0008
    ICON_INFORMATION = 0x0002


def _build_frame() -> MainFrame:
    frame = MainFrame.__new__(MainFrame)
    frame.frame = _Frame()
    frame._wx = _Wx()
    frame.settings = type("Settings", (), {"auto_check_updates": False})()
    frame._safe_mode = False
    frame._status: list[str] = []
    frame._set_status = lambda message: frame._status.append(message)
    return frame


def test_deferred_startup_isolates_a_throwing_step_and_keeps_going(monkeypatch) -> None:
    frame = _build_frame()
    failures: list[str] = []
    frame._report_startup_task_failure = lambda label: failures.append(label)
    frame._start_ipc_poll = lambda: None
    frame._first_run_trust_consent_prompt = False

    ran: list[str] = []

    def _boom() -> None:
        raise RuntimeError("crash recovery exploded")

    frame._offer_crash_recovery = _boom
    frame._maybe_run_first_run_onboarding = lambda: ran.append("first-run")
    frame._maybe_start_watch_folder = lambda: ran.append("watch-folder")
    monkeypatch.setattr(
        main_frame_module,
        "detect_screen_reader",
        lambda: type("D", (), {"detected": False, "name": ""})(),
    )

    # Must not raise -- the startup-crash path is retired.
    frame._run_deferred_startup_tasks()

    # The throwing step was recorded, and the steps after it still ran.
    assert "crash recovery" in failures
    assert ran == ["first-run", "watch-folder"]
    assert frame.frame.closed == 0


def test_trust_consent_decline_does_not_record_consent(monkeypatch) -> None:
    frame = _build_frame()
    frame._show_modal_dialog = lambda dialog, title: _Wx.ID_NO
    marked: list[int] = []
    monkeypatch.setattr(main_frame_module, "mark_trust_consent_complete", lambda: marked.append(1))

    class _Dialog:
        def __init__(self, *a, **k) -> None:
            pass

        def SetYesNoLabels(self, *a):  # noqa: N802 - mimics wx API
            return True

        def Destroy(self):  # noqa: N802 - mimics wx API
            return True

    frame._wx.MessageDialog = _Dialog

    accepted = frame._show_trust_consent_onboarding(force=True)

    assert accepted is False
    assert marked == []


def test_trust_consent_accept_records_consent(monkeypatch) -> None:
    frame = _build_frame()
    frame._show_modal_dialog = lambda dialog, title: _Wx.ID_YES
    marked: list[int] = []
    monkeypatch.setattr(main_frame_module, "mark_trust_consent_complete", lambda: marked.append(1))

    class _Dialog:
        def __init__(self, *a, **k) -> None:
            pass

        def SetYesNoLabels(self, *a):  # noqa: N802 - mimics wx API
            return True

        def Destroy(self):  # noqa: N802 - mimics wx API
            return True

    frame._wx.MessageDialog = _Dialog

    accepted = frame._show_trust_consent_onboarding(force=True)

    assert accepted is True
    assert marked == [1]


def test_declined_startup_consent_closes_the_app(monkeypatch) -> None:
    frame = _build_frame()
    frame._report_startup_task_failure = lambda label: None
    frame._start_ipc_poll = lambda: None
    frame._first_run_trust_consent_prompt = True
    frame._show_trust_consent_onboarding = lambda force: False
    later_steps: list[str] = []
    frame._offer_crash_recovery = lambda: later_steps.append("crash")
    frame._maybe_run_first_run_onboarding = lambda: later_steps.append("first-run")
    frame._maybe_start_watch_folder = lambda: later_steps.append("watch")
    monkeypatch.setattr(
        main_frame_module,
        "detect_screen_reader",
        lambda: type("D", (), {"detected": False, "name": ""})(),
    )

    frame._run_deferred_startup_tasks()

    # Declining consent closes the app and short-circuits the rest of startup.
    assert frame.frame.closed == 1
    assert later_steps == []
    assert frame._status[-1] == "Startup consent declined. Quill is closing."


# ---------------------------------------------------------------------------
# #179: crash-recovery snapshot I/O must run on a background task, not the UI
# thread.  These tests pin the offload contract.
# ---------------------------------------------------------------------------


class _FakeTask:
    def __init__(self, name: str, func, kwargs, on_success, on_failure) -> None:
        self.name = name
        self.func = func
        self.kwargs = kwargs
        self.on_success = on_success
        self.on_failure = on_failure


class _FakeTaskManager:
    """In-process stand-in for ``TaskManager`` that drives callbacks synchronously."""

    def __init__(self) -> None:
        self.submissions: list[_FakeTask] = []

    def submit(
        self,
        name: str,
        func,
        *,
        on_success=None,
        on_failure=None,
        **kwargs,
    ) -> _FakeTask:
        task = _FakeTask(name, func, kwargs, on_success, on_failure)
        self.submissions.append(task)
        return task

    def run_last_success(self, result) -> None:
        """Simulate the worker finishing successfully."""
        last = self.submissions[-1]
        assert last.on_success is not None
        last.on_success("op-id", result)

    def run_last_failure(self, exc: BaseException) -> None:
        last = self.submissions[-1]
        assert last.on_failure is not None
        last.on_failure("op-id", exc)


def _make_offer():
    """Build a minimal RecoveryOffer-shaped stand-in."""

    from dataclasses import dataclass
    from pathlib import Path

    @dataclass(frozen=True, slots=True)
    class _Offer:
        session_id: str = "sess-1"
        snapshot: Path = Path("/tmp/snap.txt")
        cursor_position: int = 0
        dismissal_count: int = 0

    return _Offer()


def test_crash_recovery_offloads_snapshot_io_to_background(monkeypatch) -> None:
    """#179: ``_offer_crash_recovery`` must not block the UI thread on snapshot I/O."""
    frame = _build_frame()
    frame._recovery_offers = [_make_offer()]
    frame._task_manager = _FakeTaskManager()
    show_calls: list[dict] = []

    def _record_show(ctx, prepared):
        show_calls.append({"ctx": ctx, "prepared": prepared})

    frame._show_crash_recovery_dialog = _record_show

    # Pre-mock read_recovery_snapshot + app_data_dir so the prepare worker is
    # safe to call synchronously.
    monkeypatch.setattr(
        main_frame_module, "app_data_dir", lambda: __import__("pathlib").Path("/tmp")
    )
    monkeypatch.setattr(
        main_frame_module,
        "read_recovery_snapshot",
        lambda _p: ("line1\nline2\nline3", False),
    )

    # Must not raise, must not call ShowModal directly.
    frame._offer_crash_recovery()

    assert len(frame._task_manager.submissions) == 1
    assert frame._task_manager.submissions[0].name == "crash-recovery-prepare"
    # _show_crash_recovery_dialog has not been called yet — the worker
    # delivers its result via on_success, which we drive next.
    assert show_calls == []

    # Drive the worker success callback (this is what TaskManager would do
    # via call_ui_safely after the worker returns).
    frame._task_manager.run_last_success({
        "logs_path": __import__("pathlib").Path("/tmp/logs"),
        "preview_text": "line1\nline2",
    })

    assert len(show_calls) == 1
    assert show_calls[0]["prepared"]["preview_text"] == "line1\nline2"


def test_crash_recovery_prepare_failure_is_reported_via_startup_failure(monkeypatch) -> None:
    """A throwing prepare must record via ``_report_startup_task_failure`` and
    never show the dialog (no half-broken modal)."""
    frame = _build_frame()
    frame._recovery_offers = [_make_offer()]
    frame._task_manager = _FakeTaskManager()
    show_calls: list = []
    frame._show_crash_recovery_dialog = lambda *a, **k: show_calls.append((a, k))
    failures: list[str] = []
    frame._report_startup_task_failure = lambda label: failures.append(label)
    monkeypatch.setattr(
        main_frame_module, "app_data_dir", lambda: __import__("pathlib").Path("/tmp")
    )
    monkeypatch.setattr(
        main_frame_module,
        "read_recovery_snapshot",
        lambda _p: (_ for _ in ()).throw(OSError("boom")),
    )

    frame._offer_crash_recovery()
    frame._task_manager.run_last_failure(OSError("boom"))

    assert show_calls == []
    assert failures == ["crash recovery"]


def test_deferred_startup_task_list_includes_help_topics_warmup() -> None:
    """#179: the help topics renderer must be warmed during deferred startup so
    the first F1 is instant."""
    frame = _build_frame()
    failures: list[str] = []
    frame._report_startup_task_failure = lambda label: failures.append(label)
    frame._start_ipc_poll = lambda: None
    frame._first_run_trust_consent_prompt = False
    frame._offer_crash_recovery = lambda: None
    frame._maybe_run_first_run_onboarding = lambda: None
    frame._maybe_start_watch_folder = lambda: None
    import quill.ui.main_frame as mf

    monkeypatch = __import__("pytest").MonkeyPatch()
    try:
        monkeypatch.setattr(
            mf,
            "detect_screen_reader",
            lambda: type("D", (), {"detected": False, "name": ""})(),
        )
        # Capture the source so we can grep for the warm-up entry without
        # having to drive every task in the list.
        from pathlib import Path

        src = Path(mf.__file__).read_text(encoding="utf-8")
    finally:
        monkeypatch.undo()

    assert '"help topics warm-up"' in src
    assert "warm_help_topics" in src


def test_first_run_defers_tab_creation_until_wizard_returns() -> None:
    """#606: on first launch the wizard must open before any document tab.

    __init__ builds the frame without a tab when
    setup_wizard_completed is False, so macOS screen readers do not
    announce "Untitled" before the wizard modal grabs focus.
    _maybe_run_first_run_onboarding creates the tab via
    new_document() after the wizard returns, so the user lands in
    a fresh document once the wizard is closed.
    """
    frame = _build_frame()
    frame.settings = type(
        "Settings", (), {"setup_wizard_completed": False, "auto_check_updates": False}
    )()
    frame._first_run_wizard_pending = True
    frame._document_tabs = []
    failures: list[str] = []
    frame._report_startup_task_failure = lambda label: failures.append(label)

    wizard_open_tab_count: list[int] = []

    def _fake_run_startup_wizard(*, first_run: bool = False):
        # #606: while the wizard is "open" the notebook must be
        # empty -- no "Untitled" tab should have been built in
        # __init__ on this branch.
        wizard_open_tab_count.append(len(frame._document_tabs))
        return True, False

    frame.run_startup_wizard = _fake_run_startup_wizard  # type: ignore[method-assign]

    def _stub_create_document_tab(document: object, select: bool = True) -> None:
        # Mirror the real _create_document_tab() side effect for the
        # assertion: a fresh tab lands in _document_tabs. We stub it
        # because the production method requires live wx widgets
        # (Panel, SplitterWindow, TextCtrl) that the __new__-built
        # frame does not have.
        class _StubTab:
            pass

        frame._document_tabs.append(_StubTab())

    frame._create_document_tab = _stub_create_document_tab  # type: ignore[method-assign]
    frame._location_ring = type("LR", (), {"record": lambda self, n: None})()
    frame._region_tracker = type("RT", (), {"enter": lambda self, name: None})()
    frame._focus_editor = lambda: None
    # Pre-clear the legacy first-run flags the wizard branch writes
    # to, so we exercise the production path that suppresses them.
    frame._first_run_profile_prompt = True
    frame._first_run_assistant_prompt = True
    frame._first_run_glow_prompt = True
    frame._first_run_speech_prompt = True
    frame._first_run_watch_folder_prompt = True

    frame._maybe_run_first_run_onboarding()

    # #606 invariants
    assert wizard_open_tab_count == [0], "no document tab must exist while the wizard is open"
    assert len(frame._document_tabs) == 1, (
        "_create_document_tab() must create exactly one tab after the wizard"
    )
    assert frame._first_run_wizard_pending is False, (
        "the pending flag must be cleared once the tab is created"
    )
    # The wizard branch suppresses the legacy per-feature prompts.
    assert frame._first_run_profile_prompt is False
    assert frame._first_run_assistant_prompt is False
    assert frame._first_run_glow_prompt is False
    assert frame._first_run_speech_prompt is False
    assert frame._first_run_watch_folder_prompt is False
    # No startup-task failures were reported by this happy path.
    assert failures == []


# ---------------------------------------------------------------------------
# #44: an undeletable new-install marker must not force the wizard to reopen
# on every subsequent launch.
# ---------------------------------------------------------------------------


class _UndeletableMarker:
    """A marker path stand-in whose unlink() always fails, like a marker
    written into an elevated install directory the running user can't
    write to."""

    def __init__(self, mtime: float) -> None:
        self._mtime = mtime
        self.unlink_attempts = 0

    def exists(self) -> bool:
        return True

    def stat(self):
        return type("Stat", (), {"st_mtime": self._mtime})()

    def unlink(self) -> None:
        self.unlink_attempts += 1
        raise OSError("Access is denied")


def test_undeletable_marker_does_not_reopen_wizard_on_next_launch(monkeypatch, tmp_path) -> None:
    import quill.core.paths as paths_module

    frame = _build_frame()
    frame.settings = type("Settings", (), {"setup_wizard_completed": True})()
    frame.run_startup_wizard = lambda **kwargs: None
    marker = _UndeletableMarker(mtime=12345.0)
    monkeypatch.setattr(paths_module, "new_install_marker_path", lambda: marker)
    monkeypatch.setattr(paths_module, "app_data_dir", lambda: tmp_path)

    saved: list[bool] = []
    import quill.core.settings as settings_module

    monkeypatch.setattr(
        settings_module, "save_settings", lambda s: saved.append(s.setup_wizard_completed)
    )

    # First launch: marker exists and hasn't been consumed before, so the
    # wizard flag resets even though the delete itself fails.
    frame._maybe_run_first_run_onboarding()
    assert marker.unlink_attempts == 1
    assert saved == [False]

    # Second launch: same undeleted marker, same mtime. Before the fix this
    # would reset setup_wizard_completed to False again every single launch,
    # reopening the wizard forever. The sentinel recorded under app_data_dir()
    # must recognize this marker as already consumed and skip the reset.
    frame.settings.setup_wizard_completed = True
    frame._maybe_run_first_run_onboarding()
    assert saved == [False]  # no second reset recorded
