"""Menu-structure gate (GATE-12).

Three invariants checked statically against source:

1. **Ctrl+Alt policy (§10.8)**: ``DEFAULT_KEYMAP`` in ``quill/core/keymap.py``
   must contain no ``Ctrl+Alt+`` binding.  The two Windows-shell actions
   (``view.send_to_tray`` / ``view.toggle_tab_control``) use
   ``Ctrl+Shift+Grave, T`` chords, not ``Ctrl+Alt+T``; they are exempt by
   design, not by omission.

2. **Required §10.3 clusters**: every Tools-menu cluster name mandated by
   §10.3 must appear in ``main_frame_menu.py``.  A missing name means the
   menu reorganisation was partially reverted or mis-named.

3. **Two-level cap (§10.4)**: no ``wx.Menu()`` variable may be *both* a child
   submenu (passed to ``AppendSubMenu``) *and* itself have ``AppendSubMenu``
   called on it — that would create three-level nesting.

Run directly (``python -m quill.tools.menu_lint``) or via pytest
(``tests/unit/tools/test_menu_lint.py``).  Exit code is non-zero when any
violation is found.
"""

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_KEYMAP_PATH = _REPO_ROOT / "quill" / "core" / "keymap.py"
_MENU_PATH = _REPO_ROOT / "quill" / "ui" / "main_frame_menu.py"

# Ctrl+Alt+ bindings explicitly exempted from §10.8 policy: these are
# Windows-shell registrations that cannot move to a QUILL-key chord.
_CTRL_ALT_ALLOWED: frozenset[str] = frozenset({
    "view.send_to_tray",
    "view.toggle_tab_control",
})

# §10.3 binding-spec cluster labels that must appear as AppendSubMenu
# arguments in main_frame_menu.py.  Checks use substring matching.
_REQUIRED_CLUSTER_LABELS: tuple[tuple[str, str], ...] = (
    ("Reading & Dictation", "R&eading && Dictation"),
    ("Comparison", '"C&omparison"'),
    ("Watch Folder", '"&Watch Folder"'),
    ("AI Assistant", '"AI &Assistant"'),
    ("Advanced", '"&Advanced"'),
    ("Quillins", '"&Quillins"'),
    ("Accessibility", '"A&ccessibility"'),
    ("Customize & Support", '"&Customize && Support"'),
    ("Writing & Language", '"&Writing && Language"'),
)


def _check_ctrl_alt(source: str) -> list[str]:
    """Return error strings for DEFAULT_KEYMAP entries bound to Ctrl+Alt+."""
    errors: list[str] = []
    try:
        tree = ast.parse(source, filename=str(_KEYMAP_PATH))
    except SyntaxError as exc:
        return [f"  SyntaxError parsing keymap.py: {exc}"]

    for node in ast.walk(tree):
        # DEFAULT_KEYMAP uses an annotated assignment (dict[str, str] type hint).
        if isinstance(node, ast.AnnAssign):
            if not (isinstance(node.target, ast.Name) and node.target.id == "DEFAULT_KEYMAP"):
                continue
            dict_node = node.value
        elif isinstance(node, ast.Assign):
            if not any(isinstance(t, ast.Name) and t.id == "DEFAULT_KEYMAP" for t in node.targets):
                continue
            dict_node = node.value
        else:
            continue
        if not isinstance(dict_node, ast.Dict):
            continue
        for key_node, val_node in zip(dict_node.keys, dict_node.values, strict=True):
            if not (isinstance(key_node, ast.Constant) and isinstance(val_node, ast.Constant)):
                continue
            command_id = str(key_node.value)
            if command_id in _CTRL_ALT_ALLOWED:
                continue
            binding = str(val_node.value)
            if re.match(r"(?i)ctrl\+alt\+", binding):
                errors.append(
                    f"  {command_id!r}: {binding!r} — "
                    "Ctrl+Alt+ is screen-reader-hostile (§10.8). "
                    "Move to a QUILL-key chord or leave unbound."
                )
    return errors


