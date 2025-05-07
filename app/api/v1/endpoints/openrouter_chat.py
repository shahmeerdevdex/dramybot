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
    tones: Dict[str, str]  # Dictionary of emotional tones and their descriptions
    themes: List[str]  # List of themes identified in the conversation
    visualSymbols: List[str]  # List of visual symbols identified in the conversation
    
class ChatResponse(BaseModel):
    response: str

class ProfileMessage(BaseModel):
    query: str
    response: str
    isUser: bool

class ProfileSummaryRequest(BaseModel):
    user_id: str
    user_type: UserType
    messages: List[ProfileMessage]  # List of profile Q&A messages
    model: Optional[str] = ""  # Model can be empty and will be determined based on user type
    
    @validator('messages')
    def messages_not_empty(cls, v):
        if not v or len(v) == 0:
            raise ValueError('messages cannot be empty')
        return v
    
    class Config:
        populate_by_name = True
        validate_assignment = True

class ProfileSummaryResponse(BaseModel):
    summary: str

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
    """Analyze chat messages to extract emotional tones, themes, and visual symbols"""
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    
    # Determine the model based on user type
    model = payload.model if payload.model else "anthropic/claude-3-haiku"
    if payload.user_type == UserType.PAID and not payload.model:
        model = "anthropic/claude-3-sonnet"  # Use a better model for paid users
    
    # Prepare the chat messages as a single string
    chat_content = "\n".join(payload.chat_messages)
    
    # Create the system prompt for analysis
    system_prompt = """You are a chat analysis assistant specializing in emotional and thematic analysis. 

Your task is to analyze conversations and extract:
1. A concise summary of the conversation
2. Emotional tones present in the conversation with detailed descriptions
3. Underlying themes in the conversation
4. Visual symbols that represent the conversation

Provide your analysis in valid JSON format with these fields:
- summary: A concise summary of the conversation
- tones: An object with emotional tones as keys and detailed paragraph descriptions as values
- themes: An array of underlying themes identified in the conversation
- visualSymbols: An array of visual symbols that represent the conversation

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
                    "content": f"Analyze the following conversation and extract:\n\n1. A concise summary\n2. Emotional tones present (like fear, anxiety, happiness, etc.) with detailed paragraph descriptions for each tone\n3. Underlying themes in the conversation (like 'lack of security', 'anticipation of danger', etc.)\n4. Visual symbols that represent the conversation (like 'rain', 'home', etc.)\n\nReturn ONLY a JSON object with these fields:\n- summary: A concise summary of the conversation\n- tones: An object with emotional tones as keys and detailed paragraph descriptions as values\n- themes: An array of underlying themes identified in the conversation\n- visualSymbols: An array of visual symbols that represent the conversation\n\n{chat_content}",
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
        if 'tones' not in analysis:
            analysis['tones'] = {
                "neutral": "The conversation has a generally neutral tone without strong emotional elements."
            }
        if 'themes' not in analysis:
            analysis['themes'] = ["general conversation"]
        if 'visualSymbols' not in analysis:
            analysis['visualSymbols'] = ["speech bubble"]
            
        return {
            "summary": analysis['summary'],
            "tones": analysis['tones'],
            "themes": analysis['themes'],
            "visualSymbols": analysis['visualSymbols']
        }
    except json.JSONDecodeError:
        # If JSON parsing fails, create a basic analysis manually
        return {
            "summary": "A conversation between two or more people.",
            "tones": {
                "neutral": "The conversation has a generally neutral tone without strong emotional elements.",
                "informative": "The conversation appears to be primarily focused on sharing information rather than expressing strong emotions."
            },
            "themes": ["general conversation", "information exchange"],
            "visualSymbols": ["speech bubble", "conversation"]
        }
        
        # This is the end of the analyze_chat function

@router.post("/profile-summary", response_model=ProfileSummaryResponse)
async def profile_summary(payload: ProfileSummaryRequest):
    """
    Generate a summary of a dreamer's profile based on Q&A messages.
    
    This endpoint takes a series of questions and answers about a dreamer's profile
    and generates a concise summary of the profile.
    
    Args:
        payload: The profile summary request payload containing user information and profile messages
    
    Returns:
        ProfileSummaryResponse: A summary of the dreamer's profile
    """
    # Get the OpenRouter API key from environment variables
    OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
    if not OPENROUTER_API_KEY:
        raise HTTPException(status_code=500, detail="OpenRouter API key not configured")
    
    # Determine the model to use based on user type
    if payload.model and payload.model.strip() != "":
        model = payload.model
    elif payload.user_type == UserType.PAID:
        model = "anthropic/claude-3-sonnet"
    else:
        model = "anthropic/claude-3-haiku"
    
    # Format the messages for the prompt
    formatted_messages = []
    for msg in payload.messages:
        if msg.isUser:
            formatted_messages.append(f"User: {msg.response}")
        else:
            formatted_messages.append(f"Question: {msg.query}")
    
    profile_content = "\n".join(formatted_messages)
    
    # Create the system prompt for profile summary
    system_prompt = """You are a profile summarization assistant. 
    
Your task is to analyze a series of questions and answers about a person's profile and generate a concise, insightful summary that captures the essence of who they are.

Provide your summary in valid JSON format with this field:
- summary: A concise summary of the person's profile based on the Q&A

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
                    "content": f"Based on the following questions and answers about a person's profile, generate a concise summary that captures the essence of who they are. Return ONLY a JSON object with a 'summary' field.\n\n{profile_content}",
                    "role": "user"
                }
            ],
            "temperature": 0.3  # Lower temperature for more focused summary
        },
    )
    
    response.raise_for_status()
    response_data = response.json()
    summary_text = response_data["choices"][0]["message"]["content"]
    
    # Extract the JSON from the response
    # Sometimes the model might wrap the JSON in markdown code blocks or add text before/after
    json_match = re.search(r'\{.*\}', summary_text, re.DOTALL)
    if json_match:
        summary_text = json_match.group(0)
    
    try:
        summary_data = json.loads(summary_text)
        
        # Ensure the summary field is present
        if 'summary' not in summary_data:
            summary_data['summary'] = "No summary available for this profile."
            
        return {"summary": summary_data['summary']}
    except json.JSONDecodeError:
        # If JSON parsing fails, create a basic summary
        return {"summary": "A profile of an individual based on questions and answers."}

