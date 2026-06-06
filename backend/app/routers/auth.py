from fastapi import APIRouter, Header

from app import schemas
from app.services import auth

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/status", response_model=schemas.AuthStatus)
def get_auth_status() -> schemas.AuthStatus:
    return schemas.AuthStatus.model_validate(auth.get_auth_status())


@router.get("/me", response_model=schemas.AuthMeResponse)
def get_current_auth_user(
    authorization: str | None = Header(default=None),
) -> schemas.AuthMeResponse:
    status_data = auth.get_auth_status()
    user = auth.get_current_user_from_authorization(authorization)

    if user is None:
        if status_data["verification_configured"]:
            message = "No authenticated user. Local fallback data ownership is enabled when auth is not required."
        else:
            message = "Authentication verification is disabled for local development; app data uses the local fallback user."
        return schemas.AuthMeResponse(
            authenticated=False,
            auth_required=bool(status_data["auth_required"]),
            verification_configured=bool(status_data["verification_configured"]),
            user=None,
            message=message,
        )

    return schemas.AuthMeResponse(
        authenticated=True,
        auth_required=bool(status_data["auth_required"]),
        verification_configured=bool(status_data["verification_configured"]),
        user=schemas.AuthUserRead(
            user_id=user.user_id,
            email=user.email,
            raw_claims=user.raw_claims,
        ),
        message="Authenticated with Supabase access token.",
    )
