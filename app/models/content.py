import uuid
from datetime import datetime

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    JSON,
    SmallInteger,
    String,
    Text,
    func,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.core.database import Base


class Topic(Base):
    """Chủ đề học tập (vd: Business Negotiation, Daily Vocabulary...)."""

    __tablename__ = "topics"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )

    level: Mapped[str] = mapped_column(
        Enum("A1", "A2", "B1", "B2", "C1", "C2"),
        nullable=False
    )

    category: Mapped[str] = mapped_column(
        Enum("Vocabulary", "Grammar"),
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now()
    )

    # Relationships
    lessons: Mapped[list["Lesson"]] = relationship(
        "Lesson",
        back_populates="topic",
        cascade="all, delete-orphan"
    )


class Lesson(Base):
    """Bài học thuộc một chủ đề."""

    __tablename__ = "lessons"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    topic_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("topics.id", ondelete="CASCADE"),
        nullable=False
    )

    order: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
        default=1
    )

    xp_reward: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
        default=100
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now()
    )

    # Relationships
    topic: Mapped["Topic"] = relationship(
        "Topic",
        back_populates="lessons"
    )

    questions: Mapped[list["Question"]] = relationship(
        "Question",
        back_populates="lesson",
        cascade="all, delete-orphan"
    )

    progress: Mapped[list["UserProgress"]] = relationship(
        "UserProgress",
        back_populates="lesson",
        cascade="all, delete-orphan"
    )


class Question(Base):
    """Flashcard / câu hỏi trong bài học."""

    __tablename__ = "questions"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    lesson_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("lessons.id", ondelete="CASCADE"),
        nullable=False
    )

    word: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )

    context_sentence: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    correct_answer: Mapped[str] = mapped_column(
        String(500),
        nullable=False
    )

    distractors: Mapped[list[str] | None] = mapped_column(
        JSON,
        nullable=True
    )

    image_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now()
    )

    # Relationships
    lesson: Mapped["Lesson"] = relationship(
        "Lesson",
        back_populates="questions"
    )