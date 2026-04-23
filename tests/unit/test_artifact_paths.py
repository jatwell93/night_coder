"""Tests for src/lib/artifact_paths.py."""

from __future__ import annotations

from pathlib import Path

import pytest

from lib import artifact_paths
from lib.artifact_paths import ArtifactPaths

VALID_RUN_ID = "run-20260423T143005Z-a1b2c3d4"
VALID_SCENARIO_ID = "SCN-PILOT-001-upstream-ok"


@pytest.fixture
def paths(tmp_path: Path) -> ArtifactPaths:
    return ArtifactPaths(root=tmp_path, run_id=VALID_RUN_ID)


class TestConstruction:
    def test_valid_run_id_accepted(self, tmp_path: Path) -> None:
        ap = ArtifactPaths(root=tmp_path, run_id=VALID_RUN_ID)
        assert ap.run_id == VALID_RUN_ID

    def test_run_id_with_path_separator_rejected(self, tmp_path: Path) -> None:
        with pytest.raises(ValueError, match="run_id"):
            ArtifactPaths(root=tmp_path, run_id="run/../etc")

    def test_run_id_with_traversal_rejected(self, tmp_path: Path) -> None:
        with pytest.raises(ValueError, match="run_id"):
            ArtifactPaths(root=tmp_path, run_id="..")

    def test_empty_run_id_rejected(self, tmp_path: Path) -> None:
        with pytest.raises(ValueError, match="run_id"):
            ArtifactPaths(root=tmp_path, run_id="")


class TestCanonicalLocations:
    def test_run_root(self, paths: ArtifactPaths, tmp_path: Path) -> None:
        assert paths.run_root == tmp_path / "runs" / VALID_RUN_ID

    def test_manifest(self, paths: ArtifactPaths) -> None:
        assert paths.manifest.name == "manifest.json"
        assert paths.manifest.parent == paths.run_root

    def test_events_log(self, paths: ArtifactPaths) -> None:
        assert paths.events_log == paths.run_root / "events.jsonl"

    def test_traces_dir(self, paths: ArtifactPaths) -> None:
        assert paths.traces_dir == paths.run_root / "traces"

    def test_logs_dir(self, paths: ArtifactPaths) -> None:
        assert paths.logs_dir == paths.run_root / "logs"


class TestPerScenarioLocations:
    def test_verdict_path(self, paths: ArtifactPaths) -> None:
        p = paths.verdict_for(VALID_SCENARIO_ID)
        assert p.parent == paths.run_root / "verdicts"
        assert p.name == f"{VALID_SCENARIO_ID}.json"

    def test_evidence_dir(self, paths: ArtifactPaths) -> None:
        p = paths.evidence_for(VALID_SCENARIO_ID)
        assert p == paths.run_root / "evidence" / VALID_SCENARIO_ID

    def test_scenario_id_traversal_rejected(self, paths: ArtifactPaths) -> None:
        with pytest.raises(ValueError, match="scenario_id"):
            paths.verdict_for("../../etc/passwd")

    def test_scenario_id_absolute_rejected(self, paths: ArtifactPaths) -> None:
        with pytest.raises(ValueError, match="scenario_id"):
            paths.evidence_for("/etc/passwd")

    def test_empty_scenario_id_rejected(self, paths: ArtifactPaths) -> None:
        with pytest.raises(ValueError, match="scenario_id"):
            paths.verdict_for("")


class TestEnsure:
    def test_ensure_run_tree_creates_all_subdirs(self, paths: ArtifactPaths) -> None:
        paths.ensure_run_tree()
        assert paths.run_root.is_dir()
        assert paths.traces_dir.is_dir()
        assert paths.logs_dir.is_dir()
        assert (paths.run_root / "verdicts").is_dir()
        assert (paths.run_root / "evidence").is_dir()

    def test_ensure_run_tree_idempotent(self, paths: ArtifactPaths) -> None:
        paths.ensure_run_tree()
        paths.ensure_run_tree()
        assert paths.run_root.is_dir()


class TestContainmentInvariant:
    def test_all_paths_are_under_root(self, paths: ArtifactPaths, tmp_path: Path) -> None:
        locations = [
            paths.run_root,
            paths.manifest,
            paths.events_log,
            paths.traces_dir,
            paths.logs_dir,
            paths.verdict_for(VALID_SCENARIO_ID),
            paths.evidence_for(VALID_SCENARIO_ID),
        ]
        root_resolved = tmp_path.resolve()
        for loc in locations:
            assert loc.resolve().is_relative_to(root_resolved), f"{loc} escapes root {tmp_path}"


class TestModuleHelper:
    def test_for_run_returns_artifact_paths(self, tmp_path: Path) -> None:
        ap = artifact_paths.for_run(tmp_path, VALID_RUN_ID)
        assert isinstance(ap, ArtifactPaths)
        assert ap.run_id == VALID_RUN_ID
