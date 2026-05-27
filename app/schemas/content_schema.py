from typing import Literal
from pydantic import BaseModel


class TopicResponse(BaseModel):
    id: str
    title: str
    level: Literal["A1", "A2", "B1", "B2", "C1", "C2"]
    category: Literal["Vocabulary", "Grammar"]
    lesson_count: int = 0

    model_config = {"from_attributes": True}

class TopicListResponse(BaseModel):
    topics: list[TopicResponse]
    total: int


class ExploreTopicResponse(TopicResponse):
    completed_lessons: int = 0
    progress_percent: float = 0.0


class ExploreStatsResponse(BaseModel):
    retention_rate: float
    daily_goal_minutes: int
    daily_goal_completed: int
    daily_goal_target: int


class ExploreResponse(BaseModel):
    vocabulary_topics: list[ExploreTopicResponse]
    grammar_topics: list[ExploreTopicResponse]
    stats: ExploreStatsResponse
    total: int

class LessonResponse(BaseModel):
    id: str
    topic_id: str
    order: int
    xp_reward: int

    model_config = {"from_attributes": True}

class LessonListResponse(BaseModel):
    topic_id: str
    topic_title: str
    lessons: list[LessonResponse]

class QuestionResponse(BaseModel):
    id: str
    word: str
    context_sentence: str | None = None
    correct_answer: str
    distractors: list[str] | None = None
    image_url: str | None = None

    model_config = {"from_attributes": True}


class LessonDetailResponse(BaseModel):
    lesson_id: str
    topic_title: str
    order: int
    xp_reward: int
    questions: list[QuestionResponse]

