from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.schemas.progress_schema import (
    ProgressSummaryResponse,
    SubmitProgressRequest,
    SubmitProgressResponse,
)
from app.services.progress_service import ProgressService

router = APIRouter(tags=["Progress"])


@router.post("/lessons/{lesson_id}/submit", response_model=SubmitProgressResponse)
async def submit_progress(
    lesson_id: str,
    data: SubmitProgressRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SubmitProgressResponse:
    return await ProgressService(db).submit_progress(current_user, lesson_id, data)


@router.get("/progress/summary", response_model=ProgressSummaryResponse)
async def get_progress_summary(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ProgressSummaryResponse:
    return await ProgressService(db).get_summary(current_user)
