from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User

from app.schemas.auth_schema import (
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    LoginRequest,
    LoginResponse,
    RefreshRequest,
    RefreshResponse,
    RegisterRequest,
    RegisterResponse,
    ResetPasswordRequest,
    ResetPasswordResponse,
)

from app.services.auth_service import AuthService
router = APIRouter(prefix="/auth", tags=["auth"])

@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Đăng ký tài khoản mới",
)
async def register(
    data: RegisterRequest,
    db: AsyncSession = Depends(get_db),
) -> RegisterResponse:
    """Đăng ký tài khoản mới với email, mật khẩu và thông tin cá nhân."""
    return await AuthService(db).register(data)

@router.post(
    "/login",
    response_model=LoginResponse,
    summary="Đăng nhập",
)
async def login(
    data: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> LoginResponse:
    """Đăng nhập bằng email và mật khẩu để nhận access token và refresh token."""
    return await AuthService(db).login(data)

@router.post(
    "/refresh",
    response_model=RefreshResponse,
    summary="Làm mới access token", 
)
async def refresh_token(
    data: RefreshRequest,
    db: AsyncSession = Depends(get_db),
)-> RefreshResponse:
    """Làm mới access token bằng refresh token."""
    return await AuthService(db).refresh_token(data)

@router.post(
    "/forgot-password",
    response_model=ForgotPasswordResponse,
    summary="Quên mật khẩu",
)
async def forgot_password(
    data: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db),
) -> ForgotPasswordResponse:
    """Gửi email để đặt lại mật khẩu."""
    return await AuthService(db).forgot_password(data)

@router.post(
    "/reset-password",
    response_model=ResetPasswordResponse,
    summary="Đặt lại mật khẩu",
)
async def reset_password(
    data: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
) -> ResetPasswordResponse:
    """Đặt lại mật khẩu."""
    return await AuthService(db).reset_password(data)

@router.get(
    "/me",
    summary="Thông tin tài khoản hiện tại",
)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
) -> dict:
    """kiểm tra token còn hợp lệ hay không, trả về thông tin cơ bản."""
    return {
        "user_id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "current_level": current_user.current_level,
    }