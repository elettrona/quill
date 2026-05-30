"""In-app Markdown / HTML preview, using the same accessible WebView stack as
the Ask Quill chat.

The rendered document goes into a ``wx.html2.WebView`` (Edge WebView2 on
Windows, WKWebView on macOS, WebKitGTK on Linux) so headings, lists, tables, and
code render properly and the browser engine's native accessibility carries the
screen-reader experience. As with the chat:

  * the page is ``lang``-tagged with readable + high-contrast / forced-colors CSS,
  * headings keep ``scroll-margin`` so jump-to-heading lands cleanly,
  * focus moves into the view on open,
  * Escape is bridged out of the native control (which swallows it) to close.

If no WebView backend is available it falls back to a read-only text control.
"""
from __future__ import annotations

import html
import json
import re


def _strip_tags(markup: str) -> str:
    text = re.sub(r"<[^>]+>", "", markup)
    return html.unescape(text)


class MarkdownPreviewDialog:
    def __init__(
        self,
        parent: object,
        title: str,
        body_html: str,
        start_anchor: str | None = None,
    ) -> None:
        import wx

        self._wx = wx
        self._fallback = None
        self.view = None

        self.dialog = wx.Dialog(
            parent, title=title, style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
        )
        self.dialog.SetSize((820, 760))
        outer = wx.BoxSizer(wx.VERTICAL)

        try:
            import wx.html2 as webview

            self.view = webview.WebView.New(self.dialog)
            self.view.SetName(title)
            try:
                self.view.AddScriptMessageHandler("quill")
                self.view.Bind(
                    webview.EVT_WEBVIEW_SCRIPT_MESSAGE_RECEIVED, self._on_script_message
                )
            except Exception:  # noqa: BLE001
                pass
            self.view.SetPage(self._page(title, body_html, start_anchor), "")
            outer.Add(self.view, 1, wx.EXPAND)
        except Exception:  # noqa: BLE001
            self.view = None
            self._fallback = wx.TextCtrl(
                self.dialog, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2
            )
            self._fallback.SetName(title)
            self._fallback.SetValue(_strip_tags(body_html))
            outer.Add(self._fallback, 1, wx.EXPAND | wx.ALL, 8)

        footer = wx.BoxSizer(wx.HORIZONTAL)
        footer.AddStretchSpacer()
        footer.Add(wx.Button(self.dialog, wx.ID_CANCEL, label="Close"), 0)
        outer.Add(footer, 0, wx.EXPAND | wx.ALL, 10)
        self.dialog.SetSizer(outer)
        self.dialog.Bind(wx.EVT_CHAR_HOOK, self._on_char_hook)

    def _on_char_hook(self, event: object) -> None:
        if event.GetKeyCode() == self._wx.WXK_ESCAPE:
            self._close()
            return
        event.Skip()

    def _close(self) -> None:
        self.dialog.EndModal(self._wx.ID_CANCEL)

    def _on_script_message(self, event: object) -> None:
        try:
            data = json.loads(event.GetString())
        except Exception:  # noqa: BLE001
            return
        if data.get("type") == "close":
            self._close()

    def _page(self, title: str, body_html: str, start_anchor: str | None) -> str:
        t = html.escape(title)
        anchor_js = ""
        if start_anchor:
            anchor_js = (
                f"var n=document.getElementById({json.dumps(start_anchor)});"
                "if(n){n.scrollIntoView();}"
            )
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{t}</title>
<style>
  :root {{ color-scheme: light dark; }}
  html, body {{ margin: 0; padding: 0; }}
  body {{ font-family: system-ui, Segoe UI, Arial, sans-serif; font-size: 1.05rem;
          line-height: 1.6; padding: 16px 20px; max-width: 60rem; }}
  h1, h2, h3, h4, h5, h6 {{ scroll-margin-top: 1.5rem; }}
  pre {{ background: Field; padding: 10px; border-radius: 8px; overflow-x: auto;
         white-space: pre-wrap; word-break: break-word; }}
  code {{ font-family: ui-monospace, Consolas, monospace; }}
  blockquote {{ border-left: 4px solid GrayText; padding-left: 1rem; }}
  table {{ border-collapse: collapse; }}
  th, td {{ border: 1px solid GrayText; padding: 0.4rem 0.6rem; }}
  a {{ color: LinkText; }}
  :focus {{ outline: 2px solid Highlight; outline-offset: 2px; }}
  @media (forced-colors: active) {{
    th, td {{ border: 1px solid CanvasText; }}
    blockquote {{ border-left-color: CanvasText; }}
  }}
</style>
</head>
<body>
<main id="content" tabindex="-1">
{body_html}
</main>
<script>
  document.addEventListener('keydown', function(e) {{
    if (e.key === 'Escape') {{
      e.preventDefault();
      if (window.quill && window.quill.postMessage) {{
        window.quill.postMessage(JSON.stringify({{type: 'close'}}));
      }}
    }}
  }});
  window.addEventListener('load', function() {{ {anchor_js} }});
</script>
</body>
</html>"""

    def _focus(self) -> None:
        if self.view is not None:
            self.view.SetFocus()
        elif self._fallback is not None:
            self._fallback.SetFocus()

    def show(self) -> None:
        self.dialog.CentreOnParent()
        try:
            self._wx.CallAfter(self._focus)
            self.dialog.ShowModal()
        finally:
            self.dialog.Destroy()
