"""FastAPI application with SQLite persistence. Run with `uvicorn assistant_api.main:create_app --factory`."""

from __future__ import annotations

import time
import uuid
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Header, HTTPException, Query, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from assistant_api.db import Repository, init_db, make_engine
from assistant_api.holiday import HolidayClient, HolidayServiceError
from assistant_api.ratelimit import RateLimiter
from assistant_api.schemas import (
    ChatRequest,
    ChatResponse,
    ErrorResponse,
    FeedbackIn,
    FeedbackOut,
    Holiday,
    HolidayList,
    Weather,
)
from assistant_api.weather import ExternalServiceError, WeatherClient
from assistant_core import AssistantService, Message, build_service
from assistant_core.config import Settings, load_settings
from assistant_core.models import Intent


def create_app(
    settings: Settings | None = None,
    service: AssistantService | None = None,
    weather: WeatherClient | None = None,
    holiday: HolidayClient | None = None,
) -> FastAPI:
    settings = settings or load_settings()
    service = service or build_service(settings)
    weather = weather or WeatherClient(
        settings.weather_url, settings.campus_lat, settings.campus_lon, timeout_s=settings.weather_timeout_s
    )
    holiday = holiday or HolidayClient()
    limiter = RateLimiter(settings.rate_limit_per_min)  # used only in the BONUS task
    engine = make_engine(settings.database_url)
    init_db(engine)
    repo = Repository(engine, settings.session_salt)

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        try:
            yield
        finally:
            engine.dispose()

    app = FastAPI(
        title="Study Assistant API",
        version="1.0.0",
        description="Backend of the CSC10014 Smart Virtual Assistant.",
        lifespan=lifespan,
    )
    app.state.engine = engine
    app.state.repository = repo

    def error(code: int, key: str, message: str) -> JSONResponse:
        return JSONResponse(status_code=code, content={"error": {"code": key, "message": message}})

    @app.exception_handler(RequestValidationError)
    async def on_validation(_: Request, exc: RequestValidationError):
        first = exc.errors()[0]
        field = ".".join(str(p) for p in first["loc"][1:]) or "body"
        return error(422, "invalid_request", f"{field}: {first['msg']}")

    @app.exception_handler(HTTPException)
    async def on_http(_: Request, exc: HTTPException):
        return error(exc.status_code, str(exc.detail).lower().replace(" ", "_"), str(exc.detail))

    def require_admin(x_api_key: str | None = Header(default=None)) -> None:
        if not settings.api_admin_key or x_api_key != settings.api_admin_key:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Missing or invalid API key")

    @app.get("/health", tags=["ops"])
    def health() -> dict:
        return {"status": "ok", "version": app.version}

    @app.get("/v1/offices", tags=["offices"])
    def list_offices() -> list[dict]:
        return [office.__dict__ for office in service.offices.all()]

    @app.post(
        "/v1/chat",
        response_model=ChatResponse,
        tags=["chat"],
        responses={422: {"model": ErrorResponse}, 429: {"model": ErrorResponse}},
    )
    def chat(req: ChatRequest, request: Request) -> ChatResponse:
        client = request.client.host if request.client else "unknown"
        if not limiter.allow(client):
            raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, "Too many requests")
        started = time.perf_counter()
        resp = service.handle(Message(text=req.message, session_id=req.session_id))
        request_id = uuid.uuid4().hex[:12]
        repo.record_interaction(
            raw_session=req.session_id,
            request_id=request_id,
            intent=resp.intent.value,
            topic=resp.sources[0].id if resp.sources else None,
            resolved=resp.intent is not Intent.UNKNOWN,
            degraded=resp.degraded,
            latency_ms=(time.perf_counter() - started) * 1000,
        )
        return ChatResponse(**resp.model_dump(), request_id=request_id)

    @app.post("/v1/feedback", response_model=FeedbackOut, status_code=201, tags=["feedback"])
    def add_feedback(fb: FeedbackIn) -> FeedbackOut:
        item = repo.add_feedback(fb.request_id, fb.rating, fb.comment)
        if item is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Interaction not found")
        return FeedbackOut(
            request_id=item.request_id,
            rating=item.rating,
            comment=item.comment,
            id=item.id,
            created_at=item.created_at,
        )

    @app.get("/v1/feedback", response_model=list[FeedbackOut], tags=["feedback"], dependencies=[Depends(require_admin)])
    def list_feedback(limit: int = Query(default=100, ge=1, le=1000)) -> list[FeedbackOut]:
        return [
            FeedbackOut(
                request_id=item.request_id,
                rating=item.rating,
                comment=item.comment,
                id=item.id,
                created_at=item.created_at,
            )
            for item in repo.list_feedback(limit)
        ]

    @app.get("/v1/stats/intents", tags=["stats"], dependencies=[Depends(require_admin)])
    def intent_stats() -> list[dict]:
        return repo.intent_stats()

    @app.get("/v1/weather", response_model=Weather, tags=["external"], responses={503: {"model": ErrorResponse}})
    def campus_weather() -> Weather:
        try:
            return weather.current()
        except ExternalServiceError:
            raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Weather service unavailable") from None

    # ── H3 Bonus: Public Holiday endpoint ─────────────────────────────────────

    @app.get(
        "/v1/holidays",
        response_model=HolidayList,
        tags=["external"],
        summary="List public holidays for a country",
        responses={503: {"model": ErrorResponse}},
    )
    def public_holidays(
        country: str = Query(default="VN", min_length=2, max_length=2, description="ISO 3166-1 alpha-2 country code"),
        year: int = Query(default=None, ge=2000, le=2100, description="Year (defaults to current year)"),
    ) -> HolidayList:
        """Return public holidays from Nager.Date API.

        Applies timeout (5 s), one retry, and a 24-hour in-memory cache.
        Returns HTTP 503 if the upstream fails and no cached data is available.
        """
        try:
            return holiday.get_holidays(country_code=country, year=year)
        except HolidayServiceError:
            raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Holiday service unavailable") from None

    @app.get(
        "/v1/holidays/next",
        response_model=Holiday | None,
        tags=["external"],
        summary="Next upcoming public holiday",
        responses={503: {"model": ErrorResponse}},
    )
    def next_holiday(
        country: str = Query(default="VN", min_length=2, max_length=2, description="ISO 3166-1 alpha-2 country code"),
    ) -> Holiday | None:
        """Return the next upcoming public holiday for a country (or null if none)."""
        try:
            return holiday.next_holiday(country_code=country)
        except HolidayServiceError:
            raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Holiday service unavailable") from None

    return app
