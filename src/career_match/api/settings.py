"""Central API settings for Career Match serving and deployment.

Environment variables (optional):

- Root ``.env`` at the repository root is loaded automatically on API import
  (``override=False`` so real deployment env vars win).
- ``CAREER_MATCH_CORS_ORIGINS`` — comma-separated browser origins allowed
  by CORS. Defaults to local Next.js origins when unset.
- ``PORT`` — listen port for production startup scripts (default 8000).
- ``HOST`` — bind address for production startup (default ``0.0.0.0``).
- ``CAREER_MATCH_MODEL_CACHE_DIR`` — directory for Hugging Face /
  sentence-transformers model cache when the host needs an explicit path.
- ``CLERK_ISSUER`` (canonical) / ``CLERK_ISSUER_URL`` (legacy alias) /
  ``CLERK_JWKS_URL`` — Clerk JWT verification for authenticated routes.
- ``DATABASE_URL`` — PostgreSQL connection string (Neon in production;
  backend only — never expose to the browser).
- ``ADZUNA_APP_ID`` / ``ADZUNA_APP_KEY`` / ``ADZUNA_COUNTRY`` — Adzuna job
  search provider (backend only).
- Resume uploads are parsed in memory with a ``2 MiB`` file size cap
  (``MAX_RESUME_FILE_BYTES``). Supported formats: PDF and DOCX.

Importing this module loads the root ``.env`` when present. It does not
download MiniLM.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_PROJECT_ROOT: Path | None = None

# Hard cap on resume_text / job_description length (characters after strip).
# Large enough for typical multi-page resumes and long JDs; small enough to
# reject accidental multi-megabyte payloads.
MAX_TEXT_CHARS = 50_000

# Conservative in-memory upload cap for resume PDF/DOCX parsing (2 MiB).
MAX_RESUME_FILE_BYTES = 2 * 1024 * 1024

# Local Next.js defaults. Production origins must come from
# CAREER_MATCH_CORS_ORIGINS — never use allow_origins=["*"] with credentials.
DEFAULT_CORS_ORIGINS: tuple[str, ...] = (
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3001",
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


def find_project_root() -> Path:
    """Return the repository root (directory containing ``pyproject.toml``)."""
    global _PROJECT_ROOT
    if _PROJECT_ROOT is not None:
        return _PROJECT_ROOT
    for parent in Path(__file__).resolve().parents:
        if (parent / "pyproject.toml").is_file():
            _PROJECT_ROOT = parent
            return parent
    _PROJECT_ROOT = Path(__file__).resolve().parents[3]
    return _PROJECT_ROOT


def load_local_env_file() -> bool:
    """Load repository-root ``.env`` for local development.

    Uses ``override=False`` so process / platform environment variables always
    win. Missing ``.env`` is normal in production and is not an error.
    """
    try:
        from dotenv import load_dotenv
    except ImportError:  # pragma: no cover - optional until api extra installed
        return False

    env_path = find_project_root() / ".env"
    if not env_path.is_file():
        return False
    return load_dotenv(env_path, override=False)


def get_runtime_config_status() -> dict[str, Any]:
    """Non-secret configuration snapshot for startup diagnostics."""
    from career_match.api.auth import get_clerk_issuer
    from career_match.jobs.factory import adzuna_is_configured
    from career_match.persistence.database import database_configured

    return {
        "database_configured": database_configured(),
        "clerk_issuer_configured": get_clerk_issuer() is not None,
        "adzuna_configured": adzuna_is_configured(),
        "cors_origins": get_cors_allow_origins(),
    }


def log_startup_config() -> None:
    """Log safe local configuration flags (never secrets)."""
    flag = os.environ.get("CAREER_MATCH_LOG_STARTUP_CONFIG", "1").strip().lower()
    if flag in {"0", "false", "no", "off"}:
        return
    status = get_runtime_config_status()
    logger.info(
        "Career Match startup config: database=%s clerk=%s adzuna=%s cors=%s",
        "yes" if status["database_configured"] else "no",
        "yes" if status["clerk_issuer_configured"] else "no",
        "yes" if status["adzuna_configured"] else "no",
        ", ".join(status["cors_origins"]),
    )


load_local_env_file()
