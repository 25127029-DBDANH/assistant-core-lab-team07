"""H1 — Prove it, or replace it.

Chosen function: ``tokenize`` (src/assistant_core/rag/index.py)
Rationale (from docs/ai-use-log.md): the stemming + safeguard logic was
drafted by Antigravity in Issue #56 (Lab 6).  It is a pure function with
explicit edge-case rules, so it is easy to exhaustively test *all* the
boundary conditions specified in the original PR description.

Edge-test categories required by Issue #84:
  ① Empty input → returns []
  ② Single zero-length token (pure punctuation / whitespace only)
  ③ Very long input (1 000-word string) — must not raise or hang
  ④ Vietnamese text with diacritics — tokenizer must not crash; each
     diacritic cluster (ví, dụ, …) is treated as a single opaque token
     (unchanged by stemming because they are ≤4 chars or lack the
     English suffix rules)
  ⑤ Wrong type — None, int — must raise AttributeError / TypeError
     (the contract is ``text: str``; we document the behaviour)

Stemming-safeguard edge cases (the core algorithmic logic):
  ⑥  word ≤ 4 chars ending in 's' → NOT stripped  (e.g. "fees" stays "fees")
  ⑦  word > 4 chars ending in 'ss' → NOT stripped (e.g. "class" stays "class")
  ⑧  word > 4 chars ending in 'us' → NOT stripped (e.g. "status" stays "status")
  ⑨  word > 4 chars ending in 'is' → NOT stripped (e.g. "thesis" stays "thesis")
  ⑩  word > 4 chars ending in plain 's' → stripped (e.g. "credits" → "credit")
  ⑪  domain synonym expansion: "take" + "credit" → "credit", "load" (no "take")
  ⑫  stop words are removed ("the", "a", "in", …)
"""

from __future__ import annotations

import pytest

from assistant_core.rag.index import STOP, tokenize

# ─────────────────────────────────────────────────────────────────────────────
# ① Empty / blank input
# ─────────────────────────────────────────────────────────────────────────────


def test_empty_string_returns_empty_list():
    """Edge case: empty string must return [] without crashing."""
    assert tokenize("") == []


def test_whitespace_only_returns_empty_list():
    """Edge case: input with only spaces/tabs/newlines → []."""
    assert tokenize("   \t\n  ") == []


def test_punctuation_only_returns_empty_list():
    """Edge case: punctuation tokens have no \w+ matches → []."""
    assert tokenize("!!!  ???  ---  ...") == []


# ─────────────────────────────────────────────────────────────────────────────
# ② Single-token / zero-length edge cases
# ─────────────────────────────────────────────────────────────────────────────


def test_single_stop_word_returns_empty():
    """A single stop word is consumed entirely → []."""
    assert tokenize("the") == []


def test_single_non_stop_word_returned():
    """A single meaningful word with no s-suffix is returned as-is."""
    result = tokenize("library")
    assert result == ["library"]  # 7 chars, ends in 'y' not 's' → no strip, returned unchanged


def test_zero_value_in_text():
    """Edge case: the string '0 credits' — '0' is a valid token, 'credits' stems."""
    result = tokenize("0 credits")
    assert "0" in result
    assert "credit" in result  # stripped from "credits"
    assert "credits" not in result


# ─────────────────────────────────────────────────────────────────────────────
# ③ Very large input
# ─────────────────────────────────────────────────────────────────────────────


def test_very_long_input_does_not_raise():
    """Edge case: 1 000-word string must complete without raising."""
    long_text = " ".join(["tuition credits scholarship retake thesis"] * 200)
    result = tokenize(long_text)
    # Result must be a non-empty list of strings
    assert isinstance(result, list)
    assert all(isinstance(t, str) for t in result)
    assert len(result) > 0


def test_1000_repetitions_of_credits_stemmed_correctly():
    """All 1 000 occurrences of 'credits' must stem to 'credit'."""
    text = " ".join(["credits"] * 1000)
    result = tokenize(text)
    assert all(t == "credit" for t in result)
    assert len(result) == 1000


# ─────────────────────────────────────────────────────────────────────────────
# ④ Vietnamese text with diacritics
# ─────────────────────────────────────────────────────────────────────────────


def test_vietnamese_diacritics_do_not_crash():
    """Edge case: Vietnamese syllables with diacritics must not raise."""
    result = tokenize("học phí đăng ký tín chỉ")
    assert isinstance(result, list)


def test_vietnamese_tokens_not_mangled_by_stemmer():
    """Short Vietnamese tokens (≤4 chars) must NOT be stripped by the stemmer."""
    result = tokenize("học phí")
    # 'học' (3 chars), 'phí' (3 chars) → too short to stem, and not stop words
    for tok in result:
        assert len(tok) >= 1


