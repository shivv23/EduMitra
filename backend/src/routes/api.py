"""API routes bridging frontend calls to agents and database."""

import io
import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status as http_status
from pydantic import BaseModel, Field

from src.auth.dependencies import get_current_user_id
from src.config.settings import settings
from src.db import (
    get_study_progress,
    get_wellness_history as db_wellness_history,
    save_wellness_checkin,
    get_recent_alerts,
)
from src.schemas.common import Language, StudyQuery
try:
    from agents.llm import groq_chat
except ImportError:
    groq_chat = None

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["API"])

# ─── Request / Response Schemas ───────────────────────────────


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    history: Optional[List[Dict[str, str]]] = None


class ChatResponse(BaseModel):
    response: str
    type: str = "text"


class QuizRequest(BaseModel):
    topic: Optional[str] = None


class QuizResponse(BaseModel):
    questions: List[Dict[str, Any]]


class WellnessCheckinRequest(BaseModel):
    sentiment_score: int = Field(..., ge=1, le=5)
    note: Optional[str] = None


class WellnessCheckinResponse(BaseModel):
    response: str
    risk_level: str
    crisis_detected: bool = False


class DashboardResponse(BaseModel):
    overall_mastery: int
    topics_covered: int
    quizzes_taken: int
    streak: int
    wellness_status: str
    last_checkin: Optional[str] = None


class VoiceResponse(BaseModel):
    transcript: str
    response: str


class UploadResponse(BaseModel):
    analysis: str
    summary: str


# ─── Gemini Chat Helper ────────────────────────────────────────


_CHAT_SYSTEM_PROMPT = (
    "You are EduMitra, an AI tutor for Indian students (grades 6-12). "
    "Answer clearly and helpfully in simple language. "
    "Reference NCERT/CBSE curriculum concepts where relevant. "
    "If asked in Hindi or another Indian language, respond in that language. "
    "Do NOT use HTML. Output plain text only. Keep responses concise."
)


async def _groq_chat(message: str, history: Optional[List[Dict[str, str]]] = None) -> str:
    try:
        if groq_chat is None:
            raise ImportError("agents module not available")
        response = await groq_chat(
            message=message,
            system_prompt=_CHAT_SYSTEM_PROMPT,
            history=history,
            max_tokens=1024,
            temperature=0.5,
            model="llama-3.3-70b-versatile",
        )
        if response:
            return response
        return "I'm thinking... Please ask again."
    except Exception as e:
        logger.error("Grok chat failed: %s", e)
        return (
            f"I understand you're asking about '{message[:60]}'. I'm having trouble connecting "
            f"to my knowledge engine. Please try again in a moment."
        )


def _demo_study_plan(user_id: str) -> dict:
    return {
        "days": [
            {"day": 1, "title": "Introduction to topic", "focus": "Core concepts", "estimated_minutes": 35, "completed": False},
            {"day": 2, "title": "Deep dive into concepts", "focus": "Understanding fundamentals", "estimated_minutes": 40, "completed": False},
            {"day": 3, "title": "Practice problems", "focus": "Application and practice", "estimated_minutes": 45, "completed": False},
            {"day": 4, "title": "Review and quiz", "focus": "Revision and testing", "estimated_minutes": 30, "completed": False},
            {"day": 5, "title": "Advanced topics", "focus": "Advanced applications", "estimated_minutes": 50, "completed": False},
            {"day": 6, "title": "Mock test", "focus": "Self-assessment", "estimated_minutes": 40, "completed": False},
            {"day": 7, "title": "Final review", "focus": "Revision and next steps", "estimated_minutes": 35, "completed": False},
        ]
    }


