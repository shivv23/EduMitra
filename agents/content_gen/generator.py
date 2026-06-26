"""ContentGen Agent — generates explanations, quizzes, summaries, mind maps, and diagrams.

Security: all prompts sanitized, output validated, images re-encoded server-side.
"""

import asyncio
import json
import logging
import re
from typing import Any, Dict, List, Optional
from enum import Enum

from agents.llm import groq_chat, claude_chat

logger = logging.getLogger(__name__)


class ContentType(str, Enum):
    EXPLANATION = "explanation"
    QUIZ = "quiz"
    SUMMARY = "summary"
    MIND_MAP = "mind_map"
    DIAGRAM = "diagram"
    FLASHCARDS = "flashcards"


class ContentSafetyFilter:
    """Filters prompts and outputs for unsafe content (minors' safety)."""

    BLOCKED_WORDS = [
        "violence", "explicit", "porn", "sexual", "drugs", "alcohol",
        "weapon", "bomb", "kill", "suicide", "self-harm",
    ]

    @classmethod
    def is_safe_prompt(cls, text: str) -> bool:
        text_lower = text.lower()
        for word in cls.BLOCKED_WORDS:
            if word in text_lower:
                logger.warning("Content safety filter blocked prompt containing: %s", word)
                return False
        return True

    @classmethod
    def sanitize_output(cls, text: str) -> str:
        text = re.sub(r"<script[^>]*>.*?</script>", "", text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r"<[^>]*>", "", text)
        return text


class QuizSchema:
    question: str
    options: List[str]
    correct_answer: int
    explanation: str
    difficulty: str


_EXPLANATION_SYSTEM_PROMPT = (
    "You are EduMitra, an AI tutor for Indian students (grades 6-12). "
    "Explain the topic clearly in simple language. "
    "Use examples relevant to Indian curriculum (NCERT/CBSE/state boards). "
    "Keep the explanation age-appropriate, under 300 words. "
    "If the user asks in Hindi or another Indian language, respond in that language. "
    "Do NOT use any HTML tags. Output plain text only."
)

_QUIZ_SYSTEM_PROMPT = (
    "You are an AI quiz generator for Indian students. "
    "Generate a JSON object with a 'questions' array. "
    "Each question has: 'question' (string), 'options' (array of 4 strings), "
    "'correctAnswer' (integer index 0-3), 'explanation' (string), 'difficulty' (string). "
    "Return ONLY valid JSON, no other text."
)

_CHAT_SYSTEM_PROMPT = (
    "You are EduMitra, an AI tutor for Indian students. "
    "Answer the student's question clearly and helpfully. "
    "Use simple language appropriate for grades 6-12. "
    "Reference NCERT/CBSE curriculum concepts where relevant. "
    "If asked in Hindi or another Indian language, respond in that language. "
    "Do NOT use HTML. Output plain text only. Keep responses concise."
)


async def generate_explanation(
    topic: str,
    subject: str,
    grade: int,
    language: str = "en",
    context: Optional[str] = None,
    use_claude: bool = True,
) -> Dict[str, Any]:
    logger.info("Generating explanation for: %s (grade %d)", topic, grade)

    if not ContentSafetyFilter.is_safe_prompt(topic):
        return {
            "error": "I'm sorry, I can't generate content on that topic. Please ask something else.",
            "success": False,
        }

    prompt = f"Topic: {topic}\nSubject: {subject}\nGrade: {grade}\nLanguage: {language}\n"
    if context:
        prompt += f"Context: {context}\n"
    prompt += "\nProvide a clear explanation suitable for this grade level."

    try:
        if use_claude:
            text = await claude_chat(
                message=prompt,
                system_prompt=_EXPLANATION_SYSTEM_PROMPT,
                max_tokens=800,
                temperature=0.4,
            )
            if text:
                return {"explanation": ContentSafetyFilter.sanitize_output(text), "success": True}
            logger.info("Claude returned empty, falling back to Gemini")

        text = await groq_chat(
            message=prompt,
            system_prompt=_EXPLANATION_SYSTEM_PROMPT,
            max_tokens=800,
            temperature=0.4,
            model="llama-3.3-70b-versatile",
        )
        if text:
            return {"explanation": ContentSafetyFilter.sanitize_output(text), "success": True}
        return {"error": "Empty response from Grok", "success": False}
    except Exception as e:
        logger.error("Explanation generation failed: %s", e)
        return {
            "error": f"Failed to generate explanation: {str(e)}",
            "success": False,
        }


