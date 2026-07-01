# PRD: QUILL Supported OCR Tool, AI Hub Services Tab, and Datalab Chandra OCR Integration

**Product:** QUILL  
**Feature area:** Supported OCR tool, AI Hub, document import, accessible document conversion  
**Status:** Draft for implementation planning  
**Owner:** Jeff Bishop / QUILL project  
**Last researched:** 2026-06-29  
**Primary audience:** QUILL maintainers, implementation agents, accessibility reviewers, release manager

---

## 1. Executive Summary

QUILL should ship a **first-class, supported OCR and document conversion tool**. This should not feel like a hidden AI experiment, a plugin-only feature, or an advanced developer service. It should be a real QUILL tool that users can rely on from the main application.

The AI Hub should add a **Services** tab that configures the providers behind this supported OCR tool. This tab must be customer-facing, friendly, and informative — not a sparse technical settings page. It should explain what each service does, why a user might choose it, what files it supports, what privacy tradeoffs exist, how billing works, and provide direct buttons to the provider’s website, documentation, pricing, API key page, and privacy/security information.

The **starting provider** should be **MarkItDown**, a free, local, pure-Python
converter for *born-digital* documents (DOCX, PPTX, XLSX, HTML, EPUB, and PDFs that
already carry a text layer). It ships first because it stands up the entire pipeline
— Services tab, provider interface, import wizard, open-result-in-QUILL — on the
lowest-risk backend: no API key, no billing, no cloud upload, no consent prompt, no
network-egress entry. It gives users real value on day one and costs nothing.

MarkItDown is **not an OCR engine**, so it does not by itself solve this PRD's
headline case — scanned / image-based PDFs. Those are answered **for free, on-device**
by the next backend, **local Tesseract OCR** (CPU-only, no GPU, no upload), delivered
as verified downloadable components. Only when free local OCR falls short on hard
documents does QUILL escalate to the **first paid cloud OCR provider, Datalab
Document Conversion / Chandra OCR** (exposed as **Datalab Chandra OCR Service**),
consent-gated. This is the free-first, three-tier flow (§11.4): MarkItDown → local
Tesseract OCR → Datalab cloud OCR, spending money and uploading only as a last resort.

The user-facing feature should be named something like **QUILL OCR and Document Conversion** or **Import with OCR / Convert Document**. It should let a user open a scanned PDF, image, Office document, spreadsheet, presentation, HTML file, or EPUB; send it to Datalab with explicit consent; receive structured Markdown, HTML, JSON, or chunks; and open the result directly in QUILL as an editable, screen-reader-friendly document.

The experience should be magical for blind and keyboard-only users:

- A simple, friendly import flow: **File → Import with OCR / Convert Document**.
- Sensible defaults: **Balanced mode**, **editable Markdown**, page delimiters enabled for multi-page documents.
- Rich advanced controls for power users.
- A provider-agnostic architecture so QUILL can later support Azure Document Intelligence, Mistral OCR, AWS Textract, Google Document AI, local Tesseract, local Marker, or an institutional on-prem endpoint.
- An accessible **OCR Review Mode** that turns noisy OCR output into a guided correction and verification workflow.

This is not just “OCR.” It is a full document rescue and conversion pipeline for making inaccessible, scanned, or structurally messy documents editable and understandable.

---

## 2. Source Research Summary

### 2.1 Datalab and Chandra facts relevant to implementation

Datalab’s Convert API converts documents to **Markdown, HTML, JSON, or chunks** and supports `fast`, `balanced`, and `accurate` processing modes. Datalab recommends `balanced` for most use cases, `fast` for simple/high-throughput documents, and `accurate` for scanned documents, complex tables, or dense layouts.

Sources:

