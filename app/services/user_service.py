import random
from datetime import date

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash, verify_password
from app.models.content import Lesson, Question, Topic
from app.models.lesson_session import UserLessonSession
from app.models.user import User
from app.models.user_meta import UserSettings
from app.models.user_progress import UserProgress
from app.schemas.user_schema import (
    ChangePasswordRequest,
    DailyGoalStatus,
    DashboardMissionItem,
    UpdateUserProfileRequest,
    UpdateUserSettingsRequest,
)


LEVELS = ["A1", "A2", "B1", "B2", "C1", "C2"]


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_dashboard(self, user: User):
        stats = user.stats
        total_xp = stats.total_xp if stats else 0
        today_xp = await self._calculate_today_xp(user.id)
        daily_goal_xp = self._daily_goal_xp(user.daily_goal_minutes)
        completed_lessons = await self._count_today_completed_lessons(user.id)

        missions = await self._get_today_missions(user)

        return {
            "streak": stats.streak_count if stats else 0,
            "today_xp": today_xp,
            "total_xp": total_xp,
            "daily_goal_minutes": user.daily_goal_minutes,
            "tier": self._calculate_tier(total_xp),
            "message": "Keep going!",
            "words_mastered": stats.words_mastered_count if stats else 0,
            "accuracy": await self._calculate_average_accuracy(user.id),
            "retention_rate": await self._calculate_retention_rate(user.id),
            "daily_goal": DailyGoalStatus(
                minutes=user.daily_goal_minutes,
                target_xp=daily_goal_xp,
                today_xp=today_xp,
                percent=self._daily_goal_percent(today_xp, daily_goal_xp),
                completed_lessons=completed_lessons,
                target_lessons=len(missions),
            ),
            "missions": missions,
        }

    async def get_profile(self, user: User):
        stats = user.stats
        total_xp = stats.total_xp if stats else 0
        words_mastered = stats.words_mastered_count if stats else 0
        total_words = await self._calculate_total_attempted_words(user.id)
        total_words = max(total_words, words_mastered)

        return {
            "email": user.email,
            "full_name": user.full_name,
            "avatar_url": user.avatar_url,
            "current_level": user.current_level,
            "total_xp": total_xp,
            "streak": stats.streak_count if stats else 0,
            "words_mastered": words_mastered,
            "total_words": total_words,
            "mastery_ratio": self._calculate_mastery_ratio(
                words_mastered,
                total_words,
            ),
            "tier": self._calculate_tier(total_xp),
        }

    async def update_settings(self, user: User, data: UpdateUserSettingsRequest):
        if not user.settings:
            user.settings = UserSettings(user_id=user.id)

        if data.daily_goal_minutes is not None:
            user.daily_goal_minutes = data.daily_goal_minutes

        if data.theme is not None:
            user.settings.theme = data.theme

        if data.high_contrast_borders is not None:
            user.settings.high_contrast_borders = data.high_contrast_borders

        if data.notifications_enabled is not None:
            user.settings.notifications_enabled = data.notifications_enabled

        if data.current_level is not None:
            user.current_level = data.current_level

        return {"message": "Cap nhat thanh cong"}

    async def update_profile(self, user: User, data: UpdateUserProfileRequest):
        if data.full_name is not None:
            user.full_name = data.full_name

        if data.avatar_url is not None:
            user.avatar_url = data.avatar_url

        if data.current_level is not None:
            user.current_level = data.current_level

        return {
            "message": "Cap nhat profile thanh cong",
            "full_name": user.full_name,
            "avatar_url": user.avatar_url,
            "current_level": user.current_level,
        }

    async def change_password(self, user: User, data: ChangePasswordRequest):
        if not verify_password(data.old_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mat khau cu khong dung",
            )

        if data.new_password != data.confirm_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Xac nhan mat khau khong khop",
            )

        user.password_hash = get_password_hash(data.new_password)

        return {"message": "Doi mat khau thanh cong"}

    async def _get_today_missions(self, user: User) -> list[DashboardMissionItem]:
        daily_goal_xp = self._daily_goal_xp(user.daily_goal_minutes)

        # Shuffle lessons with date-based seed so missions change daily
        rng = random.Random(f"{date.today()}_{user.id}")

        # 1) Pick uncompleted lessons at current level
        selected = await self._pick_lessons_for_xp(
            user.id, user.current_level, daily_goal_xp, rng,
        )
        accumulated_xp = sum(xp for _, _, xp in selected)

        # 2) If not enough XP, try higher levels
        if accumulated_xp < daily_goal_xp:
            current_idx = LEVELS.index(user.current_level)
            for next_level in LEVELS[current_idx + 1:]:
                level_rng = random.Random(f"{date.today()}_{user.id}_{next_level}")
                more = await self._pick_lessons_for_xp(
                    user.id, next_level, daily_goal_xp - accumulated_xp, level_rng,
                )
                selected.extend(more)
                accumulated_xp += sum(xp for _, _, xp in more)
                if accumulated_xp >= daily_goal_xp:
                    break

        # 3) Fallback — all lessons completed everywhere, show some completed ones
        if not selected:
            fallback_rng = random.Random(f"{date.today()}_{user.id}_fallback")
            rows = await self._find_all_lessons(user.current_level)
            fallback_rng.shuffle(rows)
            for lesson, topic in rows[:3]:
                selected.append((lesson, topic, lesson.xp_reward))

        # 4) Also include lessons studied today so user sees their progress
        today_result = await self.db.execute(
            select(UserLessonSession.lesson_id).distinct().where(
                UserLessonSession.user_id == user.id,
                func.date(UserLessonSession.studied_at) == date.today(),
            )
        )
        today_lesson_ids = {row[0] for row in today_result.all()}
        existing_ids = {lesson.id for lesson, _, _ in selected}
        missing_ids = list(today_lesson_ids - existing_ids)

        if missing_ids:
            today_stmt = (
                select(Lesson, Topic)
                .join(Topic, Topic.id == Lesson.topic_id)
                .where(Lesson.id.in_(missing_ids))
            )
            today_result = await self.db.execute(today_stmt)
            for lesson, topic in today_result.all():
                selected.append((lesson, topic, 0))  # XP already counted

        # Build mission items with progress
        lesson_ids = [lesson.id for lesson, _, _ in selected]
        progress_by_lesson = await self._get_progress_by_lesson(user.id, lesson_ids)
        question_count_by_lesson = await self._get_question_counts(lesson_ids)

        missions = []
        for lesson, topic, _ in selected:
            progress = progress_by_lesson.get(lesson.id)
            total_questions = question_count_by_lesson.get(lesson.id, 0)

            if progress and progress.is_completed:
                completed_questions = total_questions
            elif progress and progress.accuracy is not None:
                completed_questions = int(total_questions * (float(progress.accuracy) / 100))
            else:
                completed_questions = 0

            progress_percent = (
                round((completed_questions / total_questions) * 100, 2)
                if total_questions
                else 0.0
            )

            missions.append(
                DashboardMissionItem(
                    lesson_id=lesson.id,
                    topic_id=topic.id,
                    title=topic.title,
                    description=self._mission_description(topic),
                    category=topic.category,
                    level=topic.level,
                    lesson_order=lesson.order,
                    xp_reward=lesson.xp_reward,
                    completed_questions=completed_questions,
                    total_questions=total_questions,
                    progress_percent=progress_percent,
                    is_completed=bool(progress and progress.is_completed),
                    label="CORE" if topic.category == "Vocabulary" else "ELECTIVE",
                )
            )

        return missions

    async def _pick_lessons_for_xp(
        self,
        user_id: str,
        level: str,
        target_xp: int,
        rng: random.Random,
    ) -> list[tuple[Lesson, Topic, int]]:
        """Pick uncompleted lessons at a given level, accumulating XP up to target_xp."""
        rows = await self._find_uncompleted_lessons(user_id, level)
        rng.shuffle(rows)

        result: list[tuple[Lesson, Topic, int]] = []
        accumulated = 0
        for lesson, topic in rows:
            result.append((lesson, topic, lesson.xp_reward))
            accumulated += lesson.xp_reward
            if accumulated >= target_xp:
                break
        return result

    async def _find_uncompleted_lessons(
        self,
        user_id: str,
        level: str,
    ) -> list[tuple[Lesson, Topic]]:
        """Find lessons at the given level that the user has NOT completed."""
        completed_subquery = (
            select(UserProgress.lesson_id)
            .where(
                UserProgress.user_id == user_id,
                UserProgress.is_completed.is_(True),
            )
        )
        stmt = (
            select(Lesson, Topic)
            .join(Topic, Topic.id == Lesson.topic_id)
            .where(Topic.level == level)
            .where(Lesson.id.notin_(completed_subquery))
            .order_by(Topic.category.desc(), Topic.title, Lesson.order)
        )
        result = await self.db.execute(stmt)
        return list(result.all())

    async def _find_all_lessons(
        self,
        level: str,
    ) -> list[tuple[Lesson, Topic]]:
        """Get all lessons at a level (even completed ones) — used as fallback."""
        stmt = (
            select(Lesson, Topic)
            .join(Topic, Topic.id == Lesson.topic_id)
            .where(Topic.level == level)
            .order_by(Topic.category.desc(), Topic.title, Lesson.order)
        )
        result = await self.db.execute(stmt)
        return list(result.all())

    async def _get_progress_by_lesson(
        self,
        user_id: str,
        lesson_ids: list[str],
    ) -> dict[str, UserProgress]:
        if not lesson_ids:
            return {}

        result = await self.db.execute(
            select(UserProgress).where(
                UserProgress.user_id == user_id,
                UserProgress.lesson_id.in_(lesson_ids),
            )
        )
        return {progress.lesson_id: progress for progress in result.scalars().all()}

    async def _get_question_counts(self, lesson_ids: list[str]) -> dict[str, int]:
        if not lesson_ids:
            return {}

        result = await self.db.execute(
            select(Question.lesson_id, func.count(Question.id))
            .where(Question.lesson_id.in_(lesson_ids))
            .group_by(Question.lesson_id)
        )
        return {lesson_id: int(count) for lesson_id, count in result.all()}

    async def _calculate_today_xp(self, user_id: str) -> int:
        result = await self.db.execute(
            select(func.coalesce(func.sum(UserLessonSession.earned_xp), 0)).where(
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

    async def _calculate_total_attempted_words(self, user_id: str) -> int:
        result = await self.db.execute(
            select(func.count(Question.id))
            .join(Lesson, Lesson.id == Question.lesson_id)
            .join(UserProgress, UserProgress.lesson_id == Lesson.id)
            .where(
                UserProgress.user_id == user_id,
                UserProgress.is_completed.is_(True),
            )
        )
        return int(result.scalar() or 0)

    def _mission_description(self, topic: Topic) -> str:
        if topic.category == "Grammar":
            return f"Practice key grammar patterns for {topic.title.lower()}."
        return f"Build fluency with {topic.title.lower()} vocabulary."

    def _daily_goal_xp(self, daily_goal_minutes: int) -> int:
        return max(daily_goal_minutes, 1) * 30

    def _daily_goal_percent(self, today_xp: int, daily_goal_xp: int) -> float:
        if daily_goal_xp <= 0:
            return 0.0
        return round(min((today_xp / daily_goal_xp) * 100, 100), 2)

    def _calculate_tier(self, total_xp: int) -> str:
        if total_xp < 5000:
            return "Beginner"
        if total_xp < 15000:
            return "Intermediate"
        if total_xp < 30000:
            return "Advanced"
        return "Expert"

    def _calculate_mastery_ratio(self, mastered_words: int, total_words: int) -> float:
        if total_words == 0:
            return 0.0
        return round((mastered_words / total_words) * 100, 2)
