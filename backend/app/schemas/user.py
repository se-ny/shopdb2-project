from datetime import datetime
from typing import Optional, List, Literal

from pydantic import BaseModel, ConfigDict

UserStatus = Literal["ACTIVE", "INACTIVE", "SUSPENDED", "WITHDRAWN"]


class RoleResponse(BaseModel):
    role_id: int
    role_code: str
    role_name: str
    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class UserResponse(BaseModel):
    user_id: int
    org_id: Optional[int] = None
    login_id: str
    user_name: str
    email: str
    phone: Optional[str] = None
    user_status: UserStatus
    created_at: datetime
    updated_at: datetime
    roles: List[RoleResponse] = []

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    """상태 변경, 소속 조직 이동만 허용 (로그인 정보는 여기서 수정하지 않음)."""
    org_id: Optional[int] = None
    user_status: Optional[UserStatus] = None


class RoleAssign(BaseModel):
    role_id: int