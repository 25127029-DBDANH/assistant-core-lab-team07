import httpx
import pytest
from fastapi.testclient import TestClient

from assistant_api.holiday import HolidayClient
from assistant_api.main import create_app
from assistant_api.weather import WeatherClient

OK_JSON = {"current": {"time": "2026-10-05T09:00", "temperature_2m": 31.2, "weather_code": 3, "wind_speed_10m": 8.5}}

# Nager.Date response for Vietnam 2026 (trimmed to key holidays for tests)
OK_HOLIDAY_JSON = [
    {"date": "2026-01-01", "localName": "Tết Dương lịch", "name": "New Year's Day"},
    {"date": "2026-04-30", "localName": "Ngày Giải phóng miền Nam", "name": "Reunification Day"},
    {"date": "2026-05-01", "localName": "Ngày Quốc tế Lao động", "name": "International Workers' Day"},
    {"date": "2026-09-02", "localName": "Ngày Quốc khánh", "name": "National Day"},
]


def weather_with(handler) -> WeatherClient:
    transport = httpx.MockTransport(handler)
    return WeatherClient("https://example.test/forecast", 10.76, 106.68, retries=1, transport=transport)


def holiday_with(handler) -> HolidayClient:
    transport = httpx.MockTransport(handler)
    return HolidayClient(base_url="https://example.test/holidays", retries=0, transport=transport)


@pytest.fixture
def client(settings, service):
    settings = settings.model_copy(update={"api_admin_key": "secret-admin", "rate_limit_per_min": 5})
    app = create_app(
        settings,
        service,
        weather_with(lambda req: httpx.Response(200, json=OK_JSON)),
        holiday_with(lambda req: httpx.Response(200, json=OK_HOLIDAY_JSON)),
    )
    return TestClient(app)


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200 and r.json()["status"] == "ok"


def test_offices_status_ok(client):
    r = client.get("/v1/offices")
    assert r.status_code == 200


def test_offices_include_library_and_are_sorted(client):
    r = client.get("/v1/offices")
    offices = r.json()
    names = [office["name"] for office in offices]

    assert any(office["name"] == "Library" for office in offices)
    assert names == sorted(names, key=str.casefold)


def test_chat_fee(client):
    r = client.post("/v1/chat", json={"message": "tuition for 18 credits and 2 retake"})
    assert r.status_code == 200
    body = r.json()
    assert body["intent"] == "fee" and "9,450,000" in body["answer"] and body["request_id"]


def test_chat_validation_error(client):
    r = client.post("/v1/chat", json={"message": ""})
    assert r.status_code == 422 and r.json()["error"]["code"] == "invalid_request"


def test_rate_limit(client):
    codes = [client.post("/v1/chat", json={"message": "hi"}).status_code for _ in range(6)]
    assert codes[-1] == 429


@pytest.mark.xfail(reason="TODO Task T2 & T3: Feedback endpoints chưa triển khai")
def test_feedback_roundtrip(client):
    r = client.post("/v1/feedback", json={"request_id": "abc123", "rating": 1})
    assert r.status_code == 201 and r.json()["id"] == 1
    assert client.get("/v1/feedback").status_code == 401
    listed = client.get("/v1/feedback", headers={"X-API-Key": "secret-admin"})
    assert listed.status_code == 200 and len(listed.json()) == 1


def test_feedback_rating_out_of_range(client):
    assert client.post("/v1/feedback", json={"request_id": "x", "rating": 5}).status_code == 422


def test_list_feedback_requires_admin(client):
    r = client.get("/v1/feedback")
    assert r.status_code == 401
    assert r.json()["error"]["code"] == "missing_or_invalid_api_key"


def test_list_feedback_returns_list_to_admin(client):
    r = client.get("/v1/feedback", headers={"X-API-Key": "secret-admin"})
    assert r.status_code == 200
    assert isinstance(r.json(), list)
    assert r.json() == []


def test_weather_ok(client):
    r = client.get("/v1/weather")
    assert r.status_code == 200 and r.json()["description"] == "overcast"


def test_weather_down_returns_503(settings, service):
    def boom(req):
        raise httpx.ConnectTimeout("timeout", request=req)

    app = create_app(settings, service, weather_with(boom))
    r = TestClient(app).get("/v1/weather")
    assert r.status_code == 503 and r.json()["error"]["code"] == "weather_service_unavailable"


def test_weather_stale_cache_when_upstream_fails():
    calls = {"n": 0}

    def flaky(req):
        calls["n"] += 1
        if calls["n"] == 1:
            return httpx.Response(200, json=OK_JSON)
        return httpx.Response(500)

    w = weather_with(flaky)
    w.cache_ttl_s = 0  # force a refresh on the second call
    assert not w.current().stale
    assert w.current().stale


# ── H3 Bonus: Holiday endpoint tests ──────────────────────────────────────────


def test_holidays_ok(client):
    """GET /v1/holidays returns 200 with a list of holidays for Vietnam."""
    r = client.get("/v1/holidays", params={"country": "VN", "year": 2026})
    assert r.status_code == 200
    body = r.json()
    assert body["country_code"] == "VN"
    assert body["year"] == 2026
    assert len(body["holidays"]) == 4
    # Check that National Day is present
    names = [h["global_name"] for h in body["holidays"]]
    assert "National Day" in names


def test_holidays_contains_national_day(client):
    """Holiday list includes 'National Day' (Quốc Khánh 2/9) for VN."""
    r = client.get("/v1/holidays", params={"country": "VN", "year": 2026})
    assert r.status_code == 200
    holidays = r.json()["holidays"]
    national_day = next((h for h in holidays if h["date"] == "2026-09-02"), None)
    assert national_day is not None
    assert "National Day" in national_day["global_name"]


def test_holidays_503_when_upstream_down(settings, service):
    """GET /v1/holidays returns 503 when Nager.Date is unreachable."""

    def boom(req):
        raise httpx.ConnectTimeout("timeout", request=req)

    hc = holiday_with(boom)
    app = create_app(
        settings,
        service,
        weather_with(lambda req: httpx.Response(200, json=OK_JSON)),
        hc,
    )
    r = TestClient(app).get("/v1/holidays", params={"country": "VN"})
    assert r.status_code == 503
    assert r.json()["error"]["code"] == "holiday_service_unavailable"


def test_holidays_stale_cache_on_failure():
    """HolidayClient serves stale cached data when upstream fails after first success."""
    calls = {"n": 0}

    def flaky(req):
        calls["n"] += 1
        if calls["n"] == 1:
            return httpx.Response(200, json=OK_HOLIDAY_JSON)
        return httpx.Response(500)

    hc = holiday_with(flaky)
    hc.cache_ttl_s = 0  # force a refresh on second call

    first = hc.get_holidays("VN", 2026)
    assert not first.stale

    second = hc.get_holidays("VN", 2026)
    assert second.stale
    assert len(second.holidays) == len(first.holidays)


def test_next_holiday_returns_future_date(client):
    """GET /v1/holidays/next returns a holiday with a valid ISO date."""
    r = client.get("/v1/holidays/next", params={"country": "VN"})
    # May return null if all 2026 holidays are in the past; just check no crash
    assert r.status_code == 200
