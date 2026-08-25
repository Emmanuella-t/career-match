#!/usr/bin/env python3
"""Production startup for the Career Match FastAPI service.

Respects environment variables:

- ``HOST`` (default ``0.0.0.0``)
- ``PORT`` (default ``8000``)
- ``CAREER_MATCH_CORS_ORIGINS``
- ``CAREER_MATCH_MODEL_CACHE_DIR``

Usage::

    python scripts/start_api_production.py

Equivalent::

    uvicorn career_match.api.app:app --host 0.0.0.0 --port $PORT

Local development should continue to use ``scripts/run_api.py --reload``
or uvicorn with ``--reload`` on ``127.0.0.1``.
"""

from __future__ import annotations


def main() -> None:
    from career_match.api.settings import apply_model_cache_env, get_host, get_port

    apply_model_cache_env()
    host = get_host()
    port = get_port()

    import uvicorn

    uvicorn.run(
        "career_match.api.app:app",
        host=host,
        port=port,
        reload=False,
    )


if __name__ == "__main__":
    main()
