# Architecture of assistant_core

Owner: Member 7 (fill in the TODO parts once the modules exist).

## 1. Modules

| Module | Responsibility | Owner |
|---|---|---|
| `config.py` | read settings from the environment; validate | Member 2 |
| `errors.py` | named exceptions | Member 1 |
| `models.py` | public contract: Message, Response, Intent, Source | Member 1 |
| `router.py` | choose an Intent with simple rules | Member 6 |
| `knowledge.py` | office directory (CSV) and handbook (JSON) with search | Member 3 |
| `tools.py` | deterministic tuition calculation | Member 4 |
| `responder.py` | response generation behind one interface (stub LLM, template) | Member 5 |
| `service.py` | `AssistantService.handle(Message) -> Response`, the only entry point | Member 1 |
| `logging_setup.py` | structured JSON logs | Member 2 |
| `__main__.py` | command-line interface | Member 1 |

## 2. Service interface

```
AssistantService.handle(msg: Message) -> Response
Message:  text (1-2000 chars), session_id
Response: answer, intent, sources[], degraded (True if a fallback was used)
Errors:   invalid input -> ValidationError; startup -> ConfigError / DataError;
          provider failures never reach the caller (fallback instead)
```

## 3. Decisions

1. **Fees are computed in `tools.py`, never by an LLM.** The calculation is a pure function: same input,
   same output, no I/O. It is exact and easy to test, and a characterisation test locks the monolith's
   value (18 credits + 2 retake = 9,450,000 VND).
2. **The LLM sits behind the `Responder` interface, with a template fallback.** `AssistantService` receives
   its responder in the constructor. If the provider raises `ProviderError`, the service answers with
   `TemplateResponder` and sets `degraded=True`, so the error never reaches the caller. The stub needs no
   key, so tests and CI run offline.
3. **Configuration comes from the environment.** `.env.example` documents every variable and `.env` is
   never committed. `Settings.llm_api_key` uses `repr=False`, and logs contain only intent, latency, session
   and degraded, never the key or the full user message.
4. **`AssistantService` turns an invalid fee request into a friendly answer.** For example, "tuition for 31
   credits" returns "Credits must be between 1 and 30." instead of raising, so the CLI, the API (Lab 4) and
   the UI (Lab 7) do not each need their own `try/except`.

## 4. Known limitations and open questions

- **Router:** the fee rule matches the substring "fee", so "coffee shop" is routed as FEE. This is kept
  from the monolith.
- **Handbook search:** it counts every shared word, including short ones like "is" and "the", so an unrelated
  question can still return a rule. The monolith ignored words of 3 characters or fewer. To be improved in the AI weeks.
- **Dropped from the monolith:** conversation history, `stats()` and `save_history()` are not part of the
  target design. To be confirmed with the instructor.
- **Output format:** tuition is printed as `9,450,000 VND` (as in the handout); the monolith printed `9450000`.
