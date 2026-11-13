from mini_search import DOCS, build_index, search, tokenize


def test_tokenize_given():
    assert tokenize("I lost my student card!") == ["lost", "student", "card"]


def test_build_index():
    idx = build_index(DOCS)
    assert idx["credits"] == {"D1", "D2"}
    assert idx["card"] == {"D3"}


def test_build_index_repeated_terms_stop_words_and_punctuation():
    docs = {
        "D1": "The thesis, thesis! credits-credits.",
        "D2": "THESIS? credits.",
        "D3": "a an the my and to",
    }

    idx = build_index(docs)

    assert idx == {"thesis": {"D1", "D2"}, "credits": {"D1", "D2"}}


def test_build_index_empty_and_unindexable_documents():
    assert build_index({}) == {}
    assert build_index({"D1": "the a my and", "D2": "!!! ???"}) == {}


def test_s2_s3_search():
    idx = build_index(DOCS)
    assert search(idx, "I lost my student card")[0] == ("D3", 3)
    assert search(idx, "how many credits for a thesis")[0] == ("D1", 2)


def test_no_match_returns_empty():
    assert search(build_index(DOCS), "what is the capital of France") == []
