from pydantic import BaseModel
from typing import List


class ReviewLessonItem(BaseModel):
    lesson_id: str
    topic_title: str | None = None
    lesson_order: int | None = None
    xp_reward: int | None = None
    accuracy: float
    needs_review: bool

    class Config:
        from_attributes = True


class ReviewLessonsResponse(BaseModel):
    total: int
    lessons: List[ReviewLessonItem]

    class Config:
        from_attributes = True


class ReviewMistakeItem(BaseModel):
    question_id: str
    lesson_id: str
    topic_title: str
    lesson_order: int
    word: str
    context_sentence: str | None = None
    selected_answer: str | None = None
    correct_answer: str
    distractors: list[str] | None = None
    answered_at: str | None = None

    class Config:
        from_attributes = True


class ReviewMistakesResponse(BaseModel):
    total: int
    mistakes: List[ReviewMistakeItem]

    class Config:
        from_attributes = True