def _check_required_clusters(menu_source: str) -> list[str]:
    """Return error strings for §10.3 clusters absent from the menu source."""
    errors: list[str] = []
    for friendly_name, label_fragment in _REQUIRED_CLUSTER_LABELS:
        if label_fragment not in menu_source:
            errors.append(
                f'  "{friendly_name}" cluster ({label_fragment!r}) not found in main_frame_menu.py'
            )
    return errors


def _check_depth(menu_source: str) -> list[str]:
    """Return error strings for menus that create three or more submenu levels.

    The §10.4 two-level cap allows:
      TopMenu > SubMenu (depth 1) > SubSubMenu (depth 2) > items
    but prohibits a depth-2 submenu from having further submenus (that would
    make items reachable only through three submenu levels).
    """
    errors: list[str] = []
    try:
        tree = ast.parse(menu_source, filename=str(_MENU_PATH))
    except SyntaxError as exc:
        return [f"  SyntaxError parsing main_frame_menu.py: {exc}"]

    menu_vars: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if not isinstance(target, ast.Name):
                continue
            val = node.value
            if (
                isinstance(val, ast.Call)
                and isinstance(val.func, ast.Attribute)
                and val.func.attr == "Menu"
            ):
                menu_vars.add(target.id)

    # parent_to_children: parent_name -> list of child_name
    parent_to_children: dict[str, list[str]] = {}
    is_child: set[str] = set()
    has_children: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Expr):
            continue
        call = node.value
        if not isinstance(call, ast.Call):
            continue
        func = call.func
        if not (isinstance(func, ast.Attribute) and func.attr == "AppendSubMenu"):
            continue
        parent: str | None = None
        child: str | None = None
        if isinstance(func.value, ast.Name):
            parent = func.value.id
            has_children.add(parent)
        if call.args and isinstance(call.args[0], ast.Name):
            child = call.args[0].id
            is_child.add(child)
        if parent and child:
            parent_to_children.setdefault(parent, []).append(child)

    # BFS from root menus (never a child) to compute depth of each menu var.
    roots = menu_vars - is_child
    depth: dict[str, int] = {r: 0 for r in roots}
    queue = list(roots)
    while queue:
        current = queue.pop(0)
        for child in parent_to_children.get(current, []):
            if child not in depth:
                depth[child] = depth[current] + 1
                queue.append(child)

    # Violation: a menu at depth >= 2 that itself has AppendSubMenu children
    # would place items at depth 3+ below the top-level menu.
    for var in sorted(has_children):
        if depth.get(var, 0) >= 2:
            errors.append(
                f"  {var!r} (depth {depth[var]}) calls AppendSubMenu — "
                "creates three or more submenu levels, violating the §10.4 two-level cap."
            )
    return errors


def run_checks() -> list[str]:
    """Run all checks; return a flat list of error strings (empty = clean)."""
    errors: list[str] = []
    try:
        keymap_source = _KEYMAP_PATH.read_text(encoding="utf-8")
    except OSError as exc:
        return [f"Cannot read keymap.py: {exc}"]
    try:
        menu_source = _MENU_PATH.read_text(encoding="utf-8")
    except OSError as exc:
        return [f"Cannot read main_frame_menu.py: {exc}"]

    ctrl_alt = _check_ctrl_alt(keymap_source)
    if ctrl_alt:
        errors.append("Ctrl+Alt+ policy violations (§10.8):")
        errors.extend(ctrl_alt)

    clusters = _check_required_clusters(menu_source)
    if clusters:
        errors.append("Missing §10.3 Tools-menu clusters:")
        errors.extend(clusters)

    depth = _check_depth(menu_source)
    if depth:
        errors.append("Three-level nesting violations (§10.4 two-level cap):")
        errors.extend(depth)

    return errors


def main(argv: list[str] | None = None) -> int:
    errors = run_checks()
    if errors:
        print("menu_lint: FAIL", file=sys.stderr)
        for line in errors:
            print(line, file=sys.stderr)
        return 1
    print("menu_lint: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
