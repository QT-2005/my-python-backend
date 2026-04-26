from typing import Literal
from pydantic import BaseModel, EmailStr, Field, field_validator


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=1, max_length=256)
    daily_goal_minutes: Literal[5, 10, 15] = 10  # FIX: sửa typo dayly -> daily
    current_level: Literal["A1", "A2", "B1", "B2", "C1", "C2"] = "A1"

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if not any(c.islower() for c in v):
            raise ValueError("Mật khẩu phải chứa ít nhất một chữ thường")
        if not any(c.isupper() for c in v):
            raise ValueError("Mật khẩu phải chứa ít nhất một chữ hoa")
        if not any(c.isdigit() for c in v):
            raise ValueError("Mật khẩu phải chứa ít nhất một chữ số")
        return v


class RegisterResponse(BaseModel):
    user_id: str
    email: str
    full_name: str
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    user_id: str
    email: str
    full_name: str
    current_level: str
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class RefreshResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ForgotPasswordResponse(BaseModel):
    message: str = "Nếu email tồn tại, bạn sẽ nhận được hướng dẫn đặt lại mật khẩu."


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(min_length=8, max_length=128)

    @field_validator("new_password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if not any(c.islower() for c in v):
            raise ValueError("Mật khẩu phải chứa ít nhất một chữ thường")
        if not any(c.isupper() for c in v):
            raise ValueError("Mật khẩu phải chứa ít nhất một chữ hoa")
        if not any(c.isdigit() for c in v):
            raise ValueError("Mật khẩu phải chứa ít nhất một chữ số")
        return v


class ResetPasswordResponse(BaseModel):
    message: str = "Mật khẩu đã được đặt lại thành công."


class ErrorResponse(BaseModel):
    detail: str