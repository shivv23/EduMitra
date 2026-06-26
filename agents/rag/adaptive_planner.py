"""Adaptive study plan generator.

Builds personalized study plans from syllabus + student performance data.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class StudyPlan:
    def __init__(
        self,
        student_id: str,
        subject: str,
        topic: str,
        mastery_score: float,
        plan: List[Dict],
    ):
        self.student_id = student_id
        self.subject = subject
        self.topic = topic
        self.mastery_score = mastery_score
        self.plan = plan
        self.created_at = datetime.utcnow().isoformat()


async def generate_adaptive_plan(
    student_id: str,
    subject: str,
    topic: str,
    mastery_score: float,
    preferred_language: str = "en",
) -> StudyPlan:
    """Generate an adaptive study plan based on student's current mastery.

    Args:
        student_id: Authenticated student UUID.
        subject: Subject name (e.g., 'Science', 'Mathematics').
        topic: Specific topic within the subject.
        mastery_score: Current mastery score (0.0 to 1.0).
        preferred_language: Language code for the plan output.

    Returns:
        StudyPlan with daily tasks for the next 7 days.
    """
    logger.info(
        "Generating plan for student %s: subject=%s, topic=%s, mastery=%.2f",
        student_id, subject, topic, mastery_score,
    )

    # Adaptive plan logic based on mastery
    if mastery_score < 0.3:
        level = "foundation"
        focus = "core concepts and fundamentals"
    elif mastery_score < 0.6:
        level = "intermediate"
        focus = "application and practice problems"
    else:
        level = "advanced"
        focus = "advanced problems and revision"

    days = []
    for i in range(1, 8):
        day = {
            "day": i,
            "title": f"Day {i}: {_get_day_title(i, level, topic)}",
            "focus": focus if i <= 3 else "revision and testing",
            "estimated_minutes": 30 + (i * 5),
        }
        days.append(day)

    plan = StudyPlan(
        student_id=student_id,
        subject=subject,
        topic=topic,
        mastery_score=mastery_score,
        plan=days,
    )

    return plan


def _get_day_title(day: int, level: str, topic: str) -> str:
    titles = {
        1: f"Introduction to {topic}",
        2: f"Deep dive: {topic} concepts",
        3: f"Practice: {topic} problems",
        4: f"Review and quiz on {topic}",
        5: f"Advanced: {topic} applications",
        6: f"Mock test: {topic}",
        7: f"Final review and next steps",
    }
    return titles.get(day, f"Study: {topic}")
