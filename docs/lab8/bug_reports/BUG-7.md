# BUG-7: Number words in retake requests are ignored

**Found by:** Đăng (@dhdang2523-coder)   **Date:** 2026-11-28   **Severity:** major
**Where:** API (fee parsing)

## Steps to reproduce
1. Use the default fee settings: 450,000 VND per credit and a 1.5 retake multiplier.
2. Ask the assistant: `tuition for 18 credits and two retakes`.
3. On the pre-fix version, inspect the fee response.

## Expected

The assistant should parse 18 regular credits and 2 retake credits, then calculate:

`18 × 450,000 + 2 × 450,000 × 1.5 = 9,450,000 VND`.

Expected response: `Your tuition is 9,450,000 VND.`

## Actual (paste the exact output or error)

Before the fix, `two` was not recognized as a number, so the retake count became zero. The assistant returned:

`Your tuition is 8,100,000 VND.`

This undercharges by 1,350,000 VND.

## Evidence

Running the original `parse_credits` from pre-mitigation commit `97015bf` with the query returns `(18, 0)`. At the default rate and multiplier, that produces `Your tuition is 8,100,000 VND.` The regression test `tests/test_my_regressions.py::test_retake_number_as_word` now checks that the response includes `9,450,000` and excludes `8,100,000`.

## Cause (after investigation)

The original parser extracted digit sequences and looked for digits followed by `retake`. It found `18` for the regular credits but did not recognize the word `two` before `retakes`, so `retake_n` defaulted to `0`.

## Fix (commit / PR link) and regression test name

PR [#90](https://github.com/25127029-DBDANH/assistant-core-lab-team07/pull/90) added normalization for English number words from `one` through `ten` before parsing. The regression test is `tests/test_my_regressions.py::test_retake_number_as_word`.
