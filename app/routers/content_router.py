from typing import Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.content_schema import (
    ExploreResponse,
    LessonDetailResponse,
    LessonListResponse,
    TopicListResponse,
)
from app.services.content_service import ContentService

router = APIRouter(prefix="/learning", tags=["learning"])


@router.get(
    "/topics",
    response_model=TopicListResponse,
    summary="Lay danh sach chu de",
)
async def get_topics(
    level: Literal["A1", "A2", "B1", "B2", "C1", "C2"] | None = Query(
        None, description="Loc theo cap do CEFR"
    ),
    category: Literal["Vocabulary", "Grammar"] | None = Query(
        None, description="Loc theo loai noi dung"
    ),
    q: str | None = Query(None, description="Tim kiem topic hoac grammar"),
    db: AsyncSession = Depends(get_db),
) -> TopicListResponse:
    return await ContentService(db).get_topics(level=level, category=category, q=q)


@router.get(
    "/explore",
    response_model=ExploreResponse,
    summary="Lay du lieu man hinh Explore",
)
async def get_explore(
    level: Literal["A1", "A2", "B1", "B2", "C1", "C2"] | None = Query(
        None, description="Loc theo cap do CEFR"
    ),
    q: str | None = Query(None, description="Tim kiem topic hoac grammar"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ExploreResponse:
    return await ContentService(db).get_explore(current_user, level=level, q=q)


@router.get(
    "/topics/{topic_id}/lessons",
    response_model=LessonListResponse,
    summary="Lay danh sach bai hoc cua mot chu de",
)
async def get_lessons(
    topic_id: str,
    db: AsyncSession = Depends(get_db),
) -> LessonListResponse:
    return await ContentService(db).get_lessons_by_topic(topic_id)


@router.get(
    "/lessons/{lesson_id}",
    response_model=LessonDetailResponse,
    summary="Lay chi tiet bai hoc",
)
async def get_lesson_detail(
    lesson_id: str,
    db: AsyncSession = Depends(get_db),
) -> LessonDetailResponse:
    return await ContentService(db).get_lesson_detail(lesson_id)
