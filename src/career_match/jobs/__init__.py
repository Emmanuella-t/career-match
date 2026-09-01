"""Job discovery sources and provider abstractions."""

from career_match.jobs.errors import JobProviderError, JobProviderNotConfiguredError
from career_match.jobs.protocol import JobOpportunity, JobSource
from career_match.jobs.query_builder import JobSearchQuery, build_job_search_query

__all__ = [
    "JobOpportunity",
    "JobProviderError",
    "JobProviderNotConfiguredError",
    "JobSearchQuery",
    "JobSource",
    "build_job_search_query",
]
