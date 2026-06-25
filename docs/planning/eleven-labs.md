# Plan: Integrating ElevenDesk capabilities into QUILL

## Context

**ElevenDesk** (`d:\code\ElevenDesk`) is an accessible wxPython desktop client
for the ElevenLabs API by the same author as QUILL. It exposes these
ElevenLabs capabilities (see `elevendesk/api.py`):

| Capability | ElevenDesk function | ElevenLabs endpoint |
| --- | --- | --- |
| Text to speech | `text_to_speech` | `text_to_speech.convert` |
| Speech to text | `speech_to_text` | `speech_to_text.convert` |
| Speech to speech (voice changer) | `speech_to_speech` | `speech_to_speech.convert` |
| Sound effect generation | `generate_sound_effect` | `sound_generation.convert` |
| Voice design | `design_voice` | `voice_design.*` |
| Voice cloning (IVC) | `clone_voice` | `voices.ivc.create` |
| Voice library / list | `get_voices`, `get_models` | `voices.get_all`, `models.get_all` |
| Generation history | `get_history`, `get_history_audio`, `delete_history_item` | `history.*` |
| Pronunciation dictionaries | `get_pronunciation_dictionaries` | `pronunciation.get_all` |

**QUILL** is a screen-reader-first writing/document editor. It already has a
mature speech subsystem under `quill/core/speech/` and `quill/core/read_aloud.py`:

- A clean **STT provider seam** (`speech/provider.py` `SpeechToTextProvider`
  protocol, `speech/registry.py`, providers `whispercpp`/`fasterwhisper`/`vosk`).
- A **host-mediated cloud STT adapter** (`speech/cloud_transcribers.py`) driven by
  `RestSpec` data, with a single audited `urlopen` call site.
- **Quillin-declared cloud providers** (`speech/quillin_providers.py`) — extensions
  *declare* a provider; the host performs the upload. The sandbox never touches
  audio bytes or the API key.
- **TTS / Read Aloud** with local engines (SAPI5, DECTALK, eSpeak, Piper, Kokoro),
  a disk-backed `tts_cache.py`, `speech/batch_export.py` (audiobook-style WAV export),
  `speech/pronunciation.py`, and `speech/text_normalize.py`.
- Cross-cutting safety gates: `tools/network_egress_audit.py`, Safe Mode,
  DPAPI-backed credential storage, `_show_modal_dialog` dialog contract, scoped mypy.

### The most important finding

**QUILL already integrates ElevenLabs for speech-to-text.** There is a bundled,
purely-declarative Quillin `quill/quillins_bundled/elevenlabs-transcription/`
(`id: com.quill.elevenlabs`, "ElevenLabs Scribe Transcription") plus a vetted
`"elevenlabs"` entry in `CLOUD_REST_SPECS` (`host="api.elevenlabs.io"`,
`key_header="xi-api-key"`). It reuses an existing **"ElevenLabs API key"**
credential label, runs under the egress audit, is gated out of Safe Mode and
offline paths, and requires per-use consent.

That means:

1. **STT is already done** — do not rebuild it. It is the precedent/template.
2. Every additional ElevenDesk capability should follow the **same posture**:
   host-mediated REST (no `elevenlabs` SDK bundled), single audited call site,
   reuse the one credential label, Safe-Mode-gated, consented, least-privilege.

> Deliberate divergence from ElevenDesk: ElevenDesk uses the `elevenlabs` Python
> SDK. QUILL should **not** adopt the SDK. QUILL's security posture depends on a
> small number of reviewed `urlopen` call sites and an egress audit; the few
> endpoints we need are re-expressed as `RestSpec`-style data, exactly as the
> existing STT spec already is.

---

## What makes sense to integrate (and what does not)

Filtered by QUILL's mission (screen-reader-first writing/reading), not "port
everything ElevenDesk does."

### Tier 1 — Strong fit, highest value: ElevenLabs as a premium cloud TTS voice

QUILL's Read Aloud and Batch Export today use local engines. ElevenLabs offers
natural, high-quality narration. This directly serves QUILL users who want
audiobook-quality output of their own documents. **This is the headline
integration.**

Surfaces it plugs into, all already present:

- **Read Aloud** (`read_aloud.py`) — ElevenLabs as a selectable voice.
- **Batch Export / audiobook** (`speech/batch_export.py`) — the best fit: export a
  folder of `.md`/`.html`/`.docx` to natural-voice audio; latency matters less
  than for live reading, and cost is bounded per run.
- **`tts_cache.py`** — already keyed by engine + voice config + exact sentence;
  caching is *more* valuable for a paid cloud engine (avoids re-billing repeats).

