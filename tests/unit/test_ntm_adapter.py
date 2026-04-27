"""Tests for NTM adapter wiring (T080)."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from services.ntm_adapter import NtmAdapterError, assert_ntm_available


def test_assert_ntm_available_raises_when_missing() -> None:
    with (
        patch("services.ntm_adapter.shutil.which", return_value=None),
        pytest.raises(NtmAdapterError, match="ntm"),
    ):
        assert_ntm_available()


def test_assert_ntm_available_passes_when_present() -> None:
    with patch("services.ntm_adapter.shutil.which", return_value="/usr/bin/ntm"):
        assert_ntm_available()
