"""Synthetic job opportunity fixtures for discovery tests only."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID, uuid4

from career_match.jobs.protocol import JobOpportunity

_NOW = datetime(2026, 1, 15, 12, 0, 0, tzinfo=UTC)


def make_synthetic_jobs() -> list[JobOpportunity]:
    """Build a small deterministic job set for ranking tests."""
    return [
      JobOpportunity(
          id=UUID("00000000-0000-4000-8000-000000000001"),
          title="Python Backend Engineer",
          company="Acme Labs",
          location="Remote",
          description=(
              "We are hiring a Python backend engineer with FastAPI, Docker, "
              "and SQL experience to build reliable services."
          ),
          source="synthetic-fixture",
          source_url="https://example.test/jobs/python-backend",
          apply_url="https://example.test/apply/python-backend",
          employment_type="full-time",
          created_at=_NOW,
          updated_at=_NOW,
      ),
      JobOpportunity(
          id=UUID("00000000-0000-4000-8000-000000000002"),
          title="Java Enterprise Developer",
          company="Legacy Systems Inc",
          location="New York, NY",
          description=(
              "Looking for a Java and Spring developer with enterprise middleware "
              "experience. Oracle and SOAP required."
          ),
          source="synthetic-fixture",
          source_url="https://example.test/jobs/java-enterprise",
          apply_url=None,
          employment_type="full-time",
          created_at=_NOW,
          updated_at=_NOW,
      ),
      JobOpportunity(
          id=UUID("00000000-0000-4000-8000-000000000003"),
          title="Remote Python Data Engineer",
          company="DataWorks",
          location="Remote",
          description=(
              "Build Python data pipelines with pandas, SQL, and Docker. "
              "Comfort with Git and Linux is required."
          ),
          source="synthetic-fixture",
          source_url="https://example.test/jobs/python-data",
          apply_url=None,
          employment_type="contract",
          created_at=_NOW,
          updated_at=_NOW,
      ),
  ]


def make_extra_job() -> JobOpportunity:
    return JobOpportunity(
        id=uuid4(),
        title="Placeholder Job",
        company="Fixture Co",
        location="Austin, TX",
        description="General software role with teamwork and communication.",
        source="synthetic-fixture",
        source_url=None,
        apply_url=None,
        employment_type="part-time",
        created_at=_NOW,
        updated_at=_NOW,
    )
