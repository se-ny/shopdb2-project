from pydantic import BaseModel


class LoginRequest(BaseModel):
    login_id: str
    password: str


class LoginResponse(BaseModel):
    user_id: int
    user_name: str
    org_id: int | None
    roles: list[str]
    access_token: str
    token_type: str = "bearer"


class MeResponse(BaseModel):
    user_id: int
    user_name: str
    org_id: int | None
    roles: list[str]