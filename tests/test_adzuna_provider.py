"""Tests for Adzuna response normalization and client behavior."""

from __future__ import annotations

import io
import json
from datetime import UTC, datetime
from unittest.mock import patch

import pytest

from career_match.jobs.adzuna import (
    AdzunaClient,
    adzuna_configured,
    normalize_adzuna_job,
    sanitize_search_query,
)
from career_match.jobs.errors import JobProviderError


def test_adzuna_configured_requires_both_credentials() -> None:
    assert adzuna_configured("id", "key") is True
    assert adzuna_configured("id", None) is False
    assert adzuna_configured(None, "key") is False


def test_normalize_adzuna_job_maps_fields() -> None:
    fetched_at = datetime(2026, 1, 1, tzinfo=UTC)
    raw = {
        "id": "12345",
        "title": "Python Engineer",
        "company": {"display_name": "Acme Labs"},
        "location": {"display_name": "Austin, TX"},
        "description": "Build Python APIs with FastAPI.",
        "redirect_url": "https://www.adzuna.com/jobs/landing/12345",
        "created": "2026-01-01T12:00:00Z",
        "contract_time": "full_time",
        "contract_type": "permanent",
    }
    job = normalize_adzuna_job(raw, fetched_at=fetched_at)
    assert job.title == "Python Engineer"
    assert job.company == "Acme Labs"
    assert job.location == "Austin, TX"
    assert job.source == "adzuna"
    assert job.source_url == "https://www.adzuna.com/jobs/landing/12345"
    assert job.apply_url == job.source_url
    assert job.employment_type == "full-time"


def test_normalize_rejects_missing_id() -> None:
    with pytest.raises(JobProviderError):
        normalize_adzuna_job({"title": "Role"})


def test_sanitize_search_query_caps_length() -> None:
    assert len(sanitize_search_query("x" * 200)) == 80


def test_client_search_parses_results() -> None:
    payload = {
        "results": [
            {
                "id": "1",
                "title": "Backend Engineer",
                "company": {"display_name": "Beta"},
                "location": {"display_name": "Remote"},
                "description": "Python and Docker.",
                "redirect_url": "https://www.adzuna.com/jobs/landing/1",
            }
        ]
    }
    body = io.BytesIO(json.dumps(payload).encode("utf-8"))

    class _FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self):
            return body.getvalue()

    client = AdzunaClient(app_id="app", app_key="key", country="us")
    with patch("career_match.jobs.adzuna.urllib.request.urlopen", return_value=_FakeResponse()):
        jobs = client.search(what="python engineer", where="austin")

    assert len(jobs) == 1
    assert jobs[0].title == "Backend Engineer"
    assert "app" not in jobs[0].description


def test_client_search_does_not_send_resume_text() -> None:
    captured: dict[str, str] = {}

    class _FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self):
            return json.dumps({"results": []}).encode("utf-8")

    def _fake_urlopen(request, timeout=0):
        captured["url"] = request.full_url
        return _FakeResponse()

    client = AdzunaClient(app_id="app", app_key="key")
    with patch("career_match.jobs.adzuna.urllib.request.urlopen", side_effect=_fake_urlopen):
        client.search(what="python engineer", where="austin")

    assert "what=python+engineer" in captured["url"]
    assert "Jordan" not in captured["url"]


def test_client_http_error_raises_provider_error() -> None:
    import urllib.error

    client = AdzunaClient(app_id="app", app_key="key")
    with patch(
        "career_match.jobs.adzuna.urllib.request.urlopen",
        side_effect=urllib.error.HTTPError(
            url="https://api.adzuna.com",
            code=500,
            msg="error",
            hdrs=None,
            fp=None,
        ),
    ):
        with pytest.raises(JobProviderError):
            client.search(what="python")


def test_client_malformed_response_raises() -> None:
    class _FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self):
            return b"not-json"

    client = AdzunaClient(app_id="app", app_key="key")
    with patch("career_match.jobs.adzuna.urllib.request.urlopen", return_value=_FakeResponse()):
        with pytest.raises(JobProviderError):
            client.search(what="python")
