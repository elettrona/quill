# TINDRA — Naming and Go-to-Market Plan

> Working brand/GTM plan for renaming **QUILL** to **TINDRA**.
> Status: proposal. The trademark clearance in section 11 is a hard gate and is
> NOT yet done. Nothing here is committed branding until that clears.

---

## 1. The name

**TINDRA** — pronounced *TIN-druh*.

- **Acronym (it is the product):** **T**ext · **I**nput · **N**arration ·
  **D**ictation · **R**eading · **A**ccess. Type it, dictate it, hear it narrated,
  read it back, and reach it however you work — that is the whole product in six
  letters.
- **Meaning:** *tindra* is Swedish for "to twinkle / shine." Light and clarity —
  a fitting note for a low-vision and blind audience, and a quiet echo of QUILL's
  feather-and-light heritage without sitting in the crowded English "quill / pen /
  voice / aura" cluster everyone else reaches for.
- **Why it survived vetting:** of a dozen candidates checked, TINDRA was the only
  one with **no collision in the accessibility / writing / AI software category**
  (its only same-name uses are in unrelated classes — a furniture brand, a generic
  IT shop). Competitors like *Aura Reader*, *Wren AI*, *Penna*, *Plume*, and
  *Saylo* are all already writing/AI apps. See `docs/` naming research notes.
- **Lineage from QUILL:** position the change as an evolution, not a reboot —
  "QUILL is now TINDRA." Same team (Community Access), same promises, a name we
  can actually own and defend.

> Gate: TINDRA is not pristine. The `.store` domain is held by the furniture
> brand. Plan for `tindra.app` / `gettindra.com` and a Class 9 trademark search
> (section 11) before any public use.

---

## 2. What TINDRA is (one-liner and elevator pitch)

**One-liner:** *TINDRA is the private, on-device writing studio you can see, hear,
and feel — built screen-reader-first for everyone.*

**Elevator pitch:** TINDRA is a desktop writing and reading studio designed from
the first keystroke for blind, low-vision, and print-disabled people — and a joy
for everyone else. Write and edit in plain text, Markdown, HTML, or code;
transcribe and caption audio, dictate, and run commands by voice — all **offline,
on your own machine**; proof and read braille; export accessible DAISY talking
books; and ask an on-device AI assistant that never needs a cloud account.
Everything is optional, nothing is uploaded, and it launches, edits, and saves
with all of it turned off.

---

## 3. Positioning

**Category:** Accessible writing and reading studio (desktop). Not "a screen
reader," not "another Markdown editor" — the writing environment that assumes a
screen reader, braille display, and voice are first-class, not afterthoughts.

**The core promise:** *Every word, every way.* See it, hear it, feel it, speak it.

**Four brand pillars** (these are the real differentiators, and the public
"Private · Local · Universal · Multimodal" story):

1. **Private** — your words and audio stay on your machine; no account required;
   AI and network features are opt-in and audited.
2. **Local** — on-device transcription, dictation, and AI (whisper.cpp / Faster
   Whisper / llama.cpp / Apple Foundation Models). Works offline.
3. **Universal** — screen-reader-first, braille-native, low-vision-aware,
   keyboard-complete. Accessibility is the architecture, not a setting.
4. **Multimodal** — one document, read and authored as text, speech, and braille,
   with a verbosity system that lets you tune exactly how much TINDRA says.

---

## 4. Differentiation vs the competition

| They are | TINDRA is |
| --- | --- |
| Screen readers (JAWS, NVDA, Narrator) that *read other apps* | A writing app that is *natively accessible*, so you are not fighting your screen reader |
| TTS readers (Voice Dream, Speechify) that *read to you* | Read **and** write **and** dictate **and** braille, in one place |
| Markdown/writing apps (iA Writer, Obsidian, Ulysses) with accessibility bolted on | Accessibility-first, with code-aware editing and live document-language detection |
| Cloud AI writing tools | On-device AI and speech — private, offline, no subscription to a model API |
| Braille tools that are separate utilities | Braille mode, back-translation, and proofing inside the same studio |

