"""Career Match HTTP API (FastAPI).

Importing this package does **not** download MiniLM. Semantic and hybrid
matchers load their encoder lazily on first scoring request through the
shared ``MatcherService``.
"""

from career_match.api.app import app, create_app

__all__ = ["app", "create_app"]