### Tier 2 — Fits as companions to Tier 1

- **Voice library / list + models** (`get_voices`, `get_models`) — populate the
  ElevenLabs voice picker and per-voice model choice. Read-only; low risk.
- **Voice settings** (stability, similarity, style, etc., per `VoiceSettings`) —
  expose in the TTS voice configuration UI.
- **ElevenLabs pronunciation dictionaries** (`get_pronunciation_dictionaries`) —
  list and attach to ElevenLabs TTS requests. Note: QUILL has its *own*
  client-side `speech/pronunciation.py`; the ElevenLabs ones are server-side and
  only apply to ElevenLabs synthesis. Keep them clearly distinct in the UI.
- **Voice design / cloning** (`design_voice`, `clone_voice`) — "Manage ElevenLabs
  Voices": clone the user's own voice (recursive audio import, as ElevenDesk does)
  and use it for Read Aloud. Heavier; schedule after Tier 1 ships.

### Tier 3 — Optional, niche, ship only as standalone Quillins if at all

These are further from a writing editor's core and should **not** be core features:

- **Sound effect generation** (`generate_sound_effect`) — a "generate SFX from a
  prompt" tool. Marginal for writing; candidate for an optional Quillin only.
- **Speech to speech / voice changer** (`speech_to_speech`) — transform recorded
  audio into another voice. Marginal for writing; optional Quillin only.
- **Generation history browser** (`get_history*`) — re-download past generations.
  Low value once local caching/export exists; defer or skip.

### Already done — do not rebuild

- **Speech to text** — shipped as the `elevenlabs-transcription` Quillin.

---

## Recommended architecture

### The seam gap to close

STT has a first-class provider seam; **TTS does not** — Read Aloud engines are
plain functions dispatched inside `read_aloud.py`, and Quillins can declare
`transcription_providers` but there is no `tts_providers` contribution.

Two options:

- **Option A (recommended): mirror the STT design for TTS.**
  1. Add a host-mediated `speech/cloud_synthesizers.py` with a `RestSpec`-style
     data model and **one** audited `urlopen` call site, reusing the existing
     `api.elevenlabs.io` host entry. (Parallel to `cloud_transcribers.py`.)
  2. Add a `tts_providers` contribution to the Quillin manifest model
     (`quill/core/quillins/model.py`) and schema (`quill/core/schemas/extension.json`),
     plus a host adapter mirroring `speech/quillin_providers.py`.
  3. Register an ElevenLabs TTS voice source that `read_aloud.py` and
     `batch_export.py` consume through a thin engine adapter.
  4. Ship a bundled declarative Quillin `elevenlabs-tts` (no code, no `net`
     capability), exactly like `elevenlabs-transcription`.

  This keeps the sandbox away from keys/audio, reuses every safety gate, and gives
  *all* future cloud TTS providers (not just ElevenLabs) a clean path.

- **Option B (faster, less clean): hardcode an ElevenLabs engine** path in
  `read_aloud.py`/`batch_export.py` behind a feature gate, no new Quillin
  contribution type. Use this only if Tier 1 must ship before the seam work.

**Recommendation:** Option A. It matches the precedent the STT integration already
set and avoids a one-off engine that later has to be retrofitted into a seam.

### Cross-cutting requirements (apply to every new endpoint)

- **Credential reuse.** Reuse the single **"ElevenLabs API key"** label
  (DPAPI-backed on Windows, Keychain on macOS). One key unlocks STT + TTS + voices.
- **Network egress audit.** Each new outbound call (TTS convert, voices/models
  list, pronunciation list, and any Tier 2/3 endpoint) needs an entry in
  `tools/network_egress_audit.py`. Host stays `api.elevenlabs.io`.
- **Safe Mode.** All ElevenLabs (cloud) features disabled, like STT.
- **Consent model.** STT consent is per-file. Read Aloud is *continuous*, so define
  a session/document-scoped consent with a persistent "reading via ElevenLabs
  (cloud)" indicator. **Open design question — confirm with maintainer.**
- **Cost & latency.** Read Aloud synthesizes sentence-by-sentence → one API call
  per sentence. Lead with **Batch Export** (amortized, user-initiated), make live
  Read Aloud opt-in with aggressive `tts_cache` use and buffer-ahead, and surface
  that it is a metered cloud service.
- **No SDK.** Implement endpoints as REST specs; do not add `elevenlabs` to deps.
- **Dialogs** go through `_show_modal_dialog` + `apply_modal_ids` (dialog contract
  gate). **Accessibility review is mandatory** for any new UI (voice picker, manage
  voices, settings) — route new dialogs/panels through the project's
  accessibility-lead before they are considered complete.
