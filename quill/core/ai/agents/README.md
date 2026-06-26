# QUILL agents

Each `*.md` file in this folder is one **agent**: a named, reviewable instruction
set the AI Hub lists and any engine (Native, GitHub Copilot, Claude, OpenAI
Agents) can run. The format is Markdown with YAML front matter — the same shape
as Claude Code / Claude Agent SDK subagents and QUILL's own Skill packs.

**The Markdown body is the agent's instructions** (its system prompt). The front
matter is just metadata. To review or edit an agent, read or change the body.

## Format

```markdown
---
id: accessibility-editor                 # required; lowercase dotted/dashed
display_name: Accessibility Editor        # required; shown in the AI Hub
description: One-line summary of the job. # optional
risk: medium                              # low | medium | high | critical
default_scope: full_document              # see scopes below
recommended_file_types: [md, html, txt]   # optional; no leading dot
default_harness: auto                     # auto, or a specific engine id
tools: [tool.id.one, tool.id.two]         # optional; floored to SAFE_TOOL_IDS
permissions:                              # optional per-category overrides
  read_document: ask
  modify_document: preview_required
---

You are an accessibility editor. Review the document for screen-reader-hostile
structure... (the full instructions go here, in plain Markdown — as long and as
richly formatted as you like).
```

- `schema` is implied (`quill.agent/1`) and may be omitted.
- **Scopes:** `prompt_only`, `selection`, `current_section`, `document_summary`,
  `full_document`, `open_documents`, `workspace_summary`, `explicit_files`,
  `github`.
- **Permission decisions:** `allow`, `ask`, `preview_required`, `deny`. The
  Permission Broker's floor still wins, and `risk` floors decisions too.
- Legacy `<id>.json` files (with a `system_prompt` string) still load, but
  Markdown is the authoring standard.

The contract is enforced in `quill/core/ai/agent_catalog.py` and mirrors
`quill/core/schemas/agent.json`. A malformed file is reported and skipped — it
never breaks the rest of the catalog. Files named `README.md` or starting with
`_`/`.` are treated as docs and skipped.
