"""T068 [US3] integration test for DTU startup failure classification."""

from __future__ import annotations

import pytest

from services.dtu_health_service import classify_dtu_startup_failure


@pytest.mark.integration
@pytest.mark.us3
def test_dtu_startup_failure_is_classified_as_infrastructure_failure() -> None:
    classification = classify_dtu_startup_failure(
        dependency_name="wiremock",
        error_message="container failed to start: port binding error",
    )

    assert classification.status == "failed"
    assert classification.reason_code == "DTU.error.startup-failure"
