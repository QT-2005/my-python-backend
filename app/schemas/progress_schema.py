from pydantic import BaseModel, Field


class QuestionAttemptRequest(BaseModel):
    question_id: str
    selected_answer: str | None = Field(default=None, max_length=500)
    is_correct: bool


class SubmitProgressRequest(BaseModel):
    accuracy: float = Field(..., ge=0, le=100)
    time_spent: int = Field(..., gt=0)
    answers: list[QuestionAttemptRequest] = Field(default_factory=list)


class SessionMasteryResponse(BaseModel):
    title: str
    level: int
    progress_percent: float


class SubmitProgressResponse(BaseModel):
    lesson_id: str
    topic_title: str
    lesson_order: int
    accuracy: float
    time_spent: int
    earned_xp: int
    total_xp: int
    current_streak: int
    mastered_words: int
    ranking: str
    needs_review: bool
    already_completed: bool
    today_xp: int
    completed_lessons: int
    daily_goal_percent: float
    mastery: SessionMasteryResponse


class ActivityDayItem(BaseModel):
    date: str
    weekday: str
    completed_lessons: int
    xp: int
    minutes: int


class MilestoneItem(BaseModel):
    title: str
    description: str
    occurred_at: str | None = None
    is_highlighted: bool = False


class ProgressSummaryResponse(BaseModel):
    words_mastered: int
    words_mastered_since_yesterday: int
    activity: list[ActivityDayItem]
    streak: int
    accuracy: float
    retention_rate: float
    recent_milestones: list[MilestoneItem]
    daily_goal_minutes: int
    daily_goal_xp: int
    today_xp: int
    daily_goal_percent: float
    today_completed_lessons: int
    daily_goal_target_lessons: int
    ranking: str