**The wedge:** "the only writing studio where reading aloud, dictation, braille,
and AI all run **on your computer**, and where a blind or low-vision user is the
**default** user, not an accommodation."

---

## 5. Messaging and taglines

**Primary tagline candidates** (pick one; A/B the rest):

- *Every word, every way.*
- *Writing that shines — for everyone.*
- *See it. Hear it. Feel it. Write it.*
- *The accessible writing studio. Private, local, yours.*

**Acronym tagline (great for explainer/SEO):**
*Text, Input, Narration, Dictation, Reading, Access — TINDRA.*

**Proof-point one-liners (use in feature blurbs):**

- "Transcribe and caption audio entirely on your computer — nothing uploaded."
- "Dictate, or drive TINDRA hands-free by voice — offline."
- "Open a `.brf`, return to your exact place, and proof braille without leaving the editor."
- "Ask the built-in AI — no account, no cloud, no key required."
- "Decide exactly how much TINDRA says, from full context to near silence."

---

## 6. Audiences and how we sell to each

1. **Blind and low-vision individuals (core).** Channel: AppleVis, Reddit
   r/Blind, NVDA/JAWS user lists, AT YouTubers/podcasters, mailing lists. Message:
   "finally, a writing app built for *you*, that works with your screen reader
   instead of against it — and keeps everything on your machine."
2. **Braille readers and producers.** Channel: braille transcriber communities,
   NLS/AFB networks. Message: place-restore, proofing, validation, back-translate.
3. **AT trainers, TVIs, and rehab professionals.** Channel: ATIA, CSUN
   conference, vendor directories. Message: one tool to teach reading, writing,
   dictation, and braille; offline and FERPA/privacy-friendly for students.
4. **Schools, universities (DSS / disability services), and libraries.** Channel:
   procurement, accessibility offices. Message: DAISY export, no student data
   leaves the device, deployable offline, Windows + macOS.
5. **Agencies and ADA / Section 508 environments.** Message: private by default,
   network-egress audited, on-device AI — defensible for sensitive content.
6. **Developers and technical writers.** Message: code-aware editing, document
   language profiles + detection, Markdown/HTML, extensible via **Sparks**.
7. **Writers and researchers generally.** Message: a fast, distraction-free,
   private studio that also reads your draft aloud and transcribes interviews.

---

## 7. The sell (value props, proof, objections)

**Value stack:**

- *Independence* — do the whole writing-and-reading loop yourself, your way.
- *Privacy* — nothing uploaded; AI and speech are local; opt-in and audited.
- *One tool* — replaces a pile of separate readers, transcribers, and utilities.
- *No subscription tax* — on-device models, not metered cloud APIs.

**Proof points:** open-source MIT speech models with verified, pinned downloads; a
network-egress audit; DPAPI-encrypted secrets; Safe Mode; braille that never
mutates your file; DAISY 2.02 export to real talking-book players.

**Objections and answers:**

- *"Isn't this just a screen reader?"* No — it is the app you write in; your
  screen reader still runs, and TINDRA is built so it never fights it.
- *"Do I need the internet / an account?"* No. It runs fully offline; the only
  network actions are explicit, consented downloads (models, optional ffmpeg).
- *"Is the AI sending my work to the cloud?"* No — Ask TINDRA runs on-device by
  default; cloud is strictly opt-in.
- *"Will it work with my setup?"* Windows primary, macOS supported; works with
  JAWS, NVDA, Narrator, and VoiceOver.

---

## 8. Brand system and sub-brands (the rename map)

| Today (QUILL) | Proposed (TINDRA) | Notes |
| --- | --- | --- |
| QUILL / QUILL for All | **TINDRA** | Product name; "TINDRA, by Community Access" |
| Quillins (extensions) | **Sparks** | On-theme with "twinkle/shine"; a Spark adds light |
| Ask Quill (AI) | **Ask TINDRA** | Keep the verb-first, friendly framing |
| Whisperer (speech engine) | **Whisperer** (keep) | Already a deliberate sub-brand; reads well under TINDRA |
| Community Access (publisher) | **Community Access** (keep) | The org/legal entity is unchanged |

