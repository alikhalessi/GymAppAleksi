from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import or_
from sqlalchemy.sql.elements import ColumnElement

from app.services.auth import AuthUser, LOCAL_FALLBACK_USER_ID


def allows_legacy_unowned_rows(user: AuthUser) -> bool:
    return user.user_id == LOCAL_FALLBACK_USER_ID and user.source == "local_fallback"


def ownership_filter(model: Any, user: AuthUser) -> ColumnElement[bool]:
    user_id_column = model.user_id
    if allows_legacy_unowned_rows(user):
        return or_(user_id_column == user.user_id, user_id_column.is_(None))
    return user_id_column == user.user_id


def is_owned_by_user(record: Any, user: AuthUser) -> bool:
    record_user_id = getattr(record, "user_id", None)
    return record_user_id == user.user_id or (
        record_user_id is None and allows_legacy_unowned_rows(user)
    )


def require_owned(record: Any | None, user: AuthUser, detail: str) -> Any:
    if record is None or not is_owned_by_user(record, user):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
    return record
