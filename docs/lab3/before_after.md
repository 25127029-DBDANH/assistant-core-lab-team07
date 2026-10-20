# Before and After: Maintainability Comparison

Lab 3: Maintainable Python Service — Member 6 (Phạm Gia Hưng)

| Question | Monolith | assistant_core |
|---|---|---|
| Places to change the credit rate | 1 constant in code | 1 variable in `.env` |
| Tests run offline and deterministically? | no | yes |
| Missing `handbook.json` | prints and continues silently | `DataError` at startup |
| Secret printed or logged? | yes | no |
| Module-level globals | 9 (3 mutable) | 0 |
| Bare except: | 3 | 0 |
| Longest function (lines) | ~65 (`handle`) | ~15 |
| Swap the LLM without touching the service? | no | yes |

## Reflection

- **What got more complex?**: More files and a few more architectural concepts (modular separation of concerns, dependency injection, Protocol/interfaces).
- **When is that trade-off worth it?**: When the codebase is developed and maintained by a team, or when it requires robust automated testing, safe secret management, and easy extensibility without regressions.
