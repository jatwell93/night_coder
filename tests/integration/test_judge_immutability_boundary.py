"""T026 [US2] integration test for immutable judge harness boundary."""

from __future__ import annotations

from pathlib import Path

import pytest

from services.judge_harness_guard_service import assert_harness_path_is_immutable


@pytest.mark.integration
@pytest.mark.us2
def test_harness_inside_repo_is_rejected(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    harness = repo_root / "docs" / "superpowers" / "pilot" / "judge"
    harness.mkdir(parents=True)
    with pytest.raises(ValueError, match="outside"):
        assert_harness_path_is_immutable(harness_path=harness, repo_root=repo_root)


@pytest.mark.integration
@pytest.mark.us2
def test_external_harness_path_is_accepted(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    harness = tmp_path / "external-judge-harness"
    harness.mkdir()
    assert_harness_path_is_immutable(harness_path=harness, repo_root=repo_root)
