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

TODO: write three decisions, each with a reason (in your own words).
