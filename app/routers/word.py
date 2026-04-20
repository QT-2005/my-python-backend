from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.word import (
    WordCreateRequest, WordUpdateRequest,
    WordResponse, WordListResponse,
    LookupResponse, TopicListResponse,
    LevelListResponse, DeleteResponse,
)
from app.services.word_service import word_service

router = APIRouter(prefix="/api/v1/words", tags=["Dictionary"])

@router.get(
    "/lookup",
    response_model=LookupResponse,
    summary="search for a word by English or Vietnamese keyword",
)
async def lookup_word(
    q: str = Query(..., min_length=1, description="word in English or Vietnamese"),
    db: Session = Depends(get_db),
):
    word, suggestions = word_service.lookup(db, q)
    return LookupResponse(
        success=True,
        found=word is not None,
        word=WordResponse.model_validate(word) if word else None,
        suggestions=[WordResponse.model_validate(s) for s in suggestions],
    )


@router.get(
    "",
    response_model=WordListResponse,
    summary="list words with pagination and optional filters (topic/level/type/search)",
)
async def get_words(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    topic: Optional[str] = Query(None, description="filter by topic: animals/food/travel..."),
    level: Optional[str] = Query(None, description="filter by level: A1-C2"),
    word_type: Optional[str] = Query(None, description="filter by word type: noun/verb/adj/adv"),
    search: Optional[str] = Query(None, description="search by English or Vietnamese word"),
):
    words, total = word_service.get_list(
        db, skip=skip, limit=limit,
        topic=topic, level=level, word_type=word_type, search=search,
    )
    return WordListResponse(
        words=[WordResponse.model_validate(w) for w in words],
        total=total, skip=skip, limit=limit,
    )

@router.get(
    "/topics",
    response_model=TopicListResponse,
    summary="list all available topics in the dictionary",
)
async def get_topics(db: Session = Depends(get_db)):
    return TopicListResponse(topics=word_service.get_topics(db))

@router.get(
    "/levels",
    response_model=LevelListResponse,
    summary="list all available levels in the dictionary",
)
async def get_levels(db: Session = Depends(get_db)):
    return LevelListResponse(levels=word_service.get_levels(db))

@router.get(
    "/random",
    response_model=WordListResponse,
    summary="list random words (for review / flashcards)",
)
async def get_random_words(
    db: Session = Depends(get_db),
    count: int           = Query(10, ge=1, le=50, description="number of random words to return"),
    topic: Optional[str] = Query(None),
    level: Optional[str] = Query(None),
):
    words = word_service.get_random(db, count=count, topic=topic, level=level)
    return WordListResponse(words=[WordResponse.model_validate(w) for w in words],
                            total=len(words), skip=0, limit=count)


@router.get(
    "/{word_id}",
    response_model=WordResponse,
    summary="get details of a word by ID",
)
async def get_word(word_id: int, db: Session = Depends(get_db)):
    word = word_service.get_by_id(db, word_id)
    if not word:
        raise HTTPException(status_code=404, detail=f"Word not found with ID {word_id}")
    return WordResponse.model_validate(word)


@router.post(
    "",
    response_model=WordResponse,
    status_code=status.HTTP_201_CREATED,
    summary="add a new word to the dictionary",
)
async def create_word(body: WordCreateRequest, db: Session = Depends(get_db)):
    try:
        word = word_service.create(db, body)
        return WordResponse.model_validate(word)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put(
    "/{word_id}",
    response_model=WordResponse,
    summary="update information of a word",
)
async def update_word(word_id: int, body: WordUpdateRequest, db: Session = Depends(get_db)):
    word = word_service.update(db, word_id, body)
    if not word:
        raise HTTPException(status_code=404, detail=f"Word not found with ID {word_id}")
    return WordResponse.model_validate(word)

@router.delete(
    "/{word_id}",
    response_model=DeleteResponse,
    summary="delete a word from the dictionary",
)
async def delete_word(word_id: int, db: Session = Depends(get_db)):
    ok = word_service.delete(db, word_id)
    if not ok:
        raise HTTPException(status_code=404, detail=f"Word not found with ID {word_id}")
    return DeleteResponse(message=f"Deleted word with ID {word_id}")