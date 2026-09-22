from dataclasses import dataclass

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.user import User


bearer_scheme = HTTPBearer(auto_error=False)


@dataclass
class CurrentUser:
    user_id: int
    user_name: str
    org_id: int | None
    roles: list[str]


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> CurrentUser:
    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail="인증 토큰이 필요합니다.",
        )

    if credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=401,
            detail="Bearer 인증 방식이 필요합니다.",
        )

    token = credentials.credentials.strip()

    try:
        payload = decode_access_token(token)
    except ValueError as error:
        raise HTTPException(
            status_code=401,
            detail=str(error),
        ) from error

    try:
        user_id = int(payload["sub"])
    except (KeyError, TypeError, ValueError) as error:
        raise HTTPException(
            status_code=401,
            detail="유효하지 않은 인증 토큰입니다.",
        ) from error

    user = db.query(User).filter(User.user_id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="존재하지 않는 사용자입니다.",
        )

    return CurrentUser(
        user_id=user.user_id,
        user_name=user.user_name,
        org_id=payload.get("org_id"),
        roles=payload.get("roles", []),
    )


def require_role(*allowed_roles: str):
    """특정 역할만 접근할 수 있도록 검사하는 의존성입니다."""

    def checker(
        current_user: CurrentUser = Depends(get_current_user),
    ) -> CurrentUser:
        if not any(role in current_user.roles for role in allowed_roles):
            raise HTTPException(
                status_code=403,
                detail="이 작업을 수행할 권한이 없습니다.",
            )

        return current_user

    return checker