from pydantic import BaseModel, Field
from typing import Optional, List


# ── Request: Thêm từ mới ────────────────────────────────────────────────────
class WordCreateRequest(BaseModel):
    word_en: str = Field(..., min_length=1, max_length=100, description="Từ tiếng Anh")
    word_vn: str  = Field(..., min_length=1, max_length=200, description="Nghĩa tiếng Việt")
    pronunciation: Optional[str] = Field(None, max_length=100, description="Phiên âm IPA, vd: /kæt/")
    word_type: Optional[str] = Field(None, description="Loại từ: noun/verb/adj/adv")
    example_en: Optional[str] = Field(None, description="Câu ví dụ tiếng Anh")
    example_vn: Optional[str] = Field(None, description="Câu ví dụ tiếng Việt")
    level: Optional[str] = Field(None, description="Trình độ: A1/A2/B1/B2/C1/C2")
    topic: Optional[str] = Field(None, description="Chủ đề: animals/food/travel...")

class WordUpdateRequest(BaseModel):
    word_vn: Optional[str] = None
    pronunciation: Optional[str] = None
    word_type: Optional[str] = None
    example_en: Optional[str] = None
    example_vn: Optional[str] = None
    level: Optional[str] = None
    topic: Optional[str] = None


# ── Response: 1 từ ──────────────────────────────────────────────────────────
class WordResponse(BaseModel):
    word_id: int
    word_en: str
    word_vn: str
    pronunciation: Optional[str]
    word_type: Optional[str]
    example_en: Optional[str]
    example_vn: Optional[str]
    level: Optional[str]
    topic: Optional[str]

    model_config = {"from_attributes": True}

class WordListResponse(BaseModel):
    success: bool = True
    words: List[WordResponse]
    total: int
    skip: int
    limit: int

class LookupResponse(BaseModel):
    success: bool = True
    found: bool
    word: Optional[WordResponse] = None
    suggestions: List[WordResponse] = []   # gợi ý nếu không tìm chính xác

class TopicListResponse(BaseModel):
    success: bool = True
    topics:  List[str]

class LevelListResponse(BaseModel):
    success: bool = True
    levels:  List[str]

class DeleteResponse(BaseModel):
    success: bool = True
    message: str