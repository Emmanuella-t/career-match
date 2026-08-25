"""Central API settings for Career Match serving and deployment.

Environment variables (optional):

- ``CAREER_MATCH_CORS_ORIGINS`` — comma-separated browser origins allowed
  by CORS. Defaults to local Next.js origins when unset.
- ``PORT`` — listen port for production startup scripts (default 8000).
- ``HOST`` — bind address for production startup (default ``0.0.0.0``).
- ``CAREER_MATCH_MODEL_CACHE_DIR`` — directory for Hugging Face /
  sentence-transformers model cache when the host needs an explicit path.
- ``CLERK_ISSUER`` / ``CLERK_JWKS_URL`` — Clerk JWT verification for
  persistence routes.
- ``SUPABASE_URL`` / ``SUPABASE_SERVICE_ROLE_KEY`` — Postgres persistence
  (backend only; never expose the service-role key to the browser).

Importing this module does not download MiniLM.
"""

from __future__ import annotations

import os

# Hard cap on resume_text / job_description length (characters after strip).
# Large enough for typical multi-page resumes and long JDs; small enough to
# reject accidental multi-megabyte payloads.
MAX_TEXT_CHARS = 50_000

# Local Next.js defaults. Production origins must come from
# CAREER_MATCH_CORS_ORIGINS — never use allow_origins=["*"] with credentials.
DEFAULT_CORS_ORIGINS: tuple[str, ...] = (
    "http://localhost:3000",
    "http://127.0.0.1:3000",
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

DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 8000


def parse_cors_origins(raw: str | None = None) -> tuple[str, ...]:
    """Parse a comma-separated CORS origin list.

    Empty / whitespace-only values fall back to ``DEFAULT_CORS_ORIGINS``.
    Trailing slashes are stripped so ``https://app.example.com/`` matches
    the browser Origin header.
    """
    if raw is None:
        raw = os.environ.get("CAREER_MATCH_CORS_ORIGINS")
    if raw is None or not str(raw).strip():
        return DEFAULT_CORS_ORIGINS
    origins = tuple(
        part.strip().rstrip("/")
        for part in str(raw).split(",")
        if part.strip()
    )
    return origins if origins else DEFAULT_CORS_ORIGINS


def get_cors_allow_origins() -> tuple[str, ...]:
    """Return CORS origins for the current process environment."""
    return parse_cors_origins()


# Backward-compatible name used by older docs/tests; reflects local defaults.
CORS_ALLOW_ORIGINS = DEFAULT_CORS_ORIGINS


def get_host() -> str:
    """Bind host for production startup (``HOST``, default ``0.0.0.0``)."""
    return os.environ.get("HOST", DEFAULT_HOST).strip() or DEFAULT_HOST


def get_port(default: int = DEFAULT_PORT) -> int:
    """Listen port from ``PORT`` when set, otherwise ``default``."""
    raw = os.environ.get("PORT")
    if raw is None or not str(raw).strip():
        return default
    try:
        port = int(str(raw).strip())
    except ValueError as exc:
        raise ValueError(f"PORT must be an integer, got {raw!r}") from exc
    if not (1 <= port <= 65535):
        raise ValueError(f"PORT out of range: {port}")
    return port


def apply_model_cache_env() -> None:
    """Apply ``CAREER_MATCH_MODEL_CACHE_DIR`` to HF cache env vars if set.

    Does not override ``HF_HOME`` / ``SENTENCE_TRANSFORMERS_HOME`` when those
    are already present. Does not download models.
    """
    cache = os.environ.get("CAREER_MATCH_MODEL_CACHE_DIR", "").strip()
    if not cache:
        return
    os.environ.setdefault("HF_HOME", cache)
    os.environ.setdefault("TRANSFORMERS_CACHE", cache)
    os.environ.setdefault("SENTENCE_TRANSFORMERS_HOME", cache)
    os.environ.setdefault("HUGGINGFACE_HUB_CACHE", os.path.join(cache, "hub"))