def _demo_quiz(topic: Optional[str] = None) -> dict:
    t = topic or "general"
    questions = [
        {
            "question": f"What is the primary concept in {t}?",
            "options": ["Conceptual understanding", "Memorization", "Application", "Analysis"],
            "correctAnswer": 0,
            "explanation": f"Understanding the core concept of {t} is the foundation for further learning.",
        },
        {
            "question": f"Which approach is best for mastering {t}?",
            "options": ["Regular practice", "One-time study", "Group discussion only", "Reading without practice"],
            "correctAnswer": 0,
            "explanation": "Regular practice with consistent effort yields the best learning outcomes.",
        },
        {
            "question": f"What is a common application of {t}?",
            "options": ["Real-world problem solving", "Theoretical only", "No practical use", "Entertainment only"],
            "correctAnswer": 0,
            "explanation": f"{t} has many real-world applications in problem-solving and innovation.",
        },
    ]
    return {"questions": questions}


def _demo_dashboard(user_id: str) -> dict:
    return {
        "overall_mastery": 45,
        "topics_covered": 12,
        "quizzes_taken": 8,
        "streak": 3,
        "wellness_status": "good",
        "last_checkin": datetime.now(timezone.utc).isoformat(),
    }


def _demo_progress(user_id: str) -> dict:
    return {
        "overall_mastery": 45,
        "subjects": [
            {"name": "Mathematics", "mastery": 60, "trend": "+5%"},
            {"name": "Science", "mastery": 45, "trend": "+3%"},
            {"name": "English", "mastery": 70, "trend": "+2%"},
            {"name": "Social Studies", "mastery": 35, "trend": "+8%"},
            {"name": "Hindi", "mastery": 50, "trend": "+1%"},
        ],
        "recent_activity": [
            {"action": "Completed quiz", "detail": "Science: Photosynthesis", "time": "2h ago"},
            {"action": "Studied topic", "detail": "Mathematics: Algebra basics", "time": "1d ago"},
            {"action": "Wellness check-in", "detail": "Feeling good", "time": "2d ago"},
            {"action": "Uploaded notes", "detail": "History chapter 5", "time": "3d ago"},
        ],
        "streak": 3,
        "quizzes_taken": 8,
        "topics_covered": 12,
    }


def _demo_teacher_students() -> dict:
    return {
        "total": 30,
        "average_mastery": 52,
        "need_attention": 4,
        "quizzes_taken": 45,
        "students": [
            {"name": "Aarav Sharma", "grade": "8", "mastery": 78, "status": "excellent"},
            {"name": "Priya Patel", "grade": "8", "mastery": 65, "status": "on-track"},
            {"name": "Rohit Singh", "grade": "8", "mastery": 42, "status": "on-track"},
            {"name": "Ananya Gupta", "grade": "8", "mastery": 30, "status": "needs-support"},
            {"name": "Neha Verma", "grade": "8", "mastery": 88, "status": "excellent"},
            {"name": "Arjun Reddy", "grade": "8", "mastery": 55, "status": "on-track"},
            {"name": "Kavya Nair", "grade": "8", "mastery": 25, "status": "needs-support"},
            {"name": "Vikram Joshi", "grade": "8", "mastery": 70, "status": "excellent"},
        ],
    }


def _demo_parent_progress() -> dict:
    return {
        "mastery": 45,
        "subjects": [
            {"name": "Mathematics", "mastery": 60},
            {"name": "Science", "mastery": 45},
            {"name": "English", "mastery": 70},
            {"name": "Social Studies", "mastery": 35},
            {"name": "Hindi", "mastery": 50},
        ],
        "recent_alerts": [
            {"type": "academic", "message": "Completed Science quiz with 80%", "time": "2h ago"},
            {"type": "wellness", "message": "Wellness check-in: feeling good", "time": "1d ago"},
            {"type": "academic", "message": "New study plan generated for Mathematics", "time": "3d ago"},
        ],
    }


def _demo_wellness_history() -> dict:
    return {
        "checkins": [
            {"sentiment_score": 4, "created_at": (datetime.now(timezone.utc)).isoformat()},
            {"sentiment_score": 3, "created_at": (datetime.now(timezone.utc)).isoformat()},
            {"sentiment_score": 5, "created_at": (datetime.now(timezone.utc)).isoformat()},
            {"sentiment_score": 2, "created_at": (datetime.now(timezone.utc)).isoformat()},
            {"sentiment_score": 4, "created_at": (datetime.now(timezone.utc)).isoformat()},
        ]
    }


