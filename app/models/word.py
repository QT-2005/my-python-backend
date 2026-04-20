from sqlalchemy import Column, Integer, String, Text, Enum
from app.core.database import Base
import enum


class WordLevel(str, enum.Enum):
    A1 = "A1"
    A2 = "A2"
    B1 = "B1"
    B2 = "B2"
    C1 = "C1"
    C2 = "C2"


class Word(Base):
    __tablename__ = "words"

    word_id = Column(Integer, primary_key=True, autoincrement=True)
    word_en = Column(String(100), nullable=False, unique=True)   # từ tiếng Anh
    word_vn = Column(String(200), nullable=False)                # nghĩa tiếng Việt
    pronunciation = Column(String(100), nullable=True)                 # phiên âm IPA, vd: /kæt/
    word_type = Column(String(30),  nullable=True)                 # noun / verb / adj / adv
    example_en = Column(Text, nullable=True)                        # câu ví dụ tiếng Anh
    example_vn = Column(Text, nullable=True)                        # câu ví dụ tiếng Việt
    level   = Column(Enum(WordLevel), nullable=True)             # A1-C2
    topic   = Column(String(50), nullable=True)                  # animals, food, travel...

    def __repr__(self):
        return f"<Word #{self.word_id} '{self.word_en}' [{self.pronunciation}]>"