/**
 * @quill/api — Type definitions for QUILL Quillin Node.js extensions.
 *
 * A Quillin handler receives a `QuillinContext` built from the editor state
 * QUILL passes in the request, performs its work, and returns by calling
 * action methods (replaceSelection, announce, etc.).  QUILL collects those
 * actions and dispatches them on the main thread after the handler exits.
 *
 * Usage:
 *
 *   import { runHandler, QuillinContext } from '@quill/api/runtime';
 *
 *   runHandler({
 *     myCommand(ctx: QuillinContext): void {
 *       const words = ctx.getText().split(/\s+/).length;
 *       ctx.announce(`${words} words`);
 *     },
 *   });
 */

/** Editor state available to a handler at invocation time. */
export interface QuillinContextData {
  /** Current selection text, or empty string when nothing is selected. */
  selection: string;
  /** Full document text (only present when editor.read capability is granted). */
  text: string;
  /** Zero-based caret byte offset in the document. */
  cursor_offset: number;
}

/** Action recorded by an `announce` call. */
export interface AnnounceAction {
  type: 'announce';
  args: [message: string];
}

/** Action recorded by a `replaceSelection` call. */
export interface ReplaceSelectionAction {
  type: 'replace_selection';
  args: [text: string];
}

/** Action recorded by an `insertText` call. */
export interface InsertTextAction {
  type: 'insert_text';
  args: [text: string];
}

/** Action recorded by a `setText` call. */
export interface SetTextAction {
  type: 'set_text';
  args: [text: string];
}

/** Action recorded by a `setStatus` call. */
export interface SetStatusAction {
  type: 'set_status';
  args: [message: string];
}

/** Action recorded by an `openBuffer` call. */
export interface OpenBufferAction {
  type: 'open_buffer';
  args: [text: string, title: string];
}

export type QuillinAction =
  | AnnounceAction
  | ReplaceSelectionAction
  | InsertTextAction
  | SetTextAction
  | SetStatusAction
  | OpenBufferAction;

/**
 * Context object passed to every handler.  Read methods return editor state;
 * write methods queue an action that QUILL applies after the handler returns.
 * Only capabilities declared in the manifest are honoured at runtime.
 */
export interface QuillinContext {
  /** Return the current selection text, or empty string. */
  getSelection(): string;
  /** Return the full document text (requires editor.read capability). */
  getText(): string;
  /** Return the zero-based caret byte offset. */
  getCursorOffset(): number;
  /** Queue a replace-selection action (requires editor.write capability). */
  replaceSelection(text: string): void;
  /** Queue an insert-text action (requires editor.write capability). */
  insertText(text: string): void;
  /** Queue a set-text action replacing the entire document (requires editor.write). */
  setText(text: string): void;
  /** Queue an open-buffer action creating a new unsaved document (requires editor.write). */
  openBuffer(text: string, title?: string): void;
  /** Queue an announcement to the screen reader (requires ui.announce capability). */
  announce(message: string): void;
  /** Queue a status-bar update (requires ui.status capability). */
  setStatus(message: string): void;
  /** Return the list of queued actions (used internally by the runtime shim). */
  getActions(): QuillinAction[];
}

/** Map of handler function name to handler function. */
export type HandlerMap = Record<string, (ctx: QuillinContext) => void | Promise<void>>;

/**
 * Build a `QuillinContext` from the raw context data received in the request.
 * Exported for testing; production code uses `runHandler`.
 */
export function createContext(
  contextData: Partial<QuillinContextData>,
  capabilities?: string[]
): QuillinContext;

/**
 * Register handlers and start the stdio event loop.
 *
 * Call exactly once per process.  Reads one JSON line from stdin, dispatches
 * to the named handler, and writes one JSON result line to stdout.
 *
 * @param handlers  Map of handler function names to handler functions.
 */
export function runHandler(handlers: HandlerMap): void;
