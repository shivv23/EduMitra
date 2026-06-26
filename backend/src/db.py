"""Supabase client and database helper functions."""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from supabase import Client, create_client

from src.config.settings import settings

logger = logging.getLogger(__name__)

_client: Optional[Client] = None


def get_supabase() -> Client:
    global _client
    if _client is None:
        _client = create_client(settings.supabase_url, settings.supabase_service_role_key)
    return _client


async def get_student_profile(student_id: str) -> Dict[str, Any]:
    try:
        sb = get_supabase()
        result = sb.table("profiles").select("*").eq("id", student_id).limit(1).execute()
        if result.data:
            return result.data[0]
    except Exception as e:
        logger.warning("Failed to fetch profile for %s: %s", student_id, e)
    return {}


async def get_study_progress(student_id: str) -> List[Dict[str, Any]]:
    try:
        sb = get_supabase()
        result = sb.table("study_progress").select("*").eq("student_id", student_id).execute()
        return list(result.data) if result.data else []
    except Exception as e:
        logger.warning("Failed to fetch progress for %s: %s", student_id, e)
    return []


async def save_study_progress(
    student_id: str,
    subject: str,
    topic: str,
    mastery_score: float,
    quizzes_taken: int = 1,
    quizzes_passed: int = 1,
    study_plan: Optional[str] = None,
) -> Dict[str, Any]:
    try:
        sb = get_supabase()
        now = datetime.now(timezone.utc).isoformat()
        existing = (
            sb.table("study_progress")
            .select("*")
            .eq("student_id", student_id)
            .eq("subject", subject)
            .eq("topic", topic)
            .limit(1)
            .execute()
        )

        payload = {
            "student_id": student_id,
            "subject": subject,
            "topic": topic,
            "mastery_score": mastery_score,
            "quizzes_taken": quizzes_taken,
            "quizzes_passed": quizzes_passed,
            "updated_at": now,
        }
        if study_plan is not None:
            payload["study_plan"] = study_plan

        if existing.data:
            payload["quizzes_taken"] = existing.data[0].get("quizzes_taken", 0) + quizzes_taken
            payload["quizzes_passed"] = existing.data[0].get("quizzes_passed", 0) + quizzes_passed
            result = sb.table("study_progress").update(payload).eq("id", existing.data[0]["id"]).execute()
        else:
            payload["created_at"] = now
            result = sb.table("study_progress").insert(payload).execute()

        if result.data:
            return result.data[0]
    except Exception as e:
        logger.warning("Failed to save progress for %s: %s", student_id, e)
    return {}


async def get_wellness_history(student_id: str, limit: int = 20) -> List[Dict[str, Any]]:
    try:
        sb = get_supabase()
        result = (
            sb.table("wellness_data")
            .select("*")
            .eq("student_id", student_id)
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return list(result.data) if result.data else []
    except Exception as e:
        logger.warning("Failed to fetch wellness history for %s: %s", student_id, e)
    return []


async def save_wellness_checkin(
    student_id: str,
    sentiment_score: int,
    stress_level: int = 0,
    crisis_detected: bool = False,
    risk_level: str = "none",
    note: Optional[str] = None,
) -> Dict[str, Any]:
    try:
        sb = get_supabase()
        payload = {
            "student_id": student_id,
            "sentiment_score": sentiment_score,
            "stress_level": stress_level,
            "crisis_detected": crisis_detected,
            "risk_level": risk_level,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        if note:
            payload["content_encrypted"] = note
        result = sb.table("wellness_data").insert(payload).execute()
        if result.data:
            return result.data[0]
    except Exception as e:
        logger.warning("Failed to save wellness check-in: %s", e)
    return {}


async def save_alert(
    student_id: str,
    alert_type: str,
    severity: str,
    dispatched_to: Optional[str] = None,
    human_in_loop: bool = False,
) -> Dict[str, Any]:
    try:
        sb = get_supabase()
        payload = {
            "student_id": student_id,
            "alert_type": alert_type,
            "severity": severity,
            "dispatched_to": dispatched_to or "",
            "human_in_loop": human_in_loop,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        result = sb.table("alerts").insert(payload).execute()
        if result.data:
            return result.data[0]
    except Exception as e:
        logger.warning("Failed to save alert: %s", e)
    return {}


async def get_recent_alerts(student_id: str, limit: int = 10) -> List[Dict[str, Any]]:
    try:
        sb = get_supabase()
        result = (
            sb.table("alerts")
            .select("*")
            .eq("student_id", student_id)
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return list(result.data) if result.data else []
    except Exception as e:
        logger.warning("Failed to fetch alerts for %s: %s", student_id, e)
    return []


async def get_linked_students(parent_id: str) -> List[Dict[str, Any]]:
    try:
        sb = get_supabase()
        result = (
            sb.table("parent_links")
            .select("student_id, profiles!inner(id, name, grade, language)")
            .eq("parent_id", parent_id)
            .eq("verified", True)
            .execute()
        )
        return list(result.data) if result.data else []
    except Exception as e:
        logger.warning("Failed to fetch linked students for %s: %s", parent_id, e)
    return []


async def get_teacher_students_data(teacher_id: str) -> List[Dict[str, Any]]:
    try:
        sb = get_supabase()
        result = (
            sb.table("teacher_students")
            .select("student_id, subject, profiles!inner(id, name, grade)")
            .eq("teacher_id", teacher_id)
            .execute()
        )
        return list(result.data) if result.data else []
    except Exception as e:
        logger.warning("Failed to fetch teacher students for %s: %s", teacher_id, e)
    return []
