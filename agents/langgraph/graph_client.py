"""Client interface for the LangGraph supervisor graph."""

import logging
import uuid
from typing import Optional, Dict, Any

from agents.langgraph.state import GraphState
from agents.langgraph.supervisor import supervisor_graph

logger = logging.getLogger(__name__)


async def run_agent(
    student_id: str,
    user_input: str,
    conversation_history: Optional[list] = None,
    language: str = "en",
) -> Dict[str, Any]:
    """Run the EduMitra multi-agent system on a user input.

    Args:
        student_id: Authenticated student's UUID.
        user_input: Raw input from the student (text, transcribed voice, etc.).
        conversation_history: Previous conversation messages (bounded to 50).
        language: Language code (e.g., 'hi', 'ta', 'en').

    Returns:
        Dict with 'response', 'agent_trace', and 'requires_escalation' keys.
    """
    config = {"configurable": {"thread_id": str(uuid.uuid4())}}

    initial_state: GraphState = {
        "student_id": student_id,
        "raw_input": user_input,
        "sanitized_input": "",
        "intent": None,
        "conversation_history": conversation_history or [],
        "agent_outputs": {},
        "final_response": None,
        "requires_escalation": False,
        "language": language,
        "processing_error": None,
    }

    try:
        final_state = await supervisor_graph.ainvoke(initial_state, config)
    except Exception as e:
        logger.error("Graph execution failed for student %s: %s", student_id, str(e))
        return {
            "response": "I'm sorry, something went wrong. Please try again.",
            "agent_trace": {},
            "requires_escalation": False,
            "error": str(e),
        }

    return {
        "response": final_state.get("final_response", ""),
        "agent_trace": final_state.get("agent_outputs", {}),
        "requires_escalation": final_state.get("requires_escalation", False),
        "intent": final_state.get("intent"),
    }
