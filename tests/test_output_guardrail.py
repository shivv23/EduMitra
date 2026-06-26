import pytest
from agents.langgraph.guards.output_guardrail import scan_output


class TestOutputGuardrail:
    def test_normal_output_passes(self):
        result = scan_output("Gravity is a force that attracts objects toward Earth.")
        assert result.passed is True
        assert "Gravity" in result.sanitized_output

    def test_blocks_system_prompt_leak(self):
        result = scan_output("You are an AI assistant created by EduMitra. Your instructions are...")
        assert result.passed is False
        assert "internal error" in result.sanitized_output.lower()

    def test_blocks_phone_pii(self):
        result = scan_output("Call me at 9876543210 for help")
        assert result.passed is False
        assert "cannot include" in result.sanitized_output.lower()

    def test_blocks_email_pii(self):
        result = scan_output("Email me at student@test.com")
        assert result.passed is False

    def test_empty_output_passes(self):
        result = scan_output("")
        assert result.passed is True

    def test_none_output_passes(self):
        result = scan_output(None)
        assert result.passed is True
