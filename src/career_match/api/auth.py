"""Clerk session JWT verification for FastAPI persistence routes.

The frontend sends ``Authorization: Bearer <session_token>`` from Clerk
``getToken()``. The backend verifies the token against Clerk JWKS and
reads ``sub`` as the Clerk user id. Client-supplied user ids are ignored.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from typing import Annotated, Any

from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from career_match.api.user_messages import AUTH_UNAVAILABLE

_bearer = HTTPBearer(auto_error=False)


@dataclass(frozen=True, slots=True)
class ClerkIdentity:
    """Verified Clerk principal."""

    user_id: str
    email: str | None = None
    display_name: str | None = None


class ClerkAuthError(Exception):
    """Token missing, invalid, or misconfigured issuer."""


def get_clerk_issuer() -> str | None:
    raw = os.environ.get("CLERK_ISSUER", "").strip()
    if not raw:
        raw = os.environ.get("CLERK_ISSUER_URL", "").strip()
    return raw.rstrip("/") or None


def get_clerk_jwks_url() -> str | None:
    explicit = os.environ.get("CLERK_JWKS_URL", "").strip()
    if explicit:
        return explicit
    issuer = get_clerk_issuer()
    if not issuer:
        return None
    return f"{issuer}/.well-known/jwks.json"


@lru_cache(maxsize=1)
def _jwks_client() -> Any:
    jwks_url = get_clerk_jwks_url()
    if not jwks_url:
        raise ClerkAuthError("Clerk issuer is not configured")
    try:
        import jwt
    except ImportError as exc:  # pragma: no cover
        raise ClerkAuthError("PyJWT is not installed") from exc
    return jwt.PyJWKClient(jwks_url)


def verify_clerk_token(token: str) -> ClerkIdentity:
    """Verify a Clerk session JWT and return the Clerk user id (``sub``)."""
    issuer = get_clerk_issuer()
    if not issuer:
        raise ClerkAuthError("Clerk issuer is not configured")
    try:
        import jwt
    except ImportError as exc:  # pragma: no cover
        raise ClerkAuthError("PyJWT is not installed") from exc

    try:
        signing_key = _jwks_client().get_signing_key_from_jwt(token)
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            issuer=issuer,
            options={
                "require": ["exp", "iss", "sub"],
                "verify_aud": False,
            },
        )
    except ClerkAuthError:
        raise
    except Exception as exc:  # noqa: BLE001 - map all JWT failures to auth error
        raise ClerkAuthError("invalid or expired token") from exc

    user_id = payload.get("sub")
    if not isinstance(user_id, str) or not user_id.strip():
        raise ClerkAuthError("token missing subject")

    email = payload.get("email")
    if not isinstance(email, str) or not email.strip():
        email = None

    display_name = payload.get("name")
    if not isinstance(display_name, str) or not display_name.strip():
        display_name = None

    return ClerkIdentity(
        user_id=user_id.strip(),
        email=email.strip() if email else None,
        display_name=display_name.strip() if display_name else None,
    )


def reset_clerk_jwks_cache() -> None:
    """Clear cached JWKS client (tests / env changes)."""
    _jwks_client.cache_clear()


async def require_clerk_user(
    request: Request,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
) -> ClerkIdentity:
    """FastAPI dependency: require a verified Clerk Bearer token."""
    override = getattr(request.app.state, "clerk_identity_override", None)
    if override is not None:
        if callable(override):
            return override(request)
        return override

    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="authentication required")

    try:
        return verify_clerk_token(credentials.credentials)
    except ClerkAuthError as exc:
        detail = str(exc)
        if "not configured" in detail.lower() or "not installed" in detail.lower():
            raise HTTPException(
                status_code=503,
                detail=AUTH_UNAVAILABLE,
            ) from exc
        raise HTTPException(status_code=401, detail="invalid or expired token") from exc
