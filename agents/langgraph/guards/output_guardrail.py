"""Output guardrail module.

Scans LLM outputs for leaked system prompts, PII, or unsafe content before
returning to the user. This is the final safety checkpoint.
"""

import re
from typing import Optional

# Patterns that indicate system prompt leakage
SYSTEM_PROMPT_LEAK_PATTERNS = [
    re.compile(r"(you\s+are\s+)?(an?\s+)?(AI|assistant|model)\s+(created|designed|built)\s+by", re.IGNORECASE),
    re.compile(r"your\s+(instructions|prompt|system\s+prompt|rules)\s+(are|is|include)", re.IGNORECASE),
    re.compile(r"as\s+(an?\s+)?(AI|language\s+model|LLM)", re.IGNORECASE),
]

# Patterns that indicate PII in output
PII_PATTERNS = [
    re.compile(r"\b\d{10}\b"),                       # phone
    re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"),  # email
    re.compile(r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b"),  # credit card
]

# Patterns that indicate harmful content
HARMFUL_CONTENT_PATTERNS = [
    re.compile(r"(how\s+to\s+)?(harm|hurt|kill|suicide|self-harm|self-harm|cutting)", re.IGNORECASE),
]


class GuardrailResult:
    def __init__(self, passed: bool, sanitized_output: str, reason: Optional[str] = None):
        self.passed = passed
        self.sanitized_output = sanitized_output
        self.reason = reason


def scan_output(llm_output: str) -> GuardrailResult:
    """Scan LLM output for leaked prompts, PII, or harmful content.

    Returns a GuardrailResult: if failed, the output is replaced with a safe message.
    """
    if not llm_output:
        return GuardrailResult(passed=True, sanitized_output="")

    # Check for system prompt leakage
    for pattern in SYSTEM_PROMPT_LEAK_PATTERNS:
        if pattern.search(llm_output):
            return GuardrailResult(
                passed=False,
                sanitized_output="I apologize, but I encountered an internal error. Please rephrase your question.",
                reason="System prompt leak detected in output",
            )

    # Check for PII leakage
    for pattern in PII_PATTERNS:
        if pattern.search(llm_output):
            return GuardrailResult(
                passed=False,
                sanitized_output="I apologize, but I cannot include personal contact information in responses.",
                reason="PII detected in output",
            )

    # Warn about harmful content patterns (block if severe)
    for pattern in HARMFUL_CONTENT_PATTERNS:
        if pattern.search(llm_output):
            return GuardrailResult(
                passed=False,
                sanitized_output="I'm here to support you. If you're going through a difficult time, "
                "please reach out to a trusted adult, or call a mental health helpline. "
                "You are not alone.",
                reason="Harmful content pattern detected in output",
            )

    return GuardrailResult(passed=True, sanitized_output=llm_output)
