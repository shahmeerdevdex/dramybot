import os
from app.schemas.common import UserType, ChatMode
from app.core.prompts import chat_prompt
from dotenv import load_dotenv
# API Security
SECRET_KEY = "DreamyBot@2025!xNc84Kz1pYw!uEeR#9sLb"
ALGORITHM = "HS256"
load_dotenv()

# OpenRouter API Configuration
def get_openrouter_api_key():
    """Get the OpenRouter API key from environment variables"""
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OpenRouter API key not configured")
    return api_key

# Model Configuration for different user types and chat modes
MODEL_CONFIG = {
    UserType.GUEST: {
        ChatMode.GENERAL: {
            "model": "openai/gpt-4o-mini",
            "system_prompt": chat_prompt
        },
        ChatMode.DREAM: {
            "model": "anthropic/claude-3-sonnet",
            "system_prompt": "You are a dream interpreter named DreamyBot and creative assistant. Help users explore their dreams with insight and imagination..dont include greetings unless user prompt  is  hey,hi,hello, etc \n STRICLTY FOLLOW THE BELOW RULES: \n 1) Response should be returned in the MarkDown format and it should be very beautiful and should be easy to read \n2) Include heading some colors and styles"
        }
    },
    UserType.PAID: {
        ChatMode.GENERAL: {
            "model": "openai/gpt-4o-mini",
            "system_prompt": chat_prompt
        },
        ChatMode.DREAM: {
            "model": "anthropic/claude-3-opus",
            "system_prompt": "You are a dream interpreter named DreamyBot and creative assistant. Help users explore their dreams and creative ideas with deep insight and imagination..dont include greetings unless user prompt  is  hey,hi,hello, etc  \n STRICLTY FOLLOW THE BELOW RULES: \n 1) Response should be returned in the MarkDown format and it should be very beautiful and should be easy to read \n2) Include heading some colors and styles"
        }
    }
}

def get_chat_config(user_type: UserType, chat_mode: ChatMode):
    """Get the appropriate model and system prompt based on user type and chat mode."""
    # Check if the user type is valid
    if user_type not in MODEL_CONFIG:
        raise ValueError(f"Invalid user type: {user_type}")
    
    # Check if the chat mode is valid for this user type
    if chat_mode not in MODEL_CONFIG[user_type]:
        raise ValueError(f"Chat mode {chat_mode} not available for user type {user_type}")
    
    return MODEL_CONFIG[user_type][chat_mode]