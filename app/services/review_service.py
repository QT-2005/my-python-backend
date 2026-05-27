from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content import Lesson, Question, Topic
from app.models.question_attempt import UserQuestionAttempt
from app.models.user import User
from app.models.user_progress import UserProgress


class ReviewService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_review_lessons(self, user: User):
        result = await self.db.execute(
            select(UserProgress, Lesson, Topic)
            .join(Lesson, Lesson.id == UserProgress.lesson_id)
            .join(Topic, Topic.id == Lesson.topic_id)
            .where(
                UserProgress.user_id == user.id,
                UserProgress.needs_review.is_(True),
            )
            .order_by(UserProgress.last_studied_at.desc())
        )

        lessons = []
        for progress, lesson, topic in result.all():
            lessons.append(
                {
                    "lesson_id": progress.lesson_id,
                    "topic_title": topic.title,
                    "lesson_order": lesson.order,
                    "xp_reward": lesson.xp_reward,
                    "accuracy": float(progress.accuracy or 0),
                    "needs_review": bool(progress.needs_review),
                }
            )

        return {"total": len(lessons), "lessons": lessons}

    async def get_mistakes(self, user: User, limit: int = 50):
        result = await self.db.execute(
            select(UserQuestionAttempt, Question, Lesson, Topic)
            .join(Question, Question.id == UserQuestionAttempt.question_id)
            .join(Lesson, Lesson.id == UserQuestionAttempt.lesson_id)
            .join(Topic, Topic.id == Lesson.topic_id)
            .where(
                UserQuestionAttempt.user_id == user.id,
                UserQuestionAttempt.is_correct.is_(False),
            )
            .order_by(UserQuestionAttempt.answered_at.desc())
            .limit(limit)
        )

        mistakes = []
        for attempt, question, lesson, topic in result.all():
            mistakes.append(
                {
                    "question_id": question.id,
                    "lesson_id": lesson.id,
                    "topic_title": topic.title,
                    "lesson_order": lesson.order,
                    "word": question.word,
                    "context_sentence": question.context_sentence,
                    "selected_answer": attempt.selected_answer,
                    "correct_answer": question.correct_answer,
                    "distractors": question.distractors,
                    "answered_at": attempt.answered_at.isoformat()
                    if attempt.answered_at
                    else None,
                }
            )

        return {"total": len(mistakes), "mistakes": mistakes}
