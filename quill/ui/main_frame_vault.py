"""Accessible Vault UI (MainFrame mixin).

Wires the vault commands over ``quill.core.vault``:

* **Open Vault** — choose a folder; QUILL scans and indexes it and remembers it.
* **Follow Link** — with the caret on a ``[[wikilink]]``, open the target note at
  its heading/block; offer to create a missing note; ask (never guess) when a
  name is ambiguous.
* **Show Backlinks** — an accessible list of the notes that link to the current
  note, each read with its linking line; Enter opens the source at the link.
* **Insert Link to Note** — pick a note by title and insert ``[[Title]]``.

The pure helper ``relative_note_path`` is unit-tested; the rest is a wiring layer
over MainFrame (``_wx``, ``frame``, ``editor``, ``document``, ``settings``,
``commands``, ``_binding_for``, ``_show_modal_dialog``, ``open_file``,
``_set_status``, ``_announce``).
"""

from __future__ import annotations

from pathlib import Path


def relative_note_path(vault_root: Path | None, doc_path: Path | None) -> str | None:
    """Return ``doc_path`` relative to ``vault_root`` as POSIX, or None if outside."""
    if vault_root is None or doc_path is None:
        return None
    try:
        return doc_path.resolve().relative_to(vault_root.resolve()).as_posix()
    except (ValueError, OSError):
        return None


