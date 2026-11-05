from typing import Optional, TypedDict

# Strict agent input: user id, role, request id, question (nothing else)
# Agent data is a dictionary: read it like state["question"], never state.question
class AgentState(TypedDict, total=False):
    user_id: int
    role: str
    request_id: str
    question: str
    route: Optional[str]
    final_answer: Optional[str]
    sources: Optional[list[dict]]
