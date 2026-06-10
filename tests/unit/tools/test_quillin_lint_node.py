"""Tests for quillin_lint with Node.js runtime manifests.

Verifies that the linter accepts valid node runtime Quillins, checks that
the declared .js main file exists, rejects mismatched runtimes/extensions,
and that the bundled word-count-node example passes strict lint.
"""

from __future__ import annotations

import json
from pathlib import Path

from quill.tools import quillin_lint as ql

_NODE_MANIFEST = {
    "schema": "quill.extension/1",
    "id": "com.example.nodeext",
    "name": "Node Ext",
    "version": "1.0.0",
    "author": "Example Author",
    "description": "A node Quillin example.",
    "license": "MIT",
    "runtime": "node",
    "capabilities": ["editor.read", "ui.announce", "ui.command"],
    "main": "extension.js",
    "contributes": {
        "commands": [{"id": "ext.ne.go", "title": "Go", "run": {"handler": "go"}}],
        "menus": [{"parent": "Tools", "command": "ext.ne.go"}],
    },
}


def _write_node_quillin(
    directory: Path,
    manifest: object = _NODE_MANIFEST,
    *,
    with_main: bool = True,
) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "manifest.json").write_text(
        json.dumps(manifest) if not isinstance(manifest, str) else manifest,
        encoding="utf-8",
    )
    if with_main:
        js = "'use strict';\nprocess.stdout.write(JSON.stringify({result:null,actions:[]})"
        js += "+'\\n');\n"
        (directory / "extension.js").write_text(js, encoding="utf-8")
        (directory / "README.md").write_text("# Node Ext\n", encoding="utf-8")
        (directory / "LICENSE").write_text("MIT\n", encoding="utf-8")
    return directory


# ---------------------------------------------------------------------------
# Schema lens
# ---------------------------------------------------------------------------


def test_schema_accepts_node_runtime_manifest() -> None:
    errors = ql._schema_errors(_NODE_MANIFEST, ql.load_schema(), "$")
    assert errors == [], errors


def test_schema_rejects_node_with_py_main() -> None:
    bad = {**_NODE_MANIFEST, "main": "extension.py"}
    errors = ql._schema_errors(bad, ql.load_schema(), "$")
    assert errors, "expected error for node runtime with .py main"


def test_schema_rejects_unknown_runtime() -> None:
    bad = {**_NODE_MANIFEST, "runtime": "ruby"}
    errors = ql._schema_errors(bad, ql.load_schema(), "$")
    assert errors


def test_lint_manifest_object_passes_for_node() -> None:
    assert ql.lint_manifest_object(_NODE_MANIFEST) == []


# ---------------------------------------------------------------------------
# Directory lint
# ---------------------------------------------------------------------------


def test_node_quillin_directory_passes_strict(tmp_path: Path) -> None:
    directory = _write_node_quillin(tmp_path / "nodeext")
    report = ql.lint_quillin(directory)
    assert report.ok(strict=True), report.render(strict=True)


def test_node_quillin_missing_js_main_is_error(tmp_path: Path) -> None:
    directory = _write_node_quillin(tmp_path / "nodeext", with_main=False)
    (directory / "README.md").write_text("# Node Ext\n", encoding="utf-8")
    report = ql.lint_quillin(directory)
    errors = [p for p in report.errors if "does not exist" in p.message]
    assert errors, "expected error for missing .js main"


def test_node_quillin_directory_without_readme_warns(tmp_path: Path) -> None:
    directory = tmp_path / "nodeext"
    directory.mkdir()
    (directory / "manifest.json").write_text(json.dumps(_NODE_MANIFEST), encoding="utf-8")
    (directory / "extension.js").write_text("'use strict';\n", encoding="utf-8")
    report = ql.lint_quillin(directory)
    assert report.ok()  # warnings only, not errors
    assert not report.ok(strict=True)
    assert any("README" in w.message for w in report.warnings)


def test_node_quillin_with_js_main_path_traversal_is_error(tmp_path: Path) -> None:
    bad_manifest = {**_NODE_MANIFEST, "main": "../outside.js"}
    directory = tmp_path / "nodeext"
    directory.mkdir()
    (directory / "manifest.json").write_text(json.dumps(bad_manifest), encoding="utf-8")
    report = ql.lint_quillin(directory)
    # Should report a schema or manifest error for the relative path issue
    assert not report.ok()


# ---------------------------------------------------------------------------
# Bundled word-count-node
# ---------------------------------------------------------------------------


def test_bundled_word_count_node_passes_strict_lint() -> None:
    bundled = ql._REPO_ROOT / "quill" / "quillins_bundled" / "word-count-node"
    if not bundled.is_dir():
        import pytest

        pytest.skip("word-count-node bundled Quillin not found")
    report = ql.lint_quillin(bundled)
    assert report.ok(strict=True), report.render(strict=True)


def test_bundled_word_count_node_manifest_schema_valid() -> None:
    bundled = ql._REPO_ROOT / "quill" / "quillins_bundled" / "word-count-node"
    if not bundled.is_dir():
        import pytest

        pytest.skip("word-count-node bundled Quillin not found")
    import json

    manifest = json.loads((bundled / "manifest.json").read_text(encoding="utf-8"))
    assert manifest.get("runtime") == "node"
    assert manifest.get("main", "").endswith(".js")
    errors = ql._schema_errors(manifest, ql.load_schema(), "$")
    assert errors == [], errors


def test_bundled_word_count_node_main_js_exists() -> None:
    bundled = ql._REPO_ROOT / "quill" / "quillins_bundled" / "word-count-node"
    if not bundled.is_dir():
        import pytest

        pytest.skip("word-count-node bundled Quillin not found")
    import json

    manifest = json.loads((bundled / "manifest.json").read_text(encoding="utf-8"))
    main = manifest.get("main", "")
    assert (bundled / main).is_file(), f"{main} not found in word-count-node"
