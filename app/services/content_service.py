from datetime import date, datetime, timezone
 
from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
 
from app.models.content import Lesson, Question, Topic
from app.models.user_progress import UserProgress
from app.models.user_meta import UserStats
from app.schemas.content_schema import (
    LessonDetailResponse,
    LessonListResponse,
    LessonResponse,
    QuestionResponse,
    TopicListResponse,
    TopicResponse,
)

def _calc_ranking(total_xp: int) -> str:
    if total_xp >= 15_000:
        return "Top 2%"
    if total_xp >= 5_000:
        return "Top 15%"
    return "Top 50%"

def _update_streak(stats: UserStats) -> int:
    today = date.today()
    last = stats.last_active_date

    if last is None or last < today:
        if last is not None and (today - last).days == 1:
            stats.streak_count += 1
        elif last != today:
            stats.streak_count = 1
        stats.last_active_date = today
 
    return stats.streak_count

class ContentService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_topics(
        self,
        level: str | None = None,
        category: str | None = None,
    ) -> TopicListResponse:
        """Lấy danh sách chủ đề, hỗ trợ filter theo level và category."""
 
        stmt = select(Topic).options(selectinload(Topic.lessons))
 
        if level:
            valid_levels = {"A1", "A2", "B1", "B2", "C1", "C2"}
            if level not in valid_levels:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Level không hợp lệ. Chọn một trong: {', '.join(sorted(valid_levels))}",
                )
            stmt = stmt.where(Topic.level == level)
 
        if category:
            valid_categories = {"Vocabulary", "Grammar"}
            if category not in valid_categories:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Category không hợp lệ. Chọn: Vocabulary hoặc Grammar",
                )
            stmt = stmt.where(Topic.category == category)
 
        result = await self.db.execute(stmt)
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
    

    async def get_lessons_by_topic(self, topic_id: str) -> LessonListResponse:
        """Lấy danh sách bài học của một chủ đề, sắp xếp theo thứ tự."""
 
        topic_result = await self.db.execute(
            select(Topic).where(Topic.id == topic_id)
        )
        topic = topic_result.scalars().first()
        if not topic:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy chủ đề.",
            )
 
        lesson_result = await self.db.execute(
            select(Lesson)
            .where(Lesson.topic_id == topic_id)
            .order_by(Lesson.order)
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
        """Lấy chi tiết bài học gồm toàn bộ flashcards/câu hỏi."""
 
        lesson_result = await self.db.execute(
            select(Lesson)
            .options(selectinload(Lesson.questions), selectinload(Lesson.topic))
            .where(Lesson.id == lesson_id)
        )
        lesson = lesson_result.scalars().first()
        if not lesson:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy bài học.",
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
