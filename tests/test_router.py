"""Tests for router.py (one test per intent).

Owner: Member 6
"""

from assistant_core.models import Intent
from assistant_core.router import route


def test_route_greeting() -> None:
    offices = {"library", "training office"}
    assert route("hi", offices) is Intent.GREETING
    assert route("hello", offices) is Intent.GREETING
    assert route("hey", offices) is Intent.GREETING
    assert route("xin chao", offices) is Intent.GREETING
    assert route("Hello!", offices) is Intent.GREETING
    assert route("Hey?", offices) is Intent.GREETING
    assert route("  xin chao...  ", offices) is Intent.GREETING


def test_route_fee() -> None:
    offices = {"library", "training office"}
    assert route("tuition for 18 credits and 2 retake", offices) is Intent.FEE
    assert route("how much is the tuition?", offices) is Intent.FEE
    assert route("what is the fee?", offices) is Intent.FEE
    assert route("late fee policy", offices) is Intent.FEE


def test_route_office() -> None:
    offices = {"library", "training office", "student affairs"}
    assert route("where is the library?", offices) is Intent.OFFICE
    assert route("training office opening hours", offices) is Intent.OFFICE
    assert route("find student affairs", offices) is Intent.OFFICE
    assert route("Where is the Library?", {"Library"}) is Intent.OFFICE


def test_route_rule() -> None:
    offices = {"library", "training office"}
    assert route("thesis registration credits", offices) is Intent.RULE
    assert route("what is the maximum study duration?", offices) is Intent.RULE
    assert route("exam regulations and retake policy", offices) is Intent.RULE
    assert route("how to graduate with honors", offices) is Intent.RULE
