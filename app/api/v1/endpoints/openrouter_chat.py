from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field, validator
from typing import List, AsyncGenerator, Dict, Optional, Any
from enum import Enum
import requests
import jwt
import json
import asyncio
import aiohttp
import re

import os


SECRET_KEY = "DreamyBot@2025!xNc84Kz1pYw!uEeR#9sLb"
ALGORITHM = "HS256"


class UserType(str, Enum):
    GUEST = "guest"
    PAID = "paid"
    
class ChatMode(str, Enum):
    GENERAL = "general"
    DREAM = "dream"
    
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

class SummaryRequest(BaseModel):
    user_id: str
    user_type: UserType
    chat_messages: List[str]  # List of chat messages to summarize
    model: Optional[str] = ""  # Model can be empty and will be determined based on user type
    
    @validator('chat_messages')
    def chat_messages_not_empty(cls, v):
        if not v or len(v) == 0:
            raise ValueError('chat_messages cannot be empty')
        return v
    
    class Config:
        populate_by_name = True
        validate_assignment = True

class SummaryResponse(BaseModel):
    summary: str
    
class AnalysisRequest(BaseModel):
    user_id: str
    user_type: UserType
    chat_messages: List[str]  # List of chat messages to analyze
    model: Optional[str] = ""  # Model can be empty and will be determined based on user type
    
    @validator('chat_messages')
    def chat_messages_not_empty(cls, v):
        if not v or len(v) == 0:
            raise ValueError('chat_messages cannot be empty')
        return v
    
    class Config:
        populate_by_name = True
        validate_assignment = True

class AnalysisResponse(BaseModel):
    summary: str
    keywords: Dict[str, int]  # Dictionary of keywords and their counts
    emoji_count: int  # Total count of emojis
    emojis: Dict[str, int]  # Dictionary of emojis and their counts
    sentiment: str  # Overall sentiment of the conversation (positive, negative, neutral, or mixed)
    
class ChatResponse(BaseModel):
    response: str

router = APIRouter()

# Configuration for different user types and chat modes
MODEL_CONFIG = {
    UserType.GUEST: {
        ChatMode.GENERAL: {
            "model": "anthropic/claude-3-haiku",
            "system_prompt": "You are a helpful assistant for guest users. Provide concise and helpful responses."
        }
    },
    UserType.PAID: {
        ChatMode.GENERAL: {
            "model": "anthropic/claude-3-sonnet",
            "system_prompt": "You are a premium assistant for paid users. Provide detailed and comprehensive responses."
        },
        ChatMode.DREAM: {
            "model": "anthropic/claude-3-opus",
            "system_prompt": "You are a dream interpreter and creative assistant. Help users explore their dreams and creative ideas with deep insight and imagination."
        }
    }
}

def get_chat_config(user_type: UserType, chat_mode: ChatMode) -> Dict[str, str]:
    """Get the appropriate model and system prompt based on user type and chat mode."""
    # Check if the user type is valid
    if user_type not in MODEL_CONFIG:
        raise HTTPException(status_code=400, detail=f"Invalid user type: {user_type}")
    
    # Check if the chat mode is valid for this user type
    if chat_mode not in MODEL_CONFIG[user_type]:
        raise HTTPException(status_code=400, detail=f"Chat mode {chat_mode} not available for user type {user_type}")
    
    return MODEL_CONFIG[user_type][chat_mode]

