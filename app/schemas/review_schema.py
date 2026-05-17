from pydantic import BaseModel
from typing import List


class ReviewLessonItem(BaseModel):
    lesson_id: str
    accuracy: float
    needs_review: bool

    class Config:
        from_attributes = True


class ReviewLessonsResponse(BaseModel):
    total: int
    lessons: List[ReviewLessonItem]

    class Config:
        from_attributes = True