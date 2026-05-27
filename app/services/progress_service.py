from datetime import date, datetime, timedelta

from fastapi import HTTPException, status
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.content import Lesson, Question, Topic
from app.models.lesson_session import UserLessonSession
from app.models.question_attempt import UserQuestionAttempt
from app.models.user_meta import UserStats
from app.models.user_progress import UserProgress
from app.schemas.progress_schema import (
    ActivityDayItem,
    MilestoneItem,
    ProgressSummaryResponse,
    SessionMasteryResponse,
    SubmitProgressResponse,
)


class ProgressService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def submit_progress(self, user, lesson_id: str, data) -> SubmitProgressResponse:
        lesson = await self._get_lesson(lesson_id)
        question_count = max(len(lesson.questions), 1)

        result = await self.db.execute(
            select(UserProgress).where(
                UserProgress.user_id == user.id,
                UserProgress.lesson_id == lesson_id,
            )
        )
        progress = result.scalars().first()

        already_completed = bool(progress and progress.is_completed)
        was_mastered = bool(progress and progress.accuracy and progress.accuracy >= 90)

        if not progress:
            progress = UserProgress(user_id=user.id, lesson_id=lesson_id)
            self.db.add(progress)

        earned_xp = 0 if already_completed else lesson.xp_reward
        mastered_words_earned = (
            question_count if data.accuracy >= 90 and not was_mastered else 0
        )
        now = datetime.now()

        progress.is_completed = True
        progress.accuracy = data.accuracy
        progress.time_spent_seconds = data.time_spent
        progress.needs_review = data.accuracy < 70
        progress.last_studied_at = now

        stats = await self._get_or_create_stats(user)
        stats.total_xp += earned_xp
        stats.words_mastered_count += mastered_words_earned
        self._update_streak(stats)

        session = UserLessonSession(
            user_id=user.id,
            lesson_id=lesson_id,
            earned_xp=earned_xp,
            accuracy=data.accuracy,
            time_spent_seconds=data.time_spent,
            mastered_words=mastered_words_earned,
            studied_at=now,
        )
        self.db.add(session)
        self._add_question_attempts(user.id, lesson, data.answers)

        try:
            await self.db.commit()
        except Exception:
            await self.db.rollback()
            raise

        today_xp = await self._calculate_today_xp(user.id)
        completed_lessons = await self._count_today_completed_lessons(user.id)
        daily_goal_percent = self._daily_goal_percent(
            today_xp,
            self._daily_goal_xp(user.daily_goal_minutes),
        )

        return SubmitProgressResponse(
            lesson_id=lesson.id,
            topic_title=lesson.topic.title,
            lesson_order=lesson.order,
            accuracy=float(data.accuracy),
            time_spent=data.time_spent,
            earned_xp=earned_xp,
            total_xp=stats.total_xp,
            current_streak=stats.streak_count,
            mastered_words=stats.words_mastered_count,
            ranking=self._calculate_ranking(stats.total_xp),
            needs_review=progress.needs_review,
            already_completed=already_completed,
            today_xp=today_xp,
            completed_lessons=completed_lessons,
            daily_goal_percent=daily_goal_percent,
            mastery=self._build_mastery(stats.total_xp),
        )

    async def get_summary(self, user) -> ProgressSummaryResponse:
        stats = await self._get_or_create_stats(user)
        today_xp = await self._calculate_today_xp(user.id)
        daily_goal_xp = self._daily_goal_xp(user.daily_goal_minutes)
        today_completed_lessons = await self._count_today_completed_lessons(user.id)
        daily_goal_target_lessons = self._daily_goal_target_lessons(
            user.daily_goal_minutes
        )

        return ProgressSummaryResponse(
            words_mastered=stats.words_mastered_count,
            words_mastered_since_yesterday=await self._calculate_today_mastered_words(
                user.id
            ),
            activity=await self._get_activity(user.id),
            streak=stats.streak_count,
            accuracy=await self._calculate_average_accuracy(user.id),
            retention_rate=await self._calculate_retention_rate(user.id),
            recent_milestones=await self._get_recent_milestones(user.id),
            daily_goal_minutes=user.daily_goal_minutes,
            daily_goal_xp=daily_goal_xp,
            today_xp=today_xp,
            daily_goal_percent=self._daily_goal_percent(today_xp, daily_goal_xp),
            today_completed_lessons=today_completed_lessons,
            daily_goal_target_lessons=daily_goal_target_lessons,
            ranking=self._calculate_ranking(stats.total_xp),
        )

    async def _get_lesson(self, lesson_id: str) -> Lesson:
        result = await self.db.execute(
            select(Lesson)
            .options(selectinload(Lesson.topic), selectinload(Lesson.questions))
            .where(Lesson.id == lesson_id)
        )
        lesson = result.scalars().first()
        if not lesson:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lesson not found",
            )
        return lesson

    def _add_question_attempts(self, user_id: str, lesson: Lesson, answers) -> None:
        if not answers:
            return

        question_ids = {question.id for question in lesson.questions}
        invalid_ids = [
            answer.question_id
            for answer in answers
            if answer.question_id not in question_ids
        ]
        if invalid_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Question khong thuoc lesson: {', '.join(invalid_ids)}",
            )

        now = datetime.now()
        for answer in answers:
            self.db.add(
                UserQuestionAttempt(
                    user_id=user_id,
                    lesson_id=lesson.id,
                    question_id=answer.question_id,
                    selected_answer=answer.selected_answer,
                    is_correct=answer.is_correct,
                    answered_at=now,
                )
            )

    async def _get_or_create_stats(self, user) -> UserStats:
        if user.stats:
            return user.stats

        stats = UserStats(user_id=user.id)
        self.db.add(stats)
        await self.db.flush()
        user.stats = stats
        return stats

    def _update_streak(self, stats: UserStats) -> None:
        today = date.today()

        if stats.last_active_date == today:
            return

        if stats.last_active_date and (today - stats.last_active_date).days == 1:
            stats.streak_count += 1
        else:
            stats.streak_count = 1

        stats.last_active_date = today

    def _calculate_ranking(self, total_xp: int) -> str:
        if total_xp >= 15_000:
            return "Top 2%"
        if total_xp >= 5_000:
            return "Top 10%"
        return "Top 30%"

    def _daily_goal_xp(self, daily_goal_minutes: int) -> int:
        return max(daily_goal_minutes, 1) * 30

    def _daily_goal_target_lessons(self, daily_goal_minutes: int) -> int:
        if daily_goal_minutes <= 5:
            return 2
        if daily_goal_minutes <= 10:
            return 3
        return 4

    def _daily_goal_percent(self, today_xp: int, daily_goal_xp: int) -> float:
        if daily_goal_xp <= 0:
            return 0.0
        return round(min((today_xp / daily_goal_xp) * 100, 100), 2)

    def _build_mastery(self, total_xp: int) -> SessionMasteryResponse:
        level = max((total_xp // 1000) + 1, 1)
        progress_percent = round((total_xp % 1000) / 10, 2)
        return SessionMasteryResponse(
            title="Vocabulary Master",
            level=level,
            progress_percent=progress_percent,
        )

    async def _calculate_today_xp(self, user_id: str) -> int:
        result = await self.db.execute(
            select(func.coalesce(func.sum(UserLessonSession.earned_xp), 0)).where(
                UserLessonSession.user_id == user_id,
                func.date(UserLessonSession.studied_at) == date.today(),
            )
        )
        return int(result.scalar() or 0)

    async def _calculate_today_mastered_words(self, user_id: str) -> int:
        result = await self.db.execute(
            select(func.coalesce(func.sum(UserLessonSession.mastered_words), 0)).where(
                UserLessonSession.user_id == user_id,
                func.date(UserLessonSession.studied_at) == date.today(),
            )
        )
        return int(result.scalar() or 0)

    async def _count_today_completed_lessons(self, user_id: str) -> int:
        result = await self.db.execute(
            select(func.count(func.distinct(UserLessonSession.lesson_id))).where(
                UserLessonSession.user_id == user_id,
                func.date(UserLessonSession.studied_at) == date.today(),
            )
        )
        return int(result.scalar() or 0)

    async def _calculate_average_accuracy(self, user_id: str) -> float:
        result = await self.db.execute(
            select(func.avg(UserLessonSession.accuracy)).where(
                UserLessonSession.user_id == user_id
            )
        )
        value = result.scalar()
        return round(float(value or 0), 2)

    async def _calculate_retention_rate(self, user_id: str) -> float:
        total_result = await self.db.execute(
            select(func.count())
            .select_from(UserProgress)
            .where(UserProgress.user_id == user_id)
        )
        total = total_result.scalar() or 0
        if total == 0:
            return 0.0

        retained_result = await self.db.execute(
            select(func.count())
            .select_from(UserProgress)
            .where(
                UserProgress.user_id == user_id,
                UserProgress.needs_review.is_(False),
            )
        )
        retained = retained_result.scalar() or 0
        return round((retained / total) * 100, 2)

    async def _get_activity(self, user_id: str) -> list[ActivityDayItem]:
        start_day = date.today() - timedelta(days=6)
        result = await self.db.execute(
            select(
                func.date(UserLessonSession.studied_at).label("activity_date"),
                func.count(func.distinct(UserLessonSession.lesson_id)).label(
                    "completed_lessons"
                ),
                func.coalesce(func.sum(UserLessonSession.earned_xp), 0).label("xp"),
                func.coalesce(func.sum(UserLessonSession.time_spent_seconds), 0).label(
                    "seconds"
                ),
            )
            .where(
                UserLessonSession.user_id == user_id,
                func.date(UserLessonSession.studied_at) >= start_day,
            )
            .group_by(func.date(UserLessonSession.studied_at))
        )
        rows = {str(row.activity_date): row for row in result.all()}

        items: list[ActivityDayItem] = []
        for offset in range(7):
            current = start_day + timedelta(days=offset)
            key = current.isoformat()
            row = rows.get(key)
            items.append(
                ActivityDayItem(
                    date=key,
                    weekday=current.strftime("%a"),
                    completed_lessons=int(row.completed_lessons if row else 0),
                    xp=int(row.xp if row else 0),
                    minutes=int((row.seconds if row else 0) // 60),
                )
            )
        return items

    async def _get_recent_milestones(self, user_id: str) -> list[MilestoneItem]:
        result = await self.db.execute(
            select(UserLessonSession, Lesson, Topic)
            .join(Lesson, Lesson.id == UserLessonSession.lesson_id)
            .join(Topic, Topic.id == Lesson.topic_id)
            .where(
                UserLessonSession.user_id == user_id,
                UserLessonSession.earned_xp > 0,
            )
            .order_by(desc(UserLessonSession.studied_at))
            .limit(4)
        )

        milestones: list[MilestoneItem] = []
        for index, (session, lesson, topic) in enumerate(result.all()):
            milestones.append(
                MilestoneItem(
                    title=f"{topic.title} Completed",
                    description=f"Module {lesson.order} - +{session.earned_xp} XP",
                    occurred_at=session.studied_at.isoformat()
                    if session.studied_at
                    else None,
                    is_highlighted=index == 0,
                )
            )

        if milestones:
            return milestones

        return [
            MilestoneItem(
                title="First Lesson",
                description="Complete a lesson to unlock milestones.",
                occurred_at=None,
                is_highlighted=False,
            )
        ]
