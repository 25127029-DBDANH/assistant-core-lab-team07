import logging
import time
from pathlib import Path

from assistant_core.config import Settings
from assistant_core.errors import ConfigError, InvalidRequest, ProviderError
from assistant_core.knowledge import Handbook, OfficeDirectory
from assistant_core.models import Intent, Message, Response, Source
from assistant_core.responder import Responder, StubLLMResponder, TemplateResponder
from assistant_core.router import route
from assistant_core.tools import parse_credits, tuition

log = logging.getLogger("assistant_core")


class AssistantService:
    def __init__(self, settings: Settings, offices: OfficeDirectory, handbook: Handbook, responder: Responder) -> None:
        self.settings = settings
        self.offices = offices
        self.handbook = handbook
        self.responder = responder
        self.fallback = TemplateResponder()

    def handle(self, msg: Message) -> Response:
        start = time.perf_counter()
        intent = route(msg.text, self.offices.names)
        if intent is Intent.GREETING:
            response = Response(answer="Hello! I can help with offices, fees and rules.", intent=intent)
        elif intent is Intent.FEE:
            response = self._fee(msg.text)
        elif intent is Intent.OFFICE:
            response = self._office(msg.text)
        else:
            response = self._rule(msg.text)
        log.info(
            "handled",
            extra={
                "intent": response.intent.value,
                "latency_ms": round((time.perf_counter() - start) * 1000, 2),
                "session": msg.session_id,
                "degraded": response.degraded,
            },
        )
        return response

    def _fee(self, text: str) -> Response:
        try:
            credits, retake = parse_credits(text)
            total = tuition(
                credits,
                retake,
                self.settings.credit_rate_vnd,
                self.settings.retake_multiplier,
                self.settings.max_credits,
            )
        except InvalidRequest as exc:
            return Response(answer=str(exc), intent=Intent.FEE)
        return Response(answer=f"Your tuition is {total:,} VND.", intent=Intent.FEE)

    def _office(self, text: str) -> Response:
        office = self.offices.find(text)
        if office is None:
            return Response(answer="Sorry, I don't know that office.", intent=Intent.UNKNOWN)
        return Response(answer=f"{office.name}: room {office.room}, open {office.hours}.", intent=Intent.OFFICE)

    def _rule(self, text: str) -> Response:
        rule = self.handbook.search(text)
        if rule is None:
            return Response(answer="Sorry, I don't know that yet.", intent=Intent.UNKNOWN)
        sources = [Source(id=rule.id, title=rule.title)]
        try:
            answer = self.responder.explain(text, rule)
            return Response(answer=answer, intent=Intent.RULE, sources=sources)
        except ProviderError:
            log.warning("provider failed; using template fallback")
            answer = self.fallback.explain(text, rule)
            return Response(answer=answer, intent=Intent.RULE, sources=sources, degraded=True)


def build_service(settings: Settings) -> AssistantService:
    """Wire the real dependencies together (used by the CLI and, later, the API)."""
    data_dir = Path(settings.data_dir)
    offices = OfficeDirectory.from_csv(data_dir / "offices.csv")
    handbook = Handbook.from_json(data_dir / "handbook.json")
    if settings.llm_provider == "stub":
        responder: Responder = StubLLMResponder()
    else:
        raise ConfigError(f"unknown LLM_PROVIDER: {settings.llm_provider!r}")
    return AssistantService(settings, offices, handbook, responder)