# ─── Endpoints ─────────────────────────────────────────────────


@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard(user_id: str = Depends(get_current_user_id)):
    return _demo_dashboard(user_id)


@router.post("/study/query", response_model=ChatResponse)
async def study_query(req: ChatRequest, user_id: str = Depends(get_current_user_id)):
    response = await _groq_chat(req.message, req.history)
    return ChatResponse(response=response, type="text")


@router.post("/langgraph/query", response_model=ChatResponse)
async def langgraph_query(req: ChatRequest, user_id: str = Depends(get_current_user_id)):
    """Route a message through the full LangGraph supervisor pipeline."""
    try:
        from agents.langgraph.supervisor import supervisor_graph

        initial_state = {
            "raw_input": req.message,
            "student_id": user_id,
            "language": "en",
            "sanitized_input": "",
            "intent": "",
            "agent_outputs": {},
            "final_response": "",
        }
        result = await supervisor_graph.ainvoke(initial_state)
        response = result.get("final_response", "")
        if not response:
            response = await _groq_chat(req.message, req.history)
        return ChatResponse(response=response, type="text")
    except Exception as e:
        logger.warning("LangGraph supervisor failed, falling back: %s", e)
        response = await _groq_chat(req.message, req.history)
        return ChatResponse(response=response, type="text")


@router.get("/study/plan")
async def get_study_plan(user_id: str = Depends(get_current_user_id)):
    try:
        from agents.rag.adaptive_planner import generate_adaptive_plan
        plan = await generate_adaptive_plan(
            student_id=user_id,
            subject="General",
            topic="Your current topic",
            mastery_score=0.45,
        )
        return {"days": plan.plan}
    except (ImportError, NotImplementedError):
        return _demo_study_plan(user_id)


@router.post("/study/quiz", response_model=QuizResponse)
async def study_quiz(req: QuizRequest, user_id: str = Depends(get_current_user_id)):
    try:
        from agents.content_gen.generator import generate_quiz
        result = await generate_quiz(topic=req.topic or "general", num_questions=5)
        if result.get("success") and result.get("questions"):
            return QuizResponse(questions=result["questions"])
    except Exception as e:
        logger.warning("generate_quiz failed, using fallback: %s", e)

    return QuizResponse(questions=_demo_quiz(req.topic)["questions"])


@router.post("/study/voice", response_model=VoiceResponse)
async def study_voice(
    audio: UploadFile = File(...),
    language: str = Form("hi"),
    user_id: str = Depends(get_current_user_id),
):
    content = await audio.read()

    try:
        from agents.bhasha.audio_validator import validate_audio_upload
        valid, msg = validate_audio_upload(content)
        if not valid:
            raise HTTPException(status_code=http_status.HTTP_400_BAD_REQUEST, detail=msg)
    except ImportError:
        pass

    try:
        from agents.bhasha.stt_tts import transcribe_audio
        stt_result = await transcribe_audio(content, language)
        transcript = stt_result.get("transcript", "")
        if not transcript:
            return VoiceResponse(
                transcript="",
                response="I couldn't hear anything clearly. Please try speaking closer to the microphone or type your question.",
            )

        response = await _groq_chat(transcript)
        return VoiceResponse(transcript=transcript, response=response)
    except Exception as e:
        logger.warning("voice processing failed: %s", e)
        return VoiceResponse(
            transcript="",
            response="I couldn't transcribe your audio. Please try speaking clearly or type your question instead.",
        )


@router.post("/generate/image")
async def generate_image(
    prompt: str = Form(...),
    aspect_ratio: str = Form("1:1"),
    user_id: str = Depends(get_current_user_id),
):
    try:
        from agents.content_gen.image_generator import generate_image as gen_img
        result = await gen_img(prompt=prompt, aspect_ratio=aspect_ratio)
        if result.get("success"):
            return {
                "image_base64": result["image_base64"],
                "seed": result["seed"],
                "content_type": result["content_type"],
            }
        return {"error": result.get("error", "Image generation failed.")}
    except Exception as e:
        logger.warning("image generation failed: %s", e)
        return {"error": f"Image generation failed: {str(e)}"}


