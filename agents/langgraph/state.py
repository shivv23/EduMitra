from typing import TypedDict, List, Dict, Any, Optional, Annotated
from operator import add


class AgentOutput(TypedDict):
    agent_name: str
    success: bool
    data: Optional[Dict[str, Any]]
    error: Optional[str]


class GraphState(TypedDict):
    student_id: str
    sanitized_input: str
    raw_input: str
    intent: Optional[str]
    conversation_history: Annotated[List[Dict[str, str]], add]
    agent_outputs: Dict[str, AgentOutput]
    final_response: Optional[str]
    requires_escalation: bool
    language: str
    processing_error: Optional[str]
