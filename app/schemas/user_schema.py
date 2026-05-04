from pydantic import BaseModel, Field
from typing import Optional, Literal


class DashboardResponse(BaseModel):
    streak: int
    today_xp: int
    total_xp: int
    daily_goal_minutes: int
    message: Optional[str] = None

    class Config:
        from_attributes = True


class UserProfileResponse(BaseModel):
    email: str
    full_name: str
    avatar_url: Optional[str]
    current_level: str

    total_xp: int
    streak: int
    words_mastered: int
    total_words: Optional[int] = 0
    mastery_ratio: Optional[float] = 0

    class Config:
        from_attributes = True


class UpdateUserSettingsRequest(BaseModel):
    daily_goal_minutes: Optional[int] = Field(None, ge=5, le=60)
    theme: Optional[Literal["light", "dark"]]


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str = Field(min_length=6)
    confirm_password: str