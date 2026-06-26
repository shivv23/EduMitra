from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum


class Intent(str, Enum):
    STUDY_QUERY = "study_query"
    NOTES_UPLOAD = "notes_upload"
    WELLNESS_CHECK = "wellness_check"
    PROGRESS_VIEW = "progress_view"
    LANGUAGE_SWITCH = "language_switch"
    GENERAL_CHAT = "general_chat"


class AgentOutput(BaseModel):
    agent_name: str
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class GraphState(BaseModel):
    student_id: str
    sanitized_input: str
    intent: Optional[Intent] = None
    conversation_history: List[Dict[str, str]] = Field(default_factory=list, max_length=50)
    agent_outputs: Dict[str, AgentOutput] = Field(default_factory=dict)
    final_response: Optional[str] = None
    requires_escalation: bool = False
    language: str = "en"
