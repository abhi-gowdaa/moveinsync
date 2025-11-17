from typing import TypedDict, List, Optional, Annotated
from langchain_core.messages import BaseMessage
import operator

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    user_message: str
    current_page: str
    image_path: Optional[str]
    
    response: str
    pending_action: Optional[dict]
    awaiting_confirmation: bool
    consequences: List[str]
    context: dict
    session_id: Optional[str]
 