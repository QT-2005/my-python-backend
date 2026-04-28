from pydantic import BaseModel
from typing import Optional
from pydantic import BaseModel, Field

class DashboardResponse(BaseModel):
    streak: int
    today_xp: int
    total_xp: int
    daily_goal_minutes: int
    
    class Config:
        from_attributes = True

class UserProfileResponse(BaseModel):
    email: str
    full_name: str
    avatar_url: str | None
    current_level: str

    total_xp: int
    streak: int
    words_mastered: int

class UpdateUserSettingsRequest(BaseModel):
    daily_goal_minutes: Optional[int] = None
    theme: Optional[str] = None

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str = Field(min_length=6)