class VaultMixin:
    """The ``vault.*`` command handlers."""

    def open_vault(self) -> None:
        """Choose a vault folder, scan + index it, and remember it."""
        wx = self._wx
        picker = wx.DirDialog(
            self.frame,
            "Choose a vault folder (a folder of notes)",
            style=wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST,
        )
        try:
            if self._show_modal_dialog(picker, "Open Vault") != wx.ID_OK:
                self._set_status("Open Vault cancelled")
                return
            folder = picker.GetPath()
        finally:
            picker.Destroy()
        self.settings.vault_root = folder
        from quill.core.settings import save_settings

        save_settings(self.settings)
        self._vault = None  # force a reload
        if self._ensure_vault() is None:
            self._set_status("Could not open the vault")
            return
        notes = len(self._vault.notes)
        links = sum(len(targets) for targets in self._vault_index.forward.values())
        self._announce(f"Vault {Path(folder).name}: {notes} notes, {links} links.")

    def _ensure_vault(self):
        """Load and index the active vault on demand; cache it. Returns the Vault."""
        if getattr(self, "_vault", None) is not None:
            return self._vault
        root = str(getattr(self.settings, "vault_root", "") or "").strip()
        if not root or not Path(root).is_dir():
            return None
        from quill.core.vault import build_index, build_resolver, scan_vault

        self._set_status("Scanning vault...")
        self._vault = scan_vault(Path(root))
        self._vault_resolver = build_resolver(self._vault)
        self._vault_index = build_index(self._vault, self._vault_resolver)
        return self._vault

    def _vault_root_path(self) -> Path | None:
        root = str(getattr(self.settings, "vault_root", "") or "").strip()
        return Path(root) if root and Path(root).is_dir() else None

    def follow_wikilink(self) -> None:
        """Open the note the caret's ``[[link]]`` points to (Follow Link)."""
        from quill.core.vault import link_at_offset, resolve_link

        if self._ensure_vault() is None:
            self._set_status("Open a vault first (Tools > Vault > Open Vault)")
            return
        link = link_at_offset(self.editor.GetValue(), self.editor.GetInsertionPoint())
        if link is None:
            self._set_status("No wikilink at the cursor")
            return
        source_rel = relative_note_path(self._vault_root_path(), self._document_path())
        target = resolve_link(self._vault, self._vault_resolver, link, source_rel or "")
        if target is None:
            self._offer_create_note(link.target)
            return
        if target.ambiguous:
            chosen = self._choose_ambiguous(link.target, target.candidates)
            if chosen is None:
                return
            self._open_vault_note(chosen, target.offset)
            return
        self._open_vault_note(target.path, target.offset)

    def show_backlinks(self) -> None:
        """List the notes that link to the current note (Backlinks)."""
        from quill.core.vault import backlinks

        if self._ensure_vault() is None:
            self._set_status("Open a vault first (Tools > Vault > Open Vault)")
            return
        rel = relative_note_path(self._vault_root_path(), self._document_path())
        if rel is None or rel not in self._vault.notes:
            self._set_status("Save this note inside the vault to see its backlinks")
            return
        links = backlinks(self._vault_index, rel)
        if not links:
            self._set_status("No backlinks: no other note links here yet")
            return
        items = [
            (
                f"{self._vault.notes[bl.source_path].title}: {bl.context}",
                (bl.source_path, bl.offset),
            )
            for bl in links
        ]
        self._announce(f"{len(links)} notes link here.")
        self._show_vault_list(f"Backlinks to {self._vault.notes[rel].title}", items)

    def show_neighborhood(self) -> None:
        """List this note's outgoing links and backlinks together (traverse by ear)."""
        from quill.core.vault import neighborhood

        if self._ensure_vault() is None:
            self._set_status("Open a vault first (Tools > Vault > Open Vault)")
            return
        rel = relative_note_path(self._vault_root_path(), self._document_path())
        if rel is None or rel not in self._vault.notes:
            self._set_status("Save this note inside the vault to see its neighborhood")
            return
        hood = neighborhood(self._vault, self._vault_index, rel)
        items = [(f"→ {title}", (path, 0)) for path, title in hood.outgoing]
        items += [
            (
                f"← {self._vault.notes[bl.source_path].title}: {bl.context}",
                (bl.source_path, bl.offset),
            )
            for bl in hood.incoming
        ]
        if not items:
            self._set_status("This note has no links in or out yet")
            return
        self._announce(f"{len(hood.outgoing)} out, {len(hood.incoming)} in")
        self._show_vault_list(f"Neighborhood of {hood.title}", items)

    def show_unlinked_mentions(self) -> None:
        """List plain-text mentions of this note not yet linked (link-this-mention)."""
        from quill.core.vault import unlinked_mentions

        if self._ensure_vault() is None:
            self._set_status("Open a vault first (Tools > Vault > Open Vault)")
            return
        rel = relative_note_path(self._vault_root_path(), self._document_path())
        if rel is None or rel not in self._vault.notes:
            self._set_status("Save this note inside the vault to find its mentions")
            return
        mentions = unlinked_mentions(self._vault, self._vault_resolver, rel)
        if not mentions:
            self._set_status("No unlinked mentions: every mention of this note is already a link")
            return
        items = [
            (f"{self._vault.notes[m.source_path].title}: {m.context}", (m.source_path, m.offset))
            for m in mentions
        ]
        self._announce(f"{len(mentions)} unlinked mention(s)")
        self._show_vault_list(f"Unlinked mentions of {self._vault.notes[rel].title}", items)

    def insert_wikilink(self) -> None:
        """Pick a note and insert a ``[[Title]]`` link at the cursor."""
        if self._ensure_vault() is None:
            self._set_status("Open a vault first (Tools > Vault > Open Vault)")
            return
        titles = sorted({info.title for info in self._vault.notes.values()})
        if not titles:
            self._set_status("The vault has no notes to link to")
            return
        items = [(title, title) for title in titles]
        self._show_vault_list("Insert link to note", items, on_activate=self._insert_link_text)

    # --- helpers ----------------------------------------------------------

    def _document_path(self) -> Path | None:
        document = getattr(self, "document", None)
        path = getattr(document, "path", None)
        return path if isinstance(path, Path) else None

    def _open_vault_note(self, rel_path: str, offset: int) -> None:
        from quill.ui.main_frame_story_studio import offset_to_line

        root = self._vault_root_path()
        if root is None:
            return
        path = root / rel_path
        line: int | None = None
        if offset:
            try:
                text = path.read_text(encoding="utf-8")
            except OSError:
                text = ""
            line = offset_to_line(text, offset)
        self.open_file(path, line=line)

    def _insert_link_text(self, title: str) -> None:
        self.editor.WriteText(f"[[{title}]]")
        self._announce(f"Linked to {title}")

    def _offer_create_note(self, name: str) -> None:
        wx = self._wx
        root = self._vault_root_path()
        clean = name.strip()
        if root is None or not clean:
            self._set_status("No note to follow")
            return
        if (
            self._show_message_box(
                f'No note named "{clean}". Create it?',
                "Follow Link",
                wx.YES_NO | wx.ICON_QUESTION,
            )
            != wx.ID_YES
        ):
            self._set_status("No note created")
            return
        safe = "".join(ch for ch in clean if ch not in '<>:"/\\|?*').strip() or "Untitled"
        path = root / f"{safe}.md"
        try:
            if not path.exists():
                path.write_text(f"# {clean}\n", encoding="utf-8")
        except OSError as error:
            self._set_status(f"Could not create note: {error}")
            return
        self._vault = None  # re-index to include the new note
        self._ensure_vault()
        self.open_file(path)
        self._announce(f"Created and opened {clean}")

    def _choose_ambiguous(self, name: str, candidates: tuple[str, ...]) -> str | None:
        wx = self._wx
        dialog = wx.SingleChoiceDialog(
            self.frame,
            f'Several notes are named "{name}". Open which?',
            "Follow Link",
            list(candidates),
        )
        try:
            if self._show_modal_dialog(dialog, "Follow Link") != wx.ID_OK:
                return None
            index = dialog.GetSelection()
        finally:
            dialog.Destroy()
        return candidates[index] if 0 <= index < len(candidates) else None

    def _show_vault_list(self, heading: str, items, on_activate=None) -> None:
        from quill.ui.dialog_contract import apply_modal_ids
        from quill.ui.vault_dialogs import VaultListDialog

        wx = self._wx
        activate = on_activate or (lambda payload: self._open_vault_note(payload[0], payload[1]))
        view = VaultListDialog(wx, heading=heading, items=items, on_activate=activate)
        dialog = wx.Dialog(
            self.frame, title=heading, style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
        )
        outer = view.populate(dialog)
        buttons = dialog.CreateStdDialogButtonSizer(wx.OK | wx.CANCEL)
        outer.Add(buttons, 0, wx.EXPAND | wx.ALL, 10)
        apply_modal_ids(
            dialog, affirmative_id=wx.ID_OK, affirmative_label="&Open", cancel_id=wx.ID_CANCEL
        )
        try:
            self._show_modal_dialog(dialog, heading)
        finally:
            dialog.Destroy()

    def quick_switch_note(self) -> None:
        """Jump to a note by name — a filter-as-you-type switcher (Go to Note)."""
        from quill.core.vault.search import quick_switch_matches

        if self._ensure_vault() is None:
            self._set_status("Open a vault first (Tools > Vault > Open Vault)")
            return
        if not self._vault.notes:
            self._set_status("The vault has no notes yet")
            return

        def provider(query: str):
            return [(m.title, m.path) for m in quick_switch_matches(self._vault, query)]

        self._show_vault_filter(
            "Go to Note",
            prompt="Type part of a note title:",
            provider=provider,
            on_activate=lambda path: self._open_vault_note(path, 0),
            count_verb="matches",
        )

    def search_vault_notes(self) -> None:
        """Search every note; open a result at its matching line (vault-wide search)."""
        from quill.core.vault.search import search_vault

        if self._ensure_vault() is None:
            self._set_status("Open a vault first (Tools > Vault > Open Vault)")
            return

        def provider(query: str, options: dict[str, bool]):
            if not query.strip():
                return []
            hits = search_vault(
                self._vault,
                query,
                regex=options.get("Regex", False),
                whole_word=options.get("Whole word", False),
            )
            return [(hit.announce(), (hit.path, hit.line_number)) for hit in hits]

        self._show_vault_filter(
            "Search Vault",
            prompt="Search all notes:",
            provider=provider,
            on_activate=lambda payload: self._open_vault_note_at_line(payload[0], payload[1]),
            count_verb="results",
            option_labels=("Regex", "Whole word"),
        )

    def _open_vault_note_at_line(self, rel_path: str, line_number: int) -> None:
        root = self._vault_root_path()
        if root is not None:
            self.open_file(root / rel_path, line=max(0, line_number - 1))

    def _show_vault_filter(
        self, heading, *, prompt, provider, on_activate, count_verb, option_labels=()
    ) -> None:
        from quill.ui.dialog_contract import apply_modal_ids
        from quill.ui.vault_dialogs import VaultFilterDialog

        wx = self._wx
        view = VaultFilterDialog(
            wx,
            heading=heading,
            prompt=prompt,
            provider=provider,
            on_activate=on_activate,
            announce=self._announce,
            count_verb=count_verb,
            option_labels=option_labels,
        )
        dialog = wx.Dialog(
            self.frame, title=heading, style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
        )
        outer = view.populate(dialog)
        buttons = dialog.CreateStdDialogButtonSizer(wx.OK | wx.CANCEL)
        outer.Add(buttons, 0, wx.EXPAND | wx.ALL, 10)
        apply_modal_ids(
            dialog, affirmative_id=wx.ID_OK, affirmative_label="&Open", cancel_id=wx.ID_CANCEL
        )
        try:
            self._show_modal_dialog(dialog, heading)
        finally:
            dialog.Destroy()

    # --- Phase 4: tags ----------------------------------------------------

    def show_tags(self) -> None:
        """Open the spoken tag pane: filter tags, then list a tag's notes."""
        from quill.core.vault.tags import build_tag_index, notes_for_tag, tag_counts

        if self._ensure_vault() is None:
            self._set_status("Open a vault first (Tools > Vault > Open Vault)")
            return
        index = build_tag_index(self._vault)
        counts = tag_counts(index)
        if not counts:
            self._set_status("This vault has no tags yet")
            return

        def provider(query: str):
            needle = query.lstrip("#").casefold()
            return [
                (f"#{tag} — {count} note(s)", tag)
                for tag, count in counts
                if needle in tag.casefold()
            ]

        def open_tag(tag: str) -> None:
            notes = notes_for_tag(index, tag)
            self._announce(f"#{tag}: {len(notes)} note(s)")
            self._show_vault_list(f"Notes tagged #{tag}", [(n.title, (n.path, 0)) for n in notes])

        self._show_vault_filter(
            "Vault Tags",
            prompt="Filter tags:",
            provider=provider,
            on_activate=open_tag,
            count_verb="tags",
        )

    # --- Phase 5: embeds --------------------------------------------------

    def _embed_at_cursor(self):
        from quill.core.vault import link_at_offset, resolve_link
        from quill.core.vault.render import resolve_embed_content

        if self._ensure_vault() is None:
            self._set_status("Open a vault first (Tools > Vault > Open Vault)")
            return None
        link = link_at_offset(self.editor.GetValue(), self.editor.GetInsertionPoint())
        if link is None or not link.embed:
            self._set_status("No embed (![[...]]) at the cursor")
            return None
        source = relative_note_path(self._vault_root_path(), self._document_path()) or ""
        target = resolve_link(self._vault, self._vault_resolver, link, source)
        if target is None:
            self._set_status(f'No note named "{link.target}"')
            return None
        content = resolve_embed_content(self._vault, target.path, link.heading, link.block)
        title = (
            self._vault.notes[target.path].title
            if target.path in self._vault.notes
            else link.target
        )
        return link, title, content

    def speak_embed_at_cursor(self) -> None:
        """Read the content the caret's ``![[embed]]`` points to, without changing text."""
        found = self._embed_at_cursor()
        if found is None:
            return
        _link, title, content = found
        self._announce(f"Embedded from {title}: {content}" if content else f"{title} is empty")

    def resolve_embed_inline(self) -> None:
        """Replace the caret's ``![[embed]]`` with its content as one undoable edit."""
        found = self._embed_at_cursor()
        if found is None:
            return
        link, _title, content = found
        self.editor.Replace(link.start, link.end, content)
        self._announce("Resolved embed inline")

    # --- Phase 6: templates & daily notes ---------------------------------

    def insert_note_template(self) -> None:
        """Pick a template from the vault's Templates folder and insert it at the cursor."""
        root = self._vault_root_path()
        if root is None:
            self._set_status("Open a vault first (Tools > Vault > Open Vault)")
            return
        tdir = root / "Templates"
        templates = sorted(tdir.glob("*.md")) if tdir.is_dir() else []
        if not templates:
            self._set_status("No templates: add .md files to a 'Templates' folder in the vault")
            return
        self._show_vault_list(
            "Insert Template",
            [(path.stem, path) for path in templates],
            on_activate=self._apply_template,
        )

    def _apply_template(self, path) -> None:
        import datetime as _dt

        from quill.core.vault.templates import render_template, template_prompts

        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            self._set_status("Could not read the template")
            return
        answers: dict[str, str] = {}
        for question in template_prompts(text):
            answer = self._prompt_text(question)
            if answer is None:
                self._set_status("Template cancelled")
                return
            answers[question] = answer
        doc_path = self._document_path()
        title = doc_path.stem if doc_path is not None else ""
        rendered, cursor = render_template(
            text, now=_dt.datetime.now(), title=title, answers=answers
        )
        insert_at = self.editor.GetInsertionPoint()
        self.editor.WriteText(rendered)
        if cursor >= 0:
            self.editor.SetInsertionPoint(insert_at + cursor)
        self._announce("Template inserted")

    def _prompt_text(self, question: str) -> str | None:
        wx = self._wx
        dialog = wx.TextEntryDialog(self.frame, question, "Template")
        try:
            if self._show_modal_dialog(dialog, "Template") != wx.ID_OK:
                return None
            return dialog.GetValue()
        finally:
            dialog.Destroy()

    def _daily_pattern(self) -> str:
        from quill.core.vault.dailynotes import DEFAULT_PATTERN

        return str(getattr(self.settings, "vault_daily_pattern", "") or DEFAULT_PATTERN)

    def open_todays_note(self) -> None:
        """Open (creating if absent) today's daily note; set the daily cursor to today."""
        import datetime as _dt

        self._open_daily(_dt.date.today())

    def previous_daily_note(self) -> None:
        self._walk_daily(-1)

    def next_daily_note(self) -> None:
        self._walk_daily(1)

    def _walk_daily(self, delta: int) -> None:
        import datetime as _dt

        cursor = getattr(self, "_vault_daily_cursor", None) or _dt.date.today()
        self._open_daily(cursor + _dt.timedelta(days=delta))

    def _open_daily(self, day) -> None:
        from quill.core.vault.dailynotes import daily_note_relpath

        root = self._vault_root_path()
        if root is None:
            self._set_status("Open a vault first (Tools > Vault > Open Vault)")
            return
        self._vault_daily_cursor = day
        path = root / daily_note_relpath(self._daily_pattern(), day)
        existed = path.exists()
        if not existed:
            try:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(f"# {day.isoformat()}\n\n", encoding="utf-8")
            except OSError as error:
                self._set_status(f"Could not create the daily note: {error}")
                return
            self._vault = None
            self._ensure_vault()
        self.open_file(path)
        self._announce(f"{day.isoformat()}: {'opened' if existed else 'created'}")

    # --- Phase 7: export site, sync, gated publish ------------------------

    def export_vault_site(self) -> None:
        """Export the whole vault as a static, linked HTML site (background)."""
        from quill.core.vault.site_export import build_site, write_site
        from quill.io.export import render_preview_body

        if self._ensure_vault() is None:
            self._set_status("Open a vault first (Tools > Vault > Open Vault)")
            return
        wx = self._wx
        picker = wx.DirDialog(self.frame, "Choose an output folder for the website")
        try:
            if self._show_modal_dialog(picker, "Export Vault as Website") != wx.ID_OK:
                self._set_status("Export cancelled")
                return
            out_dir = picker.GetPath()
        finally:
            picker.Destroy()

        vault = self._vault
        resolver = self._vault_resolver

        def work(_progress) -> object:
            pages = build_site(
                vault, resolver, markdown_to_html=lambda t: render_preview_body(t, "markdown")
            )
            return write_site(pages, out_dir)

        self._run_background_task(
            "Exporting vault as a website",
            work,
            lambda written: self._announce(
                f"Exported {len(written)} pages to {out_dir}"  # type: ignore[arg-type]
            ),
        )

    def sync_vault(self) -> None:
        """Commit, pull, and push the vault over the user's own git remote (background)."""
        import os as _os

        from quill.core.vault.sync import run_vault_sync
        from quill.stability.safe_subprocess import run_subprocess_safely

        if _os.environ.get("QUILL_SAFE_MODE") == "1":
            self._set_status("Vault sync is disabled in Safe Mode")
            return
        root = self._vault_root_path()
        if root is None:
            self._set_status("Open a vault first (Tools > Vault > Open Vault)")
            return

        def work(_progress) -> object:
            return run_vault_sync(str(root), runner=run_subprocess_safely)

        self._run_background_task("Syncing vault", work, self._on_sync_done)

    def _on_sync_done(self, result) -> None:
        if getattr(result, "conflicts", ()):  # list them for keep-mine/theirs/merge
            self._show_vault_list(
                "Sync conflicts — resolve, then sync again",
                [(path, None) for path in result.conflicts],
                on_activate=lambda payload: None,
            )
        self._announce(result.message)

    def publish_current_note(self) -> None:
        """Publish the current note (GATED behind future.publishing; hidden while locked)."""
        from quill.core.vault.publish import prepare_note_publish
        from quill.io.export import render_preview_body

        if self._ensure_vault() is None:
            self._set_status("Open a vault first (Tools > Vault > Open Vault)")
            return
        rel = relative_note_path(self._vault_root_path(), self._document_path())
        if rel is None or rel not in self._vault.notes:
            self._set_status("Save this note inside the vault first")
            return
        payload = prepare_note_publish(
            self._vault,
            self._vault_resolver,
            rel,
            markdown_to_html=lambda t: render_preview_body(t, "markdown"),
            feature_enabled=bool(self.features.is_enabled("future.publishing")),
        )
        if payload is None:
            self._set_status("Publishing notes is not enabled yet")
            return
        self._announce(f"Prepared '{payload.title}' to publish.")

    def _register_vault_commands(self) -> None:
        self.commands.try_register(
            "vault.open", "Open Vault", self.open_vault, self._binding_for("vault.open")
        )
        self.commands.try_register(
            "vault.follow_link",
            "Follow Wikilink",
            self.follow_wikilink,
            self._binding_for("vault.follow_link"),
        )
        self.commands.try_register(
            "vault.backlinks",
            "Show Backlinks",
            self.show_backlinks,
            self._binding_for("vault.backlinks"),
        )
        self.commands.try_register(
            "vault.neighborhood",
            "Note Neighborhood",
            self.show_neighborhood,
            self._binding_for("vault.neighborhood"),
        )
        self.commands.try_register(
            "vault.unlinked_mentions",
            "Unlinked Mentions",
            self.show_unlinked_mentions,
            self._binding_for("vault.unlinked_mentions"),
        )
        self.commands.try_register(
            "vault.insert_link",
            "Insert Link to Note",
            self.insert_wikilink,
            self._binding_for("vault.insert_link"),
        )
        self.commands.try_register(
            "vault.quick_switch",
            "Go to Note",
            self.quick_switch_note,
            self._binding_for("vault.quick_switch"),
        )
        self.commands.try_register(
            "vault.search",
            "Search Vault",
            self.search_vault_notes,
            self._binding_for("vault.search"),
        )
        self.commands.try_register(
            "vault.tags", "Show Tags", self.show_tags, self._binding_for("vault.tags")
        )
        self.commands.try_register(
            "vault.speak_embed",
            "Speak Embed at Cursor",
            self.speak_embed_at_cursor,
            self._binding_for("vault.speak_embed"),
        )
        self.commands.try_register(
            "vault.resolve_embed",
            "Resolve Embed Inline",
            self.resolve_embed_inline,
            self._binding_for("vault.resolve_embed"),
        )
        self.commands.try_register(
            "vault.insert_template",
            "Insert Template",
            self.insert_note_template,
            self._binding_for("vault.insert_template"),
        )
        self.commands.try_register(
            "vault.today",
            "Open Today's Note",
            self.open_todays_note,
            self._binding_for("vault.today"),
        )
        self.commands.try_register(
            "vault.prev_daily",
            "Previous Daily Note",
            self.previous_daily_note,
            self._binding_for("vault.prev_daily"),
        )
        self.commands.try_register(
            "vault.next_daily",
            "Next Daily Note",
            self.next_daily_note,
            self._binding_for("vault.next_daily"),
        )
        self.commands.try_register(
            "vault.export_site",
            "Export Vault as Website",
            self.export_vault_site,
            self._binding_for("vault.export_site"),
        )
        self.commands.try_register(
            "vault.sync", "Sync Vault", self.sync_vault, self._binding_for("vault.sync")
        )
        # Publishing (the send path) is gated behind future.publishing (locked_off), so
        # this command stays hidden from the menu and palette until it is unlocked.
        self.commands.try_register(
            "vault.publish_note",
            "Publish Note",
            self.publish_current_note,
            self._binding_for("vault.publish_note"),
            feature_id="future.publishing",
        )