- **Tests/gates.** `pytest tests/unit tests/stability`, `ruff`, scoped
  `mypy quill\core quill\io`, `network_egress_audit`, dialog inventory/contract,
  and `python -m quill.tools.quillin_lint <dir> --strict` for any bundled Quillin.

---

## Phased delivery

### Phase 0 — Decision & spike (0.5–1 day)
- Confirm Option A vs B, and the Read Aloud consent model, with the maintainer.
- Spike one ElevenLabs TTS REST call (`text_to_speech.convert`, MP3/PCM) through a
  prototype `cloud_synthesizers.py`, reusing the stored key. Verify audio plays via
  the existing playback path.

### Phase 1 — ElevenLabs TTS in Batch Export (headline value)
- Add `speech/cloud_synthesizers.py` (RestSpec + single audited call site).
- Wire it into `speech/batch_export.py` as an engine option; integrate `tts_cache`.
- Voices/models list (`get_voices`/`get_models` → REST) for the export voice picker.
- Egress-audit entries; Safe Mode gating; accessible export dialog updates.
- Tests: REST spec parsing, cache hit/skip, Safe Mode off-path, egress audit pass.

### Phase 2 — ElevenLabs TTS in Read Aloud
- `tts_providers` Quillin contribution + manifest/schema + host adapter (Option A).
- Bundle declarative `elevenlabs-tts` Quillin (mirror `elevenlabs-transcription`).
- Read Aloud voice selection, voice settings (`VoiceSettings`), continuous-consent
  indicator, buffer-ahead + cache. Accessibility review of the voice picker.

### Phase 3 — Voice management & pronunciation (Tier 2)
- "Manage ElevenLabs Voices": library browse, voice design, IVC cloning with the
  recursive audio import ElevenDesk already implements.
- List/attach ElevenLabs pronunciation dictionaries to ElevenLabs synthesis; keep
  visibly separate from QUILL's local pronunciation system.

### Phase 4 — Optional Quillins (Tier 3, only if demand)
- Standalone, separately-installable Quillins for Sound Effects and Speech-to-Speech
  (voice changer). Not core. Generation history: defer/skip.

---

## Concrete first PR (smallest valuable slice)

1. `quill/core/speech/cloud_synthesizers.py` — `SynthSpec` data + one audited
   `urlopen`; one entry: ElevenLabs `text_to_speech.convert`.
2. `tools/network_egress_audit.py` — register the new call site (host reused).
3. `speech/batch_export.py` — add `"elevenlabs"` engine routing through it, cached.
4. Reuse the existing "ElevenLabs API key" credential; Safe Mode guard.
5. Tests + `ruff` + scoped `mypy` + egress audit green.

This delivers natural-voice audiobook export — a real win for QUILL's audience —
while touching no UI security boundary beyond what the shipped STT integration
already established, and sets up the TTS provider seam for Read Aloud.

## Risks / open questions

- **Read Aloud consent UX** for a continuous, metered cloud service (per-session vs
  per-document vs always-on indicator). Needs a maintainer decision.
- **Per-sentence cost/latency** for live Read Aloud; mitigated by cache + buffering
  but inherent to the sentence-by-sentence model.
- **New Quillin contribution type** (`tts_providers`) is a schema/host change with
  its own review surface; scope it deliberately in Phase 2.
- **macOS credential/storage parity** (Keychain) for the reused key label.
- **No-SDK constraint** means re-expressing each endpoint as reviewed REST; verify
  request/response shapes against current ElevenLabs API while building each spec.

## Additional Context and Considerations

## Yes—the blanket “no SDK” recommendation is too rigid

QUILL should probably use the **official ElevenLabs Python SDK**, but only behind a tightly controlled, host-owned adapter.

The existing plan rejects the SDK to preserve QUILL’s audited network boundary and single-call-site model.  That concern is valid, but QUILL does not need to choose between the SDK and its security architecture.

### What the SDK improves

The official SDK currently provides:

* Typed request and response models.
* Sync and asynchronous clients.
* TTS streaming support.
* Voice, model, pronunciation, history, cloning, STT, and other endpoint clients.
* Faster adaptation when ElevenLabs adds or changes request fields.
* Consistent parsing of API errors and responses.
* Support for supplying a custom configured `httpx` client.

ElevenLabs updates the SDK regularly as its API schema changes. That matters because the API is evolving quickly; manually maintained REST specifications can silently become stale or omit new parameters. ([GitHub][1])

Streaming is particularly important for QUILL Read Aloud. The SDK provides utilities for consuming audio incrementally rather than waiting for a complete MP3 response, which should make starting and stopping speech substantially more responsive. ([ElevenLabs][2])

