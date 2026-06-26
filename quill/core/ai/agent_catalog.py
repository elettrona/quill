"""Declarative Agent Catalog: validate + load agent files into ``AgentSpec`` (PRD §13).

QUILL ships no ``jsonschema`` runtime dependency, so the contract published at
``quill/core/schemas/agent.json`` is enforced here in pure, strictly-typed Python
— the same hand-rolled-validator style used by the Quillin manifest, QVP, and
sound-pack stores. Tests assert this module and the JSON schema agree.

This is wx-free core and additive: it loads bundled agent specs from
``quill/core/ai/agents/`` (and any extra directories, e.g. user-installed or
Quillin-contributed) into :class:`~quill.core.ai.harness.AgentSpec` objects the AI
Hub lists and any harness can run. Nothing in the shipping UI lists them yet, so
adding the catalog changes no user-facing behavior.

Public API:

* :func:`validate_agent` — return a list of human-readable problems (empty when
  valid). Never raises for malformed data.
* :func:`parse_agent` — build an :class:`AgentSpec`, or raise
  :class:`AgentSpecError` carrying every problem found.
* :func:`load_catalog` — load every ``*.json`` agent file under the given
  directories, returning a :class:`CatalogLoadResult` (valid specs + per-file
  errors); a bad file never aborts the load.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

from quill.core.ai.context_builder import ContextScope
from quill.core.ai.harness import AgentSpec
from quill.core.ai.permissions import Decision, PermissionCategory, RiskLevel

__all__ = [
    "SCHEMA_ID",
    "AgentSpecError",
    "CatalogLoadResult",
    "validate_agent",
    "parse_agent",
    "bundled_agents_dir",
    "load_catalog",
]

SCHEMA_ID = "quill.agent/1"

_ID_PATTERN = re.compile(r"^[a-z0-9]+([._-][a-z0-9]+)*$")
_REQUIRED = ("schema", "id", "display_name", "system_prompt")
_ALLOWED_KEYS = {
    "schema",
    "id",
    "display_name",
    "description",
    "system_prompt",
    "risk",
    "default_scope",
    "recommended_file_types",
    "default_harness",
    "tools",
    "permissions",
}


class AgentSpecError(ValueError):
    """Raised by :func:`parse_agent` for an invalid agent file; lists all problems."""

    def __init__(self, problems: list[str]) -> None:
        self.problems = problems
        super().__init__("; ".join(problems))


@dataclass(frozen=True, slots=True)
class CatalogLoadResult:
    """Outcome of loading a catalog directory tree."""

    agents: tuple[AgentSpec, ...] = ()
    errors: tuple[tuple[str, str], ...] = ()  # (file path, problem)

    def ids(self) -> list[str]:
        return [a.id for a in self.agents]


def validate_agent(data: object) -> list[str]:
    """Return a list of problems with ``data`` (empty when it is a valid spec)."""
    problems: list[str] = []
    if not isinstance(data, dict):
        return ["Agent spec must be a JSON object."]

    unknown = sorted(set(data) - _ALLOWED_KEYS)
    if unknown:
        problems.append(f"Unknown key(s): {', '.join(unknown)}.")

    for key in _REQUIRED:
        if not data.get(key):
            problems.append(f"Missing required key: {key}.")

    if data.get("schema") not in (None, SCHEMA_ID) and "schema" in data:
        problems.append(f"schema must be {SCHEMA_ID!r}.")

    agent_id = data.get("id")
    if isinstance(agent_id, str) and agent_id and not _ID_PATTERN.match(agent_id):
        problems.append(f"id {agent_id!r} must be lowercase dotted/dashed segments.")

    for str_key in ("display_name", "system_prompt", "description", "default_harness"):
        if str_key in data and not isinstance(data[str_key], str):
            problems.append(f"{str_key} must be a string.")

    risk = data.get("risk")
    if risk is not None and risk not in _enum_values(RiskLevel):
        problems.append(f"risk {risk!r} is not one of {sorted(_enum_values(RiskLevel))}.")

    scope = data.get("default_scope")
    if scope is not None and scope not in _enum_values(ContextScope):
        problems.append(f"default_scope {scope!r} is not a known context scope.")

    for list_key in ("recommended_file_types", "tools"):
        if list_key in data:
            value = data[list_key]
            if not isinstance(value, list) or not all(isinstance(v, str) for v in value):
                problems.append(f"{list_key} must be a list of strings.")

    perms = data.get("permissions")
    if perms is not None:
        if not isinstance(perms, dict):
            problems.append("permissions must be an object.")
        else:
            for cat, decision in perms.items():
                if cat not in _enum_values(PermissionCategory):
                    problems.append(f"permissions: unknown category {cat!r}.")
                if decision not in _enum_values(Decision):
                    problems.append(f"permissions[{cat!r}]: unknown decision {decision!r}.")

    return problems


def parse_agent(data: object) -> AgentSpec:
    """Build an :class:`AgentSpec` from ``data``, or raise :class:`AgentSpecError`."""
    problems = validate_agent(data)
    if problems:
        raise AgentSpecError(problems)
    assert isinstance(data, dict)  # validate_agent guarantees this

    overrides: tuple[tuple[PermissionCategory, Decision], ...] = tuple(
        (PermissionCategory(cat), Decision(dec))
        for cat, dec in dict(data.get("permissions", {})).items()
    )
    return AgentSpec(
        id=str(data["id"]),
        display_name=str(data["display_name"]),
        system_prompt=str(data["system_prompt"]),
        description=str(data.get("description", "")),
        risk=RiskLevel(data["risk"]) if data.get("risk") else RiskLevel.LOW,
        default_scope=(
            ContextScope(data["default_scope"])
            if data.get("default_scope")
            else ContextScope.SELECTION
        ),
        recommended_file_types=tuple(data.get("recommended_file_types", []) or ()),
        default_harness=str(data.get("default_harness", "auto")),
        tools=tuple(data.get("tools", []) or ()),
        permission_overrides=overrides,
    )


def bundled_agents_dir() -> Path:
    """The directory holding QUILL's built-in agent spec files."""
    return Path(__file__).resolve().parent / "agents"


def load_catalog(*dirs: Path) -> CatalogLoadResult:
    """Load every ``*.json`` agent file under ``dirs`` (default: the bundled dir).

    A malformed or duplicate file is recorded in ``errors`` and skipped; it never
    aborts the load. Later directories override earlier ids (user/extension agents
    can shadow bundled ones).
    """
    search = list(dirs) or [bundled_agents_dir()]
    specs: dict[str, AgentSpec] = {}
    errors: list[tuple[str, str]] = []

    for directory in search:
        if not directory.is_dir():
            continue
        for path in sorted(directory.glob("*.json")):
            try:
                raw = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, ValueError) as exc:
                errors.append((str(path), f"Could not read/parse: {exc}"))
                continue
            problems = validate_agent(raw)
            if problems:
                errors.extend((str(path), p) for p in problems)
                continue
            spec = parse_agent(raw)
            specs[spec.id] = spec

    return CatalogLoadResult(agents=tuple(specs.values()), errors=tuple(errors))


def _enum_values(enum_cls: type) -> set[str]:
    return {member.value for member in enum_cls}  # type: ignore[attr-defined]
