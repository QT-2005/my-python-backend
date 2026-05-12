from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, DECIMAL
from sqlalchemy.orm import relationship

from app.core.database import Base


class UserProgress(Base):
    __tablename__ = "user_progress"

    user_id = Column(
        String(36),
        ForeignKey("users.id"),
        primary_key=True
    )

    lesson_id = Column(
        String(36),
        ForeignKey("lessons.id"),
        primary_key=True
    )

    is_completed = Column(Boolean, default=False)
    accuracy = Column(DECIMAL(5, 2), nullable=True)
    time_spent_seconds = Column(Integer, nullable=True)

    # Relationships
    user = relationship(
        "User",
        backref="progress"
    )

    lesson = relationship(
        "Lesson",
        back_populates="progress"
    )