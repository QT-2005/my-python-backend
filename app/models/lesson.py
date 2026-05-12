from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base


class Lesson(Base):
    __tablename__ = "lessons"

    id = Column(String(36), primary_key=True)
    topic_id = Column(String(36), ForeignKey("topics.id"))

    xp_reward = Column(Integer, default=100)

    # Quan hệ
    progress = relationship("UserProgress", back_populates="lesson")