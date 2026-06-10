# Word Count (Node)

A bundled QUILL Quillin that demonstrates the Node.js runtime.

Counts the words in the current selection, or the whole document when nothing is selected, and announces the result with the screen reader.

## Requirements

Node.js 16 or later must be installed and reachable on PATH. External engines must also be enabled in QUILL settings (the same switch used for AI engines).

## Usage

Open the Tools menu and choose "Word Count (Node)", or search for "Word Count (Node)" in the command palette.

## How it works

This Quillin sets `"runtime": "node"` in its manifest. QUILL spawns `node extension.js` and sends a single JSON request on stdin. The handler counts words in the context provided and returns an `announce` action. QUILL then announces the result through the active screen reader.

## For extension authors

Published Node.js Quillins should depend on the `@quill/api` npm package rather than inlining the runtime shim. This bundled example inlines the shim to stay self-contained.

## License

MIT
