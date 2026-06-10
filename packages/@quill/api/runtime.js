'use strict';

/**
 * @quill/api runtime shim for QUILL Node.js Quillin extensions.
 *
 * Implements the Quillin stdio protocol:
 *   - Reads one JSON line from stdin: {"method": "<handler>", "params": {...}}
 *   - Dispatches to the named handler function, passing a QuillinContext
 *   - Writes one JSON result line to stdout: {"result": null, "actions": [...]}
 *     or {"error": "<message>"} on failure
 *
 * Handlers use the QuillinContext to read editor state and queue actions.
 * Actions are collected and returned to QUILL for dispatch on the main thread.
 */

/**
 * Build a QuillinContext from the raw context data in the request params.
 *
 * @param {object} contextData - Editor state (selection, text, cursor_offset, ...).
 * @param {string[]} [_capabilities] - Reserved; not enforced by the shim.
 * @returns {import('./index').QuillinContext}
 */
function createContext(contextData, _capabilities) {
  const data = contextData || {};
  const actions = [];

  return {
    getSelection() {
      return typeof data.selection === 'string' ? data.selection : '';
    },
    getText() {
      return typeof data.text === 'string' ? data.text : '';
    },
    getCursorOffset() {
      return typeof data.cursor_offset === 'number' ? data.cursor_offset : 0;
    },
    replaceSelection(text) {
      actions.push({ type: 'replace_selection', args: [String(text)] });
    },
    insertText(text) {
      actions.push({ type: 'insert_text', args: [String(text)] });
    },
    setText(text) {
      actions.push({ type: 'set_text', args: [String(text)] });
    },
    openBuffer(text, title) {
      actions.push({ type: 'open_buffer', args: [String(text), title != null ? String(title) : ''] });
    },
    announce(message) {
      actions.push({ type: 'announce', args: [String(message)] });
    },
    setStatus(message) {
      actions.push({ type: 'set_status', args: [String(message)] });
    },
    getActions() {
      return actions.slice();
    },
  };
}

/**
 * Register handlers and start the stdin/stdout event loop.
 * Call exactly once per process.
 *
 * @param {import('./index').HandlerMap} handlers
 */
function runHandler(handlers) {
  let inputData = '';
  process.stdin.setEncoding('utf8');

  process.stdin.on('data', function (chunk) {
    inputData += chunk;
  });

  process.stdin.on('end', function () {
    const line = inputData.trim();
    if (!line) {
      _writeError('Empty input: expected a JSON request line on stdin.');
      return;
    }

    let method, params;
    try {
      const parsed = JSON.parse(line);
      method = parsed.method;
      params = parsed.params || {};
    } catch (e) {
      _writeError('Invalid JSON input: ' + e.message);
      return;
    }

    if (typeof method !== 'string' || !method) {
      _writeError('Request missing "method" field.');
      return;
    }

    const handler = handlers[method];
    if (typeof handler !== 'function') {
      _writeError('Unknown handler: ' + method);
      return;
    }

    const ctx = createContext(params.context, params.capabilities);

    try {
      const result = handler(ctx);
      if (result && typeof result.then === 'function') {
        result.then(function () {
          _writeResult(ctx.getActions());
        }).catch(function (err) {
          _writeError(String(err));
        });
      } else {
        _writeResult(ctx.getActions());
      }
    } catch (err) {
      _writeError(String(err));
    }
  });
}

function _writeResult(actions) {
  process.stdout.write(JSON.stringify({ result: null, actions: actions }) + '\n');
}

function _writeError(message) {
  process.stdout.write(JSON.stringify({ error: String(message) }) + '\n');
}

module.exports = { createContext, runHandler };
