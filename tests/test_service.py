"""Tests for service.py: every intent, the fallback path and startup errors.

Owner: Member 7
"""

import logging

import pytest
from pydantic import ValidationError

from assistant_core.config import Settings
from assistant_core.errors import ConfigError, DataError
from assistant_core.models import Intent, Message, Response
from assistant_core.responder import StubLLMResponder
from assistant_core.service import AssistantService, build_service


def ask(service: AssistantService, text: str) -> Response:
    return service.handle(Message(text=text))


def test_greeting(service: AssistantService) -> None:
    r = ask(service, "hi")
    assert r.intent is Intent.GREETING
    assert r.answer == "Hello! I can help with offices, fees and rules."
    assert r.sources == []
    assert not r.degraded


def test_fee_matches_monolith(service: AssistantService) -> None:
    """Characterisation test: the monolith gave 9450000 for 18 credits and 2 retake."""
    r = ask(service, "tuition for 18 credits and 2 retake")
    assert r.intent is Intent.FEE
    assert r.answer == "Your tuition is 9,450,000 VND."


def test_fee_over_limit_gives_friendly_answer(service: AssistantService) -> None:
    r = ask(service, "tuition for 31 credits")
    assert r.intent is Intent.FEE
    assert "between 1 and 30" in r.answer


def test_fee_without_credits_asks_back(service: AssistantService) -> None:
    r = ask(service, "how much is the tuition")
    assert r.intent is Intent.FEE
    assert r.answer == "How many credits?"


def test_library_matches_monolith(service: AssistantService) -> None:
    r = ask(service, "where is the library")
    assert r.intent is Intent.OFFICE
    assert r.answer == "Library: room B.201, open Mon-Sat 07:00-20:00."


@pytest.mark.parametrize(
    ("question", "room"),
    [
        ("training office hours", "I.101"),
        ("student affairs", "I.102"),
        ("it helpdesk", "E.005"),
    ],
)
def test_other_offices(service: AssistantService, question: str, room: str) -> None:
    r = ask(service, question)
    assert r.intent is Intent.OFFICE
    assert f"room {room}" in r.answer


def test_rule_answer_has_source(service: AssistantService) -> None:
    r = ask(service, "can I register my thesis with 118 credits")
    assert r.intent is Intent.RULE
    assert [s.id for s in r.sources] == ["H26-5.3"]
    assert not r.degraded


def test_unknown_question(service: AssistantService) -> None:
    r = ask(service, "zzzz qqqq")
    assert r.intent is Intent.UNKNOWN
    assert r.sources == []


def test_fallback_when_provider_fails(service: AssistantService, caplog: pytest.LogCaptureFixture) -> None:
    service.responder = StubLLMResponder(fail=True)
    with caplog.at_level(logging.WARNING, logger="assistant_core"):
        r = ask(service, "thesis registration credits")
    assert r.degraded
    assert r.sources
    assert r.answer.startswith("Thesis registration:")  # template format, not the stub's "Based on"
    assert any("fallback" in rec.getMessage() for rec in caplog.records)


@pytest.mark.parametrize("text", ["", "x" * 2001])
def test_invalid_message_is_rejected(text: str) -> None:
    with pytest.raises(ValidationError):
        Message(text=text)


def test_log_has_metadata_but_not_user_text(service: AssistantService, caplog: pytest.LogCaptureFixture) -> None:
    with caplog.at_level(logging.INFO, logger="assistant_core"):
        ask(service, "thesis registration credits")
    record = next(rec for rec in caplog.records if rec.getMessage() == "handled")
    assert record.intent == "rule"
    assert record.degraded is False
    assert "thesis" not in str(vars(record))


def test_missing_data_dir_raises_data_error(tmp_path) -> None:
    with pytest.raises(DataError):
        build_service(Settings(data_dir=tmp_path))


def test_unknown_provider_raises_config_error(settings: Settings) -> None:
    with pytest.raises(ConfigError):
        build_service(settings.model_copy(update={"llm_provider": "openai"}))
