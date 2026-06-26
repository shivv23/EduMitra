"""Progress & Alert Agent — tracks mastery, predicts burnout, alerts parents/teachers.

Privacy: alerts contain minimal info, sent only to verified consent-linked guardians.
"""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

MASTERY_LEVELS = ["beginner", "developing", "proficient", "advanced", "mastered"]


async def update_mastery(
    student_id: str,
    subject: str,
    topic: str,
    quiz_score: float,
) -> Dict[str, Any]:
    """Update student's mastery score for a topic after a quiz."""
    logger.info(
        "Updating mastery: student=%s, subject=%s, topic=%s, score=%.2f",
        student_id, subject, topic, quiz_score,
    )
    try:
        import sys
        from pathlib import Path
        _backend = Path(__file__).resolve().parent.parent.parent / "backend"
        if str(_backend) not in sys.path:
            sys.path.insert(0, str(_backend))
        from src.db import save_study_progress
        return await save_study_progress(
            student_id=student_id,
            subject=subject,
            topic=topic,
            mastery_score=quiz_score,
            quizzes_taken=1,
            quizzes_passed=1 if quiz_score >= 0.4 else 0,
        )
    except Exception as e:
        logger.warning("update_mastery DB failed: %s", e)
        return {}


def calculate_burnout_risk(
    study_hours_last_week: float,
    avg_sleep_hours: float,
    stress_checkins: List[int],
    missed_quizzes: int,
) -> Dict[str, Any]:
    """Calculate burnout risk score (rule-based, documented ML upgrade path)."""
    risk_score = 0.0
    factors = []

    if study_hours_last_week > 50:
        risk_score += 0.3
        factors.append("Excessive study hours (>50/week)")
    elif study_hours_last_week > 40:
        risk_score += 0.15
        factors.append("High study hours (>40/week)")

    if avg_sleep_hours < 6:
        risk_score += 0.3
        factors.append("Insufficient sleep (<6 hours/night)")
    elif avg_sleep_hours < 7:
        risk_score += 0.1
        factors.append("Below-optimal sleep (<7 hours/night)")

    if stress_checkins:
        avg_stress = sum(stress_checkins) / len(stress_checkins)
        if avg_stress > 7:
            risk_score += 0.25
            factors.append("High average stress level")
        elif avg_stress > 5:
            risk_score += 0.1
            factors.append("Moderate average stress level")

    if missed_quizzes > 3:
        risk_score += 0.15
        factors.append("Multiple missed quizzes")
    elif missed_quizzes > 1:
        risk_score += 0.05
        factors.append("Some missed quizzes")

    risk_score = min(risk_score, 1.0)
    if risk_score >= 0.6:
        risk_level = "high"
    elif risk_score >= 0.3:
        risk_level = "medium"
    else:
        risk_level = "low"

    return {
        "risk_level": risk_level,
        "risk_score": round(risk_score, 2),
        "factors": factors,
    }
