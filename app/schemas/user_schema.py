from typing import Literal, Optional

from pydantic import BaseModel, Field


class DailyGoalStatus(BaseModel):
    minutes: int
    target_xp: int
    today_xp: int
    percent: float
    completed_lessons: int
    target_lessons: int


class DashboardMissionItem(BaseModel):
    lesson_id: str
    topic_id: str
    title: str
    description: str
    category: Literal["Vocabulary", "Grammar"]
    level: Literal["A1", "A2", "B1", "B2", "C1", "C2"]
    lesson_order: int
    xp_reward: int
    completed_questions: int
    total_questions: int
    progress_percent: float
    is_completed: bool
    label: str


# =========================
# DASHBOARD RESPONSE
# =========================
class DashboardResponse(BaseModel):
    streak: int
    today_xp: int
    total_xp: int

    daily_goal_minutes: int

    tier: str

    message: Optional[str] = None
    words_mastered: int = 0
    accuracy: float = 0.0
    retention_rate: float = 0.0
    daily_goal: DailyGoalStatus | None = None
    missions: list[DashboardMissionItem] = Field(default_factory=list)

    class Config:
        from_attributes = True


# =========================
# USER PROFILE RESPONSE
# =========================
class UserProfileResponse(BaseModel):

    # Basic Info
    email: str
    full_name: str

    avatar_url: Optional[str] = None

    current_level: str

    # Statistics
    total_xp: int
    streak: int

    words_mastered: int

    total_words: int = 0

    mastery_ratio: float = 0.0

    tier: str

    class Config:
        from_attributes = True


# =========================
# UPDATE SETTINGS REQUEST
# =========================
class UpdateUserSettingsRequest(BaseModel):

    daily_goal_minutes: Optional[int] = Field(
        default=None,
        ge=5,
        le=60,
        description="Daily learning goal in minutes"
    )

    theme: Optional[
        Literal["light", "dark"]
    ] = None

    high_contrast_borders: Optional[bool] = None

    notifications_enabled: Optional[bool] = None

    current_level: Optional[
        Literal["A1", "A2", "B1", "B2", "C1", "C2"]
    ] = None


class UpdateUserProfileRequest(BaseModel):
    full_name: Optional[str] = Field(default=None, min_length=1, max_length=150)
    avatar_url: Optional[str] = Field(default=None, max_length=500)
    current_level: Optional[
        Literal["A1", "A2", "B1", "B2", "C1", "C2"]
    ] = None


# =========================
# CHANGE PASSWORD REQUEST
# =========================
class ChangePasswordRequest(BaseModel):

    old_password: str

    new_password: str = Field(
        min_length=8,
        description="Minimum 8 characters"
    )

    confirm_password: str


# =========================
# GENERIC MESSAGE RESPONSE
# =========================
class MessageResponse(BaseModel):
    message: str
