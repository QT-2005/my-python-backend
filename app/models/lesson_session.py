import uuid
from datetime import datetime

from sqlalchemy import DateTime, DECIMAL, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class UserLessonSession(Base):
    __tablename__ = "user_lesson_sessions"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    lesson_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("lessons.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    earned_xp: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    accuracy: Mapped[float] = mapped_column(DECIMAL(5, 2), nullable=False)
    time_spent_seconds: Mapped[int] = mapped_column(Integer, nullable=False)
    mastered_words: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    studied_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )

    user = relationship("User", backref="lesson_sessions")
    lesson = relationship("Lesson", backref="lesson_sessions")
