from typing import List, Literal, Optional
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

class CamelCaseModel(BaseModel):
    """Model that configures CamelCase alias generation,
    use this as base for other models as needed (e.g. when
    returning a json dict with FastAPI)"""
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True
    )

class ChatMessage(CamelCaseModel):
    """Represents a message in the chat"""
    role: Literal['assistant', 'system', 'user']
    content: str
    color: Optional[str] = None

class ChatbotState(CamelCaseModel):
    """Encapsulates the state of the chatbot,
    for use when recovering the UI"""
    messages: List[ChatMessage]
    is_locked: bool