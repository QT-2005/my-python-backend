from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user_progress import UserProgress
from app.models.user_meta import UserStats
from app.models.lesson import Lesson


class ProgressService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def submit_progress(self, user, lesson_id: str, data):
        # =========================
        # 1. Lấy lesson (để biết XP)
        # =========================
        result = await self.db.execute(
            select(Lesson).where(Lesson.id == lesson_id)
        )
        lesson = result.scalars().first()

        if not lesson:
            raise Exception("Lesson not found")

        earned_xp = lesson.xp_reward

        # =========================
        # 2. Update user_progress
        # =========================
        result = await self.db.execute(
            select(UserProgress).where(
                UserProgress.user_id == user.id,
                UserProgress.lesson_id == lesson_id
            )
        )
        progress = result.scalars().first()

        if not progress:
            progress = UserProgress(
                user_id=user.id,
                lesson_id=lesson_id
            )
            self.db.add(progress)

        progress.is_completed = 1
        progress.accuracy = data.accuracy
        progress.time_spent_seconds = data.time_spent

        # =========================
        # 3. Update user_stats
        # =========================
        stats = user.stats

        # XP
        stats.total_xp += earned_xp

        # =========================
        # 4. Streak logic
        # =========================
        today = date.today()

        if stats.last_active_date == today:
            # đã học hôm nay rồi -> không tăng streak
            pass
        elif stats.last_active_date == date.fromordinal(today.toordinal() - 1):
            stats.streak_count += 1
        else:
            stats.streak_count = 1

        stats.last_active_date = today

        # =========================
        # 5. Words mastered (simple logic)
        # =========================
        mastered_words = 0
        if data.accuracy >= 90:
            stats.words_mastered_count += 1
            mastered_words = 1

        await self.db.commit()

        # =========================
        # 6. Ranking (fake tạm)
        # =========================
        ranking = "Top 10%"
        if stats.total_xp > 10000:
            ranking = "Top 2%"

        return {
            "earned_xp": earned_xp,
            "current_streak": stats.streak_count,
            "mastered_words": mastered_words,
            "ranking": ranking
        }