@router.post("/wellness/checkin", response_model=WellnessCheckinResponse)
async def wellness_checkin(
    req: WellnessCheckinRequest,
    user_id: str = Depends(get_current_user_id),
):
    try:
        from agents.wellness.wellness_agent import process_wellness_checkin
        text = req.note or ["struggling", "down", "okay", "good", "great"][req.sentiment_score - 1]
        result = await process_wellness_checkin(
            student_id=user_id,
            text=text,
            language="en",
        )
        risk_level = result.get("risk_level", "none")
        crisis = result.get("escalation_needed", False)

        await save_wellness_checkin(
            student_id=user_id,
            sentiment_score=req.sentiment_score,
            stress_level={"none": 1, "low": 3, "medium": 6, "high": 9}.get(risk_level, 1),
            crisis_detected=crisis,
            risk_level=risk_level,
            note=text,
        )

        if risk_level in ("high", "medium"):
            from agents.progress.alert_dispatcher import dispatch_alert
            await dispatch_alert(
                student_id=user_id,
                alert_type="wellness",
                severity=risk_level,
                message=result.get("response", "Wellness alert"),
                human_in_loop=True,
            )

        return WellnessCheckinResponse(
            response=result.get("response", "Thanks for checking in!"),
            risk_level=risk_level,
            crisis_detected=crisis,
        )
    except (ImportError, NotImplementedError):
        responses = {
            1: "I hear you. It's okay to not be okay. Please reach out to a trusted adult or call a helpline if you need support.",
            2: "I'm here for you. Remember to take breaks and talk to someone you trust about how you're feeling.",
            3: "Thanks for sharing. Doing okay is perfectly fine. Small steps lead to big improvements.",
            4: "That's great to hear! Keep up the positive momentum in your studies and self-care.",
            5: "Wonderful! Your positive attitude is inspiring. Keep taking care of yourself!",
        }
        await save_wellness_checkin(
            student_id=user_id,
            sentiment_score=req.sentiment_score,
            stress_level=req.sentiment_score * 2,
            risk_level="none",
            note=req.note,
        )
        return WellnessCheckinResponse(
            response=responses.get(req.sentiment_score, "Thanks for checking in! Take care of yourself."),
            risk_level="none",
            crisis_detected=False,
        )


@router.get("/wellness/history")
async def get_wellness_history(user_id: str = Depends(get_current_user_id)):
    records = await db_wellness_history(user_id)
    if records:
        checkins = [
            {"sentiment_score": r.get("sentiment_score", 3), "created_at": r.get("created_at", "")}
            for r in records
        ]
        return {"checkins": checkins}
    return _demo_wellness_history()


@router.get("/progress")
async def get_progress(user_id: str = Depends(get_current_user_id)):
    records = await get_study_progress(user_id)
    if records:
        subjects = {}
        for r in records:
            subj = r.get("subject", "General")
            if subj not in subjects:
                subjects[subj] = []
            subjects[subj].append(r.get("mastery_score", 0) or 0)
        subject_list = []
        for name, scores in subjects.items():
            avg = round((sum(scores) / len(scores)) * 100)
            subject_list.append({"name": name, "mastery": avg, "trend": ""})
        overall = round(sum(s["mastery"] for s in subject_list) / len(subject_list)) if subject_list else 0
        total_quizzes = sum(r.get("quizzes_taken", 0) or 0 for r in records)
        total_topics = len(records)
        return {
            "overall_mastery": overall,
            "subjects": subject_list,
            "recent_activity": [],
            "streak": 0,
            "quizzes_taken": total_quizzes,
            "topics_covered": total_topics,
        }
    return _demo_progress(user_id)