**Visual/voice identity:** light/spark motif (a single bright point, not a literal
star cluster), high-contrast and reduced-motion by default, a warm and plain
verbal tone that matches the accessibility-first ethos.

---

## 9. Go-to-market plan

**Channels (ranked):**

1. Community-first: AppleVis, r/Blind, mastodon/X AT circles, AT podcasts and
   YouTubers (early reviews from trusted blind reviewers are worth more than ads).
2. Conferences: CSUN Assistive Technology Conference, ATIA — demos and a booth.
3. Institutional: DSS offices, libraries, rehab agencies — pilots and procurement.
4. Content/SEO: the acronym page, "private offline transcription," "accessible
   Markdown editor," "BRF proofreading," "DAISY export" — long-tail terms QUILL
   already ranks-adjacent for.
5. Open-source/dev: the **Sparks** SDK and Node/Python runtimes attract tinkerers.

**Launch arc:**

- *Pre-launch:* secure name (section 11), domain, socials; brief 8–12 trusted
  blind reviewers under the new name; prepare migration messaging for existing
  QUILL users.
- *Launch:* "QUILL is now TINDRA" — a single clear post + a 90-second narrated
  demo + the comprehensive release notes already written for this cycle.
- *Post-launch:* monthly "what's new" narrated, push Sparks, court one institution
  pilot for a case study.

---

## 10. Rename / migration plan (engineering blast radius)

A rename ripples widely. Sequence it so nothing breaks for existing users.

**Inventory of what carries the name:**

- Product strings: title bar, About, menus, dialogs, status bar, wizard.
- Identifiers: `quill` Python package/module, `python -m quill`, settings dir
  (`%APPDATA%\Quill`), installer `AppId`/`AppName`/`OutputBaseFilename`, the
  `quill.exe` launcher, file associations, "Send to Quill" shell verbs,
  `build/version.toml` product_name.
- Extensions: `Quillins`, `quillins_bundled/`, the manifest schema, `@quill/api`.
- Brand assets: README, user guide, PRD, release notes, website, GitHub org/repo
  (`Community-Access/quill`), update feed/appcast.
- Credentials/keys: `QUILL:huggingface:token`, DPAPI key labels.

**Migration principles:**

1. **Keep the data dir and on-disk identity stable across the rename**, or migrate
   it explicitly with a one-time, announced move (mirror the existing data-location
   move logic) — never silently orphan a user's settings, dictionaries, autosaves.
2. **Honor old shortcuts/associations** during a transition window (the installer
   already removes stale shortcuts on upgrade — reuse that path).
3. **Two-phase strings:** display name first (TINDRA in the UI), internal
   identifiers (package name, AppId) second, behind a release boundary, since
   AppId/package changes affect upgrade-in-place.
4. **`Quillins` → `Sparks`** is the largest code/doc rename; keep a compatibility
   alias for existing manifests for one release.

**Suggested order:** (a) clear the name legally → (b) display strings + brand docs
→ (c) website/org/domain + update feed → (d) extension rebrand (Sparks) with alias
→ (e) deep identifier rename (package, AppId, data dir migration) in a major
version with a guided upgrade.

---

## 11. Trademark and domain clearance — the gate (DO THIS FIRST)

### Do we even need this for an open-source project? (Yes — but cheaply.)

A free/MIT project does **not** get a pass on trademark. Why:

- Trademark turns on **"use in commerce"** (broadly read — distributing free
  software with a website, downloads, and app-store listings counts) and
  **likelihood of confusion**. You do not have to charge money to be using a name
  in a way trademark law cares about.
- The risk for a free project is not owing damages — it is being **forced to
  rename** by a prior holder's cease-and-desist. An injunction (a "stop using it"
  order) does not require that you profited.
