from datetime import datetime
from pydantic import BaseModel, EmailStr, constr


class UserCreate(BaseModel):
    name: constr(min_length=2, max_length=256)
    email: EmailStr
    password: constr(min_length=8, max_length=128)


class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    is_active: bool
    is_verified: bool
    role: str
    created_at: datetime
    updated_at: datetime | None

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    refresh_token: str | None = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: constr(min_length=8, max_length=128)


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: constr(min_length=8, max_length=128)


class VerifyEmailRequest(BaseModel):
    token: str
