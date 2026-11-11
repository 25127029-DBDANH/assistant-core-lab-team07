# Lab 6 — Three assistant paths

Benchmark command: `python eval/compare_paths.py` (20 cases in `eval/cases.jsonl`).
The benchmark required the A1 abstention guard in `RagAnswerer.answer`; `main` still
raised `NotImplementedError` for empty retrieval results, so that prerequisite was
implemented on this branch before measuring.

| Path | Correct /20 | Abstain correct /5 | p50 (ms) | Max (ms) | Fails |
|---|---:|---:|---:|---:|---|
| deterministic | 7/20 | 5/5 | 0.0 | 2.1 | E01, E02, E05–E15 |
| retrieval | 16/20 | 4/5 | 0.0 | 1.2 | E13, E14, E15, E19 |
| llm (stub) | 16/20 | 4/5 | 0.3 | 3.3 | E13, E14, E15, E19 |

Retrieval is the best current path for handbook and regulation questions: it answers 16/20 while deterministic answers only 7/20, and retrieval-only ties the stub LLM while remaining the fastest measured path. Retrieval improves coverage through BM25 matching against handbook chunks and returns the supporting source directly, while abstention below the score threshold avoids unsupported policy claims; an LLM can make wording more natural, but the stub did not improve accuracy and needs the same retrieval, citation-grounding, and abstention controls. E14 fails because the query token `credits` does not match the handbook's `credit` token, so the first fix should normalize plurals at indexing and query time (for example, a small stemming or lemmatization step), then rerun the benchmark.

The measured latencies are local single-run observations, not a production service-level guarantee.
