from __future__ import annotations

from dataclasses import dataclass
import os
from typing import Any

import jwt
from fastapi import HTTPException, status


@dataclass(frozen=True)
class AuthUser:
    user_id: str
    email: str | None
    raw_claims: dict[str, Any]


def _env_is_true(value: str | None) -> bool:
    return (value or "").strip().lower() in {"1", "true", "yes", "on"}


def is_auth_required() -> bool:
    return _env_is_true(os.getenv("AUTH_REQUIRED"))


def get_auth_status() -> dict[str, bool | str]:
    jwt_secret_configured = bool(os.getenv("SUPABASE_JWT_SECRET"))
    jwks_url_configured = bool(os.getenv("SUPABASE_JWKS_URL"))

    verification_mode = "disabled"
    if jwt_secret_configured:
        verification_mode = "jwt_secret"
    elif jwks_url_configured:
        verification_mode = "jwks_pending"

    return {
        "auth_required": is_auth_required(),
        "supabase_url_configured": bool(os.getenv("SUPABASE_URL")),
        "jwt_secret_configured": jwt_secret_configured,
        "jwks_url_configured": jwks_url_configured,
        "verification_configured": jwt_secret_configured,
        "verification_mode": verification_mode,
    }


def parse_bearer_token(authorization: str | None) -> str | None:
    if not authorization:
        return None

    scheme, _, token = authorization.strip().partition(" ")
    if scheme.lower() != "bearer" or not token.strip():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header must use Bearer token format.",
        )

    return token.strip()


def verify_supabase_jwt(token: str) -> AuthUser:
    jwt_secret = os.getenv("SUPABASE_JWT_SECRET")
    if not jwt_secret:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Supabase JWT verification is not configured.",
        )

    try:
        claims = jwt.decode(
            token,
            jwt_secret,
            algorithms=["HS256"],
            options={"verify_aud": False},
        )
    except jwt.InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Supabase access token.",
        ) from exc

    user_id = str(claims.get("sub") or "").strip()
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Supabase access token is missing a subject.",
        )

    email = claims.get("email")
    return AuthUser(
        user_id=user_id,
        email=str(email) if email else None,
        raw_claims=claims,
    )


def get_current_user_from_authorization(authorization: str | None) -> AuthUser | None:
    token = parse_bearer_token(authorization)
    if token is None:
        if is_auth_required():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required.",
            )
        return None

    status_data = get_auth_status()
    if not status_data["verification_configured"]:
        if is_auth_required():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Authentication is required but Supabase JWT verification is not configured.",
            )
        return None

    return verify_supabase_jwt(token)