### What the SDK does **not** automatically solve

The SDK is not itself a complete reliability system.

The current client exposes configurable timeouts and accepts a custom `httpx.Client` or `httpx.AsyncClient`; its default timeout is 240 seconds. I did not find a built-in `max_retries` option in the current client implementation. QUILL would still need to implement its own retry, cancellation, telemetry, offline detection, caching, and recovery policies. ([GitHub][3])

It also adds dependencies including `httpx`, Pydantic, Requests, and WebSockets. That is manageable, but it increases packaging and supply-chain surface. ([GitHub][4])

## Recommended architecture

Use the SDK **inside one controlled gateway**:

```text
Read Aloud / Batch Export / Transcription
                 |
          QUILL provider seam
                 |
       ElevenLabsHostGateway
       - consent enforcement
       - Safe Mode enforcement
       - credential retrieval
       - retries and backoff
       - timeout policy
       - cancellation
       - caching
       - cost accounting
       - error translation
       - audit logging
                 |
        Official ElevenLabs SDK
                 |
          api.elevenlabs.io
```

Only something like this should import `elevenlabs`:

```text
quill/core/speech/elevenlabs_gateway.py
```

Everything else talks to a QUILL-defined protocol. That prevents ElevenLabs classes and assumptions from spreading throughout the editor.

### Preserve QUILL’s existing protections

The gateway should:

* Retrieve the API key from QUILL’s protected credential store and pass it explicitly to the client.
* Never depend on `ELEVENLABS_API_KEY` from the environment.
* Construct and own the SDK client itself.
* Use a QUILL-configured `httpx` transport for logging, proxy behavior, TLS settings, cancellation, and connection limits.
* Reject alternate `base_url` values in production.
* Perform Safe Mode, offline-mode, and consent checks before creating a request.
* Translate SDK exceptions into stable QUILL errors.
* Keep Quillins declarative; Quillins must never receive the SDK client, API key, or audio bytes.
* Pin the SDK to an approved version and update it deliberately after tests pass.

## Retry carefully

Retries are not universally safe for a metered generation API.

For read-only requests such as listing voices or models:

* Retry temporary connection failures, HTTP 429, and selected 5xx responses.
* Use bounded exponential backoff with jitter.
* Honor `Retry-After` where present.

For TTS and other billable generation requests:

* Do not blindly retry every failed POST.
* Retry only where QUILL can determine that no usable response was received and the failure is transient.
* Limit automatic retries to one unless ElevenLabs provides a documented idempotency mechanism.
* Preserve completed audio chunks when streaming fails, but clearly report that the passage is incomplete.
* Never retry authentication, permission, invalid-input, quota-exhaustion, or unsupported-model errors.

A blind retry after ElevenLabs accepted the request could generate the same material twice and potentially charge the user twice.

## Revised recommendation for QUILL

I would change the plan from:

> “No SDK. Re-express every endpoint as REST specs.”

to:

> **Use the official ElevenLabs Python SDK exclusively inside a host-mediated `ElevenLabsGateway`. Preserve QUILL’s provider seams, security gates, credential handling, consent model, and auditable network boundary. Add QUILL-owned resilience policies rather than depending on the SDK alone.**

### Suggested rollout

1. **Batch Export first:** SDK-based non-streaming TTS, voice/model discovery, caching, cancellation, and bounded recovery.
2. **Read Aloud second:** SDK streaming with buffering, immediate cancellation, sentence prefetch, and disk cache.
3. **Existing STT third:** optionally migrate the current manual REST ElevenLabs transcriber through the same gateway after TTS proves stable.
4. **Voice management later:** cloning, voice design, pronunciation dictionaries, and history.

So, yes: **using their official SDK is likely the better long-term reliability decision.** The important constraint is that QUILL wraps it rather than letting the SDK become QUILL’s architecture.

[1]: https://github.com/elevenlabs/elevenlabs-python "GitHub - elevenlabs/elevenlabs-python: The official Python SDK for the ElevenLabs API. · GitHub"
[2]: https://elevenlabs.io/docs/api-reference/streaming "Streaming | ElevenLabs Documentation"
[3]: https://github.com/elevenlabs/elevenlabs-python/blob/main/src/elevenlabs/base_client.py "elevenlabs-python/src/elevenlabs/base_client.py at main · elevenlabs/elevenlabs-python · GitHub"
[4]: https://github.com/elevenlabs/elevenlabs-python/blob/main/pyproject.toml "elevenlabs-python/pyproject.toml at main · elevenlabs/elevenlabs-python · GitHub"

