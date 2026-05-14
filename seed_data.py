"""
Script to generate sample data for testing
"""
import asyncio
import uuid
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.models.content import Topic, Lesson, Question


async def seed_data():
    """Generate sample topics, lessons, and questions"""
    
    # Create async engine
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=True
    )
    
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        try:
            # Create sample topics
            topic_1 = Topic(
                id=str(uuid.uuid4()),
                title="Business Negotiation",
                level="B1",
                category="Vocabulary"
            )
            
            topic_2 = Topic(
                id=str(uuid.uuid4()),
                title="Daily Vocabulary",
                level="A1",
                category="Vocabulary"
            )
            
            session.add(topic_1)
            session.add(topic_2)
            await session.flush()
            
            # Create lessons for topic_1
            lesson_1 = Lesson(
                id=str(uuid.uuid4()),
                topic_id=topic_1.id,
                order=1,
                xp_reward=100
            )
            
            lesson_2 = Lesson(
                id=str(uuid.uuid4()),
                topic_id=topic_1.id,
                order=2,
                xp_reward=100
            )
            
            session.add(lesson_1)
            session.add(lesson_2)
            await session.flush()
            
            # Create questions for lesson_1
            question_1 = Question(
                id=str(uuid.uuid4()),
                lesson_id=lesson_1.id,
                word="negotiate",
                context_sentence="We need to negotiate the contract terms.",
                correct_answer="To discuss terms and reach an agreement",
                distractors=[
                    "To reject an offer",
                    "To sign a document",
                    "To delay a decision"
                ],
                image_url=None
            )
            
            question_2 = Question(
                id=str(uuid.uuid4()),
                lesson_id=lesson_1.id,
                word="closing",
                context_sentence="The closing of the deal is scheduled for next week.",
                correct_answer="The final stage of completing a transaction",
                distractors=[
                    "Shutting a door",
                    "Ending a business",
                    "Finishing a conversation"
                ],
                image_url=None
            )
            
            session.add(question_1)
            session.add(question_2)
            
            await session.commit()
            print("✓ Sample data generated successfully!")
            
        except Exception as e:
            await session.rollback()
            print(f"✗ Error generating data: {e}")
        finally:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed_data())
