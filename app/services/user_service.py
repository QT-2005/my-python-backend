from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.user import User
from app.schemas.user_schema import (
    UpdateUserSettingsRequest,
    ChangePasswordRequest
)
from app.core.security import verify_password, get_password_hash


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    # =========================
    # HELPER METHODS
    # =========================
    def _calculate_tier(self, total_xp: int) -> str:
        if total_xp < 5000:
            return "Beginner"

        if total_xp < 15000:
            return "Intermediate"

        return "Advanced"

    def _calculate_mastery_ratio(
        self,
        mastered_words: int,
        total_words: int
    ) -> float:

        if total_words == 0:
            return 0.0

        return round(
            (mastered_words / total_words) * 100,
            2
        )

    # =========================
    # 1. DASHBOARD
    # =========================
    async def get_dashboard(self, user: User):
        stats = user.stats

        total_xp = stats.total_xp if stats else 0

        return {
            "streak": stats.streak_count if stats else 0,
            "today_xp": await self._calculate_today_xp(user.id),
            "total_xp": total_xp,
            "daily_goal_minutes": user.daily_goal_minutes,
            "tier": self._calculate_tier(total_xp),
            "message": "Keep going!"
        }

    async def _calculate_today_xp(self, user_id: str) -> int:
        """
        TODO:
        Query thật từ user_progress sau.
        """

        return 0

    # =========================
    # 2. PROFILE
    # =========================
    async def get_profile(self, user: User):
        stats = user.stats

        total_xp = stats.total_xp if stats else 0
        words_mastered = stats.words_mastered_count if stats else 0

        # TODO:
        # Sau này query thật từ bảng questions
        total_words = 100

        mastery_ratio = self._calculate_mastery_ratio(
            words_mastered,
            total_words
        )

        return {
            "email": user.email,
            "full_name": user.full_name,
            "avatar_url": user.avatar_url,
            "current_level": user.current_level,

            "total_xp": total_xp,
            "streak": stats.streak_count if stats else 0,
            "words_mastered": words_mastered,

            "total_words": total_words,
            "mastery_ratio": mastery_ratio,

            "tier": self._calculate_tier(total_xp)
        }

    # =========================
    # 3. SETTINGS
    # =========================
    async def update_settings(
        self,
        user: User,
        data: UpdateUserSettingsRequest
    ):

        try:
            if data.daily_goal_minutes is not None:
                user.daily_goal_minutes = data.daily_goal_minutes

            if data.theme is not None:

                # Defensive coding
                if not user.settings:
                    from app.models.user_meta import UserSettings

                    user.settings = UserSettings(
                        user_id=user.id
                    )

                user.settings.theme = data.theme

            return {
                "message": "Cập nhật thành công"
            }

        except Exception:
            await self.db.rollback()
            raise

    # =========================
    # 4. CHANGE PASSWORD
    # =========================
    async def change_password(
        self,
        user: User,
        data: ChangePasswordRequest
    ):

        if not verify_password(
            data.old_password,
            user.password_hash
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mật khẩu cũ không đúng"
            )

        if data.new_password != data.confirm_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Xác nhận mật khẩu không khớp"
            )

        user.password_hash = get_password_hash(
            data.new_password
        )

        return {
            "message": "Đổi mật khẩu thành công"
        }