from enum import Enum
from pydantic import BaseModel
from typing import List, Dict, Optional

class UserType(str, Enum):
    """User type enumeration"""
    GUEST = "guest"
    PAID = "paid"
    FREE = "free"
    
class ChatMode(str, Enum):
    """Chat mode enumeration"""
    GENERAL = "general"
    DREAM = "dream"

class MessageItem(BaseModel):
    """Common message format for all chat interactions"""
    query: str
    response: str
    isUser: bool
