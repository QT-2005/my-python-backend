from datetime import date
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import User
from app.schemas.user_schema import (
    UpdateUserSettingsRequest,
    ChangePasswordRequest
)
from app.core.security import verify_password, get_password_hash


class UserService:
    def __init__(self, db: Session):
        self.db = db

    # =========================
    # 1. DASHBOARD
    # =========================
    def get_dashboard(self, user: User):
        stats = user.stats

        return {
            "streak": stats.streak_count if stats else 0,
            "today_xp": self._calculate_today_xp(user.id),
            "total_xp": stats.total_xp if stats else 0,
            "daily_goal_minutes": user.daily_goal_minutes,
            "message": "Keep going!"
        }

    def _calculate_today_xp(self, user_id: str) -> int:
        """
        TODO: query từ user_progress
        """
        return 0

    # =========================
    # 2. PROFILE
    # =========================
    def get_profile(self, user: User):
        stats = user.stats

        return {
            "email": user.email,
            "full_name": user.full_name,
            "avatar_url": user.avatar_url,
            "current_level": user.current_level,

            "total_xp": stats.total_xp if stats else 0,
            "streak": stats.streak_count if stats else 0,
            "words_mastered": stats.words_mastered_count if stats else 0,

            "total_words": 0,  # TODO
            "mastery_ratio": 0.0  # TODO
        }

    # =========================
    # 3. SETTINGS
    # =========================
    def update_settings(self, user: User, data: UpdateUserSettingsRequest):
        if data.daily_goal_minutes is not None:
            user.daily_goal_minutes = data.daily_goal_minutes

        if data.theme is not None:
            if not user.settings:
                raise HTTPException(
                    status_code=404,
                    detail="User settings not found"
                )
            user.settings.theme = data.theme

        self.db.commit()
        self.db.refresh(user)

        return {"message": "Cập nhật thành công"}

    # =========================
    # 4. CHANGE PASSWORD
    # =========================
    def change_password(self, user: User, data: ChangePasswordRequest):
        if not verify_password(data.old_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mật khẩu cũ không đúng"
            )

        if data.new_password != data.confirm_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Xác nhận mật khẩu không khớp"
            )

        user.password_hash = get_password_hash(data.new_password)
        self.db.commit()

        return {"message": "Đổi mật khẩu thành công"}