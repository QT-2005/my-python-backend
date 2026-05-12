from typing import Literal
 
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
 
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.content_schema import (
    LessonDetailResponse,
    LessonListResponse,
    TopicListResponse,
)
from app.services.content_service import ContentService
 
router = APIRouter(prefix="/learning", tags=["learning"])

@router.get(
    "/topics",
    response_model=TopicListResponse,
    summary="Lấy danh sách chủ đề",
)
async def get_topics(
    level: Literal["A1", "A2", "B1", "B2", "C1", "C2"] | None = Query(
        None, description="Lọc theo cấp độ CEFR"
    ),
    category: Literal["Vocabulary", "Grammar"] | None = Query(
        None, description="Lọc theo loại nội dung"
    ),
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> TopicListResponse:
    return await ContentService(db).get_topics(level=level, category=category)

@router.get(
    "/topics/{topic_id}/lessons",
    response_model=LessonListResponse,
    summary="Lấy danh sách bài học của một chủ đề",
)
async def get_lessons(
    topic_id: str,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> LessonListResponse:
    return await ContentService(db).get_lessons_by_topic(topic_id)

@router.get(
    "/lessons/{lesson_id}",
    response_model=LessonDetailResponse,
    summary="Lấy chi tiết bài học (câu hỏi, flashcard)",
)
async def get_lesson_detail(
    lesson_id: str,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> LessonDetailResponse:
    return await ContentService(db).get_lesson_detail(lesson_id)

