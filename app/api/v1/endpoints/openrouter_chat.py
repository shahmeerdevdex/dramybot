from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from app.schemas.chat import (
    ChatRequest, ChatResponse,
    SummaryRequest, SummaryResponse,
    AnalysisRequest, AnalysisResponse,
    ProfileSummaryRequest, ProfileSummaryResponse
)
from app.services.chat_service import (
    generate_chat,
    generate_summary,
    analyze_chat,
    generate_profile_summary
)
from app.utils.openrouter import make_streaming_request
from app.core.config import get_chat_config
from app.core.prompts import DREAM_DICTIONARY_PROMPT
import json
import traceback


# Create API router
router = APIRouter()


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
    return await generate_chat(payload)


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


async def stream_response_from_openrouter(payload: ChatRequest):
    try:
        messages = []
        chat_config = get_chat_config(payload.user_type, payload.chat_mode)
        model = payload.model if payload.model else chat_config["model"]
        print(f"Model selected for streaming chat: {model}")
        # Always build the prompt with all user info and call the model
        if hasattr(payload, 'feature') and payload.feature == 'dream_dictionary':
            system_prompt = DREAM_DICTIONARY_PROMPT
            messages = [
                {"content": system_prompt, "role": "assistant"},
                {"content": payload.user_prompt, "role": "user"}
            ]
        elif hasattr(payload, 'feature') and payload.feature in ('dream_chat', 'general_chat', 'dream_free_user'):
            # Build a system prompt with all user info
            system_prompt = f''' 
                {payload.name}, is  of  {payload.age} years old, {payload.gender}. 
                Birthday: {payload.birthdate}. 
                User Onboarding Summary: {payload.onboarding_summary} 
                - User Memory Bank: {payload.memory_bank} 
                - User Dream Log: {payload.dream_log}.\n
                {chat_config["system_prompt"]}
            
            '''

            messages = [
                {"content": system_prompt, "role": "assistant"}
            ]
            if payload.last_messages and len(payload.last_messages) > 0:
                num_messages = min(len(payload.last_messages), 8)
                for i in range(num_messages):
                    role = "user" if i % 2 == 0 else "assistant"
                    messages.append({"content": payload.last_messages[i], "role": role})
            messages.append({"content": payload.user_prompt, "role": "user"})
        else:
            system_prompt = payload.system_prompt if payload.system_prompt else chat_config["system_prompt"]
            messages = [
                {"content": system_prompt, "role": "system"}
            ]
            if payload.last_messages and len(payload.last_messages) > 0:
                num_messages = min(len(payload.last_messages), 8)
                for i in range(num_messages):
                    role = "user" if i % 2 == 0 else "assistant"
                    messages.append({"content": payload.last_messages[i], "role": role})
            messages.append({"content": payload.user_prompt, "role": "user"})
        async for chunk in make_streaming_request(model, messages, chat_config["temperature"]):
            print("in call yield")
            yield chunk
    except Exception as e:
        print("Issue with Stream : ", traceback.print_exc())
        yield f"data: {{\"statusCode\": 500, \"message\": \"{str(e)}\", \"data\": null}}\n\n".encode('utf-8')
        yield b"data: [DONE]\n\n"

def chunk_string(s, chunk_size):
    for i in range(0, len(s), chunk_size):
        yield s[i:i+chunk_size]


@router.post("/summarize", response_model=SummaryResponse)
async def summarize_chat(payload: SummaryRequest):
    """
    Generate a 2-line summary of chat messages.
    
    Args:
        payload: The summary request payload containing user information and chat messages
        
    Returns:
        SummaryResponse: A summary of the chat messages
    """
    return await generate_summary(payload)


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_chat_endpoint(payload: AnalysisRequest):
    """
    Analyze chat messages to extract emotional tones, themes, and visual symbols.
    
    Args:
        payload: The analysis request payload containing user information and chat messages
        
    Returns:
        AnalysisResponse: An analysis of the chat messages
    """
    return await analyze_chat(payload)


@router.post("/profile-summary", response_model=ProfileSummaryResponse)
async def profile_summary_endpoint(payload: ProfileSummaryRequest):
    """
    Generate a summary of a dreamer's profile based on Q&A messages.
    
    This endpoint takes a series of questions and answers about a dreamer's profile
    and generates a concise summary of the profile.
    
    Args:
        payload: The profile summary request payload containing user information and profile messages
    
    Returns:
        ProfileSummaryResponse: A summary of the dreamer's profile
    """
    return await generate_profile_summary(payload)
