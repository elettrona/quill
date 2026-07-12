# PRD: Deep Git + GitHub Integration — Local Git Accessibility, Copilot, Organizations, and Codespaces

> Status: **Planning PRD**, not yet built. Supersedes the earlier "dream big"
> companion doc (same filename); this is the formalized, scoped version with
> explicit in/out decisions and a ranked build order. The near-term plan this
> document followed on from — repository create/rename/visibility/branch-
> protection/multi-file-commit, plus items-viewer write actions — is already
> **shipped** (PRD §25.12a / §25.13, 0.9.0 Beta 3). Nothing here duplicates
> that; everything here is additive.

## 0. Vision

QUILL already does something no other GitHub client does: it owns the
editor, the compare engine, and the announcement grammar a screen-reader
user actually needs, all in one process. Every mainstream git tool — the
`git` CLI itself, GitHub Desktop, VS Code's source control view, GitKraken —
was built visual-first, and the parts of git that are hardest to use with a
screen reader (a merge conflict's `<<<<<<<` markers, an interactive rebase's
reorderable todo list, `git blame`'s dense per-line gutter) have stayed
hard for a decade because nobody who owns an accessible editor also owns a
git client. QUILL owns both. This PRD is about spending that unique position
on the features that are actually hard to get right anywhere else — not on
cloning GitHub Desktop's feature list for parity's sake.

The two boldest bets in this document: **QUILL becomes the first genuinely
accessible interactive-rebase and merge-conflict experience that exists**
(§4), and **QUILL ships git and the GitHub CLI itself**, so none of this ever
depends on a screen-reader user successfully installing and configuring a
second, third, and fourth piece of software before any of it works (§2).

## 1. Scope decisions

Explicit, so nobody re-litigates these mid-build:

| In scope | Out of scope (this PRD) |
|---|---|
| **Organizations** — creating repos under an org (already shipped), listing/browsing an org's repos, transferring a repo to an org, org-level visibility | **Teams** — team membership, team permissions, team-scoped repo access. Real orgs are common among QUILL's maintainer-adjacent users; team administration is a much deeper, lower-confidence surface with unclear demand |
| **GitHub Copilot**, deeply — unifying auth, CLI-style suggestions, code review surfacing, commit-message drafting | `gh extension` ecosystem access (§3 of the earlier dream doc) — speculative, no clear user need yet |
| **GitHub Codespaces** — list/start/stop/delete, connect and edit files | `gh api` raw passthrough escape hatch (§3 of the earlier dream doc) — revisit only if a specific tier-2 feature turns out to have no PyGithub path |
| Bundling `git` and `gh` into QUILL's own distribution (§2) | Teams, extensions, and the `gh api` passthrough, per above |

Local-git accessibility (merge conflicts, interactive rebase, blame, bisect,
stash, branch switching) and the rest of the GitHub API surface (Actions,
Projects, Discussions, notifications, security alerts, releases) are
unchanged from the earlier dream doc and carried forward below with the
above adjustments folded in.

## 2. Packaging: QUILL ships `git` and `gh`, so nobody has to install them

This is the section that makes everything else in this PRD not a "power
user" feature. Today, any local-git or `gh`-CLI work in QUILL implicitly
asks the user to have already installed and configured `git` (and, for the
Copilot/Codespaces work in §5-6, `gh`) themselves — exactly the "second CLI
tool to install" friction the original GitHub-integration decision
(PyGithub over `gh` shell-outs) was written to avoid. Bundling both closes
that gap entirely.

### 2.1 Reuse the existing acquisition model — don't build a new one

QUILL already has exactly the right mechanism for this: `quill/core/
release_assets.py`, which downloads Pandoc, Vosk, Kokoro, MathCAT, the
braille pack, and libmpv this same way today. Every property that matters
for bundling a binary is already built and tested:

- **A pinned, non-moving release tag** (`assets-v1` on `Community-Access/
  quill`), never the product's own version tags — asset churn never touches
  the autoupdate feed.
- **Pinned SHA-256 per asset**, checked before anything is installed;
  `is_pinned()` rejects moving refs (`/latest/`, `/head/`, `/main/`) outright.
- **HTTPS-only, retrying, resumable** downloads (`_download_resumable`).
- **Atomic install**: download and unzip into a temp dir; only copy into the
  real target directory after the checksum passes.
- **No admin rights, ever** — everything lands under the per-user app-data
  directory (`app_data_dir() / "vendor" / ...`), the same pattern the
  braille pack already uses.
- **Safe Mode blocks it outright** (`QUILL_SAFE_MODE=1` refuses both
  `fetch_component` and `fetch_file`).
- **Explicit user action only** — no background/silent fetch, ever.

`git` and `gh` become two new entries in the `ASSETS` manifest and two new
rows in the existing **Help > Download Optional Components** dialog
(`optional_components_dialog.py`) — no new UI surface needed, just two new
components in a dialog that already exists and already does exactly this
job for six other binaries.

### 2.2 What actually gets bundled, per platform

Both `git` and `gh` publish exactly the kind of artifact this model wants:
a standalone, no-installer, unzip-and-run binary — not something that
requires an admin-rights installer wizard.

- **Windows**: **MinGit** — the official portable, minimal Git for Windows
  distribution (published as a release asset on `git-for-windows/git`,
  the same binaries GitHub Desktop itself embeds), plus the official `gh`
  Windows zip release from `cli/cli`. Both are plain zips: unpack, done.
- **macOS**: `git` is very often already present via Xcode Command Line
  Tools (the OS itself offers to install it on first invocation — outside
  QUILL's control, and the sane default path to prefer when present). `gh`
  publishes an official macOS `.tar.gz` with a plain binary inside; QUILL
  bundles that the same way it already bundles macOS speech binaries.
- **Licensing**: `git` is GPLv2, `gh` is MIT — both freely redistributable.
  Bundling flows through the same SBOM (CycloneDX) generation and Sigstore
  `cosign` signing QUILL's build already does for every release artifact
  (see the main PRD's release-engineering section), so this doesn't need a
  new compliance process, just two new entries in an existing one.

### 2.3 Detection: prefer the system's own copy

Before downloading anything, QUILL checks `PATH` for a `git`/`gh` that meets
a minimum version. If found, QUILL uses it directly — no duplicate install,
no version drift to reason about, and this is the common case for anyone
who's ever done any development work on their machine. The bundled copy
exists specifically for the person who has never installed either, which
per the vision in §0 is exactly the person this whole feature area is for.
Detection and path resolution live in a new, small, wx-free module
(`quill/core/git_binaries.py`): `resolve_git() -> Path | None`,
`resolve_gh() -> Path | None`, each checking system `PATH` first, then the
QUILL-managed vendor directory.

### 2.4 A new, narrow subprocess allowlist — not a reuse of the AI engine one

`quill/core/ai/external_engine.py`'s `_ENGINE_EXECUTABLE_BASENAMES`
allowlist (`node`, `python`, `quill-engine`) exists specifically to guard
the "spoken-to-over-stdin-JSONL accessibility engine" boundary (AI-24) — a
different threat model than "run `git`/`gh` as a normal subprocess." This
PRD's subprocess calls need their own equivalent, narrow allowlist
(`_GIT_EXECUTABLE_BASENAMES = {"git", "git.exe", "gh", "gh.exe"}`) enforced
at the one place all local-git and `gh` subprocess calls funnel through
(`quill/core/git_binaries.py`, alongside the existing `run_subprocess_safely`
wrapper `git_sync.py` already uses) — so a tampered settings file can never
turn a git-integration feature into an arbitrary-executable launcher, the
same defense-in-depth reasoning as the AI engine allowlist, applied to a
different boundary.

### 2.5 Version pinning and updates

Bundled `git`/`gh` versions are pinned in the `ASSETS` manifest exactly like
every other component; bumping either is a deliberate, reviewed manifest
change (new pinned SHA-256, new download URL), never an automatic "always
get the newest" fetch — consistent with how Pandoc/Vosk/Kokoro are already
versioned.

## 3. Architecture: two new layers, additive to what exists

QUILL's GitHub integration today is REST-API-only (PyGithub, `quill/core/
github/*`) — `local_repo.py` is explicit that it does zero subprocess work.
This PRD adds two genuinely new layers alongside it, not instead of it:

1. **`quill/core/local_git.py`** (wx-free, strict-typed) — the tier-1 local-
   git accessibility engine (§4). Subprocess-based, following `git_sync.py`'s
   existing `run_subprocess_safely`-wrapped pattern exactly. No REST calls;
   this is pure local `git` command orchestration with structured,
   screen-reader-shaped output instead of raw stdout parsing left to the UI.
2. **`quill/core/github/gh_bridge.py`** (wx-free) — the narrow `gh`-CLI
   surface this PRD actually wants: Copilot CLI-style suggestions (§6) and
   Codespaces lifecycle (§7). Detected at runtime via `git_binaries.resolve_gh()`;
   every command it wraps degrades honestly ("Codespaces needs the GitHub
   CLI; install it from Help > Download Optional Components") rather than
   silently disappearing when `gh` isn't available.

Existing `github_provider.py` / `items_provider.py` / `repo_admin.py` are
untouched by this PRD — they keep doing exactly what they do today.

## 4. Local git, made genuinely accessible (unchanged from the dream doc — the crown jewel)

The highest-value, most differentiated work in this whole PRD, and the
reason §0's boldest claim is credible:

- **Uncommitted changes viewer.** `git status` + `git diff` rendered through
  the same accessible difference walk the PR diff viewer already uses
  ("Difference 2 of 5, text changed at line 41") instead of a raw unified
  diff. Stage/unstage individual hunks or whole files from an accessible
  list.
- **Merge-conflict resolution walker.** The single biggest gap in
  screen-reader git tooling anywhere today. `<<<<<<<`/`=======`/`>>>>>>>`
  markers read as line noise; a conflict walker instead presents "Conflict 1
  of 3 in `file.py`: your version says X, their version says Y," with
  keep-yours/keep-theirs/keep-both/edit-manually as an action menu, stepping
  through the file and writing the resolved content back. Directly wired
  into an existing pain point: a conflict from the already-shipped **Sync
  Folder with GitHub** command today just lists conflicted filenames and
  tells you to go fix them elsewhere — this walker becomes that "elsewhere,"
  inside QUILL.
- **Interactive rebase, spoken.** `git rebase -i`'s pick/squash/reword/drop
  todo list, as a real QUILL list dialog — one commit per row, an action
  menu per row, standard list-reorder keystrokes, narrated throughout
  ("commit 3 of 7 marked squash"). Nobody ships this well today.
- **Blame, as a navigable read.** Put the cursor on a line, ask "who wrote
  this and when," get a spoken answer with a jump-to-that-commit's-diff
  action.
- **Bisect wizard.** `git bisect start/good/bad` as a guided "Is this
  version good or bad?" dialog with a remaining-steps counter.
- **Branch switching and a local branch list.** `git checkout`/`git switch`
  from a picker, with an uncommitted-changes guard before switching.
- **Stash, as a named list**, not `stash@{2}` indices.
- **Cherry-pick**, reusing the same conflict-resolution walker as rebase and
  merge — one UI serving three git operations.
- **Submodule awareness** — status/init/update, at minimum enough that a
  submodule-based project doesn't look silently broken inside QUILL.

None of this needs `git` bundled in principle (a user's own `git` works
fine) — but §2's bundling is what makes it available to *everyone*, not just
people who already have `git` on `PATH`.

## 5. The rest of the GitHub API surface (Organizations in, Teams out)

- **GitHub Actions, properly.** Stream a running job's log (polling
  `GET .../jobs/{id}/logs`, narrated as it grows — the same live-refresh
  pattern the Status Page already uses); trigger `workflow_dispatch` with
  its declared inputs from a generated form instead of hand-editing YAML.
- **Projects (v2), as an accessible list-that-isn't-a-board.** GitHub
  Projects is a kanban board — maximally screen-reader-hostile natively.
  Expose the same data as a filterable, sortable list (status, assignee,
  custom fields), with "change status" as a plain action instead of a drag.
- **Discussions.** Read/reply, on the same items-viewer pattern already
  built for issues/PRs.
- **Notifications, as a real inbox.** Polled (`GET /notifications`, no
  webhook receiver — matches "QUILL doesn't run background services"),
  surfaced as a list with mark-read/unsubscribe.
- **Security alerts (Dependabot / code scanning).** Read-only accessible
  list per repo.
- **Releases, authored.** Draft, generate notes from merged PRs
  (`POST .../releases/generate-notes`), attach assets, publish — a natural
  bridge to QUILL's own CHANGELOG/release-notes parsing elsewhere in the app.
- **Organizations** (new inclusion, per scope decision in §1): browse an
  org's repositories, list which orgs the signed-in account belongs to
  (`GET /user/orgs`), transfer a repo into an org
  (`POST /repos/{owner}/{repo}/transfer`), and the already-shipped
  create-repo-under-an-org path (`repo_admin.create_repository(org=...)`)
  gets a proper "which org?" picker instead of a blank free-text field.
  **Explicitly not** team creation, team membership, or team-scoped
  permissions — those stay out per §1.
- **Packages** — read-only list (what's published, what's stale); no
  publishing flow until there's a concrete need.

## 6. GitHub Copilot, deeply integrated (bold, per the excitement to build this well)

QUILL already has real Copilot infrastructure — this PRD's job is to stop
treating it as narrowly scoped and make it the front door for GitHub auth
generally.

**Today**, `copilot_auth.py`'s OAuth device flow requests only `read:user`
scope, just enough to identify the signed-in user for Copilot entitlement
in the AI Hub's engine picker. Its token is saved through the exact same
`token_store.py` slot (`quill-github-token`) as the general GitHub
integration's PAT, and — this is the key architectural fact this PRD leans
on — `apply_token_to_environment()` already exports it as `GITHUB_TOKEN`/
`GH_TOKEN`, which is precisely what `gh` CLI itself reads for auth. The
plumbing to unify these already half-exists.

**The bold move**: request a broader, still-honest scope set up front
(`read:user`, `repo`, `workflow` — the practical minimum `gh` and QUILL's
own GitHub integration both need), and make **one Copilot sign-in the single
GitHub auth QUILL ever asks for**. Sign in once, and:

- The AI Hub's Copilot engine works (today's behavior, unchanged).
- The GitHub Items viewer, repository admin, and this PRD's Organizations
  work all use the same token — no second "paste a PAT" flow for a user who
  already signed in via Copilot's much friendlier device-code flow.
- `gh`-backed features (§7's Codespaces) authenticate for free, since
  `GITHUB_TOKEN` is already in the environment.

This needs a real decision about UX sequencing (does the *first* GitHub sign-
in anywhere in QUILL become the Copilot device flow, with the PAT-paste path
demoted to an "advanced" fallback for users without Copilot access?) —
flagged as an open design question in §10, not decided here.

**Three concrete Copilot features**, once the auth story above is real:

- **`gh copilot suggest` / `gh copilot explain`, as a command-palette
  action.** "How do I do X in git" as a natural-language query, scoped
  specifically to git/gh command help — distinct from QUILL's own general AI
  assistant, and only offered when `gh` is present and Copilot-entitled.
- **Copilot code review, surfaced where comments already live.** GitHub's
  Copilot can leave automated review comments on a PR; the Items viewer
  already has a full comment thread UI (reply/edit/delete, shipped this
  release) — Copilot's review comments just need to render in that same
  thread, no new UI.
- **Commit-message drafting from the staged diff.** §4's uncommitted-changes
  viewer already has the staged diff in hand; feed it to Copilot (or QUILL's
  own already-existing AI assistant — either is a legitimate implementation,
  a build-time choice not a design one) to draft a commit message, read it
  aloud, let the user accept or edit before committing. This is the kind of
  chained, multi-subsystem flow that only a tool owning both the editor and
  the git layer can offer in one motion.

## 7. GitHub Codespaces (bold, and genuinely exciting — with an honest architecture caveat)

Codespaces has no clean stable REST equivalent for the interesting parts
(create/start/connect); this is `gh`'s territory (`gh codespace ...`),
which is exactly why §1 kept the `gh` bridge narrowly scoped to Copilot and
Codespaces rather than cutting `gh` out entirely.

**v1, high-confidence**: list, create, start, stop, and delete codespaces
for a repo via `gh_bridge.py` wrapping `gh codespace list/create/stop/
delete` — a standard provider-class-plus-dialog feature, same shape as
everything already shipped in §25.13's repository admin work. Cost/quota
awareness matters here in a way nothing else in this PRD does: starting a
codespace has a real dollar cost, so the confirmation before "Create
Codespace" needs to say so plainly, not just "this changes something on
GitHub."

**The genuinely exciting part**: "Open in QUILL" — connect to a running
codespace and edit its files without a browser, without VS Code, without
leaving the editor. Here's the honest architecture reality, so this doesn't
get built on a false premise: QUILL's existing SSH editing
(`SshEditingMixin` / `quill/core/ssh/client.py`) is SFTP-only — file open,
file save, no shell/exec channel at all. `gh codespace ssh` can hand QUILL
the connection details (host/port/proxy command) for a running codespace's
SSH endpoint, and the *file-editing* half of "Open in QUILL" is a
legitimate, near-term reuse of the existing SSH mixin's SFTP path once it
has those connection details. But *running* `git`/`gh`/build commands
**inside** the codespace is not possible through SFTP alone — that needs a
real exec/PTY channel, which `ssh/client.py` does not have today and would
be a separate, larger subproject (a screen-reader-accessible remote
terminal is its own PRD, not a paragraph in this one).

**Recommendation**: ship file-edit-only Codespaces integration first (v1,
high confidence, reuses existing SSH plumbing) and treat "run commands
inside a codespace from QUILL" as an explicitly separate, later, lower-
confidence subproject — flagged in §10, not promised here.

## 8. Non-negotiables (unchanged from every prior GitHub-integration decision)

Every feature in this PRD: off by default; blocked outright in Safe Mode;
gated behind the existing one-time GitHub consent dialog; every write named
explicitly in its own confirmation before it runs; the highest-consequence
actions (already established: rename, delete-branch, visibility-change,
merge — this PRD adds interactive-rebase-with-force-push-adjacent semantics
and Codespace creation/deletion to that tier) go through typed confirmation,
not a plain Yes/No; no admin rights required for anything, including the new
`git`/`gh` bundling; nothing here requires installing or separately
configuring a second CLI tool for a user who never wants to touch one.

## 9. New modules (concrete implementation surface)

| Module | Purpose |
|---|---|
| `quill/core/git_binaries.py` | `resolve_git()`/`resolve_gh()` (system-first, bundled-fallback), the narrow subprocess allowlist |
| `quill/core/local_git.py` | Tier-1 local git engine: status/diff/stage, conflict data model, rebase todo-list model, blame, bisect, stash, branch list/switch |
| `quill/ui/local_git_dialogs.py` | Uncommitted-changes viewer, merge-conflict walker, interactive-rebase list dialog, blame view, bisect wizard, stash/branch pickers |
| `quill/ui/main_frame_local_git.py` | Command handlers + command-palette registration for all of §4 |
| `quill/core/github/gh_bridge.py` | `gh`-CLI-backed: Copilot suggest/explain, Codespaces lifecycle |
| `quill/ui/codespaces_dialogs.py` | Codespace list/create/connect dialogs, cost-aware confirmations |
| Extensions to `quill/core/github/repo_admin.py` | Organization browsing, repo transfer-to-org |
| Extensions to `quill/core/github/items_provider.py` | Discussions, notifications, security alerts, Actions log streaming, `workflow_dispatch` |
| New `quill/ui/projects_dialog.py` | Projects (v2) as an accessible list |
| Two new `ASSETS` entries in `quill/core/release_assets.py` | MinGit (Windows), `gh` CLI (Windows + macOS) |

## 10. Ranked task list (highest confidence first)

**Tier 0 — foundation, build first (everything else depends on this):**
1. `git_binaries.py` — detection + the new subprocess allowlist. No UI, pure
   plumbing, fully unit-testable without wx or network.
2. Bundle `git`/`gh` via `release_assets.py` (§2) + two new rows in the
   existing Download Optional Components dialog. Reuses a proven mechanism;
   the main risk is just picking and pinning the right platform artifacts.

**Tier 1 — highest confidence, highest differentiation (§4):**
3. Uncommitted changes viewer (status + accessible diff + stage/unstage).
4. Merge-conflict resolution walker — the single most valuable feature in
   this entire PRD, and it slots directly into the existing Sync Folder with
   GitHub conflict-listing UX.
5. Branch list + switch, stash list.
6. Blame (navigable read).
7. Interactive rebase (spoken todo list) — higher build cost than the above
   (a real reorderable list UI + rebase state-machine handling), same
   confidence.
8. Bisect wizard.
9. Cherry-pick, reusing #4's conflict walker.

**Tier 2 — high confidence, standard provider+dialog shape (§5):**
10. Organizations: browse, transfer-to-org, org picker for repo creation.
11. Actions log streaming + `workflow_dispatch` form.
12. Notifications inbox.
13. Releases, authored (bridges to QUILL's own release-notes parsing).
14. Discussions.
15. Security alerts (read-only).
16. Projects (v2) as a list.
17. Packages (read-only).

**Tier 3 — bold, real design work needed before coding starts (§6-7):**
18. Copilot auth scope broadening + the "one GitHub sign-in" unification
    (needs the UX-sequencing decision flagged in §6 resolved first).
19. `gh copilot suggest`/`explain` command-palette action.
20. Copilot code review comments surfaced in the existing thread UI.
21. Commit-message drafting from staged diff (depends on #3).
22. Codespaces list/create/stop/delete (`gh_bridge.py`).
23. Codespaces "Open in QUILL" file editing (depends on #22, reuses SSH
    mixin — confirm `gh codespace ssh` connection-detail handoff works
    cleanly before committing to this one).

**Explicitly not ranked — future subproject, not part of this PRD's build:**
- A real exec/PTY channel in `ssh/client.py`, which is what "run commands
  inside a codespace" would actually require. Worth its own PRD once #23
  ships and there's a concrete reason to go further.

## 11. Open questions

- Does the Copilot device-flow scope broadening (§6) require re-consent
  from existing Copilot users, or can it apply only to new sign-ins? Needs
  a decision before #18.
- Is `gh codespace ssh`'s connection-detail format stable/scriptable enough
  to hand cleanly to the existing `ssh/client.py` connect path, or does it
  need its own connection-parameter translation layer? Needs a short spike
  before committing to #23's estimate.
- Minimum supported `git`/`gh` versions for the "prefer system copy" check
  in §2.3 — needs a concrete floor once #1 is scoped.
