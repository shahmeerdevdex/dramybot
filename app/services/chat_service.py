from typing import Dict, List, Any, Optional
from app.schemas.chat import (
    ChatRequest, ChatResponse, ChatResponseData,
    SummaryRequest, SummaryResponse, SummaryResponseData,
    AnalysisRequest, AnalysisResponse, AnalysisResponseData, ToneItem,
    ProfileSummaryRequest, ProfileSummaryResponse, ProfileSummaryData
)
from app.schemas.common import UserType, ChatMode
from app.core.config import get_chat_config
from app.utils.openrouter import make_openrouter_request, extract_json_from_text


async def generate_chat(payload: ChatRequest) -> ChatResponse:
    """Generate a chat response using the OpenRouter API"""
    try:
        # Get the appropriate model and system prompt based on user type and chat mode
        chat_config = get_chat_config(payload.user_type, payload.chat_mode)
        
        # Use the model and system prompt from the request if provided, otherwise use the default
        model = payload.model if payload.model else chat_config["model"]
        system_prompt = payload.system_prompt if payload.system_prompt else chat_config["system_prompt"]

        # Prepare messages with context from previous messages
        messages = [
            {
                "content": system_prompt,
                "role": "system"
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

        # Make the API request
        response_data = make_openrouter_request(
            model=model,
            messages=messages,
            temperature=payload.temperature
        )
        
        # Extract the response text
        reply = response_data["choices"][0]["message"]["content"]
        
        return ChatResponse(
            statusCode=200,
            message="fetch sucessfully",
            data=ChatResponseData(response=reply)
        )
        
    except Exception as e:
        return ChatResponse(
            statusCode=500,
            message=str(e),
            data=None
        )


async def generate_summary(payload: SummaryRequest) -> SummaryResponse:
    """Generate a 2-line summary of chat messages"""
    try:
        # Determine the model based on user type
        model = payload.model if payload.model else "anthropic/claude-3-haiku"
        if payload.user_type == UserType.PAID and not payload.model:
            model = "anthropic/claude-3-sonnet"  # Use a better model for paid users
        
        # Format the messages for the prompt
        formatted_messages = []
        for msg in payload.messages:
            if msg.isUser:
                formatted_messages.append(f"User: {msg.response}")
            else:
                formatted_messages.append(f"Question: {msg.query}")
        
        chat_content = "\n".join(formatted_messages)
        
        # Create the system prompt for summarization
        system_prompt = "You are a summarization assistant. Your task is to provide a concise 2-line summary of conversations. Do not include phrases like 'Here is a summary' or 'Here is a concise 2-line summary'. Just provide the summary directly."
        
        # Prepare the messages for the API request
        messages = [
            {
                "content": system_prompt,
                "role": "system"
            },
            {
                "content": f"Summarize the following conversation in exactly 2 lines. Be direct and concise. Do not include phrases like 'Here is a summary' or 'Here is a 2-line summary':\n\n{chat_content}",
                "role": "user"
            }
        ]
        
        # Make the API request
        response_data = make_openrouter_request(
            model=model,
            messages=messages,
            temperature=0.3  # Lower temperature for more focused summaries
        )
        
        # Extract the summary text
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
        
        return SummaryResponse(
            statusCode=200,
            message="fetch sucessfully",
            data=SummaryResponseData(summary=summary)
        )
        
    except Exception as e:
        return SummaryResponse(
            statusCode=500,
            message=str(e),
            data=None
        )


async def analyze_chat(payload: AnalysisRequest) -> AnalysisResponse:
    """Analyze chat messages to extract emotional tones, themes, and visual symbols"""
    try:
        # Determine the model based on user type
        model = payload.model if payload.model else "anthropic/claude-3-haiku"
        if payload.user_type == UserType.PAID and not payload.model:
            model = "anthropic/claude-3-sonnet"  # Use a better model for paid users
        
        # Format the messages for the prompt
        formatted_messages = []
        for msg in payload.messages:
            if msg.isUser:
                formatted_messages.append(f"User: {msg.response}")
            else:
                formatted_messages.append(f"Question: {msg.query}")
        
        chat_content = "\n".join(formatted_messages)
        
        # Create the system prompt for analysis
        system_prompt = """You are a chat analysis assistant specializing in emotional and thematic analysis. 

Your task is to analyze conversations and extract:
1. A concise summary of the conversation
2. Emotional tones present in the conversation with detailed descriptions
3. Underlying themes in the conversation
4. Visual symbols that represent the conversation

Provide your analysis in valid JSON format with these fields:
- summary: A concise summary of the conversation
- tones: An array of objects, each with 'name' and 'description' fields, where 'name' is the emotional tone and 'description' is a detailed paragraph about that tone
- themes: An array of underlying themes identified in the conversation
- visualSymbols: An array of visual symbols that represent the conversation

Ensure your response is ONLY the JSON object, nothing else."""
        
        # Prepare the messages for the API request
        messages = [
            {
                "content": system_prompt,
                "role": "system"
            },
            {
                "content": f"Analyze the following conversation and extract:\n\n1. A concise summary\n2. Emotional tones present (like fear, anxiety, happiness, etc.) with detailed paragraph descriptions for each tone\n3. Underlying themes in the conversation (like 'lack of security', 'anticipation of danger', etc.)\n4. Visual symbols that represent the conversation (like 'rain', 'home', etc.)\n\nReturn ONLY a JSON object with these fields:\n- summary: A concise summary of the conversation\n- tones: An array of objects, each with 'name' and 'description' fields, where 'name' is the emotional tone and 'description' is a detailed paragraph about that tone\n- themes: An array of underlying themes identified in the conversation\n- visualSymbols: An array of visual symbols that represent the conversation\n\n{chat_content}",
                "role": "user"
            }
        ]
        
        # Make the API request
        response_data = make_openrouter_request(
            model=model,
            messages=messages,
            temperature=0.3  # Lower temperature for more focused analysis
        )
        
        # Extract the analysis text
        analysis_text = response_data["choices"][0]["message"]["content"]
        
        # Extract the JSON from the response
        analysis = extract_json_from_text(analysis_text)
        
        # Ensure all required fields are present
        if 'summary' not in analysis:
            analysis['summary'] = "No summary available"
            
        # Convert tones from dictionary to list of ToneItem objects
        tone_items = []
        if 'tones' in analysis:
            if isinstance(analysis['tones'], dict):
                # Convert from dict format to list of ToneItem objects
                for tone_name, tone_description in analysis['tones'].items():
                    tone_items.append(ToneItem(name=tone_name, description=tone_description))
            elif isinstance(analysis['tones'], list):
                # If the model already returned a list format, ensure it has name and description fields
                for tone in analysis['tones']:
                    if isinstance(tone, dict) and 'name' in tone and 'description' in tone:
                        tone_items.append(ToneItem(**tone))
        
        # If no tones were found or conversion failed, add a default tone
        if not tone_items:
            tone_items = [
                ToneItem(
                    name="neutral", 
                    description="The conversation has a generally neutral tone without strong emotional elements."
                )
            ]
            
        if 'themes' not in analysis:
            analysis['themes'] = ["general conversation"]
        if 'visualSymbols' not in analysis:
            analysis['visualSymbols'] = ["speech bubble"]
            
        return AnalysisResponse(
            statusCode=200,
            message="fetch sucessfully",
            data=AnalysisResponseData(
                summary=analysis['summary'],
                tones=tone_items,
                themes=analysis['themes'],
                visualSymbols=analysis['visualSymbols']
            )
        )
        
    except Exception as e:
        return AnalysisResponse(
            statusCode=500,
            message=str(e),
            data=AnalysisResponseData(
                summary="A conversation between two or more people.",
                tones=[
                    ToneItem(
                        name="neutral", 
                        description="The conversation has a generally neutral tone without strong emotional elements."
                    ),
                    ToneItem(
                        name="informative", 
                        description="The conversation appears to be primarily focused on sharing information rather than expressing strong emotions."
                    )
                ],
                themes=["general conversation", "information exchange"],
                visualSymbols=["speech bubble", "conversation"]
            )
        )


async def generate_profile_summary(payload: ProfileSummaryRequest) -> ProfileSummaryResponse:
    """Generate a summary of a dreamer's profile based on Q&A messages"""
    try:
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
        
        # Prepare the messages for the API request
        messages = [
            {
                "content": system_prompt,
                "role": "system"
            },
            {
                "content": f"Based on the following questions and answers about a person's profile, generate a concise summary that captures the essence of who they are. Return ONLY a JSON object with a 'summary' field.\n\n{profile_content}",
                "role": "user"
            }
        ]
        
        # Make the API request
        response_data = make_openrouter_request(
            model=model,
            messages=messages,
            temperature=0.3  # Lower temperature for more focused summary
        )
        
        # Extract the summary text
        summary_text = response_data["choices"][0]["message"]["content"]
        
        # Extract the JSON from the response
        summary_data = extract_json_from_text(summary_text)
        
        # Ensure the summary field is present
        if 'summary' not in summary_data:
            summary_data['summary'] = "No summary available for this profile."
            
        return ProfileSummaryResponse(
            statusCode=200,
            message="fetch sucessfully",
            data=ProfileSummaryData(summary=summary_data['summary'])
        )
        
    except Exception as e:
        return ProfileSummaryResponse(
            statusCode=500,
            message=str(e),
            data=ProfileSummaryData(summary="A profile of an individual based on questions and answers.")
        )
