from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_, func

from app.models.word import Word
from app.schemas.word import WordCreateRequest, WordUpdateRequest


class WordService:
    def create(self, db: Session, req: WordCreateRequest) -> Word:
        word_en = req.word_en.strip().lower()

        if db.query(Word).filter(Word.word_en == word_en).first():
            raise ValueError(f"Từ '{req.word_en}' đã có trong từ điển")

        word = Word(
            word_en=word_en,
            word_vn=req.word_vn.strip(),
            pronunciation=req.pronunciation,
            word_type=req.word_type,
            example_en=req.example_en,
            example_vn=req.example_vn,
            level=req.level,
            topic=req.topic,
        )
        db.add(word)
        db.commit()
        db.refresh(word)
        return word

    def lookup(
        self,
        db: Session,
        keyword: str,
    ) -> Tuple[Optional[Word], List[Word]]:
        """
        Trả về (word, suggestions):
        - Nếu tìm thấy chính xác: word = Word, suggestions = []
        - Nếu không tìm thấy: word = None, suggestions = danh sách gần đúng
        """
        keyword = keyword.strip().lower()

        # Tìm chính xác tiếng Anh
        exact = db.query(Word).filter(Word.word_en == keyword).first()
        if exact:
            return exact, []

        # Tìm chính xác tiếng Việt
        exact_vn = db.query(Word).filter(
            func.lower(Word.word_vn) == keyword
        ).first()
        if exact_vn:
            return exact_vn, []

        suggestions = (
            db.query(Word)
            .filter(
                or_(
                    Word.word_en.ilike(f"%{keyword}%"),
                    Word.word_vn.ilike(f"%{keyword}%"),
                )
            )
            .limit(5)
            .all()
        )
        return None, suggestions

    def get_list(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 20,
        topic: Optional[str] = None,
        level: Optional[str] = None,
        word_type: Optional[str] = None,
        search: Optional[str] = None,
    ) -> Tuple[List[Word], int]:
        query = db.query(Word)

        if topic:
            query = query.filter(Word.topic == topic)
        if level:
            query = query.filter(Word.level == level)
        if word_type:
            query = query.filter(Word.word_type == word_type)
        if search:
            kw = f"%{search.strip().lower()}%"
            query = query.filter(
                or_(
                    Word.word_en.ilike(kw),
                    Word.word_vn.ilike(kw),
                )
            )

        total = query.count()
        words = query.order_by(Word.word_en).offset(skip).limit(limit).all()
        return words, total

    def get_by_id(self, db: Session, word_id: int) -> Optional[Word]:
        return db.query(Word).filter(Word.word_id == word_id).first()

    def update(self, db: Session, word_id: int, req: WordUpdateRequest) -> Optional[Word]:
        word = self.get_by_id(db, word_id)
        if not word:
            return None
        for field, value in req.model_dump(exclude_none=True).items():
            setattr(word, field, value)
        db.commit()
        db.refresh(word)
        return word

    def delete(self, db: Session, word_id: int) -> bool:
        word = self.get_by_id(db, word_id)
        if not word:
            return False
        db.delete(word)
        db.commit()
        return True

    def get_topics(self, db: Session) -> List[str]:
        rows = db.query(Word.topic).filter(Word.topic.isnot(None)).distinct().all()
        return sorted([r[0] for r in rows])

    def get_levels(self, db: Session) -> List[str]:
        order = ["A1", "A2", "B1", "B2", "C1", "C2"]
        rows = db.query(Word.level).filter(Word.level.isnot(None)).distinct().all()
        found = {r[0] for r in rows}
        return [l for l in order if l in found]

    def get_random(
        self, db: Session, count: int = 10,
        topic: Optional[str] = None,
        level: Optional[str] = None,
    ) -> List[Word]:
        query = db.query(Word)
        if topic:
            query = query.filter(Word.topic == topic)
        if level:
            query = query.filter(Word.level == level)
        return query.order_by(func.rand()).limit(count).all()


word_service = WordService()