"""logging_setup.py: structured JSON logs.

Owner: Member 2
Implements Lab 3, Step 10 — structured logging.
Never log secrets (API key) or the full user message.
"""

from __future__ import annotations

import json
import logging
import sys


class JsonFormatter(logging.Formatter):
    """Emit each log record as a single JSON object.

    Extra attributes ``intent``, ``latency_ms``, ``session`` and
    ``degraded`` are included when present on the record.
    """

    def format(self, record: logging.LogRecord) -> str:
        data: dict[str, object] = {
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        for key in ("intent", "latency_ms", "session", "degraded"):
            if hasattr(record, key):
                data[key] = getattr(record, key)
        return json.dumps(data, ensure_ascii=False)


def setup_logging(level: str = "INFO") -> None:
    """Configure the root ``assistant_core`` logger.

    * Logs are written to **stderr** so they do not mix with the answer
      on stdout.
    * Uses :class:`JsonFormatter` for structured, machine-readable output.
    """
    logger = logging.getLogger("assistant_core")
    logger.setLevel(level.upper())

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)
