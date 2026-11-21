"""UI logic without Streamlit, so it can be unit-tested."""

from __future__ import annotations

from ui.api_client import ChatResult

WELCOME = (
    "Hi! I can answer questions about fees, offices and the student handbook. "
    "Try: \u201cCan I register my thesis with 118 credits?\u201d"
)
EXAMPLES = [
    "Can I register my thesis with 118 credits?",
    "Tuition for 18 credits and 2 retake",
    "Where is the library?",
    "I lost my student card",
]


def validate_input(text: str) -> str | None:
    """Return an error message for bad input, or None if it is fine."""
    t = text.strip()
    if not t:
        return "Please type a question."
    if len(t) > 2000:
        return "Your question is too long (max 2000 characters)."
    return None


def format_sources(sources: list[dict]) -> str:
    """'Sources: H26#5.3 \u2014 5.3 Thesis registration' or '' if none.

    Each source dict has keys 'id' and 'title' (from the API schema).
    Returns an empty string when sources is empty so the caller can do
    ``if formatted_sources:`` without special-casing.
    """
    if not sources:
        return ""
    return "Sources: " + "; ".join(f"{s['id']} \u2014 {s['title']}" for s in sources)


def status_note(result: ChatResult) -> str | None:
    """A short note shown under the answer, explaining special situations.

    Returns:
        str  \u2014 a human-readable note when the answer needs extra context.
        None \u2014 when the answer is a plain, confident response.
    """
    if result.escalate:
        return (
            "I could not find this in the official documents. " "A staff member can help: Training Office, room I.101."
        )
    if result.degraded:
        return "Shown directly from the source document (the AI helper was unavailable)."
    return None
