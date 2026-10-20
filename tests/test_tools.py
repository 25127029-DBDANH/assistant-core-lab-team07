"""Tests for tools.py (parse_credits, tuition, characterisation test).

Owner: Member 4
"""

import pytest

from assistant_core.errors import InvalidRequest
from assistant_core.tools import parse_credits, tuition


def test_parse_with_retake() -> None:
    """Test parsing input with both credits and retake credits."""
    assert parse_credits("tuition for 18 credits and 2 retake") == (18, 2)


def test_parse_without_retake() -> None:
    """Test parsing input with credits only (no retake specified)."""
    assert parse_credits("tuition for 18 credits") == (18, 0)


def test_parse_missing_credits() -> None:
    """Test parsing input without any credit count raises InvalidRequest."""
    with pytest.raises(InvalidRequest, match="How many credits?"):
        parse_credits("how much is tuition")


def test_tuition_value() -> None:
    """Characterisation test: locks in monolith tuition calculation behavior."""
    assert tuition(18, 2, 450_000, 1.5, 30) == 9_450_000


def test_tuition_without_retake() -> None:
    """Test tuition calculation when retake credits is zero."""
    assert tuition(18, 0, 450_000, 1.5, 30) == 8_100_000


@pytest.mark.parametrize("credits", [0, 31, -1, -10])
def test_tuition_out_of_range(credits: int) -> None:
    """Test that tuition raises InvalidRequest for credits out of [1, max_credits]."""
    with pytest.raises(InvalidRequest, match=r"Credits must be between 1 and 30\."):
        tuition(credits, 0, 450_000, 1.5, 30)


def test_tuition_boundary_valid() -> None:
    """Test boundary credit values 1 and max_credits (30) are both valid."""
    assert tuition(1, 0, 450_000, 1.5, 30) == 450_000
    assert tuition(30, 0, 450_000, 1.5, 30) == 13_500_000
