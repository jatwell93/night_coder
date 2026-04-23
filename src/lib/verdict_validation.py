"""Validate judge verdicts against the project's JSON Schema contract.

Mirrors :mod:`lib.manifest_validation` but for
``specs/001-overnight-vps-system/contracts/judge-verdict.schema.json``.
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
    "VerdictValidationError",
    "is_valid_verdict",
    "validate_verdict",
]

_REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SCHEMA_PATH = (
    _REPO_ROOT / "specs" / "001-overnight-vps-system" / "contracts" / "judge-verdict.schema.json"
)
_SCHEMA_PATH_ENV = "NIGHT_CODER_VERDICT_SCHEMA"


class VerdictValidationError(ValueError):
    """Raised when a judge verdict fails schema validation."""


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


def validate_verdict(data: dict[str, Any], *, schema_path: Path | None = None) -> None:
    """Validate ``data`` against the judge verdict schema.

    Raises
    ------
    VerdictValidationError
        If the verdict violates the schema.
    """
    validator = _load_validator(_resolve_schema_path(schema_path))
    errors = sorted(validator.iter_errors(data), key=lambda e: list(e.absolute_path))
    if not errors:
        return
    first = errors[0]
    path = "/".join(str(p) for p in first.absolute_path) or "<root>"
    msg = f"Verdict invalid at {path}: {first.message}"
    raise VerdictValidationError(msg) from first


def is_valid_verdict(data: dict[str, Any], *, schema_path: Path | None = None) -> bool:
    """Return ``True`` if ``data`` passes validation, ``False`` otherwise."""
    try:
        validate_verdict(data, schema_path=schema_path)
    except (VerdictValidationError, jsonschema.SchemaError):
        return False
    return True
