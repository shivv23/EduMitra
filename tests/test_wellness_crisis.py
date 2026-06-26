import pytest
from agents.wellness.crisis_classifier import (
    classify_crisis_risk,
    build_crisis_response,
    HELPLINES,
)


class TestCrisisClassifier:
    def test_high_risk_detected(self):
        risk, matched = classify_crisis_risk("I want to kill myself")
        assert risk == "high"
        assert "kill myself" in matched

    def test_high_risk_alternative_phrasing(self):
        risk, matched = classify_crisis_risk("I feel like ending my life")
        assert risk == "high"

    def test_medium_risk_detected(self):
        risk, matched = classify_crisis_risk("I feel hopeless and worthless")
        assert risk == "medium"

    def test_low_risk_detected(self):
        risk, matched = classify_crisis_risk("I'm so stressed about exams")
        assert risk == "low"

    def test_no_crisis_detected(self):
        risk, matched = classify_crisis_risk("Can you help me understand photosynthesis?")
        assert risk == "none"
        assert matched == []

    def test_normal_study_query_not_flagged(self):
        risk, matched = classify_crisis_risk("Explain Newton's laws of motion")
        assert risk == "none"

    def test_empty_text_returns_none(self):
        risk, matched = classify_crisis_risk("")
        assert risk == "none"


class TestCrisisResponse:
    def test_high_risk_returns_helplines(self):
        response = build_crisis_response("high")
        assert "helpline" in response.lower() or "call" in response.lower()
        # Verify helplines are from the configurable constant, not generated
        for h in HELPLINES:
            assert h["number"] in response

    def test_medium_risk_contains_support_message(self):
        response = build_crisis_response("medium")
        assert "helpline" in response.lower() or "help" in response.lower()

    def test_low_risk_returns_empty_pre_response(self):
        response = build_crisis_response("low")
        assert response == ""

    def test_helplines_are_not_generated_by_llm(self):
        """Verify helplines are a static configurable constant, never generated."""
        assert len(HELPLINES) > 0
        for h in HELPLINES:
            assert "name" in h
            assert "number" in h
            assert isinstance(h["number"], str)


class TestMedicalClaimGuard:
    """The Wellness Agent must NEVER make medical claims or diagnoses."""

    FORBIDDEN_PATTERNS = [
        "I diagnose you with",
        "you have depression",
        "prescribe",
        "clinical treatment",
        "you are suffering from",
    ]

    DISCLAIMER_TEXT = "I'm not a mental health professional"

    def test_response_contains_disclaimer(self):
        from agents.wellness.wellness_agent import DISCLAIMER
        assert "not a mental health professional" in DISCLAIMER.lower()
