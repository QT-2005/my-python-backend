import secrets
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.models.user_meta import UserSettings, UserStats
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

# Lưu tạm reset token trong memory (production nên dùng Redis hoặc DB)
_reset_tokens: dict[str, dict] = {}


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_by_id(self, user_id: str) -> User | None:
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalars().first()

    async def get_user_by_email(self, email: str) -> User | None:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalars().first()

    # app/services/auth_service.py

    async def register(self, data: RegisterRequest) -> RegisterResponse:
        if await self.get_user_by_email(data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email đã được sử dụng.",
            )

        user = User(
            email=data.email,
            full_name=data.full_name,
            password_hash=hash_password(data.password),
            daily_goal_minutes=data.daily_goal_minutes,
            current_level=data.current_level,
        )

        self.db.add(user)
        await self.db.flush()  # Lưu tạm để lấy user.id

        # Kiểm tra nếu UserSettings đã tồn tại
        result = await self.db.execute(select(UserSettings).filter_by(user_id=user.id))
        existing_user_settings = result.scalars().first()

        if not existing_user_settings:
            self.db.add(UserSettings(user_id=user.id))
        
        # Kiểm tra và thêm UserStats nếu chưa có
        result_stats = await self.db.execute(select(UserStats).filter_by(user_id=user.id))
        existing_user_stats = result_stats.scalars().first()
        
        if not existing_user_stats:
            self.db.add(UserStats(user_id=user.id))

        await self.db.commit()
        await self.db.refresh(user)

        return RegisterResponse(
            user_id=user.id,
            email=user.email,
            full_name=user.full_name,
            access_token=create_access_token(user.id),
            refresh_token=create_refresh_token(user.id),
        )

    async def login(self, data: LoginRequest) -> LoginResponse:
        user = await self.get_user_by_email(data.email)
        if not user or not verify_password(data.password, user.password_hash):  # FIX: password_hash
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email hoặc mật khẩu không đúng.",
            )
        return LoginResponse(
            user_id=user.id,
            email=user.email,
            full_name=user.full_name,
            current_level=user.current_level,
            access_token=create_access_token(user.id),
            refresh_token=create_refresh_token(user.id),
        )

    async def refresh_token(self, data: RefreshRequest) -> RefreshResponse:  # FIX: nhận RefreshRequest
        payload = decode_token(data.refresh_token)

        if not payload or payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token không hợp lệ hoặc đã hết hạn.",
            )
        user = await self.get_user_by_id(payload["sub"])
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Tài khoản không tồn tại.",
            )
        return RefreshResponse(
            access_token=create_access_token(user.id)
        )

    async def forgot_password(self, data: ForgotPasswordRequest) -> ForgotPasswordResponse:
        user = await self.get_user_by_email(data.email)
        if user:
            # Tạo reset token
            token = secrets.token_urlsafe(32)
            # Lưu reset token vào _reset_tokens cùng với thông tin người dùng và thời gian hết hạn
            _reset_tokens[token] = {
                "user_id": user.id,
                "expires": datetime.now(timezone.utc) + timedelta(hours=1),  # Token có hạn trong 1 giờ
            }
            # Gửi email (ở đây là chỉ mock)
            await self.send_reset_email(data.email, token)
        return ForgotPasswordResponse()

    async def reset_password(self, data: ResetPasswordRequest) -> ResetPasswordResponse:
        record = _reset_tokens.get(data.token)
        
        if not record or datetime.now(timezone.utc) > record["expires"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token không hợp lệ hoặc đã hết hạn.",
            )
        
        # Lấy thông tin người dùng từ _reset_tokens
        user = await self.get_user_by_id(record["user_id"])
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tài khoản không tồn tại.",
            )
        
        # Cập nhật mật khẩu cho người dùng
        user.password_hash = hash_password(data.new_password)
        await self.db.commit()
        
        # Xóa token đã sử dụng khỏi bộ nhớ
        del _reset_tokens[data.token]

        return ResetPasswordResponse()

    async def send_reset_email(self, email: str, token: str):
        # TODO: Tích hợp SMTP thật (settings.SMTP_HOST, SMTP_USER, ...)
        reset_link = f"http://example.com/reset-password?token={token}"
        print(f"[DEV] Gửi email đến {email} với link: {reset_link}")