@router.post("/generate", response_model=ChatResponse)
async def generate_chat_response(payload: ChatRequest):
    """
    Generate a chat response using the OpenRouter API.
    
    This endpoint supports conversation context through the last_messages parameter.
    Up to 8 previous messages can be included to provide context for the current response.
    Messages are processed in pairs (user message followed by assistant response).
    
    Args:
        payload: The chat request payload containing user information, message context, and prompt
    
    Returns:
        ChatResponse: The generated response from the AI model
    """
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    
    # Get the appropriate model and system prompt based on user type and chat mode
    chat_config = get_chat_config(payload.user_type, payload.chat_mode)
    
    # Use the model and system prompt from the request if provided, otherwise use the default
    model = payload.model if payload.model else chat_config["model"]
    system_prompt = payload.system_prompt if payload.system_prompt else chat_config["system_prompt"]

    # Prepare messages with context from previous messages
    messages = [
        {
            "content": system_prompt,
            "role": "system"  # Changed from 'assistant' to 'system' for proper role assignment
        }
    ]
    
    # Add previous messages as context (up to 8 messages)
    if payload.last_messages and len(payload.last_messages) > 0:
        # Determine how many previous messages to include (up to 8)
        num_messages = min(len(payload.last_messages), 8)
        
        # Add the previous messages to the context
        for i in range(num_messages):
            # Alternate between user and assistant roles
            role = "user" if i % 2 == 0 else "assistant"
            messages.append({
                "content": payload.last_messages[i],
                "role": role
            })
    
    # Add the current user prompt
    messages.append({
        "content": payload.user_prompt,
        "role": "user"
    })

    # Chat completion (POST /chat/completions)
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}"
        },
        json={
            "model": model,
            "messages": messages
        },
    )
    response.raise_for_status()
    response = response.json()
    reply = response["choices"][0]["message"]["content"]

    return {"response": reply}

@router.post("/stream")
async def generate_streaming_response(payload: ChatRequest):
    """
    Generate a streaming chat response using the OpenRouter API.
    
    This endpoint supports conversation context through the last_messages parameter.
    Up to 8 previous messages can be included to provide context for the current response.
    Messages are processed in pairs (user message followed by assistant response).
    
    The response is streamed back to the client as Server-Sent Events (SSE).
    
    Args:
        payload: The chat request payload containing user information, message context, and prompt
    
    Returns:
        StreamingResponse: A streaming response containing the generated text chunks
    """
    return StreamingResponse(
        stream_response_from_openrouter(payload),
        media_type="text/event-stream"
    )

async def stream_response_from_openrouter(payload: ChatRequest) -> AsyncGenerator[bytes, None]:
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    
    # Get the appropriate model and system prompt based on user type and chat mode
    try:
        chat_config = get_chat_config(payload.user_type, payload.chat_mode)
        
        # Use the model and system prompt from the request if provided, otherwise use the default
        model = payload.model if payload.model else chat_config["model"]
        system_prompt = payload.system_prompt if payload.system_prompt else chat_config["system_prompt"]
    except HTTPException as e:
        # Return the error as an SSE event
        yield f"data: {json.dumps({'error': e.detail})}\n\n".encode('utf-8')
        yield f"data: [DONE]\n\n".encode('utf-8')
        return
    
    # Create request data with message context
    messages = [
        {
            "content": system_prompt,
            "role": "system"  # Changed from 'assistant' to 'system' for proper role assignment
        }
    ]
    
    # Add previous messages as context (up to 8 messages)
    if payload.last_messages and len(payload.last_messages) > 0:
        # Determine how many previous messages to include (up to 8)
        num_messages = min(len(payload.last_messages), 8)
        
        # Add the previous messages to the context
        for i in range(num_messages):
            # Alternate between user and assistant roles
            role = "user" if i % 2 == 0 else "assistant"
            messages.append({
                "content": payload.last_messages[i],
                "role": role
            })
    
    # Add the current user prompt
    messages.append({
        "content": payload.user_prompt,
        "role": "user"
    })
    
    request_data = {
        "model": model,
        "messages": messages,
        "stream": True  # Enable streaming
    }
    
    # Set up headers
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "text/event-stream"
    }
    
    # Use aiohttp for async HTTP requests
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=request_data
        ) as response:
            # Check if the request was successful
            if response.status != 200:
                error_text = await response.text()
                error_msg = f"Error from OpenRouter API: {response.status} - {error_text}"
                yield f"data: {json.dumps({'error': error_msg})}\n\n".encode('utf-8')
                return
            
            # Process the streaming response
            async for line in response.content:
                line = line.decode('utf-8').strip()
                if not line:
                    continue
                    
                # OpenRouter sends "data: [DONE]" to indicate the end of the stream
                if line == "data: [DONE]":
                    break
                    
                # Lines start with "data: " - remove this prefix
                if line.startswith("data: "):
                    json_str = line[6:]  # Remove "data: " prefix
                    try:
                        data = json.loads(json_str)
                        if "choices" in data and len(data["choices"]) > 0:
                            delta = data["choices"][0].get("delta", {})
                            content = delta.get("content", "")
                            if content:
                                # Format as SSE event
                                yield f"data: {json.dumps({'response': content})}\n\n".encode('utf-8')
                                # Small delay to avoid overwhelming the client
                                await asyncio.sleep(0.01)
                    except json.JSONDecodeError as e:
                        print(f"Error parsing JSON: {e} - Line: {line}")
                        continue
    
    # Send a final event to indicate the end of the stream
    yield f"data: [DONE]\n\n".encode('utf-8')

