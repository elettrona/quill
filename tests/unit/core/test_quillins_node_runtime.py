"""Tests for Node.js runtime support in the Quillins model and validation.

Covers:
- Model constants (RUNTIME_PYTHON, RUNTIME_NODE, RUNTIMES)
- ExtensionManifest.runtime field and is_node_runtime property
- validate_manifest with runtime field
- parse_manifest with node runtime
- Schema agreement for node runtime manifests
"""

from __future__ import annotations

from quill.core.quillins.model import (
    RUNTIME_NODE,
    RUNTIME_PYTHON,
    RUNTIMES,
    ExtensionManifest,
)
from quill.core.quillins.validation import parse_manifest, validate_manifest
from quill.tools import quillin_lint as ql

# ---------------------------------------------------------------------------
# Base fixtures
# ---------------------------------------------------------------------------

_PYTHON_MANIFEST = {
    "schema": "quill.extension/1",
    "id": "com.example.pyext",
    "name": "Python Ext",
    "version": "1.0.0",
    "capabilities": ["editor.read", "editor.write", "ui.announce", "ui.command"],
    "main": "extension.py",
    "contributes": {"commands": [{"id": "ext.py.go", "title": "Go", "run": {"handler": "go"}}]},
}

_NODE_MANIFEST = {
    "schema": "quill.extension/1",
    "id": "com.example.nodeext",
    "name": "Node Ext",
    "version": "1.0.0",
    "runtime": "node",
    "capabilities": ["editor.read", "ui.announce", "ui.command"],
    "main": "extension.js",
    "contributes": {"commands": [{"id": "ext.node.go", "title": "Go", "run": {"handler": "go"}}]},
}


# ---------------------------------------------------------------------------
# Model constants
# ---------------------------------------------------------------------------


def test_runtime_constants_have_expected_values() -> None:
    assert RUNTIME_PYTHON == "python"
    assert RUNTIME_NODE == "node"


def test_runtimes_contains_both() -> None:
    assert RUNTIME_PYTHON in RUNTIMES
    assert RUNTIME_NODE in RUNTIMES
    assert len(RUNTIMES) == 2


def test_extension_manifest_defaults_to_python_runtime() -> None:
    manifest = ExtensionManifest(id="x", name="X", version="1.0.0")
    assert manifest.runtime == RUNTIME_PYTHON
    assert not manifest.is_node_runtime


def test_extension_manifest_node_runtime_flag() -> None:
    manifest = ExtensionManifest(id="x", name="X", version="1.0.0", runtime=RUNTIME_NODE)
    assert manifest.runtime == RUNTIME_NODE
    assert manifest.is_node_runtime


def test_extension_manifest_python_runtime_flag() -> None:
    manifest = ExtensionManifest(id="x", name="X", version="1.0.0", runtime=RUNTIME_PYTHON)
    assert not manifest.is_node_runtime


def test_is_layer_two_true_for_both_runtimes() -> None:
    py = ExtensionManifest(id="x", name="X", version="1.0.0", runtime=RUNTIME_PYTHON, main="ext.py")
    node = ExtensionManifest(id="x", name="X", version="1.0.0", runtime=RUNTIME_NODE, main="ext.js")
    assert py.is_layer_two
    assert node.is_layer_two


def test_is_layer_two_false_without_main() -> None:
    manifest = ExtensionManifest(id="x", name="X", version="1.0.0", runtime=RUNTIME_NODE)
    assert not manifest.is_layer_two


# ---------------------------------------------------------------------------
# validate_manifest — node runtime
# ---------------------------------------------------------------------------


def test_valid_node_manifest_has_no_errors() -> None:
    assert validate_manifest(_NODE_MANIFEST) == []


def test_node_manifest_missing_runtime_defaults_to_python() -> None:
    raw = {k: v for k, v in _NODE_MANIFEST.items() if k != "runtime"}
    # No runtime field → defaults to python → .js main fails
    errors = validate_manifest(raw)
    assert any("python runtime" in e for e in errors)


def test_node_manifest_with_py_main_fails() -> None:
    bad = {**_NODE_MANIFEST, "main": "extension.py"}
    errors = validate_manifest(bad)
    assert any("node runtime" in e and ".js" in e for e in errors)


