import argparse
import sys

from pydantic import ValidationError

from assistant_core.config import load_settings
from assistant_core.errors import AssistantError
from assistant_core.logging_setup import setup_logging
from assistant_core.models import Message
from assistant_core.service import build_service


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="assistant_core", description="Study assistant (Lab 3)")
    parser.add_argument("text", nargs="+", help="your question")
    parser.add_argument("--session", default="local", help="session id")
    args = parser.parse_args(argv)

    try:
        settings = load_settings()
        setup_logging(settings.log_level)
        service = build_service(settings)
        response = service.handle(Message(text=" ".join(args.text), session_id=args.session))
    except ValidationError:
        print("Invalid message: it must be 1-2000 characters.", file=sys.stderr)
        return 2
    except AssistantError as exc:
        print(f"Startup error: {exc}", file=sys.stderr)
        return 1

    suffix = "".join(f" (source: {s.id})" for s in response.sources)
    print(response.answer + suffix)
    return 0


if __name__ == "__main__":
    sys.exit(main())
