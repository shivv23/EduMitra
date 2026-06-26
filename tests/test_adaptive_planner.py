import pytest
from agents.rag.adaptive_planner import generate_adaptive_plan


class TestAdaptivePlanner:
    async def test_generates_7_day_plan(self):
        plan = await generate_adaptive_plan(
            student_id="test-123",
            subject="Science",
            topic="Photosynthesis",
            mastery_score=0.5,
        )
        assert len(plan.plan) == 7
        assert plan.student_id == "test-123"

    async def test_low_mastery_focuses_on_foundation(self):
        plan = await generate_adaptive_plan(
            student_id="test-123",
            subject="Science",
            topic="Photosynthesis",
            mastery_score=0.2,
        )
        day1 = plan.plan[0]
        assert "core concepts" in day1["focus"].lower() or "foundation" in day1["title"].lower()

    async def test_high_mastery_focuses_on_advanced(self):
        plan = await generate_adaptive_plan(
            student_id="test-123",
            subject="Science",
            topic="Photosynthesis",
            mastery_score=0.8,
        )
        day1 = plan.plan[0]
        assert "advanced" in day1["title"].lower() or "advanced" in day1["focus"].lower()
