from pydantic import BaseModel, Field, validator
from typing import List, Dict, Optional, Any
from app.schemas.common import UserType, ChatMode, MessageItem
from app.schemas.base import StandardResponse

# Chat Request/Response Models
class ChatRequest(BaseModel):
    user_id: str
    user_type: UserType
    chat_mode: ChatMode = ChatMode.GENERAL  # Default to general chat
    feature: str
    last_messages: List[str] = Field(
        default=[],
        description="List of previous messages in the conversation. Up to 8 messages will be used."
        "The messages should be ordered chronologically with the oldest message first."
        "Odd-indexed messages (0, 2, 4, 6) will be treated as user messages, "
        "and even-indexed messages (1, 3, 5, 7) will be treated as assistant responses."
    )
    model: Optional[str] = ""  # Model can be empty and will be determined based on user type and chat mode
    temperature: Optional[float] = 0.7
    system_prompt: Optional[str] = ""
    user_prompt: str
    
    @validator('user_prompt')
    def user_prompt_must_not_be_empty(cls, v):
        if not v or v.strip() == "":
            raise ValueError('user_prompt cannot be empty')
        return v
    
    class Config:
        # This allows the model to accept missing fields that have defaults
        populate_by_name = True
        validate_assignment = True

class ChatResponseData(BaseModel):
    response: str

class ChatResponse(StandardResponse):
    data: ChatResponseData

# Summary Request/Response Models
class SummaryRequest(BaseModel):
    user_id: str
    user_type: UserType
    messages: List[MessageItem]  # List of chat messages to summarize
    model: Optional[str] = ""  # Model can be empty and will be determined based on user type
    
    @validator('messages')
    def messages_not_empty(cls, v):
        if not v or len(v) == 0:
            raise ValueError('messages cannot be empty')
        return v
    
    class Config:
        populate_by_name = True
        validate_assignment = True

class SummaryResponseData(BaseModel):
    summary: str

class SummaryResponse(StandardResponse):
    data: SummaryResponseData

# Analysis Request/Response Models

class ToneItem(BaseModel):
    name: str
    description: str
    manifests: str
    triggers: str
class AnalysisRequest(BaseModel):
    user_id: str
    user_type: UserType
    messages: List[MessageItem]  # List of chat messages to analyze
    model: Optional[str] = ""  # Model can be empty and will be determined based on user type
    
    @validator('messages')
    def messages_not_empty(cls, v):
        if not v or len(v) == 0:
            raise ValueError('messages cannot be empty')
        return v
    
    class Config:
        populate_by_name = True
        validate_assignment = True

class AnalysisResponseData(BaseModel):
    title: str
    shortText: str
    dreamDescription: str
    summary: dict = {
        "dreamEntry": "",
        "summarizedAnalysis": "",
        "thoughtReflection": "",
        "alignedAction": ""
    }
    tones: List[ToneItem]  # List of emotional tones with name, description, manifests, and triggers
    themes:  List[ToneItem]  # List of themes identified in the conversation
    visualSymbols: List[ToneItem]  # List of visual symbols identified in the conversation

class AnalysisResponse(StandardResponse):
    data: AnalysisResponseData

# Profile Summary Request/Response Models
class ProfileSummaryRequest(BaseModel):
    user_id: str
    user_type: UserType
    messages: List[MessageItem]  # List of profile Q&A messages
    model: Optional[str] = ""  # Model can be empty and will be determined based on user type
    
    @validator('messages')
    def messages_not_empty(cls, v):
        if not v or len(v) == 0:
            raise ValueError('messages cannot be empty')
        return v
    
    class Config:
        populate_by_name = True
        validate_assignment = True

class ProfileSummaryData(BaseModel):
    summary: str

class ProfileSummaryResponse(StandardResponse):
    data: ProfileSummaryData
