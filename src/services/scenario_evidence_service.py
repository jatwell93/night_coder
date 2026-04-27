"""Scenario evidence assembler (T028)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ScenarioEvidence:
    scenario_id: str
    expected_outcome: str
    observed_outcome: str
    evidence_refs: tuple[str, ...]


def assemble_scenario_evidence(
    *,
    scenario_id: str,
    expected_outcome: str,
    observed_outcome: str,
    evidence_refs: list[str],
) -> ScenarioEvidence:
    if not evidence_refs:
        msg = "evidence_refs must not be empty"
        raise ValueError(msg)
    return ScenarioEvidence(
        scenario_id=scenario_id,
        expected_outcome=expected_outcome,
        observed_outcome=observed_outcome,
        evidence_refs=tuple(evidence_refs),
    )
