from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user

from app.models.user import User
from app.services.user_service import UserService
from app.schemas.user_schema import (
    DashboardResponse,
    UserProfileResponse,
    UpdateUserSettingsRequest,
    ChangePasswordRequest
)

router = APIRouter(prefix="/user", tags=["User"])


@router.get("/dashboard", response_model=DashboardResponse)
def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return UserService(db).get_dashboard(current_user)


@router.get("/profile", response_model=UserProfileResponse)
def get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return UserService(db).get_profile(current_user)


@router.patch("/settings")
def update_settings(
    data: UpdateUserSettingsRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return UserService(db).update_settings(current_user, data)


@router.put("/security")
def change_password(
    data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return UserService(db).change_password(current_user, data)