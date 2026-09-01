"""Job discovery sources and provider abstractions."""

from career_match.jobs.errors import JobProviderError, JobProviderNotConfiguredError
from career_match.jobs.protocol import JobOpportunity, JobSource
from career_match.jobs.query_builder import (
    JobSearchQuery,
    JobSearchQueryPlan,
    build_job_search_queries,
    build_job_search_query,
)

__all__ = [
    "JobOpportunity",
    "JobProviderError",
    "JobProviderNotConfiguredError",
    "JobSearchQuery",
    "JobSearchQueryPlan",
    "JobSource",
    "build_job_search_queries",
    "build_job_search_query",
]
