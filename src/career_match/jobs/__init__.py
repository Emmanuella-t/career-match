"""Job discovery sources and provider abstractions."""

from career_match.jobs.protocol import JobOpportunity, JobSource
from career_match.jobs.sources import InMemoryJobSource, PostgresJobOpportunitySource

__all__ = [
    "InMemoryJobSource",
    "JobOpportunity",
    "JobSource",
    "PostgresJobOpportunitySource",
]