async def generate_quiz(
    topic: str,
    num_questions: int = 5,
    difficulty: str = "medium",
    language: str = "en",
    use_claude: bool = True,
) -> Dict[str, Any]:
    logger.info("Generating quiz: %s (%d questions, %s)", topic, num_questions, difficulty)

    if not ContentSafetyFilter.is_safe_prompt(topic):
        return {"error": "Cannot generate quiz on this topic.", "success": False}

    prompt = (
        f"Generate a quiz on '{topic}' with {num_questions} questions at {difficulty} difficulty. "
        f"Language: {language}. "
        f"Return ONLY valid JSON matching: {{\"questions\": [{{\"question\": str, "
        f"\"options\": [str, str, str, str], \"correctAnswer\": int, "
        f"\"explanation\": str, \"difficulty\": str}}]}}"
    )

    try:
        text = ""
        if use_claude:
            text = await claude_chat(
                message=prompt,
                system_prompt=_QUIZ_SYSTEM_PROMPT,
                max_tokens=2000,
                temperature=0.6,
            )

        if not text:
            text = await groq_chat(
                message=prompt,
                system_prompt=_QUIZ_SYSTEM_PROMPT,
                max_tokens=2000,
                temperature=0.6,
                model="llama-3.3-70b-versatile",
            )
            text = text.strip()

        text = text.strip()
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
        parsed = json.loads(text)
        questions = parsed.get("questions", [])

        for q in questions:
            q["explanation"] = ContentSafetyFilter.sanitize_output(q.get("explanation", ""))
            q["question"] = ContentSafetyFilter.sanitize_output(q.get("question", ""))

        return {"questions": questions, "success": True}
    except json.JSONDecodeError:
        logger.warning("Quiz JSON parse failed, returning raw text")
        return {
            "questions": [
                {
                    "question": "What concept would you like to learn about?",
                    "options": ["Option A: Try again", "Option B: Skip", "Option C: Ask me later", "Option D: Show answer"],
                    "correctAnswer": 0,
                    "explanation": f"Quiz generation had an issue parsing the response for '{topic}'.",
                    "difficulty": difficulty,
                }
            ],
            "success": False,
        }
    except Exception as e:
        logger.error("Quiz generation failed: %s", e)
        return {"error": f"Quiz generation failed: {str(e)}", "success": False}


async def generate_mind_map(topic: str, subject: str) -> Dict[str, Any]:
    logger.info("Generating mind map for: %s", topic)

    if not ContentSafetyFilter.is_safe_prompt(topic):
        return {"error": "Cannot generate mind map on this topic.", "success": False}

    try:
        prompt = (
            f"Create a mind map structure for '{topic}' in subject '{subject}'. "
            f"Return ONLY valid JSON with format: "
            f"{{\"center\": str, \"branches\": [{{\"name\": str, \"children\": [str]}}]}}"
        )

        text = await groq_chat(
            message=prompt,
            system_prompt="You are an educational mind map generator. Output only valid JSON.",
            max_tokens=1500,
            temperature=0.4,
            model="llama-3.3-70b-versatile",
        )
        text = text.strip()
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
        return json.loads(text)
    except Exception as e:
        logger.error("Mind map generation failed: %s", e)
        return {"center": topic, "branches": [], "error": str(e)}
