from typing import Literal, Optional

from pydantic import BaseModel, Field


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