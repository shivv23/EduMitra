import logging

from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime, timezone

from src.auth.dependencies import get_current_user_id, require_admin
from src.config.settings import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/data", tags=["Data Protection"])


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def right_to_erasure(student_id: str = Depends(get_current_user_id)):
    """Delete all data for the authenticated student (right to erasure per DPDP Act)."""
    try:
        from src.db import get_supabase
        sb = get_supabase()
        # wellness_data, study_progress, alerts all use student_id column
        for table in ["wellness_data", "study_progress", "alerts"]:
            sb.table(table).delete().eq("student_id", student_id).execute()
        # profiles uses id as the column
        sb.table("profiles").delete().eq("id", student_id).execute()
        logger.info("Erasure completed for student %s", student_id)
        return
    except Exception as e:
        logger.error("Erasure failed for %s: %s", student_id, e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erasure request failed. Please contact support.",
        )


@router.get("/retention-policy")
async def retention_policy(user_id: str = Depends(get_current_user_id)):
    return {
        "student_profile": "365 days after last activity",
        "study_progress": "365 days after last activity",
        "wellness_data": "90 days (encrypted at rest)",
        "session_memory": "180 days",
        "alerts": "365 days (audit log retained anonymized)",
        "raw_audio_uploads": "24 hours",
        "policy_version": "1.0",
        "dpdp_compliant": True,
    }


@router.get("/export", summary="Export my data (DPDP right to data portability)")
async def export_my_data(student_id: str = Depends(get_current_user_id)):
    """Export all data for the authenticated student (right to data portability per DPDP Act)."""
    try:
        from src.db import get_student_profile, get_study_progress, get_wellness_history, get_recent_alerts
        profile = await get_student_profile(student_id)
        progress = await get_study_progress(student_id)
        wellness = await get_wellness_history(student_id)
        alerts = await get_recent_alerts(student_id)

        export = {
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "student_id": student_id,
            "profile": profile,
            "study_progress": progress,
            "wellness_data": wellness,
            "alerts": alerts,
            "dpdp_compliant": True,
            "policy_version": "1.0",
        }
        return export
    except Exception as e:
        logger.error("Data export failed for %s: %s", student_id, e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Data export failed. Please try again later.",
        )
