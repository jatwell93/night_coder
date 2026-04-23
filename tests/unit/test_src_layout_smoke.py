"""Smoke test: src/ pythonpath wiring and package layout.

Verifies that ``pyproject.toml``'s ``[tool.pytest.ini_options].pythonpath = ["src"]``
setting is active, so tests can import from ``src/lib``, ``src/services``, and
``src/cli`` without additional setup. If this fails, every downstream Phase 2+
test will also fail — fix packaging before touching anything else.
"""

from __future__ import annotations


def test_lib_importable() -> None:
    import lib

    assert lib.__doc__ is not None


def test_services_importable() -> None:
    import services

    assert services.__doc__ is not None


def test_cli_importable() -> None:
    import cli

    assert cli.__doc__ is not None
