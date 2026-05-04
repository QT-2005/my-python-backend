from pydantic import BaseModel, Field


class SubmitProgressRequest(BaseModel):
    accuracy: float = Field(ge=0, le=100)
    time_spent: int = Field(gt=0)


class SubmitProgressResponse(BaseModel):
    earned_xp: int
    current_streak: int
    mastered_words: int
    ranking: str