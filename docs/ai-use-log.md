# AI Use Log

| Date | Who | Tool | Asked for | Kept / Changed | Verified by |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 2026-11-08 | me | Antigravity | write SQL F1/F2 and open PR for #37 | queries reviewed, scope trimmed to F1+F2 only | ran against seeded 300-row DB, F1 sum = 300, pytest and ruff pass |
| 2026-11-14 | DMH554 | Antigravity | verify S2/S3 search scoring/ranking and add edge-case tests for #53 | kept existing search impl, added 5 edge-case tests | pytest 68 passed, ruff clean, manual output verification |
| 2026-11-19 | DMH554 | Antigravity | implement L1 format_sources and L2 status_note in ui/logic.py for #67 | reviewed spec and implemented; removed xfail markers | pytest 78 passed (9/9 test_ui.py), ruff clean |
| 2026-11-25 | EddieOuttaHere | Antigravity | H1: write edge tests for `tokenize` (rag/index.py) — empty, 0, very long, Vietnamese diacritics, wrong type, stemming safeguards, synonym expansion; Bonus G2: draft Vietnamese authority-impersonation regex patterns in guard.py | reviewed all patterns against real attack examples; corrected 4 test assertions against actual tokenize behaviour; verified no false positives on 3 benign Vietnamese questions | pytest 24/24 test_ai_proven.py passed; pytest test_my_regressions.py 10/10 passed; ruff clean |
