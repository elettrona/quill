# Writing Assistant setup

Quill supports a local-first Writing Assistant workflow. By default, Quill does not send document content to the network.

## Local provider (recommended)

1. Install and start Ollama.
2. In Quill, open **Tools > Authoring and Automation > AI Connection Preferences**.
3. Set provider to **ollama** and choose a local model.
4. Leave API key blank for local-only endpoints.

## Authenticated endpoint

1. Open **AI Connection Preferences**.
2. Enter host, model, and provider values supplied by your endpoint.
3. Enter API key if required.

On Windows, Quill stores the optional key in a DPAPI-protected local file so the plaintext key is not written to disk.
