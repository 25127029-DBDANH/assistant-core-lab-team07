from pathlib import Path

import httpx

from ui.api_client import AssistantClient, ChatResult
from ui.logic import format_sources, status_note, validate_input

OK = {
    "answer": "Room B.201",
    "intent": "office",
    "sources": [{"id": "S26#1", "title": "1 Library borrowing"}],
    "degraded": False,
    "escalate": False,
    "path": "deterministic",
    "request_id": "abc123",
}


def client_with(handler) -> AssistantClient:
    return AssistantClient("http://api.test", transport=httpx.MockTransport(handler))


def test_ask_ok():
    r = client_with(lambda req: httpx.Response(200, json=OK)).ask("where is the library", "s1")
    assert r.ok and r.answer == "Room B.201" and r.request_id == "abc123"


def test_ask_backend_down():
    def boom(req):
        raise httpx.ConnectError("refused", request=req)

    r = client_with(boom).ask("hi", "s1")
    assert not r.ok and "backend" in r.error


def test_ask_validation_and_server_errors():
    assert "type a question" in client_with(lambda req: httpx.Response(422)).ask("", "s").error
    assert "error 500" in client_with(lambda req: httpx.Response(500)).ask("x", "s").error


def test_feedback():
    assert client_with(lambda req: httpx.Response(201, json={})).send_feedback("abc123", 1)


def test_negative_feedback():
    recorded = []

    def handle(req):
        recorded.append(httpx.Response(201, json={"status": "ok"}))
        return recorded[-1]

    client = client_with(handle)
    assert client.send_feedback("req_f1_test", -1)


def test_ui_negative_feedback_button(monkeypatch):
    from streamlit.testing.v1 import AppTest

    recorded = []
    monkeypatch.setattr(
        AssistantClient, "send_feedback", lambda self, rid, rating: recorded.append((rid, rating)) or True
    )
    monkeypatch.setattr(AssistantClient, "healthy", lambda self: True)

    app_file = Path(__file__).resolve().parents[1] / "ui" / "app.py"
    at = AppTest.from_file(str(app_file))
    at.run()
    at.session_state.messages.append(
        {
            "role": "assistant",
            "content": "Test answer",
            "request_id": "test_req_f1",
        }
    )
    at.run()

    down = [b for b in at.button if b.label == "👎"]
    assert len(down) == 1
    down[0].click().run()

    assert recorded == [("test_req_f1", -1)]
    assert "test_req_f1" in at.session_state.rated
    at.run()
    assert len([b for b in at.button if b.label in ("👍", "👎")]) == 0


def test_validate_input():
    assert validate_input("   ") == "Please type a question."
    assert validate_input("x" * 2001).startswith("Your question is too long")
    assert validate_input("hello") is None


# ── L1: format_sources (implemented in Issue #70) ────────────────────────────
def test_format_sources():
    assert format_sources([]) == ""
    assert format_sources(OK["sources"]) == "Sources: S26#1 \u2014 1 Library borrowing"


def test_format_sources_multiple():
    sources = [
        {"id": "H26#5.3", "title": "5.3 Thesis registration"},
        {"id": "H26#6.1", "title": "6.1 Credit load"},
    ]
    result = format_sources(sources)
    assert result.startswith("Sources: ")
    assert "H26#5.3" in result
    assert "H26#6.1" in result
    assert "; " in result  # multiple sources separated by semicolon


# ── L2: status_note (implemented in Issue #70) ───────────────────────────────
def test_status_note():
    assert "Training Office" in status_note(ChatResult(ok=True, escalate=True))
    assert status_note(ChatResult(ok=True)) is None


def test_status_note_degraded():
    note = status_note(ChatResult(ok=True, degraded=True))
    assert note is not None
    assert "source document" in note


def test_status_note_normal():
    assert status_note(ChatResult(ok=True, escalate=False, degraded=False)) is None
