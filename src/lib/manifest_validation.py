"""Validate run manifests against the project's JSON Schema contract.

The canonical schema lives outside the package at
``specs/001-overnight-vps-system/contracts/run-manifest.schema.json`` — it is
the single source of truth shared with reviewers and downstream consumers.

This module keeps the schema external (rather than duplicating it under
``src/``) so contract changes land in one place and are visible to anyone
reading the spec.
"""

from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Any

import jsonschema
from jsonschema import Draft202012Validator, FormatChecker

__all__ = [
    "DEFAULT_SCHEMA_PATH",
    "ManifestValidationError",
    "is_valid_manifest",
    "validate_manifest",
]

_REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SCHEMA_PATH = (
    _REPO_ROOT / "specs" / "001-overnight-vps-system" / "contracts" / "run-manifest.schema.json"
)
_SCHEMA_PATH_ENV = "NIGHT_CODER_MANIFEST_SCHEMA"


class ManifestValidationError(ValueError):
    """Raised when a run manifest fails schema validation.

    The message includes the JSON-pointer path of the failing field so
    operators can jump directly to the offending value.
    """


def _resolve_schema_path(override: Path | None = None) -> Path:
    if override is not None:
        return override
    env_override = os.environ.get(_SCHEMA_PATH_ENV)
    if env_override:
        return Path(env_override)
    return DEFAULT_SCHEMA_PATH


@lru_cache(maxsize=8)
def _load_validator(schema_path: Path) -> Draft202012Validator:
    with schema_path.open("r", encoding="utf-8") as fh:
        schema = json.load(fh)
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema, format_checker=FormatChecker())


def validate_manifest(data: dict[str, Any], *, schema_path: Path | None = None) -> None:
    """Validate ``data`` against the run manifest schema.

    Parameters
    ----------
    data:
        The manifest dictionary (already deserialised from JSON).
    schema_path:
        Optional schema file override. Defaults to :data:`DEFAULT_SCHEMA_PATH`,
        or the ``NIGHT_CODER_MANIFEST_SCHEMA`` environment variable when set.

    Raises
    ------
    ManifestValidationError
        If the manifest violates the schema. The exception message includes the
        path of the first failing field.
    """
    validator = _load_validator(_resolve_schema_path(schema_path))
    errors = sorted(validator.iter_errors(data), key=lambda e: list(e.absolute_path))
    if not errors:
        return
    first = errors[0]
    path = "/".join(str(p) for p in first.absolute_path) or "<root>"
    msg = f"Manifest invalid at {path}: {first.message}"
    raise ManifestValidationError(msg) from first


def is_valid_manifest(data: dict[str, Any], *, schema_path: Path | None = None) -> bool:
    """Return ``True`` if ``data`` passes validation, ``False`` otherwise."""
    try:
        validate_manifest(data, schema_path=schema_path)
    except (ManifestValidationError, jsonschema.SchemaError):
        return False
    return True
