"""Streamlit chat UI.   Run:  streamlit run ui/app.py      (the API must be running on port 8000)

The UI never imports assistant_core: it only talks to the backend through the HTTP API.

Bonus features (Issue #70):
  - st.write_stream: answers appear word-by-word like live typing (simulated from the
    full response already returned by the backend, so latency is unchanged but UX is
    dramatically more natural).
  - st.expander sources: each cited regulation clause is shown in an expandable card
    that separates the clause ID badge from its full title, making citations scannable.
"""

from __future__ import annotations

import os
import sys
import time
import uuid
from collections.abc import Generator
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # so "import ui..." works under streamlit

from ui.api_client import AssistantClient
from ui.logic import EXAMPLES, WELCOME, format_sources, status_note, validate_input

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="FIT Study Assistant",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="expanded",
)

client = AssistantClient(os.getenv("ASSISTANT_API_URL", "http://127.0.0.1:8000"))

# ---------------------------------------------------------------------------
# Session state initialisation
# ---------------------------------------------------------------------------
if "session_id" not in st.session_state:
    st.session_state.session_id = uuid.uuid4().hex[:12]
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": WELCOME}]
if "rated" not in st.session_state:
    st.session_state.rated = set()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _word_stream(text: str, delay: float = 0.03) -> Generator[str, None, None]:
    """Yield the answer one word at a time for a live-typing effect.

    ``delay`` is in seconds between words.  0.03 s gives ~33 words/s which
    feels natural without being annoyingly slow.
    """
    for word in text.split():
        yield word + " "
        time.sleep(delay)


def _render_sources_expander(sources: list[dict]) -> None:
    """Render each cited clause as a collapsible st.expander card.

    Layout inside each card:
      ┌─────────────────────────────────────────────────────────┐
      │ 📄 H26#6.1  [expanded header]                           │
      │   Full title: 6.1 Credit Load                           │
      │   This regulation was used to answer your question.     │
      └─────────────────────────────────────────────────────────┘
    """
    if not sources:
        return
    st.caption("**Referenced regulations:**")
    for src in sources:
        clause_id: str = src.get("id", "")
        title: str = src.get("title", "")
        with st.expander(f"📄 `{clause_id}`  —  {title}", expanded=False):
            col_id, col_title = st.columns([1, 3])
            col_id.metric(label="Clause ID", value=clause_id)
            col_title.markdown(f"**Full title:** {title}")
            st.caption(
                "This regulation was retrieved from the official student handbook "
                "and used to answer your question. Always verify with the Training Office "
                "for binding decisions."
            )


def _render_message(msg: dict, idx: int) -> None:
    """Render a single chat bubble (history replay — no streaming)."""
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

        # Bonus: expander-style source cards (replaces plain st.caption)
        if msg.get("sources_raw"):
            _render_sources_expander(msg["sources_raw"])
        elif msg.get("sources"):
            # Legacy fallback: plain text sources for messages stored without sources_raw
            st.caption(msg["sources"])

        if msg.get("note"):
            st.info(msg["note"], icon="ℹ️")

        rid = msg.get("request_id")
        if rid and rid not in st.session_state.rated:
            c1, c2, _ = st.columns([1, 1, 6])
            if c1.button("👍", key=f"up{idx}", help="This answer was helpful"):
                client.send_feedback(rid, 1)
                st.session_state.rated.add(rid)
                st.toast("Thanks for your feedback! 🙌")
                st.rerun()
            if c2.button("👎", key=f"down{idx}", help="This answer needs improvement"):
                client.send_feedback(rid, -1)
                st.session_state.rated.add(rid)
                st.toast("Thanks — we will look at this answer.")
                st.rerun()


# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.title("🎓 FIT Study Assistant")

if not client.healthy():
    st.error(
        "⚠️ The assistant backend is not reachable. "
        "Start it with:  `uvicorn assistant_api.main:create_app --factory`",
        icon="🔌",
    )

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    if st.button("🔄 New conversation", use_container_width=True, help="Clear chat history and start a fresh session"):
        st.session_state.session_id = uuid.uuid4().hex[:12]
        st.session_state.messages = [{"role": "assistant", "content": WELCOME}]
        st.session_state.rated = set()
        st.session_state.pop("pending", None)
        st.rerun()

    st.divider()
    st.subheader("💡 Try an example")
    for ex in EXAMPLES:
        if st.button(ex, use_container_width=True):
            st.session_state.pending = ex
    st.divider()
    st.caption(
        "🤖 This is an AI assistant powered by Safe RAG. "
        "It answers questions about fees, offices and the student handbook. "
        "**Check important decisions with the Training Office.**"
    )

# ---------------------------------------------------------------------------
# Chat history (replay without streaming)
# ---------------------------------------------------------------------------
for i, msg in enumerate(st.session_state.messages):
    _render_message(msg, i)

# ---------------------------------------------------------------------------
# New question
# ---------------------------------------------------------------------------
question = st.chat_input(
    "Ask a question (e.g., thesis registration, lost student card, fees)..."
) or st.session_state.pop("pending", None)

if question:
    problem = validate_input(question)
    if problem:
        st.warning(problem, icon="⚠️")
    else:
        # Echo the user's question immediately
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)

        # Call backend while showing spinner
        with st.spinner("Thinking…"):
            result = client.ask(question, st.session_state.session_id)

        with st.chat_message("assistant"):
            if result.ok:
                # ── Bonus: stream the answer word-by-word ──────────────────
                st.write_stream(_word_stream(result.answer))

                # ── Bonus: expander source cards ───────────────────────────
                _render_sources_expander(result.sources)

                note = status_note(result)
                if note:
                    st.info(note, icon="ℹ️")

                # Persist to session state (keep sources_raw for re-render)
                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": result.answer,
                        "sources": format_sources(result.sources),
                        "sources_raw": result.sources,  # for expander re-render
                        "note": note,
                        "request_id": result.request_id,
                    }
                )
            else:
                error_msg = f"⚠️ {result.error}"
                st.markdown(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

        st.rerun()
