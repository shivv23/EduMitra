"""Wellness Agent — detects emotional state and offers supportive coaching.

SAFETY-CRITICAL: Never diagnoses, prescribes, or claims to be medical professional.
"""

import logging
from typing import Dict, Any

from agents.wellness.crisis_classifier import classify_crisis_risk, build_crisis_response

logger = logging.getLogger(__name__)

DISCLAIMER = (
    "I'm here to support you as a wellness companion. I'm not a mental health "
    "professional or a substitute for professional medical advice, diagnosis, or treatment. "
    "If you're experiencing a crisis, please reach out to a helpline or a trusted adult."
)


async def process_wellness_checkin(
    student_id: str,
    text: str,
    language: str = "en",
) -> Dict[str, Any]:
    """Process a wellness check-in from a student.

    Args:
        student_id: Authenticated student UUID.
        text: The student's message (already sanitized).
        language: Language code.

    Returns:
        Dict with risk_level, response, and escalation_needed flag.
    """
    logger.info("Wellness check-in for student %s (lang: %s)", student_id, language)

    # 1. Deterministic crisis classification
    risk_level, matched_keywords = classify_crisis_risk(text)

    # 2. Build response
    crisis_response = build_crisis_response(risk_level)

    if crisis_response:
        response = f"{DISCLAIMER}\n\n{crisis_response}"
        escalation_needed = risk_level in ("high", "medium")
    else:
        # Low stress — generate supportive CBT-style response
        # Placeholder: connect to LLM with strict safety guardrails
        response = (
            f"{DISCLAIMER}\n\n"
            "It sounds like you're managing your studies. Remember to take breaks, "
            "stay hydrated, and get enough sleep. You're doing great!"
        )
        escalation_needed = False

    return {
        "risk_level": risk_level,
        "response": response,
        "escalation_needed": escalation_needed,
        "matched_keywords": matched_keywords,
    }
