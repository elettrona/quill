'use strict';

/**
 * Word Count (Node) — a bundled example Node.js Quillin.
 *
 * Demonstrates the Quillin stdio protocol using a self-contained runtime shim.
 * Published Quillins would depend on the @quill/api npm package instead.
 *
 * Protocol:
 *   stdin:  {"method": "wordCount", "params": {"capabilities": [...], "context": {...}}}
 *   stdout: {"result": null, "actions": [{"type": "announce", "args": ["N words"]}]}
 */

// ---------------------------------------------------------------------------
// Inline runtime shim (see packages/@quill/api/runtime.js for the full version)
// ---------------------------------------------------------------------------

function createContext(contextData) {
  const data = contextData || {};
  const actions = [];
  return {
    getSelection: function () { return typeof data.selection === 'string' ? data.selection : ''; },
    getText: function () { return typeof data.text === 'string' ? data.text : ''; },
    replaceSelection: function (text) { actions.push({ type: 'replace_selection', args: [String(text)] }); },
    announce: function (message) { actions.push({ type: 'announce', args: [String(message)] }); },
    setStatus: function (message) { actions.push({ type: 'set_status', args: [String(message)] }); },
    getActions: function () { return actions.slice(); },
  };
}

function runHandler(handlers) {
  var inputData = '';
  process.stdin.setEncoding('utf8');
  process.stdin.on('data', function (chunk) { inputData += chunk; });
  process.stdin.on('end', function () {
    var line = inputData.trim();
    if (!line) {
      process.stdout.write(JSON.stringify({ error: 'Empty input.' }) + '\n');
      return;
    }
    try {
      var parsed = JSON.parse(line);
      var method = parsed.method;
      var params = parsed.params || {};
      var handler = handlers[method];
      if (typeof handler !== 'function') {
        process.stdout.write(JSON.stringify({ error: 'Unknown handler: ' + method }) + '\n');
        return;
      }
      var ctx = createContext(params.context);
      handler(ctx);
      process.stdout.write(JSON.stringify({ result: null, actions: ctx.getActions() }) + '\n');
    } catch (err) {
      process.stdout.write(JSON.stringify({ error: String(err) }) + '\n');
    }
  });
}

// ---------------------------------------------------------------------------
// Quillin handlers
// ---------------------------------------------------------------------------

runHandler({
  wordCount: function wordCount(ctx) {
    var text = ctx.getSelection() || ctx.getText();
    var trimmed = text.trim();
    var words = trimmed.length === 0 ? 0 : trimmed.split(/\s+/).length;
    var label = words === 1 ? '1 word' : words + ' words';
    ctx.announce(label);
  },
});