def test_python_manifest_with_js_main_fails() -> None:
    bad = {**_PYTHON_MANIFEST, "main": "extension.js"}
    errors = validate_manifest(bad)
    assert any("python runtime" in e and ".py" in e for e in errors)


def test_unknown_runtime_fails() -> None:
    bad = {**_NODE_MANIFEST, "runtime": "ruby"}
    errors = validate_manifest(bad)
    assert any("runtime" in e and "ruby" in e for e in errors)


def test_runtime_field_is_not_required() -> None:
    raw = {k: v for k, v in _PYTHON_MANIFEST.items()}
    assert "runtime" not in raw
    assert validate_manifest(raw) == []


def test_node_runtime_handler_requires_main() -> None:
    no_main = {k: v for k, v in _NODE_MANIFEST.items() if k != "main"}
    errors = validate_manifest(no_main)
    assert any("main" in e for e in errors)


def test_node_runtime_handler_requires_ui_command_capability() -> None:
    bad = dict(_NODE_MANIFEST)
    bad["capabilities"] = ["editor.read", "ui.announce"]  # missing ui.command
    errors = validate_manifest(bad)
    assert any("ui.command" in e for e in errors)


def test_node_manifest_snippet_command_does_not_need_main() -> None:
    raw = {
        "schema": "quill.extension/1",
        "id": "com.example.nodesnip",
        "name": "Node Snip",
        "version": "1.0.0",
        "runtime": "node",
        "capabilities": [],
        "contributes": {
            "commands": [{"id": "ext.ns.snip", "title": "Snip", "run": {"snippet": "hello"}}]
        },
    }
    assert validate_manifest(raw) == []


# ---------------------------------------------------------------------------
# parse_manifest — node runtime round-trip
# ---------------------------------------------------------------------------


def test_parse_manifest_node_returns_correct_runtime() -> None:
    manifest = parse_manifest(_NODE_MANIFEST)
    assert manifest.runtime == RUNTIME_NODE
    assert manifest.is_node_runtime
    assert manifest.main == "extension.js"


def test_parse_manifest_python_default_runtime() -> None:
    manifest = parse_manifest(_PYTHON_MANIFEST)
    assert manifest.runtime == RUNTIME_PYTHON
    assert not manifest.is_node_runtime
    assert manifest.main == "extension.py"


def test_parse_manifest_missing_runtime_defaults_to_python() -> None:
    raw = {k: v for k, v in _PYTHON_MANIFEST.items()}
    assert "runtime" not in raw
    manifest = parse_manifest(raw)
    assert manifest.runtime == RUNTIME_PYTHON


# ---------------------------------------------------------------------------
# Schema agreement (lint_manifest_object uses both lenses)
# ---------------------------------------------------------------------------


def test_schema_accepts_node_manifest() -> None:
    errors = ql._schema_errors(_NODE_MANIFEST, ql.load_schema(), "$")
    assert errors == [], errors


def test_schema_rejects_node_manifest_with_py_main() -> None:
    bad = {**_NODE_MANIFEST, "main": "extension.py"}
    errors = ql._schema_errors(bad, ql.load_schema(), "$")
    assert errors, "expected schema to reject node runtime with .py main"


def test_schema_accepts_python_manifest_with_py_main() -> None:
    errors = ql._schema_errors(_PYTHON_MANIFEST, ql.load_schema(), "$")
    assert errors == [], errors


def test_schema_rejects_python_manifest_with_js_main() -> None:
    bad = {**_PYTHON_MANIFEST, "main": "extension.js"}
    errors = ql._schema_errors(bad, ql.load_schema(), "$")
    assert errors, "expected schema to reject python runtime with .js main"


def test_schema_rejects_unknown_runtime_value() -> None:
    bad = {**_NODE_MANIFEST, "runtime": "ruby"}
    errors = ql._schema_errors(bad, ql.load_schema(), "$")
    assert any("is not one of" in e or "ruby" in e for e in errors)


def test_lint_manifest_object_agrees_on_valid_node_manifest() -> None:
    assert ql.lint_manifest_object(_NODE_MANIFEST) == []


def test_lint_manifest_object_rejects_node_with_py_main() -> None:
    bad = {**_NODE_MANIFEST, "main": "extension.py"}
    assert ql.lint_manifest_object(bad) != []