@router.post("/summarize", response_model=SummaryResponse)
async def summarize_chat(payload: SummaryRequest):
    """Generate a 2-line summary of chat messages"""
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    
    # Determine the model based on user type
    model = payload.model if payload.model else "anthropic/claude-3-haiku"
    if payload.user_type == UserType.PAID and not payload.model:
        model = "anthropic/claude-3-sonnet"  # Use a better model for paid users
    
    # Prepare the chat messages as a single string
    chat_content = "\n".join(payload.chat_messages)
    
    # Create the system prompt for summarization
    system_prompt = "You are a summarization assistant. Your task is to provide a concise 2-line summary of conversations. Do not include phrases like 'Here is a summary' or 'Here is a concise 2-line summary'. Just provide the summary directly."
    
    # Chat completion request
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}"
        },
        json={
            "model": model,
            "messages": [
                {
                    "content": system_prompt,
                    "role": "system"
                },
                {
                    "content": f"Summarize the following conversation in exactly 2 lines. Be direct and concise. Do not include phrases like 'Here is a summary' or 'Here is a 2-line summary':\n\n{chat_content}",
                    "role": "user"
                }
            ],
            "max_tokens": 100,  # Limit the response length for a concise summary
            "temperature": 0.3  # Lower temperature for more focused summaries
        },
    )
    
    response.raise_for_status()
    response_data = response.json()
    summary = response_data["choices"][0]["message"]["content"]
    
    # Clean up the summary
    summary = summary.strip()
    
    # Remove common prefixes that models might add despite instructions
    prefixes_to_remove = [
        "Here is a 2-line summary:", 
        "Here is a concise 2-line summary:",
        "Here's a 2-line summary:",
        "Here's a concise 2-line summary:",
        "2-line summary:",
        "Summary:",
    ]
    
    for prefix in prefixes_to_remove:
        if summary.lower().startswith(prefix.lower()):
            summary = summary[len(prefix):].strip()
    
    # Ensure the summary is exactly 2 lines
    lines = summary.split("\n")
    if len(lines) > 2:
        summary = "\n".join(lines[:2])
    elif len(lines) == 1 and len(summary) > 50:
        # If it's a single long line, try to split it into two roughly equal parts at a sentence boundary
        mid_point = len(summary) // 2
        # Look for a period, question mark, or exclamation point near the middle
        for i in range(mid_point - 10, mid_point + 10):
            if i < len(summary) and summary[i] in ['.', '!', '?']:
                summary = summary[:i+1] + "\n" + summary[i+1:].strip()
                break
    
    return {"summary": summary}

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_chat(payload: AnalysisRequest):
    """Analyze chat messages to extract keywords, count them, and identify emojis"""
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    
    # Determine the model based on user type
    model = payload.model if payload.model else "anthropic/claude-3-haiku"
    if payload.user_type == UserType.PAID and not payload.model:
        model = "anthropic/claude-3-sonnet"  # Use a better model for paid users
    
    # Prepare the chat messages as a single string
    chat_content = "\n".join(payload.chat_messages)
    
    # Create the system prompt for analysis
    system_prompt = """You are a chat analysis assistant. Your task is to analyze conversations and extract:
1. A concise one-line summary
2. Key emotional and topical keywords (like 'fear', 'anxiety', 'happiness', etc.)
3. All emojis used in the conversation

Provide your analysis in valid JSON format with these fields:
- summary: a one-line summary of the conversation
- keywords: an object with keywords as keys and their counts as values
- emoji_count: total number of emojis found
- emojis: an object with emojis as keys and their counts as values

Ensure your response is ONLY the JSON object, nothing else."""
    
    # Chat completion request
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}"
        },
        json={
            "model": model,
            "messages": [
                {
                    "content": system_prompt,
                    "role": "system"
                },
                {
                    "content": f"Analyze the following conversation and extract a summary, keywords (especially emotional ones like fear, anxiety, etc.), and emojis. Also determine the overall sentiment (positive, negative, neutral, or mixed).\n\nReturn ONLY a JSON object with these fields:\n- summary: A one-line summary of the conversation\n- keywords: An object with emotional keywords as keys and their counts as values\n- emoji_count: Total number of emojis found\n- emojis: An object with emojis as keys and their counts as values\n- sentiment: Overall sentiment of the conversation (positive, negative, neutral, or mixed)\n\n{chat_content}",
                    "role": "user"
                }
            ],
            "temperature": 0.3  # Lower temperature for more focused analysis
        },
    )
    
    response.raise_for_status()
    response_data = response.json()
    analysis_text = response_data["choices"][0]["message"]["content"]
    
    # Extract the JSON from the response
    # Sometimes the model might wrap the JSON in markdown code blocks or add text before/after
    json_match = re.search(r'\{.*\}', analysis_text, re.DOTALL)
    if json_match:
        analysis_text = json_match.group(0)
    
    try:
        analysis = json.loads(analysis_text)
        
        # Ensure all required fields are present
        if 'summary' not in analysis:
            analysis['summary'] = "No summary available"
        if 'keywords' not in analysis:
            analysis['keywords'] = {}
        if 'emoji_count' not in analysis:
            # Count emojis in the original text as a fallback
            emoji_pattern = re.compile("[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F700-\U0001F77F\U0001F780-\U0001F7FF\U0001F800-\U0001F8FF\U0001F900-\U0001F9FF\U0001FA00-\U0001FA6F\U0001FA70-\U0001FAFF\U00002702-\U000027B0\U000024C2-\U0001F251]")
            emojis = emoji_pattern.findall(chat_content)
            analysis['emoji_count'] = len(emojis)
        if 'emojis' not in analysis:
            analysis['emojis'] = {}
            
        return {
            "summary": analysis['summary'],
            "keywords": analysis['keywords'],
            "emoji_count": analysis['emoji_count'],
            "emojis": analysis['emojis'],
            "sentiment": analysis.get('sentiment', 'neutral')  # Default to neutral if not provided
        }
    except json.JSONDecodeError:
        # If JSON parsing fails, create a basic analysis manually
        # Extract emojis
        emoji_pattern = re.compile("[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F700-\U0001F77F\U0001F780-\U0001F7FF\U0001F800-\U0001F8FF\U0001F900-\U0001F9FF\U0001FA00-\U0001FA6F\U0001FA70-\U0001FAFF\U00002702-\U000027B0\U000024C2-\U0001F251]")
        emojis = emoji_pattern.findall(chat_content)
        emoji_dict = {}
        for emoji in emojis:
            if emoji in emoji_dict:
                emoji_dict[emoji] += 1
            else:
                emoji_dict[emoji] = 1
        
        # Extract potential keywords (enhanced approach with emotional categories)
        emotional_keywords = {
            # Anxiety/Fear related
            "anxiety": ["anxiety", "anxious", "nervous", "worried", "uneasy", "tense", "apprehensive"],
            "fear": ["fear", "scared", "afraid", "terrified", "frightened", "panic", "dread"],
            "stress": ["stress", "stressful", "pressure", "strain", "overwhelmed", "burdened"],
            "worry": ["worry", "concerned", "troubled", "distressed"],
            
            # Happiness/Joy related
            "happiness": ["happy", "happiness", "joyful", "delighted", "pleased", "glad", "content"],
            "excitement": ["excited", "thrilled", "enthusiastic", "eager", "energetic"],
            "gratitude": ["grateful", "thankful", "appreciative", "blessed", "appreciated"],
            "love": ["love", "adore", "cherish", "affection", "fond", "loved"],
            
            # Sadness related
            "sadness": ["sad", "unhappy", "depressed", "gloomy", "miserable", "melancholy"],
            "disappointment": ["disappointed", "letdown", "disheartened", "dismayed"],
            "grief": ["grief", "mourning", "sorrow", "heartbroken", "devastated"],
            "loneliness": ["lonely", "alone", "isolated", "abandoned", "neglected"],
            
            # Anger related
            "anger": ["angry", "mad", "furious", "outraged", "irritated", "annoyed"],
            "frustration": ["frustrated", "exasperated", "aggravated", "impatient"],
            "resentment": ["resentful", "bitter", "indignant", "offended"],
            
            # Confidence/Doubt related
            "confidence": ["confident", "assured", "certain", "self-assured", "bold"],
            "doubt": ["doubt", "uncertain", "unsure", "hesitant", "skeptical", "confused"],
            
            # Fatigue/Energy related
            "fatigue": ["tired", "exhausted", "drained", "weary", "fatigued"],
            "energy": ["energetic", "lively", "vibrant", "invigorated", "refreshed"]
        }
        
        # Flatten the list for simple keyword matching
        common_emotional_keywords = []
        for category, words in emotional_keywords.items():
            common_emotional_keywords.extend(words)
        
        keyword_dict = {}
        for keyword in common_emotional_keywords:
            # Case insensitive count
            count = len(re.findall(r'\b' + re.escape(keyword) + r'\b', chat_content.lower()))
            if count > 0:
                keyword_dict[keyword] = count
        
        # Generate a simple summary using the summarize endpoint
        summary_request = SummaryRequest(
            user_id=payload.user_id,
            user_type=payload.user_type,
            chat_messages=payload.chat_messages
        )
        summary_response = await summarize_chat(summary_request)
        
        # Determine sentiment based on keyword counts
        sentiment = "neutral"
        positive_categories = ["happiness", "excitement", "gratitude", "love", "confidence", "energy"]
        negative_categories = ["anxiety", "fear", "stress", "worry", "sadness", "disappointment", "grief", "loneliness", "anger", "frustration", "resentment", "doubt", "fatigue"]
        
        # Count occurrences of words in each category
        positive_count = 0
        negative_count = 0
        for category in positive_categories:
            for word in emotional_keywords.get(category, []):
                positive_count += len(re.findall(r'\b' + re.escape(word) + r'\b', chat_content.lower()))
        
        for category in negative_categories:
            for word in emotional_keywords.get(category, []):
                negative_count += len(re.findall(r'\b' + re.escape(word) + r'\b', chat_content.lower()))
        
        # Determine overall sentiment
        if positive_count > 0 and negative_count > 0:
            if positive_count > negative_count * 2:
                sentiment = "positive"
            elif negative_count > positive_count * 2:
                sentiment = "negative"
            else:
                sentiment = "mixed"
        elif positive_count > 0:
            sentiment = "positive"
        elif negative_count > 0:
            sentiment = "negative"
        
        return {
            "summary": summary_response.summary,
            "keywords": keyword_dict,
            "emoji_count": len(emojis),
            "emojis": emoji_dict,
            "sentiment": sentiment
        }

