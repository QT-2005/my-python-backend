from datetime import date

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.lesson import Lesson
from app.models.user_meta import UserStats
from app.models.user_progress import UserProgress


class ProgressService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def submit_progress(self, user, lesson_id: str, data):

        # =========================
        # 1. Get lesson
        # =========================
        result = await self.db.execute(
            select(Lesson).where(Lesson.id == lesson_id)
        )

        lesson = result.scalars().first()

        if not lesson:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lesson not found"
            )

        earned_xp = lesson.xp_reward

        # =========================
        # 2. Get/Create progress
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

        progress.is_completed = True
        progress.accuracy = data.accuracy
        progress.time_spent_seconds = data.time_spent

        # =========================
        # 3. User stats
        # =========================
        if not user.stats:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User stats not found"
            )

        stats: UserStats = user.stats

        # XP
        stats.total_xp += earned_xp

        # =========================
        # 4. Streak logic
        # =========================
        today = date.today()

        if stats.last_active_date == today:
            pass

        elif (
            stats.last_active_date
            and stats.last_active_date == date.fromordinal(today.toordinal() - 1)
        ):
            stats.streak_count += 1

        else:
            stats.streak_count = 1

        stats.last_active_date = today

        # =========================
        # 5. Mastered words
        # =========================
        if data.accuracy >= 90:
            stats.words_mastered_count += 1

        # =========================
        # 6. Save DB
        # =========================
        try:
            await self.db.commit()

        except Exception:
            await self.db.rollback()
            raise

        # =========================
        # 7. Ranking
        # =========================
        ranking = "Top 10%"

        if stats.total_xp >= 10000:
            ranking = "Top 2%"

        # =========================
        # 8. Response
        # =========================
        return {
            "earned_xp": earned_xp,
            "current_streak": stats.streak_count,
            "mastered_words": stats.words_mastered_count,
            "ranking": ranking
        }