- [Datalab Convert API overview](https://documentation.datalab.to/docs/recipes/conversion/conversion-api-overview)
- [Datalab SDK document conversion](https://documentation.datalab.to/docs/welcome/sdk/conversion)
- [Datalab API overview](https://documentation.datalab.to/docs/welcome/api)

The Python SDK supports:

```python
from datalab_sdk import DatalabClient, ConvertOptions

client = DatalabClient()
options = ConvertOptions(
    output_format="markdown",
    mode="balanced",
    paginate=True,
)
result = client.convert("document.pdf", options=options)
print(result.markdown)
```

The SDK requires Python 3.10+ and is installed with:

```bash
pip install datalab-python-sdk
```

Sources:

- [Datalab Python SDK docs](https://documentation.datalab.to/docs/welcome/sdk)
- [Datalab Python SDK on PyPI](https://pypi.org/project/datalab-python-sdk/)

Datalab’s REST API uses:

```http
POST https://www.datalab.to/api/v1/convert
X-API-Key: YOUR_API_KEY
```

The API returns a `request_id` and `request_check_url`; clients poll until processing is complete. Datalab says results are deleted from its servers one hour after processing completes, so QUILL must retrieve promptly and store only what the user asks to keep.

Source:

- [Datalab API overview](https://documentation.datalab.to/docs/welcome/api)

Supported file types include:

- PDF: `.pdf`
- Spreadsheets: `.xls`, `.xlsx`, `.xlsm`, `.xltx`, `.csv`, `.ods`
- Word documents: `.doc`, `.docx`, `.odt`
- Presentations: `.ppt`, `.pptx`, `.odp`
- HTML: `.html`
- EPUB: `.epub`
- Images: `.png`, `.jpg`, `.jpeg`, `.webp`, `.gif`, `.tiff`

Source:

- [Datalab supported file types](https://documentation.datalab.to/docs/common/supportedfiletypes)

Current documented limits:

- 200 MB maximum file size for PDFs, images, and Office documents.
- 7,000 pages maximum per request.
- Free tier: 10 requests per minute and 5 concurrent requests.
- Team plan: 200 requests per minute and 400 concurrent requests.
- Concurrent pages in flight: 5,000.

Source:

- [Datalab API limits and rate limiting](https://documentation.datalab.to/docs/common/limits)

Security and data-handling guidance:

- Store API keys in environment variables or secure storage; never hardcode or commit them.
- Use per-key spend limits.
- Rotate keys if compromised.
- Do not log webhook secrets or sensitive document payloads.
- Results are automatically deleted from Datalab servers one hour after processing completes.
- Datalab has an opt-in setting for using documents to improve models.
- For on-prem deployments, the container should be placed behind TLS, protected by network controls, and authenticated externally.

Source:

- [Datalab security best practices](https://documentation.datalab.to/platform/security)

Pricing and billing notes:

- Datalab uses per-page pricing; add-ons such as word bounding boxes and table/list bounding boxes are additive.
- New accounts receive a monthly free allowance: $20/month for work email accounts and $10/month for personal email accounts.
- Pay-as-you-go has no subscription or minimum spend after adding a payment method.
- Team plan is documented at $400/month and includes $400 of monthly usage, production rate limits, clickthrough BAA/DPA, SOC 2 report access, and additional custom processor capacity.
- Current public search results for the Datalab pricing page list Convert `fast` / `balanced` at **$4 per 1,000 pages**. Treat this as volatile and always link to Datalab’s pricing page rather than hard-coding rates in QUILL UI.

Sources:

- [Datalab billing docs](https://documentation.datalab.to/platform/billing)
- [Datalab pricing page](https://www.datalab.to/pricing)

Chandra OCR 2 specifics:

- Chandra OCR 2 outputs Markdown, HTML, and JSON while preserving layout.
- It supports 90+ languages.
- It has strong support for handwriting, tables, math, forms, checkboxes, images, diagrams, captions, and structured data.
- The open-source package supports vLLM and Hugging Face inference modes.
- The Datalab managed platform states it runs an improved Chandra with higher accuracy than open weights, zero data retention by default, SOC 2 Type 2, and custom BAAs.
- The Chandra repository says commercial self-hosting requires a license.

Sources:

- [Chandra OCR 2 GitHub repository](https://github.com/datalab-to/chandra)
- [Chandra OCR 2 model card on Hugging Face](https://huggingface.co/datalab-to/chandra-ocr-2)
- [Datalab Chandra 2 announcement](https://www.datalab.to/blog/chandra-2)

On-prem / enterprise option:

- Datalab offers paid on-prem options for teams with data privacy, regulated-environment, high-volume, customization, or SLA needs.
- Datalab says its container image mimics the cloud-hosted API for a simpler transition.

Source:

- [Datalab on-prem overview](https://documentation.datalab.to/docs/on-prem/overview)

---

## 3. Product Positioning: OCR Is a Supported QUILL Tool

This PRD must treat OCR as a **supported QUILL tool**, not just a service connector.

MarkItDown (free, local, born-digital) is the starting provider implementation and
Datalab Chandra is the first OCR provider added right after, but the product feature is:

> **QUILL OCR and Document Conversion**

This tool should appear in normal QUILL workflows, have help documentation, have stable menu placement, have accessible status and error handling, and be included in release notes as a supported feature.

### 4.1 User-facing promise

QUILL should be able to say:

> QUILL includes a supported OCR and document conversion tool for turning scanned, image-based, and poorly structured documents into editable, accessible content.

### 4.2 Required product surfaces

OCR must be available from the main app, not only from AI Hub settings.

Required surfaces:

```text
File
  Import with OCR / Convert Document...

Tools
  OCR and Document Conversion
    Import with OCR...
    Review Last OCR Result...
    OCR Service Settings...
    Delete OCR Temporary Files...

AI Hub
  Services
    Datalab Chandra OCR Service
```

Recommended Help menu entries:

```text
Help
  QUILL Help
    OCR and Document Conversion
    OCR Privacy and Cloud Services
    Supported OCR File Types
    Troubleshooting OCR
```

### 4.3 What “supported” means

For this PRD, **supported** means:

1. The OCR tool is part of QUILL’s documented feature set.
2. It is reachable from standard menus.
3. It has user-facing help.
4. It has clear error messages.
5. It has privacy and upload consent UX.
6. It has regression tests.
7. It has screen-reader testing requirements.
8. It has release-note coverage.
9. It has diagnostic logging that does not expose secrets or document content.
10. It can be disabled or left unconfigured without breaking QUILL.
11. It is not labeled “experimental” once MVP acceptance criteria are met.
12. Provider-specific failures are handled as service failures, not as QUILL crashes.

### 4.4 Supported feature boundary

QUILL supports the OCR workflow and user experience. MarkItDown (born-digital) and
local Tesseract (scanned) provide the free local backends; Datalab provides the first
paid cloud OCR backend.

QUILL should support:

- Opening the import tool.
- Selecting supported files.
- Explaining cloud upload.
- Submitting the file to the configured OCR provider.
- Tracking progress.
- Cancelling the job.
- Retrieving results.
- Opening editable Markdown/HTML/text output.
- Preserving useful structure.
- Guiding review of tables, forms, images, captions, low-confidence text, and page boundaries.
- Saving, exporting, or discarding the converted result.
- Reporting actionable errors.

QUILL should not promise:

- Perfect OCR.
- Perfect reconstruction of every table or form.
- That cloud providers are always available.
- That provider pricing will remain fixed.
- That cloud processing is appropriate for every sensitive document.

### 4.5 Release positioning

Release notes should describe this as a supported QUILL feature:

> QUILL now includes a supported OCR and document conversion tool. You can import scanned PDFs, images, Office files, and other documents, convert them to editable Markdown or HTML, and review the result in an accessible workflow. The first supported provider is Datalab Chandra OCR Service, configurable from AI Hub → Services.

---

### 2.2 Comparable services to plan for later

QUILL should not be locked into one OCR provider. The Services tab should support future provider adapters.

| Provider | Why it matters | Source |
|---|---|---|
| Datalab / Chandra | Best initial fit for QUILL because it directly returns Markdown, HTML, JSON, and chunks; strong complex-layout OCR; service and on-prem paths. | [Datalab Convert API](https://documentation.datalab.to/docs/recipes/conversion/conversion-api-overview) |
| Azure AI Document Intelligence | Layout model can output Markdown; tables changed to HTML table representation in v4.0 GA; strong enterprise story. | [Azure layout model docs](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/prebuilt/layout?view=doc-intel-4.0.0) |
| Mistral OCR | Returns Markdown, document structure metadata, images, tables, hyperlinks, confidence scores, optional block extraction; supports PDFs and images. | [Mistral OCR docs](https://docs.mistral.ai/studio-api/document-processing/basic_ocr) |
| AWS Textract | Strong forms/tables/query/signature extraction and AWS enterprise availability. More JSON-structure oriented than Markdown-first. | [Amazon Textract analyzing documents](https://docs.aws.amazon.com/textract/latest/dg/how-it-works-analyzing.html) |
| Google Document AI | Enterprise Document OCR supports printed and handwritten text in 200+ languages; Form Parser handles key-value pairs, checkboxes, and tables. | [Google Document AI processor list](https://docs.cloud.google.com/document-ai/docs/processors-list) |
| Local Tesseract (Tier 2 — promoted) | **Free, offline, CPU-only (no GPU) OCR** for scanned PDFs and images, via `ocrmypdf` + Tesseract. Supports 100+ languages; weaker on complex layout than cloud document-intelligence but private and free. Fetched as a verified downloadable component (native binary + `.traineddata`). QUILL's free answer for scanned documents. | [Tesseract GitHub repository](https://github.com/tesseract-ocr/tesseract) · [OCRmyPDF](https://github.com/ocrmypdf/OCRmyPDF) |
| MarkItDown (local) | **Not an OCR engine.** Free, cross-platform, pure-Python conversion of *born-digital* files (DOCX, PPTX, XLSX, HTML, EPUB, and PDFs that already have a text layer) to Markdown. Ideal free first-pass so paid OCR is only spent on genuinely scanned/image documents. Returns little or nothing for image-based PDFs. | [MarkItDown GitHub repository](https://github.com/microsoft/markitdown) |

---

## 4. Problem Statement

Many users receive inaccessible or semi-accessible documents:

- Scanned PDFs with no text layer.
- PDFs with bad reading order.
- Images of letters, forms, receipts, or print handouts.
- Word/PDF files where tables are inaccessible.
- Multi-column documents where screen readers read content in the wrong order.
- Forms with checkboxes, signatures, and labels.
- Documents with math, diagrams, captions, handwriting, or low-quality scans.

Current “OCR” workflows often dump unstructured text into the editor and leave the user to clean up the mess. That fails QUILL’s promise to meet people where they are.

QUILL should provide a first-class, accessible, service-backed document conversion workflow that gives users structure, review tools, and confidence.

---

## 5. Product Vision

Add an **AI Hub → Services** tab where users can configure and test document-intelligence services. Then add a **File → Import with OCR / Convert Document** command powered by those services.

The result should feel like this:

> “I opened a PDF that used to be locked away from me. QUILL asked how I wanted it converted, told me clearly that it would be sent to Datalab, gave me a progress update, then opened a clean Markdown document with headings, tables, lists, image captions, and page breaks. When something looked uncertain, QUILL guided me through it.”

---

## 6. Goals

### 6.1 User goals

1. Convert inaccessible PDFs and images into editable Markdown.
2. Preserve document structure whenever possible: headings, lists, tables, forms, checkboxes, images, captions, and page boundaries.
3. Provide a simple default path for nontechnical users.
4. Provide rich advanced settings for power users and institutions.
5. Make cloud upload explicit, understandable, and optional.
6. Allow BYOK API key usage.
7. Support institutional on-prem endpoints.
8. Provide accessible correction/review workflows.

### 6.2 Product goals

1. Establish a reusable **Services** architecture inside AI Hub.
2. Ship free-first: MarkItDown (born-digital) and local Tesseract OCR (scanned) as
   free local services before any paid cloud provider; Datalab / Chandra as the first
   paid cloud OCR service.
3. Route every import free-first across the three tiers (§11.4).
4. Avoid vendor lock-in through a provider adapter abstraction.
5. Make the import pipeline asynchronous, cancellable, recoverable, and screen-reader friendly.
6. Build the foundation for future services: Mistral OCR, Azure Document Intelligence, AWS Textract, Google Document AI, local Tesseract, local Marker, local Chandra, or QUILL-hosted endpoints.

### 6.3 Accessibility goals

1. Every feature must be keyboard accessible.
2. All controls must have meaningful accessible names, roles, states, and descriptions.
3. Progress updates must be announced politely and not spam screen readers.
4. Results must open in controls that support caret navigation and screen-reader reading.
5. Tables must have a guided accessible review path.
6. OCR confidence and warnings must be conveyed textually, not only visually.
7. Avoid emoji or decorative Unicode in status messages by default.

---

## 7. Non-Goals for Initial Release

1. Do not bundle any local engine (MarkItDown, Tesseract, Marker, Chandra) in the
   QUILL installer — all are verified downloadable components (§Z.3).
2. Do not require a GPU for any supported tier. Local Tesseract OCR (Tier 2) is
   CPU-only by design; GPU-hungry local ML engines (Marker / local Chandra) are
   deferred to Phase 7.
3. Do not build a full PDF editor.
4. Do not promise perfect reconstruction of every document.
5. Do not silently upload files to any cloud service.
6. Do not make Datalab the only possible service in the architecture.
7. Do not build enterprise billing management in QUILL beyond usage warnings and links.
8. Do not implement automatic remediation of every OCR error in v1.

---

## 8. User Personas

### 8.1 Blind everyday user

Needs to convert a scanned letter, handout, form, or PDF into readable text quickly. They may not understand OCR jargon. They want a safe default and a clear warning before cloud upload.

### 8.2 Blind power user / document fixer

Wants control over page ranges, output type, OCR mode, table handling, image captions, block IDs, word confidence, and correction workflows.

### 8.3 Institutional accessibility worker

Needs to process many documents, may need BAA/DPA, SOC 2, on-prem, auditability, and predictable costs.

### 8.4 Developer / contributor

Needs provider adapters, testable job orchestration, stable service interfaces, and simulated/mock responses for CI.

---

## 9. Proposed Information Architecture

### 9.1 AI Hub

Add a new top-level tab:

```text
AI Hub
  General
  Models
  Prompts
  Agents
  Services    ← new
  Privacy
  Diagnostics
```

The **Services** tab manages external and local services QUILL can call.

### 9.2 Services tab layout

Use an accessible list or tree with detail pane.

```text
Services
  Document Conversion and OCR
    MarkItDown (local, free — Tier 1)
    Local Tesseract OCR (local, free, CPU-only — Tier 2)
    Datalab Chandra OCR Service (cloud, paid — Tier 3)
    Azure Document Intelligence
    Mistral OCR
    AWS Textract
    Google Document AI
    Local Marker
  Speech and Transcription
    Whisper / Faster Whisper
    Cloud transcription providers
  AI Assistants and Coding Services
    GitHub Copilot
    Claude
    OpenAI-compatible endpoints
```

For v1, only **Datalab Chandra OCR Service** must be fully implemented. Others may appear as disabled “coming later” entries only if this does not clutter or confuse the UI.

### 8.3 Services tab must be friendly and customer-facing

The Services tab must feel like a helpful product page inside QUILL, not a developer settings dialog. Many users will not know what an OCR service, API key, endpoint, or provider means. The UI should explain those concepts in plain language and guide the user toward a successful setup.

The Services tab should answer these questions without requiring the user to leave QUILL:

- What does this service do?
- Why would I use it?
- What kinds of documents can it help with?
- Is it local or cloud-based?
- Will my document be uploaded?
- What output can QUILL create from it?
- Does it cost money?
- Where do I get an API key?
- Where can I read the provider’s privacy, security, and pricing information?
- What should I do if I am part of a school, company, legal office, medical office, or other organization with privacy rules?

Required tone:

- Friendly.
- Plain language.
- Confidence-building.
- Honest about cloud upload and cost.
- Not scary, but not vague.
- Helpful for nontechnical users.
- Detailed enough for power users and institutional users.

### 8.4 Services tab page model

Each service should use a rich detail page with these sections:

```text
Service name
Short plain-language description
Status and setup summary
What this service can do
Best for
Supported file types
Output options
Privacy and data handling
Pricing and account notes
Setup steps
Buttons and links
Advanced technical settings
Diagnostics and troubleshooting
```

### 8.5 Required buttons and links

Each configured cloud service page should include customer-facing buttons. For Datalab, include:

| Button | Purpose |
|---|---|
| Visit Datalab Website | Opens the provider’s main website. |
| Get or Manage API Key | Opens the provider’s API key/account page when known; otherwise opens documentation. |
| View Pricing | Opens the provider’s pricing page. |
| Read Privacy and Security Information | Opens provider security/privacy docs. |
| Read API Documentation | Opens provider API docs. |
| Read Supported File Types | Opens provider supported file types documentation. |
| Test Connection | Verifies whether QUILL can reach the service. |
| Configure This Service | Moves focus to setup fields. |
| Use This Service for OCR | Sets this provider as the default OCR provider. |
| Open QUILL OCR Help | Opens QUILL’s help page for OCR and document conversion. |

Buttons must have clear accessible names. Avoid vague names like “Learn More” when a precise button label is possible.

### 8.6 Datalab Chandra OCR customer-facing description

The Datalab service page should include a friendly description like this:

```text
Datalab Chandra OCR Service helps QUILL turn scanned PDFs, images, forms, tables, and complex documents into editable content. It can return Markdown, HTML, JSON, or structured chunks. For most QUILL users, Markdown is the recommended output because it opens directly in the editor and is easy to read, search, edit, and save.

This is a cloud service. When you convert a document with this provider, QUILL sends the selected file to Datalab, waits for processing, retrieves the result, and opens the converted document for you. QUILL will always ask before uploading a document.
```

### 8.7 Service status summary

At the top of each service page, show a concise status summary:

```text
Status: Ready
Default OCR provider: Yes
Account/API key: Configured
Endpoint: Datalab cloud
Default mode: Balanced
Default output: Markdown
Cloud upload required: Yes
```

Possible status values:

- Ready
- Not configured
- Needs API key
- Disabled
- Connection failed
- Provider unavailable
- Local provider not installed
- Enterprise/on-prem endpoint configured

### 8.8 Plain-language setup steps

Datalab setup should be presented as a numbered checklist:

```text
1. Create or sign in to your Datalab account.
2. Get an API key from Datalab.
3. Paste the API key into QUILL.
4. Choose your default conversion mode.
5. Press Test Connection.
6. Use File → Import with OCR / Convert Document.
```

Add a short explanation of API keys:

```text
An API key is like a password that lets QUILL use your Datalab account. Keep it private. QUILL stores it securely and will not show it in logs.
```

### 8.9 Friendly provider comparison

The Services tab should eventually include a provider comparison view. For v1, it can be a simple informational table with Datalab active and others marked future/planned.

Example:

| Service | Best for | Local or cloud | Status |
|---|---|---|---|
| Datalab Chandra OCR Service | Scanned PDFs, complex layouts, Markdown/HTML conversion | Cloud or enterprise on-prem | Supported |
| MarkItDown | Free, fast conversion of born-digital DOCX/PPTX/XLSX/HTML/EPUB and text-layer PDFs (not scanned images) | Local (Tier 1) | Supported (MVP) |
| Local Tesseract | Free, offline, CPU-only OCR for scanned PDFs and images | Local (Tier 2) | Supported |
| Azure Document Intelligence | Enterprise Azure environments | Cloud | Planned |
| Mistral OCR | Markdown-first OCR workflows | Cloud | Planned |
| Google Document AI | Google Cloud document processing | Cloud | Planned |
| AWS Textract | AWS forms, tables, and document extraction | Cloud | Planned |

### 8.10 Services tab accessibility requirements

The rich information must remain accessible:

- Use real headings so screen reader users can jump by heading.
- Use normal text controls, tables, lists, buttons, and links.
- Do not rely on icons or color alone.
- Every external link button must say where it goes.
- If a link opens a browser, announce that it opens in the browser.
- Keep provider descriptions readable and concise.
- Put technical settings after friendly overview content.
- Provide a “Copy service summary” button for support requests.
- Provide a “Copy diagnostics without secrets” button.
- Make every section reachable by keyboard.

### 8.11 Customer-facing service summary copy

Add a button named **Copy Service Summary**. It should copy a safe summary like:

```text
QUILL OCR service summary
Provider: Datalab Chandra OCR Service
Status: Ready
Endpoint type: Cloud
Default mode: Balanced
Default output: Markdown
Cloud upload required: Yes
API key present: Yes
API key value: Not included
Last connection test: Successful
```

This helps users ask for support without exposing secrets.

---

## 10. Datalab Chandra OCR Service Configuration UX

### 10.1 Service card

Accessible name:

> Datalab Chandra OCR Service

Description:

> Converts PDFs, images, Office documents, spreadsheets, presentations, HTML, and EPUB files into Markdown, HTML, JSON, or chunks using Datalab’s document conversion service and Chandra OCR.

Fields:

| Field | Control | Default | Notes |
|---|---|---:|---|
| Enable service | Checkbox | Off | User must opt in. |
| API key | Password edit | Empty | Stored in secure credential storage, not plain config. |
| Endpoint | Edit | `https://www.datalab.to` | Allows on-prem or enterprise endpoint later. |
| Default mode | Combo box | Balanced | Fast, Balanced, Accurate. |
| Default output | Combo box | Markdown | Markdown, HTML, JSON, Chunks. |
| Add page delimiters | Checkbox | On | Recommended for screen reader navigation. |
| Extract images | Checkbox | On | Maps extracted images to document output. |
| Generate image captions | Checkbox | On | Valuable for screen-reader users. |
| Default processing region | Combo box | Account default | Account default, US, EU. |
| Confirm before upload | Checkbox | On and locked for v1 | Never silently upload. |
| Save converted copy automatically | Checkbox | Off | User chooses where to save. |
| Show advanced options on import | Checkbox | Off | Simple by default. |
| Monthly usage warning | Number/edit | Optional | Local soft warning only. |

Buttons:

- **Visit Datalab Website**
- **Get or Manage API Key**
- **View Datalab Pricing**
- **Read Datalab Privacy and Security Information**
- **Read Datalab API Documentation**
- **Read Supported File Types**
- **Test Connection**
- **Use This Service for OCR**
- **Open QUILL OCR Help**
- **Copy Service Summary**
- **Copy Diagnostics Without Secrets**
- **Reset Service Settings**

These buttons should appear near the friendly overview and setup checklist, not hidden only in advanced settings.

### 10.2 Test Connection behavior

When the user presses **Test Connection**:

1. Validate that an API key exists.
2. Make a minimal authenticated request if Datalab exposes a suitable account/status endpoint.
3. If no lightweight endpoint is available, perform a safe SDK initialization and show “API key present; full validation will occur on first conversion.”
4. Never upload a user document for testing unless the user explicitly chooses a sample test file.
5. Announce success or failure to the screen reader and place focus on the result message.

Example success message:

> Datalab service is configured. QUILL can use this service when you choose Import with OCR.

Example failure message:

> Datalab service could not be verified. Check your API key, internet connection, and endpoint URL.

---

## 11. File Import and Conversion UX

### 11.1 Menu entry

Add:

```text
File
  Import with OCR / Convert Document...
```

Optional later shortcut:

```text
Ctrl+Shift+O
```

Only assign the shortcut if it does not conflict with existing QUILL or expected Windows conventions.

### 11.2 Import wizard: simple path

Step 1: Choose file.

Supported types should be read from the selected provider’s capability descriptor.

Step 2: Choose output.

Default choices:

1. **Open as editable Markdown** — recommended.
2. **Open as accessible HTML preview and Markdown source**.
3. **Open plain text only**.
4. **Open OCR Review Mode**.
5. **Advanced: save JSON or chunks for automation.**

Step 3: Consent and cost note.

Required cloud notice:

> This document will be sent to Datalab for processing. Do not continue unless you are allowed to upload this document to that service. Datalab says conversion results are deleted from its servers one hour after processing completes. QUILL will retrieve the result promptly and will not send documents automatically.

Buttons:

- **Convert**
- **Cancel**
- **Service Settings**

### 11.3 Import wizard: advanced options

Advanced options should be collapsible and fully keyboard accessible.

Provider-specific Datalab options:

| Option | QUILL label | Datalab parameter |
|---|---|---|
| Output format | Output format | `output_format` |
| Processing mode | Processing mode | `mode` |
| Page delimiters | Add page delimiters | `paginate` |
| Maximum pages | Maximum pages | `max_pages` |
| Page range | Page range | `page_range` |
| Skip cached results | Force fresh conversion | `skip_cache` |
| Extract images | Extract images | inverse of `disable_image_extraction` |
| Generate image captions | Generate image captions | inverse of `disable_image_captions` |
| Include Markdown in chunks | Include Markdown in chunks/JSON | `include_markdown_in_chunks` |
| Token-efficient Markdown | Optimize Markdown for AI token usage | `token_efficient_markdown` |
| Add block IDs | Add block IDs to HTML | `add_block_ids` |
| Word bounding boxes | Include word boxes and confidence | `word_bboxes` |
| Track changes | Extract tracked changes | `extras=track_changes` |
| Chart understanding | Understand charts and diagrams | `extras=chart_understanding` |
| Extract links | Extract links | `extras=extract_links` |
| Table cell boxes | Include table cell boxes | `extras=table_cell_bboxes` |
| List item boxes | Include list item boxes | `extras=list_item_bboxes` |
| Infographic mode | Infographic understanding | `extras=infographic` |
| New block types | Use expanded block detection | `extras=new_block_types` |
| Region | Processing region | `processing_location` |

Default advanced setting recommendations:

```yaml
output_format: markdown
mode: balanced
paginate: true
disable_image_extraction: false
disable_image_captions: false
token_efficient_markdown: false
add_block_ids: false
word_bboxes: false
extras: ""
```

For “OCR Review Mode,” use:

```yaml
output_format: html,json
mode: accurate
paginate: true
word_bboxes: true
add_block_ids: true
include_markdown_in_chunks: true
extras: "table_cell_bboxes,list_item_bboxes,extract_links,chart_understanding,new_block_types"
```

Because this costs more, QUILL must warn the user before enabling expensive add-ons.

### 11.4 Free-first, three-tier conversion (local text → local OCR → cloud OCR)

Not every document needs paid, cloud OCR — and even scanned documents usually don't.
QUILL routes every import through **three tiers**, spending money (and uploading a
file) only as a last resort:

- **Tier 1 — MarkItDown (free, local, no upload).** Extracts the existing text layer
  from *born-digital* files (DOCX, PPTX, XLSX, HTML, EPUB, and PDFs that already
  carry text). Not an OCR engine — it does not recognize scanned images.
- **Tier 2 — Local Tesseract OCR (free, local, no upload).** Real OCR for scanned /
  image-based PDFs and photos of documents, run entirely on the user's machine via
  `ocrmypdf` + Tesseract. **CPU-only — no GPU required.** Lower accuracy than cloud
  document-intelligence on complex layouts, but free, offline, and private.
- **Tier 3 — Datalab Chandra cloud OCR (paid, cloud, consent-gated).** The accuracy
  escalation for hard documents: complex tables, forms, handwriting, math, dense or
  multi-column layouts, and poor scans. Only reached when the free local tiers fall
  short or the user explicitly chooses it.

This means the PRD's headline case — rescuing a scanned PDF — has a **free, local,
private** answer (Tier 2). Cloud AI is an *upgrade*, never a toll gate.

#### Routing model

```text
1. Choose file.
2. Born-digital type? -> Tier 1: MarkItDown locally (free, no upload).
     - Enough usable text -> open it. Done. No OCR, no cloud, no cost.
     - Little/no text (looks scanned) -> fall through to Tier 2.
3. Scanned / image-based, or Tier 1 came back empty? -> Tier 2: local Tesseract OCR
   (free, offline, no upload).
     - Good enough -> open it. Done. Still free, still on-device.
     - Poor result, or complex layout (tables/forms/handwriting/math/multi-column),
       or user asks for higher accuracy -> offer Tier 3.
4. Tier 3: Datalab cloud OCR — paid, consent-gated. Reached only when free local
   tiers fall short, or the user explicitly selects it.
```

The user always keeps control: a **"Prefer free local conversion when possible"**
setting (default on) governs Tiers 1–2, and an **"Always ask which provider"** option
lets power users choose the tier per import.

#### "Empty / low-quality result" detection and the escalation prompts

The real design work is deciding when a tier *failed to recover the content*, rather
than silently handing the user a blank or garbled document. Two decision points,
each tuned in Phase 0:

- **Tier 1 → 2 (empty text layer):** extracted characters below a threshold relative
  to page count (e.g. a multi-page PDF yielding < ~50 characters per page), or output
  that is only images/whitespace with no headings, paragraphs, or table text.
- **Tier 2 → 3 (weak OCR):** very low mean OCR confidence, sparse recognized text, or
  a user judgment that the result is unusable. (Tesseract exposes per-word/character
  confidence, so QUILL can surface a mean-confidence signal.)

QUILL must never silently open an empty or clearly-broken result. At each fall-through
point, show an accessible prompt. Tier 1 → 2 (stays free and local):

> QUILL could not find readable text in this document. It looks scanned or
> image-based. Run free on-device OCR (local Tesseract)? This stays on your computer
> and does not upload anything.
>
> Buttons: **Run local OCR** · **Open empty result anyway** · **Cancel**

Tier 2 → 3 (introduces cost + upload, so it is the only prompt that mentions either):

> On-device OCR finished, but the result looks low-quality or the layout is complex.
> For higher accuracy you can convert it with Datalab cloud OCR. This uploads the
> file to a cloud service and may cost money.
>
> Buttons: **Keep local result** · **Convert with cloud OCR** · **Cancel**

Announce each outcome and move focus to the message, per §16.

#### Cost and privacy story

This is materially better than "everything scanned goes to paid cloud OCR": born-
digital files cost nothing (Tier 1), scanned documents still cost nothing and never
leave the machine (Tier 2), and per-page cloud spend + upload is reserved only for
documents that genuinely need the accuracy (Tier 3). The Services tab should state
each tier's tradeoff plainly on its card (free/local/no-upload vs. paid/cloud/upload).

#### Footprint and acquisition (all tiers are downloadable components)

None of these tiers ship inside the installer. Each is fetched on demand through the
pinned, SHA-256-verified acquisition path (§Z.3), with cancelable accessible
progress, blocked in Safe Mode, and re-downloadable/replaceable:

- **MarkItDown** — pure-Python, cross-platform (Win/macOS/Linux, Python 3.10+), no
  GPU, no native binary, no ML model. Install only scoped extras
  (`markitdown[pdf,docx,pptx,xlsx]`); the `xlsx` extra pulls in `pandas`, the one
  non-trivial dependency, droppable if spreadsheets are deferred.
- **Tesseract OCR** — `ocrmypdf` (Python) plus the **Tesseract native binary and
  per-language `.traineddata` files**. **CPU-only, no GPU.** The binary is
  platform-specific and language packs add weight, so QUILL fetches the right binary
  per OS and only the language data the user needs (default: English; others
  downloadable on demand) as **verified downloadable components in all install
  locations**. This is the one tier with a native, per-platform payload — still free,
  offline, and private.

Because Tiers 1 and 2 are local and perform no upload, they need **no API key, no
consent prompt, and no network-egress audit entry** — genuinely simpler cards than
the cloud provider. Only Tier 3 (Datalab) carries a key, a mandatory consent prompt,
and a GATE-9 egress-audit entry.

---

## 12. OCR Review Mode

OCR Review Mode is the differentiator. This is where QUILL can be magical.

### 12.1 Purpose

Give the user a guided, accessible way to inspect and correct OCR output without needing to visually compare page images.

### 12.2 Layout

Use a split-pane or dialog with:

1. **Document outline tree**
   - Pages
   - Headings
   - Tables
   - Forms
   - Images and captions
   - Low-confidence text
   - Warnings

2. **Editable converted content**
   - Markdown or structured text in a normal QUILL editing surface.

3. **Context / confidence pane**
   - Read-only multiline edit field.
   - Shows source page number, block type, confidence, bounding box text if available, and nearby context.

4. **Actions pane**
   - Accept block
   - Edit block
   - Mark as needs review
   - Convert table to Markdown
   - Convert table to CSV
   - Re-run selected pages in accurate mode
   - Add correction to OCR dictionary
   - Export review report

### 12.3 Keyboard model

Suggested commands:

| Command | Action |
|---|---|
| F6 | Cycle panes |
| Shift+F6 | Cycle panes backward |
| F2 | Edit selected block |
| Ctrl+Enter | Accept current block |
| Ctrl+Shift+Enter | Accept all blocks on page |
| Alt+R | Re-run selected page or block |
| Alt+T | Open table review |
| Alt+I | Review images and captions |
| Alt+F | Review form fields and checkboxes |
| Alt+L | Jump to next low-confidence item |
| Alt+P | Announce page and block position |
| Escape | Close secondary dialogs or return to previous pane |

### 12.4 Screen reader announcements

Announcements must be helpful and not noisy.

Good examples:

> Page 3, table, 6 rows, 4 columns, confidence medium.

> Low-confidence word: “Arizona.” Current text may be incorrect.

> Image caption generated: “Bar chart showing monthly enrollment.” Review recommended.

Avoid:

- Repeating the full document content on every focus change.
- Announcing raw JSON.
- Emoji or decorative symbols.
- Long automatic speech while the user is arrowing.

### 12.5 Review report

QUILL should optionally generate a Markdown review report:

```markdown
# OCR Review Report

Source file: example.pdf
Provider: Datalab Chandra OCR Service
Mode: accurate
Pages processed: 12
Output: Markdown

## Warnings

- Page 4: 12 low-confidence words.
- Page 6: Complex table detected.
- Page 9: Image caption generated and not manually verified.

## User actions

- Page 4: Corrected 3 words.
- Page 6: Converted table to Markdown.
```

---

## 13. Architecture

### 13.1 Core components

```text
quill/
  ai_hub/
    services_tab.py
    service_registry.py
    credential_store.py
    service_models.py
  services/
    base.py
    document_conversion.py
    datalab_provider.py                # Tier 3: paid cloud OCR (accuracy escalation)
    markitdown_provider.py             # Tier 1: local, free born-digital conversion
    local_tesseract_provider.py        # Tier 2: local, free OCR (ocrmypdf+Tesseract, CPU-only)
    azure_document_intel_provider.py   # future
    mistral_ocr_provider.py            # future
  document_import/
    import_wizard.py
    conversion_job.py
    conversion_result.py
    ocr_review_mode.py
    markdown_postprocessor.py
    html_to_markdown.py
    table_tools.py
  security/
    privacy_prompts.py
    redaction_helpers.py               # future
  tests/
    fixtures/
      simple_scanned.pdf
      table_complex.pdf
      form_checkbox.pdf
      handwritten_note.png
```

### 13.2 Provider interfaces

```python
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Protocol, Optional, Mapping, Any


class OutputFormat(str, Enum):
    MARKDOWN = "markdown"
    HTML = "html"
    JSON = "json"
    CHUNKS = "chunks"
    TEXT = "text"


class ProcessingMode(str, Enum):
    FAST = "fast"
    BALANCED = "balanced"
    ACCURATE = "accurate"


@dataclass(frozen=True)
class ServiceCapability:
    provider_id: str
    display_name: str
    supports_cloud: bool
    supports_on_prem: bool
    supported_extensions: tuple[str, ...]
    output_formats: tuple[OutputFormat, ...]
    processing_modes: tuple[ProcessingMode, ...]
    max_file_size_mb: Optional[int] = None
    max_pages_per_request: Optional[int] = None
    supports_page_range: bool = False
    supports_confidence: bool = False
    supports_bounding_boxes: bool = False
    supports_tables: bool = False
    supports_image_captions: bool = False


@dataclass
class ConversionOptions:
    output_format: OutputFormat = OutputFormat.MARKDOWN
    mode: ProcessingMode = ProcessingMode.BALANCED
    paginate: bool = True
    page_range: Optional[str] = None
    max_pages: Optional[int] = None
    extract_images: bool = True
    generate_image_captions: bool = True
    include_confidence: bool = False
    include_block_ids: bool = False
    extras: tuple[str, ...] = ()


@dataclass
class ConversionProgress:
    status: str
    percent: Optional[int] = None
    current_page: Optional[int] = None
    total_pages: Optional[int] = None
    message: str = ""


@dataclass
class ConversionResult:
    provider_id: str
    source_path: Path
    output_format: OutputFormat
    markdown: Optional[str] = None
    html: Optional[str] = None
    json_data: Optional[Mapping[str, Any]] = None
    chunks: Optional[Mapping[str, Any]] = None
    images: Optional[Mapping[str, bytes]] = None
    metadata: Optional[Mapping[str, Any]] = None
    warnings: tuple[str, ...] = ()
    parse_quality_score: Optional[float] = None


class DocumentConversionProvider(Protocol):
    def capabilities(self) -> ServiceCapability:
        ...

    def validate_configuration(self) -> tuple[bool, str]:
        ...

    def convert(
        self,
        source_path: Path,
        options: ConversionOptions,
        progress_callback,
        cancel_token,
    ) -> ConversionResult:
        ...
```

### 13.3 Datalab provider behavior

Use the SDK by default when available:

```python
from datalab_sdk import DatalabClient, ConvertOptions as DatalabConvertOptions
```

Fallback to REST if the SDK is not installed or if packaging makes direct REST more reliable.

Datalab options mapping:

```python
DatalabConvertOptions(
    output_format=options.output_format.value,
    mode=options.mode.value,
    paginate=options.paginate,
    max_pages=options.max_pages,
    page_range=options.page_range,
    disable_image_extraction=not options.extract_images,
    disable_image_captions=not options.generate_image_captions,
    word_bboxes=options.include_confidence,
    add_block_ids=options.include_block_ids,
    extras=",".join(options.extras) if options.extras else None,
)
```

### 13.4 Asynchronous job orchestration

QUILL is a wxPython app. Network calls and polling must never block the UI thread.

Use:

- Worker thread or task executor for conversion.
- `wx.CallAfter` for UI updates.
- Cancel token checked between polling attempts.
- Exponential backoff for transient failures.
- Specific handling for HTTP 429 / rate limits.
- Job log that excludes document content and secrets.

Job state model:

```text
queued
validating
uploading
submitted
processing
retrieving
postprocessing
opening
complete
cancelled
failed
```

### 13.5 Temporary files

Use:

```text
%LOCALAPPDATA%\QUILL\Temp\ocr_jobs\<job_id>\
```

Contents:

```text
source_copy.ext
result.md
result.html
result.json
images\
job_metadata.json
```

Default cleanup:

- Delete temporary source copy after successful import unless user enables “keep job files.”
- Keep converted result only in the open document until the user saves.
- Auto-delete failed job temp folders older than 7 days.
- Never store API keys in job metadata.

### 13.6 Credential storage

Do not store API keys in JSON settings.

Preferred options:

1. Python `keyring` package using Windows Credential Manager.
2. Windows DPAPI through `win32crypt` or a small credential helper.
3. Environment variable fallback: `DATALAB_API_KEY`.

Suggested key names:

```text
QUILL/services/datalab/api_key
QUILL/services/datalab/endpoint
```

Config file may store non-secret settings:

```json
{
  "services": {
    "datalab": {
      "enabled": true,
      "endpoint": "https://www.datalab.to",
      "default_mode": "balanced",
      "default_output_format": "markdown",
      "paginate": true,
      "confirm_before_upload": true
    }
  }
}
```

---

## 14. Markdown Post-Processing

Datalab will return Markdown, but QUILL should still apply a careful post-processing pass.

### 14.1 Required post-processing

1. Normalize line endings.
2. Ensure page delimiters are consistent and easy to search.
3. Convert any unsupported or problematic Unicode to accessible text when QUILL’s “screen reader friendly symbols” option is enabled.
4. Ensure tables are navigable.
5. Ensure generated image captions are clearly marked as generated.
6. Preserve links when available.
7. Add source metadata at the top only if the user opts in.

Recommended optional metadata block:

```markdown
<!--
Converted by QUILL
Provider: Datalab Chandra OCR Service
Mode: balanced
Source: filename.pdf
Pages: 12
Review recommended: yes
-->
```

### 14.2 Page delimiters

Use a consistent, screen-reader-friendly delimiter:

```markdown
<!-- Page 1 -->
```

or:

```markdown
[Page 1]
```

Default recommendation: `<!-- Page 1 -->` for Markdown cleanliness, with a QUILL command to jump page-to-page.

### 14.3 Tables

Default table behavior:

- Preserve Markdown tables when simple.
- For complex tables, preserve HTML table if Markdown would destroy structure.
- Offer a **Table Review** action.
- Offer exports:
  - Markdown table
  - HTML table
  - CSV
  - TSV

---

## 15. Privacy, Consent, and Safety Requirements

### 15.1 Required consent prompt

Before every cloud upload, unless a future enterprise admin policy explicitly changes this:

> QUILL will send this document to Datalab for OCR and document conversion. Only continue if you are allowed to upload this file to that service. Consider whether the document contains private, medical, legal, educational, financial, employment, or confidential information.

Buttons:

- **Convert**
- **Cancel**
- **Open service privacy notes**

### 15.2 Sensitive document warning

If filename or user-selected classification suggests sensitive content, add an extra warning. Do not inspect content deeply without consent.

Potential triggers:

- Filename includes: `medical`, `health`, `patient`, `tax`, `ssn`, `social security`, `passport`, `driver`, `w2`, `w-2`, `bank`, `legal`, `contract`, `student`, `iep`, `disability`, `accommodation`.
- User manually selects “Sensitive document.”

### 15.3 Logging rules

Never log:

- API keys.
- Full request payloads.
- File contents.
- OCR output.
- URLs with signed tokens.
- Webhook secrets.
- Full error bodies that may contain document content.

May log:

- Provider id.
- Non-secret endpoint host.
- Job state transitions.
- File extension.
- File size.
- Page count.
- Mode.
- Output format.
- Error category.

### 15.4 Data retention

QUILL must make local retention explicit:

- Open converted result in an unsaved document.
- Ask before saving converted files.
- Provide **Delete OCR temporary files now** command.
- Respect Datalab’s stated one-hour result deletion window by retrieving promptly.

---

## 16. Accessibility Requirements

### 16.1 AI Hub Services tab

- The services list must be keyboard navigable.
- Service status must be available textually:
  - Enabled
  - Not configured
  - Needs API key
  - Connection failed
  - Ready
- Password/API key field must expose an accessible name and help text.
- “Test Connection” results must be placed in a focusable status field and announced.

### 16.2 Import wizard

- All steps must have clear headings.
- Focus must move to the first actionable control on each step.
- Progress updates must be concise.
- Cancel must remain reachable by keyboard while processing.
- Errors must focus a readable details field.

### 16.3 OCR Review Mode

- Use normal edit controls for readable text whenever possible.
- Avoid custom-drawn controls unless accessible objects are implemented.
- Tables must have row/column navigation support.
- Low-confidence items must be discoverable by keyboard.
- All generated captions must be identified as generated.

### 16.4 Screen reader testing matrix

Minimum manual test matrix:

| Screen reader | Browser/UI surface | Required |
|---|---|---|
| NVDA current stable | QUILL wxPython UI | Yes |
| JAWS current stable | QUILL wxPython UI | Yes |
| Narrator Windows 11 | QUILL wxPython UI | Yes |
| VoiceOver macOS | Future if cross-platform | Later |

---

## 17. Error Handling

### 17.1 Common errors

| Error | User-facing message |
|---|---|
| No API key | “Datalab is not configured. Add an API key in AI Hub, Services.” |
| Invalid API key | “Datalab rejected the API key. Check or replace the key.” |
| Offline | “QUILL cannot reach the service. Check your internet connection.” |
| Unsupported file | “This service does not support that file type.” |
| File too large | “This file is larger than the service limit. Try a smaller file or process a page range.” |
| Too many pages | “This document has more pages than the service allows in one request. Use a page range.” |
| 429/rate limit | “The service is busy or your account is rate-limited. QUILL will wait and retry.” |
| Payment/credits issue | “The service reported a billing or credit issue. Check your Datalab account.” |
| Cancelled | “Conversion cancelled. No result was imported.” |
| Bad result | “The service returned an incomplete result. Try accurate mode or a smaller page range.” |

### 17.2 Error details

Each error dialog should include:

- Friendly summary.
- Technical details button.
- Copy details button.
- Open service settings button where relevant.
- Retry button where relevant.

---

## 18. Cost and Usage UX

### 18.1 Principles

- QUILL should not pretend to know exact billing unless the provider returns it.
- QUILL should explain that OCR service pricing is provider-controlled and may change.
- QUILL should link to the provider’s pricing page.
- QUILL should warn before using expensive modes or add-ons.

### 18.2 Estimated usage prompt

Before conversion:

```text
Estimated pages: 42
Provider: Datalab Chandra OCR Service
Mode: Balanced
Output: Markdown
Cost: See Datalab pricing. Your account may include free credits or usage allowance.
```

If Datalab returns `cost_breakdown`, show it after conversion in the job summary.

### 18.3 Usage history

Optional v1.1 feature:

```text
AI Hub → Services → Usage
  Datalab
    Documents processed this month: 8
    Pages submitted: 316
    Last conversion: 2026-06-29
```

No content should be stored in usage history.

---

## 19. Feature Flags

Add feature flags:

```json
{
  "features": {
    "ai_hub_services_tab": true,
    "markitdown_local_conversion": true,
    "local_tesseract_ocr": true,
    "datalab_document_conversion": true,
    "prefer_free_local_conversion": true,
    "ocr_review_mode": false,
    "service_usage_history": false
  }
}
```

---

## 20. Implementation Plan

The plan is sequenced **free-first**, in the three tiers of §11.4. The full pipeline
— Services tab, provider interface, import wizard, open-result-in-QUILL — is proven
on the lowest-risk backend first: **MarkItDown** (free, local, born-digital, Phases
0–3). Then **local Tesseract OCR** (free, offline, no upload) lands next (Phase 4),
so scanned / image-based PDFs get a **free, private** answer before any paid path
exists. Only then does the **first cloud OCR provider, Datalab Chandra** (paid,
consent-gated), arrive as the accuracy escalation (Phase 5). OCR Review Mode and
further providers follow. Every engine is a verified **downloadable component**
(§Z.3), never bundled in the installer.

### Phase 0: Spike and verification

Deliverables:

1. Verify MarkItDown packaging and scoped extras (`markitdown[pdf,docx,pptx,xlsx]`)
   in QUILL's Python environment; confirm cross-platform install and footprint
   (note the `pandas` weight from the `xlsx` extra).
2. Build a throwaway script that converts with MarkItDown:
   - born-digital DOCX
   - PPTX and XLSX
   - HTML and EPUB
   - a text-layer PDF
   - a *scanned* image-only PDF (to confirm it returns little/no text)
3. Calibrate the "empty result" detection heuristic (§11.4) against the scanned
   sample versus the born-digital samples.
4. Verify the Datalab SDK also packages cleanly (so Phase 5 is unblocked), and run
   a throwaway Datalab conversion of the scanned PDF, complex table PDF, image with
   text, and checkbox form. Confirm image retrieval, billing/cost response fields,
   error response shapes, whether `output_format="markdown,html"` is supported in
   one request, and on-prem endpoint assumptions.
5. Document sample results in `docs/research/markitdown_spike.md` and
   `docs/research/datalab_chandra_spike.md`.

Exit criteria:

- MarkItDown converts each born-digital sample to Markdown locally.
- The scanned-PDF sample is reliably classified as "empty / needs OCR."
- One successful Datalab conversion via SDK and one via REST fallback.
- One handled failure for invalid Datalab API key and one handled 429/rate-limit case.

### Phase 1: Services tab foundation

Deliverables:

1. `ServiceRegistry`
2. `CredentialStore` (built now; the MarkItDown card uses none of it — proves the
   registry works for a keyless, no-upload provider)
3. `ServiceDescriptor`
4. `AIHubServicesPanel`
5. MarkItDown service card (local, free, no API key, no consent prompt, no
   egress-audit entry)
6. Settings persistence
7. Unit tests for settings and registry

Exit criteria:

- User can see and enable the MarkItDown service, save settings, and reopen AI Hub
  with state intact.
- A keyless/no-upload provider renders correctly with no API-key or consent UI.

### Phase 2: MarkItDown provider adapter (starting provider)

Deliverables:

1. `MarkItDownDocumentConversionProvider`
2. Scoped-extra dependency handling via the §Z.3 on-demand acquisition path
3. Capability descriptor (born-digital extensions only; no OCR, no cloud)
4. Progress callback + cancel support
5. Result normalization to `ConversionResult`
6. "Empty result" detection (§11.4)
7. Markdown post-processing reuse
8. Unit tests (fully local; no network, no key)

Exit criteria:

- Provider converts each born-digital sample to Markdown, entirely offline.
- Empty/near-empty output is flagged rather than silently returned.
- Provider handles cancellation and missing-dependency errors.

### Phase 3: Import wizard (free-first local path — MVP)

Deliverables:

1. `ImportWithOcrDialog`
2. Simple mode and advanced mode
3. Progress dialog
4. Save/open result in QUILL
5. Page delimiter support
6. Recent import settings
7. Free-first behavior wired to MarkItDown (Tier 1 only for now — local OCR lands in
   Phase 4, cloud OCR in Phase 5)

Exit criteria:

- User can choose a born-digital file and open converted Markdown in QUILL, for
  free, with no upload and no consent prompt.
- UI remains responsive; screen reader announces status; cancel works.
- This is the shippable MVP: the whole pipeline works end-to-end on MarkItDown.

### Phase 4: Local Tesseract OCR (free, offline — Tier 2)

This is where scanned / image-based PDFs — the PRD's headline case — become supported
**for free, on-device, with no upload.** Cloud OCR is not required to reach this
milestone.

Deliverables:

1. Local Tesseract service card (no API key, no consent prompt, no egress-audit entry)
2. `TesseractDocumentConversionProvider` wrapping `ocrmypdf` + Tesseract (CPU-only)
3. **Downloadable-component acquisition (§Z.3):** fetch the platform-correct
   Tesseract binary and per-language `.traineddata` on demand, verified by SHA-256,
   with accessible cancelable progress, Safe-Mode blocked, re-downloadable. English
   by default; additional language packs downloadable in all install locations.
4. Language selection UI (which OCR languages to download/use)
5. Capability descriptor (scanned PDFs + images; CPU-only; free; no cloud)
6. Progress, cancel, and mean-confidence signal from Tesseract
7. Tier 1 → Tier 2 routing (§11.4): on an empty text layer, offer free local OCR
8. Unit tests with a bundled tiny fixture image; no network, no key

Exit criteria:

- User can convert a scanned PDF or image to editable Markdown **entirely offline,
  for free**, after the language data is downloaded once.
- The Tesseract binary and language packs install as verified downloadable components
  and are re-downloadable/replaceable.
- No GPU is required; the flow works on a CPU-only machine.

### Phase 5: Datalab Chandra cloud OCR (paid accuracy escalation — Tier 3)

The accuracy upgrade for hard documents (complex tables, forms, handwriting, math,
dense/multi-column layouts, poor scans). Free local tiers already cover the common
case; this is opt-in, paid, and consent-gated.

Deliverables:

1. Datalab service card + settings UI (API key, endpoint, mode, output, etc.)
2. Test connection action; API key stored securely and never logged
3. `DatalabDocumentConversionProvider` (SDK implementation + REST fallback)
4. Progress, cancel, retry/backoff, result normalization
5. Cloud-upload consent prompt (mandatory, per §15) and network-egress audit entry
6. Tier 2 → Tier 3 routing (§11.4): on weak local OCR or complex layout, offer the
   consent-gated Datalab conversion
7. Unit tests with mocked API responses; integration test guarded by `DATALAB_API_KEY`

Exit criteria:

- User can enable Datalab, configure a key securely, and convert a hard document to
  Markdown after an explicit consent prompt.
- Free tiers still run by default; the paid path is only offered when local OCR is
  weak or the user explicitly chooses higher accuracy.
- Cancellation and common errors are handled; no key or document content is logged.

### Phase 6: OCR Review Mode v1

Deliverables:

1. OCR review document outline
2. Low-confidence navigation when confidence data exists
3. Table review entry points
4. Image caption review
5. Review report generation
6. Re-run selected page range in accurate mode

Exit criteria:

- User can review warnings and accept/edit blocks by keyboard.
- User can generate a review report.
- JAWS/NVDA/Narrator testing passes basic flows.

### Phase 7: Provider expansion

Add provider adapters based on demand:

1. Mistral OCR
2. Azure Document Intelligence
3. Google Document AI
4. AWS Textract
5. Datalab on-prem profile templates
6. Local Marker / local Chandra (heavier local ML engines; may want a GPU)

Exit criteria:

- Services tab supports multiple providers without UI redesign.
- Import wizard can select provider based on capability.

---

## 21. Test Plan

### 21.1 Unit tests

- Service registry loads descriptors.
- Credentials are saved and retrieved through mock secure store.
- Datalab options map correctly.
- Unsupported file types are rejected.
- Page range validation.
- Error mapping.
- Markdown post-processing.
- Sensitive filename warning triggers.

### 21.2 Integration tests

Use opt-in environment variable:

```bash
set QUILL_RUN_DATALAB_TESTS=1
set DATALAB_API_KEY=...
```

Tests:

- Convert sample PDF to Markdown.
- Convert sample image to Markdown.
- Convert sample table PDF to HTML/JSON.
- Invalid API key returns friendly error.
- Cancel during polling.

### 21.3 Accessibility tests

Manual scripts:

1. Configure Datalab with NVDA.
2. Configure Datalab with JAWS.
3. Import scanned PDF with keyboard only.
4. Read progress messages.
5. Review generated Markdown.
6. Use OCR Review Mode.
7. Correct low-confidence text.
8. Export review report.

### 21.4 Privacy tests

- Confirm no API key in config.
- Confirm no API key in logs.
- Confirm source file content is not logged.
- Confirm temporary files are cleaned up.
- Confirm cloud consent prompt appears every time in v1.

---

## 22. Acceptance Criteria

### 22.1 MVP acceptance criteria (MarkItDown — free, local, no upload)

1. AI Hub contains a Services tab.
2. MarkItDown is the default document-conversion provider and requires no API key.
3. User can import a born-digital file (DOCX, PPTX, XLSX, HTML, EPUB, text-layer PDF)
   via File → Import with OCR / Convert Document.
4. User can also discover the feature from Tools → OCR and Document Conversion.
5. Conversion runs locally, for free, with no upload and no consent prompt.
6. Conversion runs without freezing the UI.
7. Progress is accessible.
8. Result opens as an editable Markdown document.
9. Headings, lists, tables, and page delimiters are preserved when MarkItDown returns them.
10. When MarkItDown recovers little or no text (a scanned/image document), QUILL says
    so and does not silently open an empty document.
11. Errors are understandable and actionable.
12. Basic NVDA, JAWS, and Narrator tests pass.
13. No document content is written to logs.

### 22.2 Local-OCR milestone acceptance criteria (Tesseract — free, offline)

1. Local Tesseract OCR can be enabled with no API key and no consent prompt.
2. The Tesseract binary and at least English language data install as verified
   downloadable components, and are re-downloadable/replaceable, in all install
   locations.
3. A scanned / image-based PDF or an image converts to editable Markdown **entirely
   offline, for free**, with nothing leaving the machine.
4. The flow works on a **CPU-only machine — no GPU required.**
5. Additional OCR languages can be downloaded on demand.
6. When a born-digital file's text layer is empty, QUILL offers this free local OCR
   (Tier 1 → Tier 2) before ever mentioning cloud or cost.

### 22.3 Cloud-OCR milestone acceptance criteria (Datalab Chandra — paid cloud)

1. Datalab Chandra OCR Service can be enabled and configured.
2. API key is stored securely and never appears in config or logs.
3. QUILL explicitly asks for consent before every cloud upload.
4. A hard document (complex tables, forms, handwriting, poor scan) converts to
   editable Markdown via Datalab.
5. Free-first routing holds: born-digital → MarkItDown and scanned → local Tesseract
   run for free by default; the paid cloud path is offered only when local OCR is
   weak or the user explicitly chooses higher accuracy.
6. Tables, forms, image captions, and confidence data are preserved when returned.
7. Rate-limit, billing, offline, and cancellation errors are handled gracefully.

### 22.4 “Magical” acceptance criteria

1. A blind user can convert a scanned PDF without needing sighted help.
2. The default output is immediately readable and editable.
3. QUILL guides the user to complex tables, forms, images, and uncertain OCR areas.
4. The user can re-run hard pages in accurate mode.
5. The user can export a clean Markdown document and an OCR review report.
6. The same Services architecture can support a second OCR provider without rewriting the import UI.

---

## 23. Risks and Mitigations

| Risk | Mitigation |
|---|---|
| Vendor pricing changes | Do not hard-code prices; link to provider pricing; show provider-returned cost if available. |
| Cloud privacy concern | Explicit consent; BYOK; on-prem endpoint support; local fallback later. |
| Long-running jobs | Async worker; progress dialog; cancellation; retry/backoff. |
| Bad OCR output | OCR Review Mode; re-run page range; allow accurate mode; preserve original source reference. |
| Complex table loss | Preserve HTML/JSON when Markdown cannot represent table accurately; add Table Review. |
| API instability | SDK plus REST fallback; provider abstraction; robust error handling. |
| Accessibility regressions | Manual SR test scripts; avoid custom controls; use standard wx controls. |
| Large documents hit limits | Page range segmentation; warn at file selection; future batch splitting. |
| Secret leakage | Secure credential store; log redaction; automated tests. |

---

## 24. Open Questions

1. Should QUILL name the service **Datalab Chandra OCR Service** or **Datalab Document Conversion** in the UI? Recommendation: user-facing name should be “Datalab Chandra OCR Service,” with technical description mentioning Datalab Convert API.
2. Should OCR Review Mode be part of MVP or behind a beta flag? Recommendation: ship initial review warnings in MVP; full Review Mode behind a beta flag.
3. Should QUILL support multiple output formats in one request if Datalab allows comma-separated formats in the current API? Verify in Phase 0.
4. Should a QUILL-hosted relay service ever exist for users who cannot manage API keys? Recommendation: not for MVP; revisit with strong privacy, funding, and abuse controls.
5. Should institutions be able to preconfigure service settings through an admin config file? Recommendation: yes in v1.1.
6. Should QUILL support redaction before upload? Recommendation: future feature; very difficult to make reliable for scanned documents without already doing OCR.

---

## 25. Recommended Implementation Prompt for Coding Agent

Use this prompt with Claude Code, Codex, or another coding agent:

```text
You are implementing QUILL's AI Hub Services tab and the first document-conversion provider: Datalab Chandra OCR Service.

Read the PRD in docs/prd/ai-hub-services-datalab-chandra-ocr.md. Implement this in phases and keep a running implementation log.

Core requirements:
1. Ship OCR as a supported QUILL tool with stable File and Tools menu access, Help documentation, and release-note coverage.
2. Add an accessible AI Hub → Services tab that is rich, friendly, customer-facing, and includes provider descriptions, benefits, supported file types, privacy notes, pricing/account notes, setup steps, diagnostics, and external website/documentation/pricing/security buttons.
2. Add a provider registry and provider interface for document conversion services.
3. Add secure credential storage for service API keys; never store secrets in JSON config or logs.
4. Implement Datalab Chandra OCR Service using datalab-python-sdk where possible and a REST fallback where needed.
5. Add File → Import with OCR / Convert Document.
6. Add a simple import flow with safe defaults: Balanced mode, Markdown output, page delimiters on, image extraction/captioning on.
7. Add advanced options mapped to Datalab Convert API parameters.
8. Show a required cloud upload consent prompt before every upload.
9. Run conversion asynchronously so the wxPython UI never freezes.
10. Open the converted result as a new editable Markdown document.
11. Add robust error handling for missing key, invalid key, offline, unsupported file, file too large, too many pages, rate limits, billing/credits, cancellation, and incomplete result.
12. Add tests and mocks. Integration tests must be opt-in and require DATALAB_API_KEY.

Accessibility requirements:
- Keyboard-only support for every control.
- Standard wx controls wherever possible.
- Meaningful accessible names, descriptions, and status messages.
- Progress updates must be announced politely and must not spam screen readers.
- No emoji or decorative Unicode in status messages.

Security requirements:
- Do not log API keys, document content, OCR output, signed URLs, or full sensitive payloads.
- Store only non-secret service settings in config.
- Temporary files must be cleaned up.
- Consent is mandatory for v1.

Start with the foundation and do not overbuild provider-specific UI into the core
architecture. Sequence the providers **free-first** in three tiers: (1) MarkItDown —
free local born-digital conversion (the MVP); (2) local Tesseract OCR — free, offline,
CPU-only OCR for scanned PDFs/images, delivered as verified downloadable components
(native binary + language data) in all install locations; (3) Datalab Chandra — paid
cloud OCR as the accuracy escalation, consent-gated. Route every import free-first
(§11.4). Azure, Mistral, AWS, Google, and heavier local ML engines should be possible
later through the same adapter interface.
```

---

## 26. Suggested File/Issue Breakdown

### Epic: AI Hub Services Foundation

- Issue: Add ServiceDescriptor and ServiceRegistry.
- Issue: Add secure CredentialStore.
- Issue: Add AI Hub Services tab.
- Issue: Add service settings persistence.
- Issue: Add service diagnostics panel.

### Epic: MarkItDown local conversion (Tier 1 — MVP)

- Issue: Add MarkItDown provider adapter.
- Issue: Add scoped-extra dependency acquisition (§Z.3).
- Issue: Add "empty result" detection.
- Issue: Add Tier 1 → Tier 2 escalation prompt.
- Issue: Add local (no-network) unit tests.

### Epic: Local Tesseract OCR (Tier 2 — free, offline)

- Issue: Add Tesseract provider adapter (ocrmypdf + Tesseract, CPU-only).
- Issue: Add downloadable-component acquisition for the Tesseract binary (per-OS).
- Issue: Add downloadable language-pack (.traineddata) management, all locations.
- Issue: Add OCR language selection UI.
- Issue: Add mean-confidence signal and Tier 2 → Tier 3 escalation prompt.
- Issue: Add local unit tests with a bundled fixture image.

### Epic: Datalab Chandra OCR Service (Tier 3 — paid cloud)

- Issue: Add Datalab provider adapter.
- Issue: Add SDK implementation.
- Issue: Add REST fallback.
- Issue: Add option mapping.
- Issue: Add mock response tests.
- Issue: Add integration test harness.

### Epic: Import with OCR

- Issue: Add File → Import with OCR / Convert Document.
- Issue: Add import wizard simple mode.
- Issue: Add advanced options.
- Issue: Add consent prompt.
- Issue: Add progress and cancellation.
- Issue: Open result in new Markdown document.

### Epic: Accessible OCR Review

- Issue: Add conversion warnings panel.
- Issue: Add low-confidence navigation.
- Issue: Add table review mode.
- Issue: Add image caption review.
- Issue: Add OCR review report export.

### Epic: Documentation

- Issue: Add user help page.
- Issue: Add privacy help page.
- Issue: Add admin/on-prem configuration page.
- Issue: Add troubleshooting page.
- Issue: Add developer provider-adapter guide.

---

## 27. User Documentation Draft

### Import with OCR / Convert Document

Use this feature when a PDF, image, or other document is hard to read, has no text, or has tables and layout that do not work well with your screen reader.

1. Open the **File** menu.
2. Choose **Import with OCR / Convert Document**.
3. Pick your file.
4. Choose how QUILL should open the result. **Editable Markdown** is recommended.
5. Review the cloud upload notice.
6. Choose **Convert**.

QUILL will send the document to the selected service, retrieve the converted result, and open it as a new document. Review the result before relying on it, especially for legal, medical, financial, educational, or other sensitive documents.

### Choosing a mode

- **Fast**: Best for simple, clean documents.
- **Balanced**: Recommended for most documents.
- **Accurate**: Best for scanned pages, complex tables, dense layouts, forms, and handwriting. It may take longer and may cost more.

### Privacy note

QUILL will not send a document to a cloud service unless you choose to continue after the upload notice. Do not upload documents unless you are allowed to send them to the selected service.

---

## 28. Final Recommendation

Implement this as a **supported OCR tool powered by a Services-first architecture**, not as a hidden connector or one-off experimental command.

The **MVP starting backend is MarkItDown** — free, local, born-digital, no key, no
upload — which stands up the whole tool safely and cheaply:

- Configure once in **AI Hub → Services** (MarkItDown needs no key).
- Import from **File → Import with OCR / Convert Document**.
- Default to **free local conversion + Markdown + page delimiters**.
- Open the result directly in QUILL, with nothing leaving the machine.
- Build the provider interface so alternatives can be added cleanly.

The **free OCR backend, local Tesseract (Tier 2)**, lands next so scanned /
image-based PDFs get a **free, offline, private** answer — no GPU, no cloud, no cost:

- Enable it in **AI Hub → Services** (no key, no consent prompt).
- Fetch the Tesseract binary and language data as **verified downloadable components
  in all install locations** (§Z.3).
- OCR scanned PDFs and images entirely on-device.

The **paid cloud OCR backend, Datalab Chandra OCR Service (Tier 3)**, follows as the
accuracy escalation for hard documents:

- Enable and configure it in **AI Hub → Services** (secure API key).
- Default to **Balanced + Markdown + page delimiters**.
- Require explicit upload consent on every conversion.
- Reach it through **free-first routing** (§11.4): QUILL tries MarkItDown, then free
  local OCR, and offers paid Datalab OCR only when the local tiers fall short.

This gives QUILL a powerful, practical path for turning inaccessible documents into
editable, navigable, screen-reader-friendly content — free and local by default,
spending on cloud OCR only when a document genuinely needs the accuracy — while
preserving user choice, privacy, and future flexibility.

---

## Appendix Z. AI menu discoverability + the extensible AI Hub Services framework

*(Added during planning integration — ties this PRD to the AI menu, the verified
on-demand acquisition path, and the broader "services" direction.)*

### Z.1 Tight AI Hub **and** AI menu integration

The configuration home is **AI Hub → Services** (per §9). For discoverability, the
top-level **AI menu** also surfaces the supported OCR tool directly, so users who
live in the menus never have to know where the Services tab is:

- **AI → Import with OCR / Convert Document…** — the primary action (mirrors
  **File → Import with OCR**; same handler).
- **AI → Services…** — opens the AI Hub on the Services tab.

Both honor QUILL's invariants: the dialog contract (`_show_modal_dialog`),
cancelable spoken progress (`AIProgressDialog`), Safe Mode gating, and the
network-egress audit (GATE-9) for every provider call. Upload is consent-gated
(a document leaves the machine only on an explicit action).

### Z.2 The AI Hub Services framework is the extensible home for *all* document-intelligence services

This PRD's "Services tab + provider interface" is deliberately a **framework**, not
an OCR-only feature. Every future document-intelligence service plugs into the same
tab, the same provider interface (§13.2), the same credential storage, the same
consent/audit/Safe-Mode rules, and the same accessible card UX. Planned tenants:

- **Document conversion / OCR:** MarkItDown (free, local, born-digital — the MVP
  starting provider), then Datalab Chandra (first paid OCR provider), then Mistral
  OCR, Azure Document Intelligence, AWS Textract, Google Document AI, and local engines.
- **Scribe for Documents (Pneuma Solutions):** the partner document-conversion
  service specced in [`scribe.md`](scribe.md) is a natural **Services-tab tenant** —
  same "configure once, convert, open result in QUILL" shape, just with an OAuth
  connection instead of an API key. Its OAuth flow reuses QUILL's existing
  authorization-code pattern (see `scribe.md` §2.1).
- A single **service descriptor** (id, friendly name, category, capabilities,
  config schema, optional credential, optional **on-demand component**, menu
  placement) lets a new service appear in the Services tab + AI menu with no
  bespoke UI.

### Z.3 Local engines are verified downloadable components — everywhere

For **local** engines (MarkItDown, Tesseract, and later Marker / local Chandra),
QUILL must not bloat the installer. Every one is fetched on demand through the same
**pinned, SHA-256-verified release-asset** mechanism shipped for the speech engine
and Kokoro (`quill/core/release_assets.py`; QUILL-PRD.md §5.25f, "Recommended host and
redistribution rules"): a service that needs a local dependency, binary, or model
declares it as a release asset, and QUILL downloads + verifies + unpacks it with
cancelable, accessible progress, blocked in Safe Mode — and offers a
**re-download/replace** when one is already present, with **newer-version awareness**
on the roadmap (a `version` field already exists on the asset model). This applies in
**all install locations** (per-user, all-users, and portable) — no engine is ever
assumed pre-present.

**Tesseract specifics (Tier 2, the free OCR engine):** unlike the pure-Python
MarkItDown, Tesseract is a **native, per-OS binary plus per-language `.traineddata`
files**, and it is **CPU-only (no GPU dependency)**. QUILL therefore declares:

- one Tesseract binary asset **per platform** (Windows/macOS/Linux), resolved to the
  running OS; and
- **language-pack assets** downloaded individually — English by default, other
  languages fetched on demand from the OCR language-selection UI —

so users install only the OS binary and the languages they actually use. Heavier
local ML engines (Marker / local Chandra) follow the same path but may additionally
want a GPU; Tesseract deliberately does not.

### Z.4 Net

OCR ships **free-first and real** — MarkItDown then local Tesseract before any paid
cloud provider — inside a **services framework** that the AI menu and AI Hub present
uniformly, whose engines are all verified downloadable components (no installer
bloat, CPU-only where possible), that partner services (Scribe) and cloud providers
(Datalab) join without new plumbing, and that inherits QUILL's privacy, consent,
accessibility, and verified-acquisition guarantees. That is the magical, future-proof
shape: one accessible home for document intelligence — free and local by default,
paid cloud only when a document truly needs it, many services over time.
