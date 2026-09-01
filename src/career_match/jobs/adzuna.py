"""Adzuna REST API client and response normalization."""

from __future__ import annotations

import json
import logging
import re
import urllib.error
import urllib.parse
import urllib.request
import uuid
from datetime import UTC, datetime
from typing import Any

from career_match.jobs.errors import JobProviderError
from career_match.jobs.protocol import JobOpportunity

logger = logging.getLogger(__name__)

ADZUNA_SOURCE = "adzuna"
ADZUNA_ATTRIBUTION_URL = "https://www.adzuna.com"
DEFAULT_TIMEOUT_SECONDS = 10.0
MAX_RESULTS_PER_PAGE = 50
MAX_SEARCH_QUERY_CHARS = 80
MAX_LOCATION_CHARS = 120

_ADZUNA_ID_NAMESPACE = uuid.UUID("f47ac10b-58cc-4372-a567-0e02b2c3d479")


def adzuna_configured(app_id: str | None, app_key: str | None) -> bool:
    return bool(app_id and app_key)


def normalize_adzuna_job(
    raw: dict[str, Any],
    *,
    fetched_at: datetime | None = None,
) -> JobOpportunity:
    """Map one Adzuna search result into a Career Match JobOpportunity."""
    external_id = str(raw.get("id", "")).strip()
    if not external_id:
        raise JobProviderError("adzuna result missing id")

    title = str(raw.get("title", "")).strip()
    if not title:
        raise JobProviderError("adzuna result missing title")

    company_block = raw.get("company") or {}
    company = None
    if isinstance(company_block, dict):
        company = str(company_block.get("display_name") or "").strip() or None

    location_block = raw.get("location") or {}
    location = None
    if isinstance(location_block, dict):
        location = str(location_block.get("display_name") or "").strip() or None

    description = str(raw.get("description") or "").strip()
    if not description:
        description = title

    redirect_url = str(raw.get("redirect_url") or "").strip() or None
    employment_type = _derive_employment_type(raw)
    created_at = _parse_timestamp(raw.get("created")) or (fetched_at or datetime.now(UTC))

    return JobOpportunity(
        id=uuid.uuid5(_ADZUNA_ID_NAMESPACE, f"adzuna:{external_id}"),
        title=title,
        company=company,
        location=location,
        description=description,
        source=ADZUNA_SOURCE,
        source_url=redirect_url,
        apply_url=redirect_url,
        employment_type=employment_type,
        created_at=created_at,
        updated_at=fetched_at or created_at,
    )


def _derive_employment_type(raw: dict[str, Any]) -> str | None:
    contract_time = str(raw.get("contract_time") or "").strip().lower()
    contract_type = str(raw.get("contract_type") or "").strip().lower()
    if contract_time == "full_time":
        return "full-time"
    if contract_time == "part_time":
        return "part-time"
    if contract_type == "permanent":
        return "permanent"
    if contract_type == "contract":
        return "contract"
    return None


def _parse_timestamp(value: Any) -> datetime | None:
    if not value:
        return None
    text = str(value).strip()
    if not text:
        return None
    normalized = text.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def sanitize_search_query(value: str) -> str:
    cleaned = re.sub(r"\s+", " ", value).strip()
    return cleaned[:MAX_SEARCH_QUERY_CHARS]


def sanitize_location(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = re.sub(r"\s+", " ", value).strip()
    if not cleaned:
        return None
    return cleaned[:MAX_LOCATION_CHARS]


class AdzunaClient:
    """Minimal Adzuna jobs search client (stdlib HTTP, no secrets logged)."""

    def __init__(
        self,
        *,
        app_id: str,
        app_key: str,
        country: str = "us",
        timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
    ) -> None:
        self._app_id = app_id.strip()
        self._app_key = app_key.strip()
        self._country = country.strip().lower() or "us"
        self._timeout = timeout_seconds

    def search(
        self,
        *,
        what: str,
        where: str | None = None,
        employment_type: str | None = None,
        page: int = 1,
        results_per_page: int = MAX_RESULTS_PER_PAGE,
    ) -> list[JobOpportunity]:
        what_clean = sanitize_search_query(what)
        if not what_clean:
            return []

        params: dict[str, str | int] = {
            "app_id": self._app_id,
            "app_key": self._app_key,
            "what": what_clean,
            "results_per_page": min(max(results_per_page, 1), MAX_RESULTS_PER_PAGE),
            "content-type": "application/json",
        }
        where_clean = sanitize_location(where)
        if where_clean:
            params["where"] = where_clean

        employment_params = _employment_type_params(employment_type)
        params.update(employment_params)

        url = (
            f"https://api.adzuna.com/v1/api/jobs/{self._country}/search/{max(page, 1)}"
        )
        query = urllib.parse.urlencode(params)
        request = urllib.request.Request(
            f"{url}?{query}",
            headers={"Accept": "application/json", "User-Agent": "CareerMatch/1.0"},
            method="GET",
        )

        try:
            with urllib.request.urlopen(request, timeout=self._timeout) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            logger.warning("adzuna http error status=%s", exc.code)
            raise JobProviderError("adzuna request failed") from exc
        except urllib.error.URLError as exc:
            logger.warning("adzuna network error")
            raise JobProviderError("adzuna request timed out or failed") from exc
        except (TimeoutError, json.JSONDecodeError) as exc:
            logger.warning("adzuna response parse failure")
            raise JobProviderError("adzuna response was malformed") from exc

        if not isinstance(payload, dict):
            raise JobProviderError("adzuna response was malformed")

        results = payload.get("results")
        if results is None:
            return []
        if not isinstance(results, list):
            raise JobProviderError("adzuna response was malformed")

        fetched_at = datetime.now(UTC)
        opportunities: list[JobOpportunity] = []
        for item in results:
            if not isinstance(item, dict):
                continue
            try:
                opportunities.append(
                    normalize_adzuna_job(item, fetched_at=fetched_at)
                )
            except JobProviderError:
                continue
        return opportunities


def _employment_type_params(employment_type: str | None) -> dict[str, int]:
    if not employment_type:
        return {}
    normalized = employment_type.strip().lower()
    if normalized in {"full-time", "full time", "fulltime"}:
        return {"full_time": 1}
    if normalized in {"part-time", "part time", "parttime"}:
        return {"part_time": 1}
    if normalized == "permanent":
        return {"permanent": 1}
    if normalized == "contract":
        return {"contract": 1}
    return {}
