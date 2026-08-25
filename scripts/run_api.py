#!/usr/bin/env python3
"""Run the Career Match FastAPI service with uvicorn.

Usage:
    python scripts/run_api.py
    python scripts/run_api.py --port 8000 --reload

``--port`` defaults to ``PORT`` when set, otherwise 8000.
``--host`` defaults to 127.0.0.1 for local development.

Importing the app does not download MiniLM; the semantic encoder loads on
the first semantic/hybrid match request.

For production binding (0.0.0.0 + PORT), use::

    python scripts/start_api_production.py
"""

from __future__ import annotations

import argparse
import os


def main() -> None:
    default_port = int(os.environ["PORT"]) if os.environ.get("PORT", "").strip() else 8000
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=default_port)
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload for local development.",
    )
    args = parser.parse_args()

    import uvicorn

    uvicorn.run(
        "career_match.api.app:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
    )


if __name__ == "__main__":
    main()
