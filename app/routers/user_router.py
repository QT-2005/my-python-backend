from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.user_schema import UpdateUserSettingsRequest

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.user_schema import DashboardResponse
from app.schemas.user_schema import UserProfileResponse
from app.schemas.user_schema import ChangePasswordRequest
from app.core.security import verify_password, get_password_hash

router = APIRouter(prefix="/user", tags=["User"])


@router.get("/dashboard", response_model=DashboardResponse)
def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    stats = current_user.stats

    if not stats:
        return DashboardResponse(
            streak=0,
            today_xp=0,
            total_xp=0,
            daily_goal_minutes=current_user.daily_goal_minutes
        )

    return DashboardResponse(
        streak=stats.streak_count,
        today_xp=0,  # TODO: tính sau
        total_xp=stats.total_xp,
        daily_goal_minutes=current_user.daily_goal_minutes
    )

@router.get("/profile", response_model=UserProfileResponse)
def get_profile(
    current_user: User = Depends(get_current_user)
):
    stats = current_user.stats

    return UserProfileResponse(
        email=current_user.email,
        full_name=current_user.full_name,
        avatar_url=current_user.avatar_url,
        current_level=current_user.current_level,

        total_xp=stats.total_xp if stats else 0,
        streak=stats.streak_count if stats else 0,
        words_mastered=stats.words_mastered_count if stats else 0
    )

@router.patch("/settings")
def update_settings(
    data: UpdateUserSettingsRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # update bảng users
    if data.daily_goal_minutes is not None:
        current_user.daily_goal_minutes = data.daily_goal_minutes

    # update bảng user_settings
    if data.theme is not None:
        if current_user.settings:
            current_user.settings.theme = data.theme

    db.commit()
    db.refresh(current_user)

    return {
        "message": "Cập nhật thành công"
    }

@router.put("/security")
def change_password(
    data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # kiểm tra password cũ
    if not verify_password(data.old_password, current_user.password_hash):
        return {"message": "Mật khẩu cũ không đúng"}

    # hash password mới
    new_password_hash = get_password_hash(data.new_password)

    # cập nhật DB
    current_user.password_hash = new_password_hash
    db.commit()

    return {"message": "Đổi mật khẩu thành công"}    