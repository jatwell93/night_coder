"""T017 [US1] integration tests for offline/online profile enforcement."""

from __future__ import annotations

import pytest

from services.run_profile_service import profile_allows_command


@pytest.mark.integration
@pytest.mark.us1
def test_offline_profile_blocks_network_egress() -> None:
    assert not profile_allows_command("offline", "curl https://example.com")


@pytest.mark.integration
@pytest.mark.us1
def test_online_profile_allows_network_egress() -> None:
    assert profile_allows_command("online", "curl https://example.com")


@pytest.mark.integration
@pytest.mark.us1
def test_unknown_profile_rejected() -> None:
    with pytest.raises(ValueError, match="Unknown profile"):
        profile_allows_command("staging", "echo ok")
