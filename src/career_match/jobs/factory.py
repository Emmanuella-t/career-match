"""Job source factory for provider-neutral discovery."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

from career_match.jobs.adzuna import AdzunaClient, adzuna_configured
from career_match.jobs.adzuna_source import AdzunaJobSource
from career_match.jobs.protocol import JobSource

if TYPE_CHECKING:
    from career_match.persistence.store import PersistenceStore


def get_adzuna_settings() -> tuple[str | None, str | None, str]:
    app_id = os.environ.get("ADZUNA_APP_ID", "").strip() or None
    app_key = os.environ.get("ADZUNA_APP_KEY", "").strip() or None
    country = os.environ.get("ADZUNA_COUNTRY", "us").strip().lower() or "us"
    return app_id, app_key, country


def adzuna_is_configured() -> bool:
    """Return whether Adzuna external job search credentials are present."""
    app_id, app_key, _country = get_adzuna_settings()
    return adzuna_configured(app_id, app_key)


def create_job_source(
    store: PersistenceStore,
    *,
    override: JobSource | None = None,
) -> JobSource:
    """Return the configured job source for discovery."""
    if override is not None:
        return override

    app_id, app_key, country = get_adzuna_settings()
    if adzuna_configured(app_id, app_key):
        client = AdzunaClient(app_id=app_id, app_key=app_key, country=country)
        return AdzunaJobSource(client)

    from career_match.jobs.sources import PostgresJobOpportunitySource

    return PostgresJobOpportunitySource(store)
