from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db

from app.core.dependencies import get_current_user

from app.models.user import User

from app.schemas.review_schema import (
    ReviewLessonsResponse
)

from app.services.review_service import ReviewService


router = APIRouter(
    prefix="/review",
    tags=["Review"]
)


# =====================================
# GET REVIEW LESSONS
# =====================================
@router.get(
    "",
    response_model=ReviewLessonsResponse
)
async def get_review_lessons(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):

    service = ReviewService(db)

    return await service.get_review_lessons(
        current_user
    )