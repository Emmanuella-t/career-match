"""Central API settings for Career Match serving."""

from __future__ import annotations

# Hard cap on resume_text / job_description length (characters after strip).
# Large enough for typical multi-page resumes and long JDs; small enough to
# reject accidental multi-megabyte payloads.
MAX_TEXT_CHARS = 50_000

# Development browser origins for the Next.js prototype. Not a production
# open-CORS policy.
CORS_ALLOW_ORIGINS: tuple[str, ...] = (
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:43173",
    "http://localhost:43173",
)

DEFAULT_MATCHER = "semantic"
SUPPORTED_MATCHERS: tuple[str, ...] = ("semantic", "hybrid", "lexical")

SCORE_DISCLAIMER = (
    "This score reflects resume-to-job relevance and is not a hiring probability."
)

API_TITLE = "Career Match API"
API_VERSION = "0.1.0"
API_DESCRIPTION = (
    "HTTP service for Career Match resume-to-job relevance scoring. "
    "Scores are development relevance signals, not hiring decisions."
)