- **Open-source licenses cover copyright, not the name.** MIT/GPL explicitly tend
  to *exclude* trademarks. (Debian shipped Firefox as **"Iceweasel"** for years
  purely over Mozilla's trademark, even though the code was free.)
- App stores and domain registrars have their own takedown/dispute processes that
  do not care whether you profit.

**What being free / open-source genuinely changes:** you can skip *registering your
own* mark (registration is optional), and you can clear the name for **$0** with a
DIY knockout. **What it does not change:** you should still run that free knockout
before building brand and community — which is exactly what this project is doing
(app stores, a website, marketing to the blind community, consolidating other
products under the name). The expensive part is optional; the cheap check is not.

(This is general principle, not legal advice.)

Web research narrows the field; it does **not** clear a name. Before any public
use of TINDRA:

1. **USPTO Class 9 search** (computer software) + the specific goods
   (word-processing / accessibility software), ideally via a trademark attorney —
   plus international classes if you sell outside the US.
2. **Domain — the exact-match names are already taken.** Verified via WHOIS:
   `tindra.com` is registered (since **2006**, IONOS, transfer-locked) and
   `tindra.org` is registered (since **2015**, Key-Systems, owner redacted);
   `tindra.store` is the furniture brand and the known "Tindra" brands also hold
   `tindra-design.com` and `tindrah.com`. "Tindra" is also a common Swedish given
   name, so exact-match domains across TLDs are largely claimed.
   - **Options:** (a) pursue a **broker purchase** of `tindra.com`/`.org` if the
     budget and a willing seller exist (premium, uncertain) — confirm with an
     authoritative registrar WHOIS first; or (b) **go prefixed/alternate** and
     own it cleanly: `tindra.app`, `usetindra.com`, `gettindra.com` / `.org`,
     `tindra.io`, or `tindra.studio`. For a community/nonprofit publisher
     (Community Access), a prefixed `.org` (e.g., `gettindra.org`) or `tindra.app`
     reads well and is far cheaper than chasing the 2006-era `.com`.
   - A free domain is **not** the same as a clear trademark — keep step 1 (Class 9
     search) as the real gate; lock matching socials and the GitHub org alongside.
3. **App stores / package registries:** check the Microsoft Store, Mac App Store,
   npm/PyPI for `tindra` collisions.
4. **Defensive filing:** once cleared, file the mark in the relevant classes before
   launch; secure `Sparks` (or the chosen extension name) too if distinctive.

### Preliminary knockout findings for TINDRA (DIY $0 pass — NOT a clearance)

Done as a free web + database scan (June 2026). **Encouraging, but not
conclusive** — the authoritative USPTO and Justia databases could not be queried
programmatically (the USPTO tool is a JavaScript app; Justia blocked automated
access), so these results are a preliminary knockout, not a clearance opinion.

- **Trademark databases:** no TINDRA mark surfaced in software (Class 9 / 42) or
  the accessibility / writing space via Trademarkia, Justia, or uspto.report
  searches. **Action: re-run directly on `search.uspto.gov`** before relying on
  this — a web scan misses pending, common-law, and foreign marks.
- **App stores / package registries:** no `tindra` app or package found on the
  Microsoft Store, Mac App Store, Google Play, PyPI, or npm.
- **Same-niche software:** **none found** — there is no accessibility / writing /
  AI app named Tindra. (Contrast the earlier candidates: *Aura Reader*, *Wren AI*,
  *Penna*, *Plume*, *Saylo* are all already writing/AI apps.)
- **Other uses, in unrelated classes (lower trademark risk):** Tindra Design —
  Swedish furniture/lighting (`tindra-design.com`, `tindra.store`); Tindrah of
  Sweden — jewellery (`tindrah.com`, note the "h"); Tindarsoft — a generic IT
  services shop; a "Tindra" app *landing-page template*; and "Tindra" is a common
  **Swedish given name** (so expect scattered personal/social uses).
- **Domains:** `tindra.com` (registered 2006) and `tindra.org` (registered 2015)
  are both taken — see the domain note above for alternates.

**Knockout verdict:** TINDRA is the **strongest result of any candidate checked** —
no same-class (software) and no same-niche (accessibility/writing/AI) conflict
turned up in a free pass; the collisions are all in unrelated categories. That is
a genuine green-ish light to proceed to the next step. **But** confirm on the
authoritative USPTO database, and — because "Tindra" is a real Swedish word and a
common given name — get a paid attorney knockout (~$300–$850, below) before any
hard public launch or trademark filing.

### What this costs (indicative, 2026, US — not legal or financial advice)

Ballpark ranges. Actual figures vary by attorney, firm, jurisdiction, and how many
trademark classes you file in. Treat these as planning numbers, not quotes.

**Trademark search and clearance**

| Step | Typical cost (USD) | Notes |
| --- | --- | --- |
| DIY USPTO search (free TESS-style search) | $0 | Cheap insurance, but **not** reliable on its own — misses similar/common-law marks |
| Attorney "knockout" / preliminary search + read | $300 – $800 | Fast same-week go/no-go; the cost-effective first real step |
| Full comprehensive clearance search (search-firm report, e.g. Corsearch/CompuMark) | $700 – $2,500 | Federal + state + common-law + domains |
| Attorney written clearance opinion | $1,000 – $2,500 | Recommended before spending on rebrand/launch |
| **Realistic all-in clearance** | **$1,500 – $5,000** | Knockout + comprehensive + opinion |

**Filing the trademark (after it clears)**

| Item | Typical cost (USD) | Notes |
| --- | --- | --- |
| USPTO government fee | ~$350 per class | Class 9 (software) at minimum; possibly Class 42 (SaaS) |
| Attorney filing fee | $500 – $1,500 per class | Some firms bundle search + file |
| **Per-class total to file** | **~$850 – $2,000** | Budget 1–2 classes |
| International (Madrid Protocol), optional | $3,000 – $10,000+ | Only if selling outside the US under the mark |

**Domains**

| Item | Typical cost (USD) | Notes |
| --- | --- | --- |
| Alternate TLDs (`tindra.app`, `usetindra.com`, `gettindra.org`, `.io`, `.studio`) | $10 – $60 / year each | The cheap, clean route — recommended |
| Broker purchase of `tindra.org` | ~$500 – $5,000 | Uncertain; depends on the owner |
| Broker purchase of `tindra.com` (6-letter, held since 2006) | ~$2,000 – $30,000+ | Premium and uncertain; the owner may simply not sell |

**Bottom line.** A sane, defensible budget is roughly **$2,000 – $6,000** all-in:
a knockout-plus-comprehensive clearance with an attorney opinion (~$1,500–$5,000),
one or two class filings (~$850–$2,000 each), and cheap alternate domains
($10–$60/yr). Add a premium domain acquisition only if you specifically want the
exact-match `.com`/`.org` and have the budget for it. Start with the **$300–$800
knockout search** — it is the cheapest way to learn early whether TINDRA is worth
spending the rest on.

### Suggested vendors (starting points, not an endorsement)

Verify current fees, reviews, and that you are working with a **licensed U.S.
trademark attorney** before engaging. Match the vendor to the goal: for a real
go/no-go and a defensible launch you want a *comprehensive search plus an attorney
opinion*, not just a filing service.

**1. Do this yourself first (free preliminary "knockout"):**

- **USPTO trademark search** — `search.uspto.gov` (the official tool that replaced
  TESS). Search the exact mark and close variants in Class 9 / 42.
- **Trademarkia** — free public search for a quick read of existing marks.
- **Domains / handles** — a registrar (Namecheap, Cloudflare, GoDaddy) for
  `tindra.app` etc.; Namechk or similar for social handles.

**2. Flat-fee trademark attorneys (the recommended path — search + opinion + file):**

- **Gerben IP** (gerbenlaw.com) — well-established; flat ~**$3,000** covers a
  comprehensive federal/state/common-law search, an attorney **opinion letter**,
  and filing in up to two classes (plus USPTO fees). Good all-in option.
- **Dawsey IP** — ~**$850** flat for a comprehensive U.S. search; single-class
  filing free of attorney fee (you still pay the ~$350/class USPTO fee). Strong
  value for the search step.
- **Flat Fee Trademark** (flatfeetrademark.com), **Knowmad Law**, **The Trademark
  Firm**, **Counsel for Creators**, **Cognition IP** (startup-focused) — other
  reputable flat-fee attorney options worth quoting.

**3. Budget DIY-with-filing (cheapest, but shallowest — use with caution):**

- **Trademark Engine**, **LegalZoom**, **Trademarkia (filing service)**, **Bizee**,
  **Rocket Lawyer** — these *file* inexpensively, but their "search" is typically
  shallow and they do not give a real clearance opinion. Fine for a low-stakes
  mark; **not** a substitute for an attorney clearance before a rebrand investment.

**4. Comprehensive search-report firms (usually accessed *through* your attorney):**

- **Corsearch** and **CompuMark (Clarivate)** — the professional full-search
  reports an attorney orders and interprets. You rarely buy these directly.

**5. Finding / vetting an attorney:**

- **INTA** (International Trademark Association) member directory; your **state bar**
  referral service; reviews on **Avvo** / **Martindale**.

**Recommended sequence:** start with a **~$300–$850 attorney knockout or
comprehensive search** (e.g., Dawsey's ~$850 comprehensive, or a knockout from a
flat-fee firm) → if it comes back clean, proceed to the **opinion + filing**
(Gerben's bundled ~$3,000, or search + per-class filing elsewhere) → register
alternate domains in parallel. Spend nothing on rebrand or premium domains until
the knockout passes.

If clearance fails, the runner-up process is the same: pick the next distinctive
coinage and re-run steps 1–4. Do not skip this for speed.

---

## 12. Risks and mitigations

- **Name still blocked at clearance.** Mitigation: keep 1–2 vetted alternates
  ready; budget for the attorney search up front.
- **Existing QUILL users confused by the change.** Mitigation: "QUILL is now
  TINDRA" everywhere for a release; in-app one-time notice; unchanged data and
  workflows.
- **Upgrade-in-place breakage from AppId/package rename.** Mitigation: stage it
  (display name now, identifiers in a major version) with a tested migration.
- **SEO reset / loss of QUILL search equity.** Mitigation: 301s from old pages,
  keep QUILL as a documented former name, lean on the acronym and feature terms.
- **"Twinkle" reads as frivolous to enterprise buyers.** Mitigation: lead with the
  acronym and the Private/Local/Universal/Multimodal pillars in institutional
  materials; save the poetry for consumer copy.

---

## 13. Rollout timeline (indicative)

- **Phase 0 — Clear it (weeks 0–4):** trademark search, domains, socials, org.
- **Phase 1 — Rebrand the surface (weeks 4–8):** UI display strings, README, user
  guide, PRD, release notes, website; "QUILL is now TINDRA" messaging.
- **Phase 2 — Sparks + ecosystem (weeks 8–12):** extension rebrand with alias,
  Ask TINDRA, marketing site, reviewer outreach.
- **Phase 3 — Deep rename (next major version):** package/AppId/data-dir migration,
  installer identity, update feed, file associations — guided and reversible.

---

## 14. Open decisions for sign-off

1. Tagline: pick the primary from section 5.
2. Extensions name: **Sparks** vs an alternative (Glints, Embers).
3. Data-dir strategy: keep `Quill` path vs migrate to `TINDRA` (and when).
4. Domain: `tindra.app` vs `gettindra.com` as primary.
5. Whether to keep "for All" ("TINDRA for All") or run with "TINDRA" alone.

---

*Heritage note: TINDRA is the evolution of QUILL by Community Access — same
mission (writing for everyone, private and on-device), a name we can own.*