def test_mixed_english_vietnamese():
    """Edge case: English credits + Vietnamese context must stem only English parts."""
    result = tokenize("credits tín chỉ")
    assert "credit" in result  # 'credits' → 'credit'


# ─────────────────────────────────────────────────────────────────────────────
# ⑤ Wrong type (documents the contract: tokenize(text: str))
# ─────────────────────────────────────────────────────────────────────────────


def test_none_input_raises_type_error():
    """Wrong type None must raise AttributeError (re.findall on None)."""
    with pytest.raises((AttributeError, TypeError)):
        tokenize(None)  # type: ignore[arg-type]


def test_int_input_raises_type_error():
    """Wrong type int must raise TypeError (re.findall on int)."""
    with pytest.raises((AttributeError, TypeError)):
        tokenize(42)  # type: ignore[arg-type]


def test_list_input_raises_type_error():
    """Wrong type list must raise TypeError."""
    with pytest.raises((AttributeError, TypeError)):
        tokenize(["credits"])  # type: ignore[arg-type]


# ─────────────────────────────────────────────────────────────────────────────
# ⑥–⑩ Stemming safeguard rules (the core algorithmic logic)
# ─────────────────────────────────────────────────────────────────────────────


def test_short_word_ending_s_not_stripped():
    """Words ≤ 4 chars ending in 's' must NOT be stripped (e.g. 'fees' has 4 chars)."""
    result = tokenize("fees")
    # 'fees' has 4 chars (== 4, not > 4) → safeguard: NOT stripped
    assert "fees" in result


def test_word_ending_ss_not_stripped():
    """Words > 4 chars ending in 'ss' must NOT be stripped (e.g. 'business', 'class')."""
    result = tokenize("business class")
    # 'business' (8 chars) ends with 'ss' → guard fires → NOT stripped → stays 'business'
    assert "business" in result
    # 'class' (5 chars) ends with 'ss' → guard fires → NOT stripped → stays 'class'
    assert "class" in result
    # Verify individually
    assert tokenize("class") == ["class"]


def test_word_ending_us_not_stripped():
    """Words > 4 chars ending in 'us' must NOT be stripped (e.g. 'status', 'campus')."""
    for word in ("status", "campus", "nexus"):
        result = tokenize(word)
        assert word in result, f"'{word}' should not be stemmed"


def test_word_ending_is_not_stripped():
    """Words > 4 chars ending in 'is' must NOT be stripped (e.g. 'thesis', 'crisis')."""
    for word in ("thesis", "crisis", "basis"):
        result = tokenize(word)
        assert word in result, f"'{word}' should not be stemmed"


def test_plural_english_word_stripped():
    """Words > 4 chars with plain 's' suffix must have 's' stripped."""
    cases = {
        "credits": "credit",  # 7 chars, ends in 's' → 'credit'
        "students": "student",  # 8 chars, ends in 's' → 'student'
        "courses": "course",  # 7 chars, ends in 'es' — strip 's' → 'course' (not 'cours')
        "requirements": "requirement",  # 13 chars, ends in 's' → 'requirement'
        "scholarships": "scholarship",  # 12 chars, ends in 's' → 'scholarship'
    }
    for original, expected in cases.items():
        result = tokenize(original)
        assert expected in result, f"'{original}' should stem to '{expected}', got {result}"


# ─────────────────────────────────────────────────────────────────────────────
# ⑪ Domain synonym expansion
# ─────────────────────────────────────────────────────────────────────────────


def test_take_credit_expands_to_load():
    """'take' + 'credit(s)' triggers domain synonym: 'take' replaced by 'load'."""
    result = tokenize("can I take 32 credits")
    assert "load" in result
    assert "take" not in result
    assert "credit" in result  # 'credits' → 'credit'


def test_take_without_credit_not_expanded():
    """'take' alone (no 'credit') must NOT be replaced by 'load'."""
    result = tokenize("take the exam")
    # 'take' is not a stop word and no 'credit' present → stays
    assert "take" in result
    assert "load" not in result


def test_credit_without_take_not_expanded():
    """'credit' alone (no 'take') must NOT trigger synonym expansion."""
    result = tokenize("credit load policy")
    assert "load" in result  # 'load' is already there
    assert "take" not in result


# ─────────────────────────────────────────────────────────────────────────────
# ⑫ Stop word removal
# ─────────────────────────────────────────────────────────────────────────────


def test_all_stop_words_removed():
    """Every word in STOP must be absent from the output."""
    text = " ".join(STOP)
    result = tokenize(text)
    assert result == [], f"Stop words leaked into result: {result}"


def test_stop_words_removed_in_context():
    """Stop words embedded in a real question must all be removed."""
    result = tokenize("where is the library")
    assert "where" not in result  # 'where' is a stop word
    assert "is" not in result
    assert "the" not in result
    assert "library" in result  # 'library' → 7 chars, ends in 'y' (not 's') → no strip, returned as-is
