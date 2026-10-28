"""External integration: Public holidays via Nager.Date API (no API key needed).

Demonstrates three habits for any external service call:
  - timeout      – never block the server indefinitely
  - retry        – retry once on transient network errors
  - cache fallback – serve stale data rather than a hard 503

API used: https://date.nager.at/api/v3/PublicHolidays/{year}/{countryCode}
(free, no auth, JSON response)
"""

from __future__ import annotations

import logging
import time
from datetime import date, datetime, timezone

import httpx

from assistant_api.schemas import Holiday, HolidayList

log = logging.getLogger("assistant_api.holiday")

NAGER_BASE = "https://date.nager.at/api/v3"


class HolidayServiceError(Exception):
    """Upstream holiday service failed and no cached value is available."""


class HolidayClient:
    """Fetch public holidays from Nager.Date with timeout, retry, and cache fallback."""

    def __init__(
        self,
        base_url: str = NAGER_BASE,
        timeout_s: float = 5.0,
        retries: int = 1,
        cache_ttl_s: float = 86_400,  # 24 h — holiday lists rarely change
        transport: httpx.BaseTransport | None = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.retries = retries
        self.cache_ttl_s = cache_ttl_s
        self._client = httpx.Client(timeout=timeout_s, transport=transport)
        # cache: key=(year, country_code) → (monotonic_timestamp, HolidayList)
        self._cache: dict[tuple[int, str], tuple[float, HolidayList]] = {}

    # ------------------------------------------------------------------
    def get_holidays(self, country_code: str = "VN", year: int | None = None) -> HolidayList:
        """Return public holidays for *country_code* in *year* (default: current year).

        Failure modes handled:
          - timeout          → retry, then stale cache, then HolidayServiceError
          - non-200 status   → same escalation
          - malformed JSON   → same escalation
        """
        if year is None:
            year = datetime.now(timezone.utc).year

        cache_key = (year, country_code.upper())
        cached = self._cache.get(cache_key)
        if cached and time.monotonic() - cached[0] < self.cache_ttl_s:
            return cached[1]

        url = f"{self.base_url}/PublicHolidays/{year}/{country_code.upper()}"
        last_exc: Exception | None = None

        for attempt in range(self.retries + 1):
            try:
                resp = self._client.get(url)
                resp.raise_for_status()
                items = resp.json()
                holiday_list = HolidayList(
                    country_code=country_code.upper(),
                    year=year,
                    holidays=[
                        Holiday(
                            date=item["date"],
                            name=item.get("localName") or item["name"],
                            global_name=item["name"],
                        )
                        for item in items
                    ],
                    stale=False,
                )
                self._cache[cache_key] = (time.monotonic(), holiday_list)
                return holiday_list
            except (httpx.HTTPError, KeyError, ValueError) as exc:
                last_exc = exc
                log.warning(
                    "holiday attempt %d failed for %s/%s: %s",
                    attempt + 1,
                    country_code,
                    year,
                    type(exc).__name__,
                )
                time.sleep(0.3 * (attempt + 1))

        # graceful fallback: serve stale cached result if available
        if cached:
            log.warning("serving stale holiday cache for %s/%s", country_code, year)
            return cached[1].model_copy(update={"stale": True})

        raise HolidayServiceError(f"holiday service unavailable for {country_code}/{year}") from last_exc

    def next_holiday(self, country_code: str = "VN") -> Holiday | None:
        """Return the next upcoming public holiday (or None if none found)."""
        today = date.today().isoformat()
        data = self.get_holidays(country_code)
        upcoming = [h for h in data.holidays if h.date >= today]
        return upcoming[0] if upcoming else None
