"""JSON schemas for the verbosity data files (verbosity §20, §30, §35).

These are the data contracts the later sub-PRs validate against: the persisted
verbosity settings, the custom-profile store, a QUILL Verbosity Pack (``.qvp.json``),
and an exported/imported profile. They are plain draft-07 schema dicts so the
QVP loader (sub-PR 1.3) and storage layer (sub-PR 1.2) can validate without any
code execution — QVP files are strictly data.

Pure and wx-free.
"""

from __future__ import annotations

from typing import Any

__all__ = [
    "VERBOSITY_SETTINGS_SCHEMA",
    "CUSTOM_PROFILE_SCHEMA",
    "QVP_SCHEMA",
    "PROFILE_IO_SCHEMA",
    "SCHEMAS",
    "schema_for",
]

_CHANNEL_NAMES = ["SPEECH", "BRAILLE", "SOUND", "VISUAL"]
_PROFILE_NAMES = ["Beginner", "Normal", "Expert", "Quiet"]

VERBOSITY_SETTINGS_SCHEMA: dict[str, Any] = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "QUILL verbosity settings",
    "type": "object",
    "properties": {
        "profile": {"type": "string", "enum": _PROFILE_NAMES},
        "channels": {
            "type": "array",
            "items": {"type": "string", "enum": _CHANNEL_NAMES},
            "uniqueItems": True,
        },
        "validation_timing": {"type": "string", "enum": ["live", "on_focus", "on_button"]},
        "quiet_mode": {"type": "boolean"},
        "meeting_mode": {"type": "boolean"},
    },
    "additionalProperties": True,
}

CUSTOM_PROFILE_SCHEMA: dict[str, Any] = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "QUILL custom verbosity profile",
    "type": "object",
    "required": ["name"],
    "properties": {
        "name": {"type": "string", "minLength": 1},
        "base": {"type": "string", "enum": _PROFILE_NAMES},
        "channels": {
            "type": "array",
            "items": {"type": "string", "enum": _CHANNEL_NAMES},
            "uniqueItems": True,
        },
        "per_verb_overrides": {"type": "object", "additionalProperties": {"type": "string"}},
        "per_chord_overrides": {"type": "object", "additionalProperties": {"type": "string"}},
        "templates": {"type": "object", "additionalProperties": {"type": "string"}},
        "data_order": {
            "type": "object",
            "additionalProperties": {"type": "array", "items": {"type": "string"}},
        },
    },
    "additionalProperties": False,
}

QVP_SCHEMA: dict[str, Any] = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "QUILL Verbosity Pack",
    "type": "object",
    "required": ["name", "author", "description", "version", "license", "templates"],
    "properties": {
        "name": {"type": "string", "minLength": 1},
        "author": {"type": "string", "minLength": 1},
        "description": {"type": "string"},
        "version": {"type": "string", "minLength": 1},
        "license": {"type": "string", "minLength": 1},
        "min_quill_version": {"type": "string"},
        "preview": {"type": "string"},
        "tags": {"type": "array", "items": {"type": "string"}},
        "dependencies": {"type": "array", "items": {"type": "string"}},
        "templates": {
            "type": "object",
            "additionalProperties": {"type": "string"},
        },
    },
    "additionalProperties": False,
}

PROFILE_IO_SCHEMA: dict[str, Any] = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "QUILL verbosity profile import/export",
    "type": "object",
    "required": ["format", "profile"],
    "properties": {
        "format": {"const": "quill-verbosity-profile"},
        "version": {"type": "string"},
        "profile": CUSTOM_PROFILE_SCHEMA,
    },
    "additionalProperties": False,
}

#: Schemas keyed by short name.
SCHEMAS: dict[str, dict[str, Any]] = {
    "settings": VERBOSITY_SETTINGS_SCHEMA,
    "custom_profile": CUSTOM_PROFILE_SCHEMA,
    "qvp": QVP_SCHEMA,
    "profile_io": PROFILE_IO_SCHEMA,
}


def schema_for(name: str) -> dict[str, Any]:
    """Return the schema registered under ``name`` (raises ``KeyError`` if unknown)."""
    return SCHEMAS[name]
