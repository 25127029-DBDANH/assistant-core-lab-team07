from mini_search import DOCS, build_index, search, tokenize


def test_tokenize_given():
    assert tokenize("I lost my student card!") == ["lost", "student", "card"]


def test_s1_index():
    idx = build_index(DOCS)
    assert idx["credits"] == {"D1", "D2"}
    assert idx["card"] == {"D3"}


def test_s2_s3_search():
    idx = build_index(DOCS)
    assert search(idx, "I lost my student card")[0] == ("D3", 3)
    assert search(idx, "how many credits for a thesis")[0] == ("D1", 2)


def test_no_match_returns_empty():
    assert search(build_index(DOCS), "what is the capital of France") == []


# --- S2/S3 edge-case tests added for issue #53 ---


def test_search_empty_query():
    """An empty query string has no tokens, so no documents can match."""
    assert search(build_index(DOCS), "") == []


def test_search_all_stop_words():
    """A query made entirely of stop words produces no tokens, so no matches."""
    assert search(build_index(DOCS), "a the is") == []


def test_search_tie_break_by_doc_id():
    """When two documents share the same score, they are sorted by doc_id ascending."""
    idx = build_index(DOCS)
    results = search(idx, "students", k=2)
    # "students" appears in D1 and D4 (score 1 each); D1 < D4 alphabetically
    assert results == [("D1", 1), ("D4", 1)]


def test_search_k_limits_results():
    """The k parameter caps the number of results returned."""
    idx = build_index(DOCS)
    results = search(idx, "credits", k=1)
    assert len(results) == 1
    assert results[0][0] in ("D1", "D2")


def test_search_full_result_list():
    """search returns the complete expected list, not just the first element."""
    idx = build_index(DOCS)
    assert search(idx, "how many credits for a thesis") == [("D1", 2), ("D2", 1)]
