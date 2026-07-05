"""Audio Studio wizard — the document-narration journey pages.

Four pages: what to read (folder + types + filters), who reads it (engine,
voice, pace, round-robin rotation, translated editions), how chapters work
(mode, headings, the transition sounder, gaps), and output (format, existing-
file policy, mastering and diagnostics). Together they collect every field of
the classic Batch Export dialog — nothing is lost in the rebrand.
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import wx

from quill.core.i18n import _
from quill.ui.audio_studio.pages_base import StudioPage, set_accessible_name
from quill.ui.audio_studio.request import (
    ALL_EXTENSIONS,
    EXISTING_POLICIES,
    EXTENSION_GROUPS,
    FORMAT_CHOICES,
    FORMAT_INDEX,
    MODE_CHOICES,
    MODE_INDEX,
    BatchSpeechRequest,
)
from quill.ui.dialog_contract import apply_listbox_activation

# (label, engine_id) pairs, mirroring the Speech Hub's engine list.
EngineOptions = list[tuple[str, str]]
# engine_id -> [(voice_label, voice_id), ...]
VoicesFor = Callable[[str], list[tuple[str, str]]]


class DocSourcePage(StudioPage):
    """What should I read? Folder, file types, and discovery filters."""

    def __init__(self, parent: wx.Window, defaults: BatchSpeechRequest) -> None:
        super().__init__(
            parent,
            "audio_studio.doc_source",
            _("What should I read?"),
            _("Pick the folder of documents and which file types to include."),
        )
        self.add_label(_("&Source folder (documents to convert):"))
        row = wx.BoxSizer(wx.HORIZONTAL)
        self.source = wx.TextCtrl(self, value=str(defaults.source_folder))
        self.source.SetName(_("Source folder"))
        browse = wx.Button(self, label=_("B&rowse..."))
        browse.Bind(wx.EVT_BUTTON, self._on_browse)
        row.Add(self.source, 1, wx.EXPAND | wx.RIGHT, 6)
        row.Add(browse, 0)
        self.sizer.Add(row, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 12)

        self.recursive = wx.CheckBox(self, label=_("Include su&bfolders"))
        self.recursive.SetValue(defaults.recursive)
        self.sizer.Add(self.recursive, 0, wx.LEFT | wx.TOP, 12)

        self.add_label(_("File &types to include:"))
        self.ext_boxes: list[tuple[wx.CheckBox, str]] = []
        ext_row = wx.BoxSizer(wx.HORIZONTAL)
        for text, ext in ALL_EXTENSIONS:
            cb = wx.CheckBox(self, label=_(text))
            cb.SetValue(ext in defaults.extensions)
            ext_row.Add(cb, 0, wx.RIGHT, 10)
            self.ext_boxes.append((cb, ext))
        self.sizer.Add(ext_row, 0, wx.LEFT | wx.TOP, 12)

        self.add_label(_("Only incl&ude files matching (globs, ; or , separated; blank = all):"))
        self.include = wx.TextCtrl(self, value=defaults.include_glob)
        self.include.SetName(_("Include files matching"))
        self.sizer.Add(self.include, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 12)
        self.add_label(_("E&xclude files matching (globs, ; or , separated):"))
        self.exclude = wx.TextCtrl(self, value=defaults.exclude_glob)
        self.exclude.SetName(_("Exclude files matching"))
        self.sizer.Add(self.exclude, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 12)

    def _on_browse(self, _evt: wx.Event) -> None:
        with wx.DirDialog(self, _("Choose the folder of documents to convert")) as dlg:
            if dlg.ShowModal() == wx.ID_OK:  # GATE-42-OK: native folder picker
                self.source.SetValue(dlg.GetPath())

    def selected_extensions(self) -> tuple[str, ...]:
        exts: list[str] = []
        for cb, ext in self.ext_boxes:
            if cb.GetValue():
                exts.extend(EXTENSION_GROUPS.get(ext, (ext,)))
        return tuple(exts)

    def collect(self, req: BatchSpeechRequest) -> None:
        req.source_folder = Path(self.source.GetValue().strip())
        req.recursive = self.recursive.GetValue()
        req.extensions = self.selected_extensions()
        req.include_glob = self.include.GetValue().strip()
        req.exclude_glob = self.exclude.GetValue().strip()

    def is_valid(self) -> tuple[bool, str]:
        text = self.source.GetValue().strip()
        if not text or not Path(text).is_dir():
            return False, _("Choose a source folder that exists.")
        if not self.selected_extensions():
            return False, _("Select at least one file type to include.")
        return True, ""


class VoicesPage(StudioPage):
    """Who should read it? Engine, voice, pace, rotation, translated editions."""

    def __init__(
        self,
        parent: wx.Window,
        defaults: BatchSpeechRequest,
        *,
        engine_options: EngineOptions,
        engine_available: dict[str, bool],
        voices_for: VoicesFor,
        on_preview: Callable[[str, str], None],
    ) -> None:
        super().__init__(
            parent,
            "audio_studio.voices",
            _("Who should read it?"),
            _("Choose the voice — or a whole cast — and hear a preview."),
        )
        self._engine_options = engine_options
        self._engine_available = engine_available
        self._voices_for = voices_for
        self._on_preview = on_preview
        self._voice_pairs: list[tuple[str, str]] = []
        # Round-robin rotation: ordered (voice_id, label) for the selected engine.
        self._rr_voices: list[tuple[str, str]] = []
        # Translation targets: ordered (lang_code, engine, voice_id, display_label).
        self._tr_targets: list[tuple[str, str, str, str]] = []

        self.add_label(_("&Engine:"))
        self.engine = wx.Choice(
            self, choices=[self._engine_label(lbl, eid) for lbl, eid in engine_options]
        )
        self.engine.SetName(_("Engine"))
        self.engine.Bind(wx.EVT_CHOICE, lambda _e: self._on_engine_change())
        self.sizer.Add(self.engine, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 12)
        self.select_engine(defaults.engine)

        self.add_label(_("&Voice:"))
        voice_row = wx.BoxSizer(wx.HORIZONTAL)
        self.voice = wx.Choice(self, choices=[])
        self.voice.SetName(_("Voice"))
        preview_btn = wx.Button(self, label=_("&Preview voice"))
        preview_btn.Bind(wx.EVT_BUTTON, self._on_preview_click)
        voice_row.Add(self.voice, 1, wx.EXPAND | wx.RIGHT, 6)
        voice_row.Add(preview_btn, 0)
        self.sizer.Add(voice_row, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 12)

        pace_row = wx.BoxSizer(wx.HORIZONTAL)
        pace_row.Add(wx.StaticText(self, label=_("R&ate (WPM):")), 0, wx.ALIGN_CENTER_VERTICAL)
        self.rate = wx.SpinCtrl(self, min=80, max=450, initial=defaults.rate)
        set_accessible_name(self.rate, _("Rate (WPM)"))
        pace_row.Add(self.rate, 0, wx.LEFT | wx.RIGHT, 6)
        pace_row.Add(wx.StaticText(self, label=_("&Kokoro speed:")), 0, wx.ALIGN_CENTER_VERTICAL)
        self.speed = wx.SpinCtrlDouble(self, min=0.5, max=2.0, inc=0.05, initial=defaults.speed)
        set_accessible_name(self.speed, _("Kokoro speed"))
        pace_row.Add(self.speed, 0, wx.LEFT, 6)
        self.sizer.Add(pace_row, 0, wx.LEFT | wx.TOP, 12)

        # --- Round-robin voices (optional) ---
        self.add_label(_("Round-&robin voices (each article gets the next voice; optional):"))
        rr_add_row = wx.BoxSizer(wx.HORIZONTAL)
        self.rr_pick = wx.Choice(self, choices=[])
        self.rr_pick.SetName(_("Round-robin voice to add"))
        rr_add = wx.Button(self, label=_("A&dd voice"))
        rr_add.Bind(wx.EVT_BUTTON, lambda _e: self.rr_add())
        rr_add_row.Add(self.rr_pick, 1, wx.EXPAND | wx.RIGHT, 6)
        rr_add_row.Add(rr_add, 0)
        self.sizer.Add(rr_add_row, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 12)
        # A dedicated label immediately before the list: a screen reader names a list
        # from its preceding StaticText, so SetName alone leaves it announced unnamed.
        self.add_label(_("Voice o&rder (the rotation; use the buttons below to reorder):"))
        self.rr_list = wx.ListBox(self, style=wx.LB_SINGLE)
        self.rr_list.SetName(_("Round-robin voice order"))
        apply_listbox_activation(self.rr_list, lambda _e: self.rr_pick.SetFocus())
        self.sizer.Add(self.rr_list, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 12)
        rr_btn_row = wx.BoxSizer(wx.HORIZONTAL)
        rr_up = wx.Button(self, label=_("Move U&p"))
        rr_down = wx.Button(self, label=_("Move Dow&n"))
        rr_remove = wx.Button(self, label=_("Re&move"))
        rr_up.Bind(wx.EVT_BUTTON, lambda _e: self.rr_move(-1))
        rr_down.Bind(wx.EVT_BUTTON, lambda _e: self.rr_move(1))
        rr_remove.Bind(wx.EVT_BUTTON, lambda _e: self.rr_remove())
        for btn in (rr_up, rr_down, rr_remove):
            rr_btn_row.Add(btn, 0, wx.RIGHT, 6)
        self.sizer.Add(rr_btn_row, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 12)

        # --- Translated editions (optional) ---
        self.add_label(_("Also export in other &languages (translated):"))
        from quill.core.ai.translation import SUPPORTED_LANGUAGES

        self._tr_lang_pairs = sorted(SUPPORTED_LANGUAGES.items())  # (name, code)
        self._tr_voice_opts: list = []
        tr_add_row = wx.BoxSizer(wx.HORIZONTAL)
        self.tr_lang = wx.Choice(self, choices=[name for name, _c in self._tr_lang_pairs])
        self.tr_lang.SetName(_("Translation language"))
        self.tr_lang.Bind(wx.EVT_CHOICE, lambda _e: self.reload_tr_voices())
        self.tr_voice = wx.Choice(self, choices=[])
        self.tr_voice.SetName(_("Translation voice"))
        tr_add = wx.Button(self, label=_("Add lan&guage"))
        tr_add.Bind(wx.EVT_BUTTON, lambda _e: self.tr_add())
        tr_add_row.Add(self.tr_lang, 1, wx.EXPAND | wx.RIGHT, 6)
        tr_add_row.Add(self.tr_voice, 2, wx.EXPAND | wx.RIGHT, 6)
        tr_add_row.Add(tr_add, 0)
        self.sizer.Add(tr_add_row, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 12)
        self.add_label(_("Languages &chosen (translated exports):"))
        self.tr_list = wx.ListBox(self, style=wx.LB_SINGLE)
        self.tr_list.SetName(_("Translation targets"))
        apply_listbox_activation(self.tr_list, lambda _e: self.tr_lang.SetFocus())
        self.sizer.Add(self.tr_list, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 12)
        tr_btn_row = wx.BoxSizer(wx.HORIZONTAL)
        tr_remove = wx.Button(self, label=_("Remove la&nguage"))
        tr_remove.Bind(wx.EVT_BUTTON, lambda _e: self.tr_remove())
        tr_btn_row.Add(tr_remove, 0, wx.RIGHT, 6)
        tr_btn_row.Add(
            wx.StaticText(self, label=_("Trans&late with:")), 0, wx.ALIGN_CENTER_VERTICAL
        )
        self.tr_provider = wx.Choice(
            self, choices=[_("AI provider (cloud)"), _("LibreTranslate (local)")]
        )
        self.tr_provider.SetName(_("Translate with"))
        self.tr_provider.SetSelection(1 if defaults.translation_provider == "libretranslate" else 0)
        tr_btn_row.Add(self.tr_provider, 0, wx.LEFT, 6)
        self.sizer.Add(tr_btn_row, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 12)

        self.reload_voices(initial_voice=defaults.voice)
        self.seed_rotation(defaults.round_robin_voices)
        self.reload_tr_voices()
        self.seed_translations(defaults.translation_targets)

    # -- engine / voice -------------------------------------------------------

    def _engine_label(self, label: str, engine_id: str) -> str:
        if not self._engine_available.get(engine_id, True):
            return _("{engine} (not installed)").format(engine=label)
        return label

    def select_engine(self, engine_id: str) -> None:
        for i, (_lbl, eid) in enumerate(self._engine_options):
            if eid == engine_id:
                self.engine.SetSelection(i)
                return
        self.engine.SetSelection(0)

    def current_engine_id(self) -> str:
        idx = self.engine.GetSelection()
        if 0 <= idx < len(self._engine_options):
            return self._engine_options[idx][1]
        return self._engine_options[0][1] if self._engine_options else "sapi5"

    def reload_voices(self, *, initial_voice: str = "") -> None:
        engine_id = self.current_engine_id()
        self._voice_pairs = self._voices_for(engine_id)
        labels = [lbl for lbl, _vid in self._voice_pairs]
        self.voice.Set(labels)
        self.rr_pick.Set(labels)
        if labels:
            self.rr_pick.SetSelection(0)
        chosen = 0
        for i, (_lbl, vid) in enumerate(self._voice_pairs):
            if vid == initial_voice:
                chosen = i
                break
        if self._voice_pairs:
            self.voice.SetSelection(chosen)

    def _on_engine_change(self) -> None:
        # Voices are engine-specific, so switching engines clears the rotation.
        self.reload_voices()
        self._rr_voices = []
        self._refresh_rr_list()

    def current_voice_id(self) -> str:
        idx = self.voice.GetSelection()
        if 0 <= idx < len(self._voice_pairs):
            return self._voice_pairs[idx][1]
        return ""

    def _on_preview_click(self, _evt: wx.Event) -> None:
        self._on_preview(self.current_engine_id(), self.current_voice_id())

    # -- round-robin rotation --------------------------------------------------

    def seed_rotation(self, voice_ids: tuple[str, ...]) -> None:
        """Pre-fill the rotation from saved ids, mapping each to its current label."""
        by_id = {vid: lbl for lbl, vid in self._voice_pairs}
        self._rr_voices = [(vid, by_id[vid]) for vid in voice_ids if vid in by_id]
        self._refresh_rr_list()

    def _refresh_rr_list(self, *, select: int = -1) -> None:
        self.rr_list.Set([lbl for _vid, lbl in self._rr_voices])
        if self._rr_voices:
            index = select if 0 <= select < len(self._rr_voices) else 0
            self.rr_list.SetSelection(index)

    def _rr_selected_index(self) -> int:
        idx = self.rr_list.GetSelection()
        return idx if 0 <= idx < len(self._rr_voices) else -1

    def rr_add(self) -> None:
        idx = self.rr_pick.GetSelection()
        if not (0 <= idx < len(self._voice_pairs)):
            return
        label, vid = self._voice_pairs[idx]
        if any(existing == vid for existing, _ in self._rr_voices):
            return  # already in the rotation
        self._rr_voices.append((vid, label))
        self._refresh_rr_list(select=len(self._rr_voices) - 1)

    def rr_move(self, delta: int) -> None:
        idx = self._rr_selected_index()
        target = idx + delta
        if idx < 0 or not (0 <= target < len(self._rr_voices)):
            return
        self._rr_voices[idx], self._rr_voices[target] = (
            self._rr_voices[target],
            self._rr_voices[idx],
        )
        self._refresh_rr_list(select=target)

    def rr_remove(self) -> None:
        idx = self._rr_selected_index()
        if idx < 0:
            return
        del self._rr_voices[idx]
        self._refresh_rr_list(select=min(idx, len(self._rr_voices) - 1))

    # -- translated editions ----------------------------------------------------

    def _current_tr_lang(self) -> tuple[str, str]:
        idx = self.tr_lang.GetSelection()
        return self._tr_lang_pairs[idx] if 0 <= idx < len(self._tr_lang_pairs) else ("", "")

    def reload_tr_voices(self) -> None:
        from quill.core.speech.voice_languages import voices_for_language

        _name, code = self._current_tr_lang()
        # Local tiers first (eSpeak/SAPI), then the premium multilingual cloud voices
        # (OpenAI/Gemini/ElevenLabs) — each needs its provider API key at run time.
        self._tr_voice_opts = voices_for_language(code) if code else []
        self.tr_voice.Set([v.display for v in self._tr_voice_opts])
        if self._tr_voice_opts:
            self.tr_voice.SetSelection(0)

    def _refresh_tr_list(self, *, select: int = -1) -> None:
        self.tr_list.Set([t[3] for t in self._tr_targets])
        if self._tr_targets:
            index = select if 0 <= select < len(self._tr_targets) else 0
            self.tr_list.SetSelection(index)

    def tr_add(self) -> None:
        name, code = self._current_tr_lang()
        vidx = self.tr_voice.GetSelection()
        if not code or not (0 <= vidx < len(self._tr_voice_opts)):
            return
        v = self._tr_voice_opts[vidx]
        if any(t[0] == code and t[2] == v.voice_id for t in self._tr_targets):
            return
        self._tr_targets.append((code, v.engine, v.voice_id, f"{name}: {v.display}"))
        self._refresh_tr_list(select=len(self._tr_targets) - 1)

    def tr_remove(self) -> None:
        idx = self.tr_list.GetSelection()
        if 0 <= idx < len(self._tr_targets):
            del self._tr_targets[idx]
            self._refresh_tr_list(select=min(idx, len(self._tr_targets) - 1))

    def seed_translations(self, targets: tuple[tuple[str, str, str], ...]) -> None:
        from quill.core.ai.translation import LANGUAGE_NAMES

        self._tr_targets = [
            (lang, engine, voice_id, f"{LANGUAGE_NAMES.get(lang, lang)}: {voice_id} — {engine}")
            for lang, engine, voice_id in targets
        ]
        self._refresh_tr_list()

    # -- collect ------------------------------------------------------------------

    def collect(self, req: BatchSpeechRequest) -> None:
        req.engine = self.current_engine_id()
        req.voice = self.current_voice_id()
        req.rate = int(self.rate.GetValue())
        req.speed = float(self.speed.GetValue())
        req.round_robin_voices = tuple(vid for vid, _lbl in self._rr_voices)
        req.translation_targets = tuple((c, e, v) for c, e, v, _ in self._tr_targets)
        req.translation_provider = (
            "libretranslate" if self.tr_provider.GetSelection() == 1 else "ai_assistant"
        )


class ChaptersPage(StudioPage):
    """How should chapters work? Mode, headings, the transition sounder, gaps."""

    def __init__(self, parent: wx.Window, defaults: BatchSpeechRequest) -> None:
        super().__init__(
            parent,
            "audio_studio.chapters",
            _("How should chapters work?"),
            _("Shape the chapter structure and the sound between chapters."),
        )
        self.add_label(_("Chapter &mode:"))
        self.mode = wx.Choice(
            self,
            choices=[_("Single chaptered file"), _("Separate file per article")],
        )
        self.mode.SetName(_("Chapter mode"))
        self.mode.SetSelection(MODE_INDEX.get(defaults.chapter_mode, 0))
        self.sizer.Add(self.mode, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 12)

        self.speak_headings = wx.CheckBox(self, label=_("Speak each &heading aloud"))
        self.speak_headings.SetValue(defaults.speak_headings)
        self.sizer.Add(self.speak_headings, 0, wx.LEFT | wx.TOP, 12)
        self.combine = wx.CheckBox(self, label=_("&Combine empty headings into the next article"))
        self.combine.SetValue(defaults.combine_headings)
        self.sizer.Add(self.combine, 0, wx.LEFT | wx.TOP, 12)
        self.sound = wx.CheckBox(self, label=_("Play a transition s&ounder between headings"))
        self.sound.SetValue(defaults.sound_enabled)
        self.sizer.Add(self.sound, 0, wx.LEFT | wx.TOP, 12)

        gap_grid = wx.FlexGridSizer(cols=2, vgap=4, hgap=8)
        self.sound_volume = self.add_ms_spin(
            gap_grid, _("Sounder &volume (0-100):"), defaults.sound_volume, hi=100
        )
        self.article_gap = self.add_ms_spin(
            gap_grid, _("Pause between &articles (ms):"), defaults.article_gap_ms
        )
        self.sentence_gap = self.add_ms_spin(
            gap_grid, _("Pause between se&ntences (ms):"), defaults.sentence_gap_ms
        )
        self.tail_padding = self.add_ms_spin(
            gap_grid,
            _("Trailing pad per section, anti-cli&pping (ms):"),
            defaults.tail_padding_ms,
        )
        self.sizer.Add(gap_grid, 0, wx.LEFT | wx.TOP, 12)

    def collect(self, req: BatchSpeechRequest) -> None:
        idx = self.mode.GetSelection()
        req.chapter_mode = MODE_CHOICES[idx] if 0 <= idx < len(MODE_CHOICES) else "single"
        req.speak_headings = self.speak_headings.GetValue()
        req.combine_headings = self.combine.GetValue()
        req.sound_enabled = self.sound.GetValue()
        req.sound_volume = int(self.sound_volume.GetValue())
        req.article_gap_ms = int(self.article_gap.GetValue())
        req.sentence_gap_ms = int(self.sentence_gap.GetValue())
        req.tail_padding_ms = int(self.tail_padding.GetValue())


class OutputPage(StudioPage):
    """Where does the audio go? Format, existing-file policy, diagnostics."""

    def __init__(self, parent: wx.Window, defaults: BatchSpeechRequest) -> None:
        super().__init__(
            parent,
            "audio_studio.output",
            _("Output and diagnostics"),
            _("Choose the audio format and what happens to existing files."),
        )
        self.add_label(_("Output &format:"))
        self.format = wx.Choice(
            self,
            choices=[
                _("MP3 (with chapter markers)"),
                _("M4B audiobook (native chapters)"),
                _("WAV"),
            ],
        )
        self.format.SetName(_("Output format"))
        self.format.SetSelection(FORMAT_INDEX.get(defaults.output_format, 0))
        self.sizer.Add(self.format, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 12)

        self.add_label(_("If an audio file already e&xists:"))
        self.on_existing = wx.Choice(
            self, choices=[_("Skip (resume)"), _("Overwrite"), _("Rename (keep both)")]
        )
        self.on_existing.SetName(_("If an audio file already exists"))
        policy = "skip" if defaults.skip_existing else defaults.on_existing
        policy_idx = EXISTING_POLICIES.index(policy) if policy in EXISTING_POLICIES else 1
        self.on_existing.SetSelection(policy_idx)
        self.sizer.Add(self.on_existing, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 12)

        self.normalize = wx.CheckBox(self, label=_("Normalize &loudness to audiobook (ACX) level"))
        self.normalize.SetValue(defaults.normalize_loudness)
        self.sizer.Add(self.normalize, 0, wx.LEFT | wx.TOP, 12)
        self.dry_run = wx.CheckBox(
            self, label=_("Dr&y run: write preview text only (don't synthesize)")
        )
        self.dry_run.SetValue(defaults.dry_run)
        self.sizer.Add(self.dry_run, 0, wx.LEFT | wx.TOP, 12)
        self.save_spoken = wx.CheckBox(
            self, label=_("Save the te&xt sent to speech (one sidecar per document)")
        )
        self.save_spoken.SetValue(defaults.save_spoken_text)
        self.sizer.Add(self.save_spoken, 0, wx.LEFT | wx.TOP, 12)
        self.audition = wx.CheckBox(
            self,
            label=_("A&udition: convert only the first document, so you can judge the result"),
        )
        self.audition.SetValue(defaults.audition)
        self.sizer.Add(self.audition, 0, wx.LEFT | wx.TOP, 12)

        self.add_label(_("&Temporary files folder (blank = system temp):"))
        tmp_row = wx.BoxSizer(wx.HORIZONTAL)
        self.temp_folder = wx.TextCtrl(self, value=defaults.temp_folder)
        self.temp_folder.SetName(_("Temporary files folder"))
        tmp_browse = wx.Button(self, label=_("Browse temp&..."))
        tmp_browse.Bind(wx.EVT_BUTTON, self._on_browse_temp)
        tmp_row.Add(self.temp_folder, 1, wx.EXPAND | wx.RIGHT, 6)
        tmp_row.Add(tmp_browse, 0)
        self.sizer.Add(tmp_row, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 12)

    def _on_browse_temp(self, _evt: wx.Event) -> None:
        with wx.DirDialog(self, _("Choose a folder for temporary files")) as dlg:
            if dlg.ShowModal() == wx.ID_OK:  # GATE-42-OK: native folder picker
                self.temp_folder.SetValue(dlg.GetPath())

    def collect(self, req: BatchSpeechRequest) -> None:
        fidx = self.format.GetSelection()
        req.output_format = FORMAT_CHOICES[fidx] if 0 <= fidx < len(FORMAT_CHOICES) else "mp3"
        pidx = self.on_existing.GetSelection()
        req.on_existing = EXISTING_POLICIES[pidx] if 0 <= pidx < 3 else "overwrite"
        req.skip_existing = req.on_existing == "skip"
        req.normalize_loudness = self.normalize.GetValue()
        req.dry_run = self.dry_run.GetValue()
        req.save_spoken_text = self.save_spoken.GetValue()
        req.audition = self.audition.GetValue()
        req.temp_folder = self.temp_folder.GetValue().strip()
