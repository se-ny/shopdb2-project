from datetime import datetime
from typing import Optional, List, Literal

from pydantic import BaseModel, ConfigDict, EmailStr

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


class UserCreate(BaseModel):
    """관리자가 직접 계정을 발급할 때 사용 (예: 관리자 계정, 테스트 계정)."""
    login_id: str
    password: str
    user_name: str
    email: EmailStr
    phone: Optional[str] = None
    org_id: Optional[int] = None
    role_ids: List[int] = []


class RoleAssign(BaseModel):
    role_id: int