@router.get("/progress/burnout-risk")
async def get_burnout_risk(user_id: str = Depends(get_current_user_id)):
    try:
        from agents.progress.memory_tracker import calculate_burnout_risk
        records = await get_study_progress(user_id)
        total_quizzes = sum(r.get("quizzes_taken", 0) or 0 for r in records)
        wellness_data = await db_wellness_history(user_id, limit=10)
        stress_levels = [w.get("stress_level", 0) or 0 for w in wellness_data]
        risk = calculate_burnout_risk(
            study_hours_last_week=28,
            avg_sleep_hours=6.5,
            stress_checkins=stress_levels if stress_levels else [3, 4, 2, 5, 3],
            missed_quizzes=max(0, 3 - total_quizzes),
        )
        return risk
    except Exception as e:
        logger.warning("burnout risk failed: %s", e)
        return {"risk_level": "low", "risk_score": 0.15, "factors": []}


@router.get("/teacher/students")
async def get_teacher_students(user_id: str = Depends(get_current_user_id)):
    try:
        from src.db import get_teacher_students_data, get_study_progress
        relations = await get_teacher_students_data(user_id)
        if not relations:
            return _demo_teacher_students()

        student_ids = list(set(r["student_id"] for r in relations if r.get("student_id")))
        students = []
        for sid in student_ids:
            profile = next((r.get("profiles", {}) for r in relations if r.get("student_id") == sid), {})
            progress = await get_study_progress(sid)
            scores = [p.get("mastery_score", 0) or 0 for p in progress]
            avg_mastery = round((sum(scores) / len(scores)) * 100) if scores else 0
            status = "excellent" if avg_mastery >= 75 else ("on-track" if avg_mastery >= 40 else "needs-support")
            name = profile.get("name", "Unknown")
            grade = profile.get("grade", "")
            students.append({"name": name, "grade": str(grade), "mastery": avg_mastery, "status": status})

        total = len(students)
        avg = round(sum(s["mastery"] for s in students) / total) if total else 0
        need_attention = sum(1 for s in students if s["mastery"] < 40)
        return {
            "total": total,
            "average_mastery": avg,
            "need_attention": need_attention,
            "quizzes_taken": 0,
            "students": students,
        }
    except Exception as e:
        logger.warning("teacher/students DB failed, using demo: %s", e)
        return _demo_teacher_students()


@router.get("/parent/child-progress")
async def get_parent_child_progress(user_id: str = Depends(get_current_user_id)):
    try:
        from src.db import get_linked_students, get_study_progress, get_recent_alerts
        linked = await get_linked_students(user_id)
        if not linked:
            return _demo_parent_progress()

        subjects = {}
        for link in linked:
            student_id = link.get("student_id", "")
            progress = await get_study_progress(student_id)
            for p in progress:
                subj = p.get("subject", "General")
                score = (p.get("mastery_score", 0) or 0) * 100
                if subj not in subjects:
                    subjects[subj] = []
                subjects[subj].append(score)

        subject_list = [
            {"name": name, "mastery": round(sum(scores) / len(scores))}
            for name, scores in subjects.items()
        ] or [{"name": "General", "mastery": 0}]

        overall = round(sum(s["mastery"] for s in subject_list) / len(subject_list)) if subject_list else 0
        child_ids = [link.get("student_id", "") for link in linked if link.get("student_id")]
        alerts = []
        for cid in child_ids:
            alerts.extend(await get_recent_alerts(cid, limit=3))
        alerts.sort(key=lambda a: a.get("created_at", ""), reverse=True)
        alerts = alerts[:5]
        recent = [
            {"type": a.get("alert_type", "info"), "message": a.get("message", ""), "time": a.get("created_at", "")}
            for a in alerts[:5]
        ] if alerts else [
            {"type": "info", "message": "No recent alerts", "time": ""},
        ]

        return {"mastery": overall, "subjects": subject_list, "recent_alerts": recent}
    except Exception as e:
        logger.warning("parent/child-progress DB failed, using demo: %s", e)
        return _demo_parent_progress()
