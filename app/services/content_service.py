from datetime import date

from fastapi import HTTPException, status
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.content import Lesson, Topic
from app.models.user import User
from app.models.user_progress import UserProgress
from app.schemas.content_schema import (
    ExploreResponse,
    ExploreStatsResponse,
    ExploreTopicResponse,
    LessonDetailResponse,
    LessonListResponse,
    LessonResponse,
    QuestionResponse,
    TopicListResponse,
    TopicResponse,
)


class ContentService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_topics(
        self,
        level: str | None = None,
        category: str | None = None,
        q: str | None = None,
    ) -> TopicListResponse:
        stmt = select(Topic).options(selectinload(Topic.lessons))

        if level:
            valid_levels = {"A1", "A2", "B1", "B2", "C1", "C2"}
            if level not in valid_levels:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=(
                        "Level khong hop le. Chon mot trong: "
                        f"{', '.join(sorted(valid_levels))}"
                    ),
                )
            stmt = stmt.where(Topic.level == level)

        if category:
            valid_categories = {"Vocabulary", "Grammar"}
            if category not in valid_categories:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Category khong hop le. Chon: Vocabulary hoac Grammar",
                )
            stmt = stmt.where(Topic.category == category)

        if q:
            keyword = f"%{q.strip()}%"
            stmt = stmt.where(
                or_(
                    Topic.title.like(keyword),
                    Topic.level.like(keyword),
                    Topic.category.like(keyword),
                )
            )

        result = await self.db.execute(stmt.order_by(Topic.level, Topic.title))
        topics = result.scalars().all()

        topic_responses = [
            TopicResponse(
                id=t.id,
                title=t.title,
                level=t.level,
                category=t.category,
                lesson_count=len(t.lessons),
            )
            for t in topics
        ]

        return TopicListResponse(topics=topic_responses, total=len(topic_responses))

    async def get_explore(
        self,
        user: User,
        level: str | None = None,
        q: str | None = None,
    ) -> ExploreResponse:
        stmt = select(Topic).options(selectinload(Topic.lessons))

        if level:
            stmt = stmt.where(Topic.level == level)

        if q:
            keyword = f"%{q.strip()}%"
            stmt = stmt.where(Topic.title.like(keyword))

        topic_result = await self.db.execute(stmt.order_by(Topic.level, Topic.title))
        topics = topic_result.scalars().all()

        progress_result = await self.db.execute(
            select(UserProgress.lesson_id).where(
                UserProgress.user_id == user.id,
                UserProgress.is_completed.is_(True),
            )
        )
        completed_lesson_ids = set(progress_result.scalars().all())

        topic_items: list[ExploreTopicResponse] = []
        for topic in topics:
            total_lessons = len(topic.lessons)
            completed_lessons = sum(
                1 for lesson in topic.lessons if lesson.id in completed_lesson_ids
            )
            progress_percent = (
                round((completed_lessons / total_lessons) * 100, 2)
                if total_lessons
                else 0.0
            )
            topic_items.append(
                ExploreTopicResponse(
                    id=topic.id,
                    title=topic.title,
                    level=topic.level,
                    category=topic.category,
                    lesson_count=total_lessons,
                    completed_lessons=completed_lessons,
                    progress_percent=progress_percent,
                )
            )

        daily_goal_target = self._daily_goal_target_lessons(user.daily_goal_minutes)

        return ExploreResponse(
            vocabulary_topics=[
                item for item in topic_items if item.category == "Vocabulary"
            ],
            grammar_topics=[item for item in topic_items if item.category == "Grammar"],
            stats=ExploreStatsResponse(
                retention_rate=await self._calculate_retention_rate(user.id),
                daily_goal_minutes=user.daily_goal_minutes,
                daily_goal_completed=await self._count_today_completed_lessons(user.id),
                daily_goal_target=daily_goal_target,
            ),
            total=len(topic_items),
        )

    async def get_lessons_by_topic(self, topic_id: str) -> LessonListResponse:
        topic_result = await self.db.execute(select(Topic).where(Topic.id == topic_id))
        topic = topic_result.scalars().first()
        if not topic:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Khong tim thay chu de.",
            )

        lesson_result = await self.db.execute(
            select(Lesson).where(Lesson.topic_id == topic_id).order_by(Lesson.order)
        )
        lessons = lesson_result.scalars().all()

        return LessonListResponse(
            topic_id=topic_id,
            topic_title=topic.title,
            lessons=[
                LessonResponse(
                    id=l.id,
                    topic_id=l.topic_id,
                    order=l.order,
                    xp_reward=l.xp_reward,
                )
                for l in lessons
            ],
        )

    async def get_lesson_detail(self, lesson_id: str) -> LessonDetailResponse:
        lesson_result = await self.db.execute(
            select(Lesson)
            .options(selectinload(Lesson.questions), selectinload(Lesson.topic))
            .where(Lesson.id == lesson_id)
        )
        lesson = lesson_result.scalars().first()
        if not lesson:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Khong tim thay bai hoc.",
            )

        return LessonDetailResponse(
            lesson_id=lesson.id,
            topic_title=lesson.topic.title,
            order=lesson.order,
            xp_reward=lesson.xp_reward,
            questions=[
                QuestionResponse(
                    id=q.id,
                    word=q.word,
                    context_sentence=q.context_sentence,
                    correct_answer=q.correct_answer,
                    distractors=q.distractors,
                    image_url=q.image_url,
                )
                for q in lesson.questions
            ],
        )

    async def _calculate_retention_rate(self, user_id: str) -> float:
        total_result = await self.db.execute(
            select(func.count())
            .select_from(UserProgress)
            .where(UserProgress.user_id == user_id)
        )
        total = total_result.scalar() or 0
        if total == 0:
            return 0.0

        retained_result = await self.db.execute(
            select(func.count())
            .select_from(UserProgress)
            .where(
                UserProgress.user_id == user_id,
                UserProgress.needs_review.is_(False),
            )
        )
        retained = retained_result.scalar() or 0
        return round((retained / total) * 100, 2)

    async def _count_today_completed_lessons(self, user_id: str) -> int:
        result = await self.db.execute(
            select(func.count())
            .select_from(UserProgress)
            .where(
                UserProgress.user_id == user_id,
                UserProgress.is_completed.is_(True),
                func.date(UserProgress.last_studied_at) == date.today(),
            )
        )
        return int(result.scalar() or 0)

    def _daily_goal_target_lessons(self, daily_goal_minutes: int) -> int:
        if daily_goal_minutes <= 5:
            return 2
        if daily_goal_minutes <= 10:
            return 3
        return 4
