from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app.core.security import verify_password, create_access_token
from app.core.deps import get_current_user, CurrentUser
from app.models.user import User
from app.schemas.auth import LoginRequest, LoginResponse, MeResponse

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = (
        db.query(User)
        .options(joinedload(User.roles))
        .filter(User.login_id == payload.login_id)
        .first()
    )
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="아이디 또는 비밀번호가 올바르지 않습니다.")

    if user.user_status != "ACTIVE":
        raise HTTPException(status_code=403, detail="비활성화된 계정입니다.")

    role_codes = [r.role_code for r in user.roles]
    token = create_access_token(user.user_id, user.org_id, role_codes)

    return LoginResponse(
        user_id=user.user_id,
        user_name=user.user_name,
        org_id=user.org_id,
        roles=role_codes,
        access_token=token,
    )


@router.get("/me", response_model=MeResponse)
def get_me(current_user: CurrentUser = Depends(get_current_user)):
    return MeResponse(
        user_id=current_user.user_id,
        user_name=current_user.user_name,
        org_id=current_user.org_id,
        roles=current_user.roles,
    )