"""LangGraph Supervisor — routes requests to specialized agents based on intent."""

import asyncio
import logging
from typing import Literal

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from agents.langgraph.state import GraphState
from agents.langgraph.sanitizer import sanitize_input, build_safe_prompt
from agents.langgraph.guards.output_guardrail import scan_output
from agents.langgraph.circuit_breaker import agent_node_wrapper

logger = logging.getLogger(__name__)

# ─── Intent Classification ─────────────────────────────────────


def classify_intent(state: GraphState) -> GraphState:
    """Classify the user's intent from their input."""
    text = state.get("sanitized_input", "").lower()

    if any(word in text for word in ["upload", "photo", "image", "picture", "handwritten", "notes", "diagram"]):
        state["intent"] = "notes_upload"
    elif any(word in text for word in ["stress", "anxious", "worried", "sad", "depressed", "burnout", "tired"]):
        state["intent"] = "wellness_check"
    elif any(word in text for word in ["progress", "score", "mastery", "improvement", "report"]):
        state["intent"] = "progress_view"
    else:
        state["intent"] = "study_query"

    return state


# ─── Router ────────────────────────────────────────────────────


def route_to_agent(state: GraphState) -> Literal[
    "multimodal_agent",
    "curriculum_rag_agent",
    "wellness_agent",
    "content_gen_agent",
    "bhasha_mitra_agent",
    "progress_alert_agent",
]:
    """Route to the appropriate agent based on classified intent."""
    intent = state.get("intent", "study_query")

    if intent == "notes_upload":
        return "multimodal_agent"
    elif intent == "wellness_check":
        return "wellness_agent"
    elif intent == "progress_view":
        return "progress_alert_agent"
    else:
        return "curriculum_rag_agent"


# ─── Agent Stubs (wired to full implementations in P3-P8) ──────


async def curriculum_rag_agent(state: GraphState) -> GraphState:
    """Curriculum RAG Agent — retrieves context from ChromaDB and answers via Gemini."""
    logger.info("CurriculumRAGAgent invoked for student %s", state["student_id"])
    prompt = state.get("sanitized_input") or state.get("raw_input", "")
    try:
        from agents.rag.retriever import retrieve_context, format_context_for_prompt
        from agents.rag.vector_store import seed_curriculum
        from agents.langgraph.sanitizer import build_safe_prompt
        from agents.llm import groq_chat

        await asyncio.to_thread(seed_curriculum)

        results = await retrieve_context(
            query=prompt,
            student_id=state["student_id"],
        )
        context = format_context_for_prompt(results)

        system_prompt = (
            "You are EduMitra, an AI tutor for Indian students. "
            "Answer clearly using NCERT/CBSE curriculum concepts. "
            "If asked in Hindi or another Indian language, respond in that language. "
            "Keep responses concise and age-appropriate. No HTML."
        )
        if context:
            system_prompt += f"\n\nRelevant curriculum context:\n{context}"

        response = await groq_chat(
            message=prompt,
            system_prompt=system_prompt,
            max_tokens=1024,
            temperature=0.5,
            model="llama-3.3-70b-versatile",
        )
        state["agent_outputs"]["curriculum_rag"] = {
            "agent_name": "curriculum_rag",
            "success": True,
            "data": {"message": response or "I'm thinking..."},
            "error": None,
        }
    except Exception as e:
        logger.error("CurriculumRAGAgent failed: %s", e)
        state["agent_outputs"]["curriculum_rag"] = {
            "agent_name": "curriculum_rag",
            "success": False,
            "data": {"message": "I'm having trouble connecting. Please try again."},
            "error": str(e),
        }
    return state


async def content_gen_agent(state: GraphState) -> GraphState:
    """ContentGen Agent — generates explanations and quizzes via Gemini."""
    logger.info("ContentGenAgent invoked for student %s", state["student_id"])
    try:
        from agents.content_gen.generator import generate_explanation
        topic = state.get("sanitized_input") or state.get("raw_input", "")
        result = await generate_explanation(topic=topic, subject="General", grade=8)
        state["agent_outputs"]["content_gen"] = {
            "agent_name": "content_gen",
            "success": result.get("success", False),
            "data": {"message": result.get("explanation", result.get("error", "No content generated."))},
            "error": None if result.get("success") else result.get("error"),
        }
    except Exception as e:
        logger.error("ContentGenAgent failed: %s", e)
        state["agent_outputs"]["content_gen"] = {
            "agent_name": "content_gen",
            "success": False,
            "data": {"message": "Content generation failed. Please try again."},
            "error": str(e),
        }
    return state


async def multimodal_agent(state: GraphState) -> GraphState:
    """Multimodal Agent — analyzes images (called when file is pre-uploaded)."""
    logger.info("MultimodalAgent invoked for student %s", state["student_id"])
    state["agent_outputs"]["multimodal"] = {
        "agent_name": "multimodal",
        "success": True,
        "data": {"message": "Upload your image or notes for analysis."},
        "error": None,
    }
    return state


