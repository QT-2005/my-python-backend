from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user

from app.services.progress_service import ProgressService
from app.schemas.progress_schema import (
    SubmitProgressRequest,
    SubmitProgressResponse
)

router = APIRouter(prefix="/lessons", tags=["Progress"])


@router.post("/{lesson_id}/submit", response_model=SubmitProgressResponse)
async def submit_progress(
    lesson_id: str,
    data: SubmitProgressRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await ProgressService(db).submit_progress(
        current_user,
        lesson_id,
        data
    )