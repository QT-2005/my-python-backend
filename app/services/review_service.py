from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.user_progress import UserProgress


class ReviewService:
    def __init__(self, db: AsyncSession):
        self.db = db

    # =====================================
    # GET REVIEW LESSONS
    # =====================================
    async def get_review_lessons(self, user: User):

        result = await self.db.execute(
            select(UserProgress).where(
                UserProgress.user_id == user.id,
                UserProgress.needs_review == True
            )
        )

        review_lessons = result.scalars().all()

        formatted_lessons = []

        for progress in review_lessons:
            formatted_lessons.append({
                "lesson_id": progress.lesson_id,
                "accuracy": float(progress.accuracy or 0),
                "needs_review": progress.needs_review
            })

        return {
            "total": len(formatted_lessons),
            "lessons": formatted_lessons
        }