async def wellness_agent(state: GraphState) -> GraphState:
    """Wellness Agent — processes check-in via deterministic classifier."""
    logger.info("WellnessAgent invoked for student %s", state["student_id"])
    try:
        from agents.wellness.wellness_agent import process_wellness_checkin
        text = state.get("sanitized_input") or state.get("raw_input", "")
        result = await process_wellness_checkin(
            student_id=state["student_id"],
            text=text,
            language=state.get("language", "en"),
        )
        state["agent_outputs"]["wellness"] = {
            "agent_name": "wellness",
            "success": True,
            "data": {
                "message": result.get("response", ""),
                "risk_level": result.get("risk_level", "none"),
                "escalation": result.get("escalation_needed", False),
            },
            "error": None,
        }
    except Exception as e:
        logger.error("WellnessAgent failed: %s", e)
        state["agent_outputs"]["wellness"] = {
            "agent_name": "wellness",
            "success": False,
            "data": {"message": "Wellness check-in encountered an issue.", "risk_level": "none"},
            "error": str(e),
        }
    return state


async def bhasha_mitra_agent(state: GraphState) -> GraphState:
    """BhashaMitra Agent — handles voice/STT (needs Sarvam API key)."""
    logger.info("BhashaMitraAgent invoked for student %s", state["student_id"])
    state["agent_outputs"]["bhasha_mitra"] = {
        "agent_name": "bhasha_mitra",
        "success": True,
        "data": {"message": "Voice support is available in the Voice tab."},
        "error": None,
    }
    return state


async def progress_alert_agent(state: GraphState) -> GraphState:
    """Progress & Alert Agent — tracks mastery and alerts."""
    logger.info("ProgressAlertAgent invoked for student %s", state["student_id"])
    state["agent_outputs"]["progress_alert"] = {
        "agent_name": "progress_alert",
        "success": True,
        "data": {"message": "Your progress is being tracked. Check the Progress page for details."},
        "error": None,
    }
    return state


# ─── Input Processing ─────────────────────────────────────────


def process_input(state: GraphState) -> GraphState:
    """First node: sanitize input and wrap in safe prompt."""
    raw = state.get("raw_input", "")
    state["sanitized_input"] = sanitize_input(raw)
    return state


def final_output(state: GraphState) -> GraphState:
    """Final node: run output guardrail and prepare response."""
    last_agent = list(state["agent_outputs"].keys())[-1] if state["agent_outputs"] else None
    if last_agent:
        agent_data = state["agent_outputs"].get(last_agent, {})
        data = agent_data.get("data", {})
        if isinstance(data, dict):
            raw_response = str(data.get("message", str(data)))
        else:
            raw_response = str(data)
        guardrail = scan_output(raw_response)
        if guardrail.passed:
            state["final_response"] = guardrail.sanitized_output
        else:
            logger.warning("Output guardrail blocked response: %s", guardrail.reason)
            state["final_response"] = guardrail.sanitized_output
    return state


# ─── Build Graph ────────────────────────────────────────────────


def build_supervisor_graph() -> StateGraph:
    workflow = StateGraph(GraphState)

    # Nodes (agent nodes wrapped with circuit breaker + timeout)
    workflow.add_node("process_input", process_input)
    workflow.add_node("classify_intent", classify_intent)
    workflow.add_node("curriculum_rag_agent", agent_node_wrapper("curriculum_rag", curriculum_rag_agent))
    workflow.add_node("content_gen_agent", agent_node_wrapper("content_gen", content_gen_agent))
    workflow.add_node("multimodal_agent", agent_node_wrapper("multimodal", multimodal_agent))
    workflow.add_node("wellness_agent", agent_node_wrapper("wellness", wellness_agent))
    workflow.add_node("bhasha_mitra_agent", agent_node_wrapper("bhasha_mitra", bhasha_mitra_agent))
    workflow.add_node("progress_alert_agent", agent_node_wrapper("progress_alert", progress_alert_agent))
    workflow.add_node("final_output", final_output)

    # Edges
    workflow.set_entry_point("process_input")
    workflow.add_edge("process_input", "classify_intent")
    workflow.add_conditional_edges("classify_intent", route_to_agent, {
        "curriculum_rag_agent": "curriculum_rag_agent",
        "content_gen_agent": "content_gen_agent",
        "multimodal_agent": "multimodal_agent",
        "wellness_agent": "wellness_agent",
        "bhasha_mitra_agent": "bhasha_mitra_agent",
        "progress_alert_agent": "progress_alert_agent",
    })

    # All agents route to final output
    for agent_node in [
        "curriculum_rag_agent",
        "content_gen_agent",
        "multimodal_agent",
        "wellness_agent",
        "bhasha_mitra_agent",
        "progress_alert_agent",
    ]:
        workflow.add_edge(agent_node, "final_output")

    workflow.add_edge("final_output", END)

    # Compile with in-memory checkpointing
    memory = MemorySaver()
    return workflow.compile(checkpointer=memory)


supervisor_graph = build_supervisor_graph()
