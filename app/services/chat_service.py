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
from app.core.prompts import combined_prompt,summary_prompt,dream_summary_prompt, DREAM_DICTIONARY_PROMPT, DREAM_FREE_USER


async def generate_chat(payload: ChatRequest) -> ChatResponse:
    """Generate a chat response using the OpenRouter API"""
    try:
        chat_config = get_chat_config(payload.user_type, payload.chat_mode)
        model = payload.model if payload.model else chat_config["model"]
        print(f"Model selected for chat: {model}")
        # Always build the prompt with all user info and call the model
        if hasattr(payload, 'feature') and payload.feature == 'dream_dictionary':
            system_prompt = DREAM_DICTIONARY_PROMPT
            messages = [
                {"content": system_prompt, "role": "system"},
                {"content": payload.user_prompt, "role": "user"}
            ]
        elif hasattr(payload, 'feature') and payload.feature in ('dream_chat', 'general_chat'):
            # Build a system prompt with all user info
            system_prompt = (
                f"{payload.name}, you are {payload.age} years old, {payload.gender}. "
                f"Birthday: {payload.birthdate}. "
                f"User Onboarding Summary: {payload.onboarding_summary} "
                f"- User Memory Bank: {payload.memory_bank} "
                f"- User Dream Log: {payload.dream_log}.\n"
                f"Dream: {payload.user_prompt}\n"
                "Interpret this dream in a way that references the user's age, name, and background."
            )
            messages = [
                {"content": system_prompt, "role": "system"}
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
        response_data = await make_openrouter_request(
            model=model,
            messages=messages,
            temperature=payload.temperature
        )
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
            data=ChatResponseData(response="An error occurred: {}".format(str(e)))
        )


async def generate_summary(payload: SummaryRequest) -> SummaryResponse:
    """Generate a 2-line summary of chat messages"""
    try:
        # Determine the model based on user type
        model = payload.model if payload.model else "google/gemma-3-27b-it"
        if payload.user_type == UserType.PAID and not payload.model:
            model = "google/gemma-3-27b-it"  # Use a better model for paid users
        
        # Format the messages for the prompt
        formatted_messages = []
        for msg in payload.messages:
            if msg.isUser:
                formatted_messages.append(f"User: {msg.response}")
            else:
                formatted_messages.append(f"Question: {msg.query}")
        
        chat_content = "\n".join(formatted_messages)
        
        # Create the system prompt for summarization
        #system_prompt = "You are a summarization assistant. Your task is to provide a concise 2-line summary of conversations. Do not include phrases like 'Here is a summary' or 'Here is a concise 2-line summary'. Just provide the summary directly."
        system_prompt = summary_prompt
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
        response_data = await make_openrouter_request(
            model=model,
            messages=messages,
            temperature=0.5  # Lower temperature for more focused summaries
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


async def analyze_chat(payload: AnalysisRequest):
    """Analyze chat messages to extract emotional tones, themes, and visual symbols"""
    try:
        # Determine the model based on user type
        model = payload.model if payload.model else "google/gemma-3-27b-it"
        if payload.user_type == UserType.PAID and not payload.model:
            model = "google/gemma-3-27b-it"  # Use a better model for paid users
        
        # Format the messages for the prompt
        formatted_messages = ""
        for msg in payload.messages:
            if msg.query:
                formatted_messages=formatted_messages+ f"User: {msg.query} \n"
            if msg.response:
                formatted_messages=formatted_messages + f"response: {msg.response} \n"
        
        user_prompt = formatted_messages
        

        messages = [
            {
                "content": combined_prompt+formatted_messages,
                "role": "system"
            },
            {
                "content": user_prompt,
                "role": "user"
            }
        ]
        
        # Make the API request
        response_data = await make_openrouter_request(
            model="google/gemma-3-27b-it",
            messages=messages,
            temperature=0.5  # Lower temperature for more focused analysis
        )
        
        # Extract the analysis text
        analysis_text = response_data["choices"][0]["message"]["content"]
        
        # Extract the JSON from the response
        analysis = extract_json_from_text(analysis_text)

        print("analysis ", analysis)

        if not analysis:
            print("analysis is empty")
            return {
                "statusCode": 400,
                "message": "Need more context of dream to interpret",
                "data": {
                    "title":'NA',
                      "dreamDescription": "NA",
                    "shortText":'NA',
                     "summary" : {
                        "dreamEntry": "NA",
                        "summarizedAnalysis": "NA",
                        "thoughtReflection": "NA",
                        "alignedAction": "NA"
                    },
                    "tones": [
                        ToneItem(
                            name="NA",
                            description="NA",
                            manifests="NA",
                            triggers="NA"
                        ),
                        ToneItem(
                            name="NA",
                            description="NA",
                            manifests="NA",
                            triggers="NA"
                        )
                    ],
                    "themes": [ ToneItem(
                            name="NA",
                            description="NA",
                            manifests="NA",
                            triggers="NA"
                        )],
                    "visualSymbols": [ ToneItem(
                            name="NA",
                            description="NA",
                            manifests="NA",
                            triggers="NA"
                        )]
                }
            }

        
        # Ensure all required fields are present
        if 'title' not in analysis:
            analysis['title'] = "Dream Analysis"
        if 'shortText' not in analysis:
            analysis['shortText'] = "A dream narrative with symbolic elements."
        
        if 'dreamDescription' not in analysis:
            analysis['dreamDescription'] = "NA"
            
        # Ensure summary object has all required fields
        if 'summary' not in analysis or not isinstance(analysis['summary'], dict):
            analysis['summary'] = {
                "dreamEntry": "A dream narrative that explores the subconscious mind.",
                "summarizedAnalysis": "The dream appears to represent inner thoughts and emotions.",
                "thoughtReflection": "This dream may be revealing underlying concerns or desires.",
                "alignedAction": "Consider reflecting on the symbols and emotions present in this dream."
            }
        else:
            # Ensure all summary fields exist
            required_summary_fields = ["dreamEntry", "summarizedAnalysis", "thoughtReflection", "alignedAction"]
            for field in required_summary_fields:
                if field not in analysis['summary']:
                    analysis['summary'][field] = f"No {field} available."
            
        # Convert tones to list of ToneItem objects
        tone_items = []
        if 'tones' in analysis and isinstance(analysis['tones'], list):
            for tone in analysis['tones']:
                if isinstance(tone, dict):
                    # Ensure all required fields exist
                    if 'name' not in tone:
                        tone['name'] = "unnamed tone"
                    if 'description' not in tone:
                        tone['description'] = "No description available."
                    if 'manifests' not in tone:
                        tone['manifests'] = "This tone may manifest in various aspects of daily life."
                    if 'triggers' not in tone:
                        tone['triggers'] = "This tone may be triggered by various life circumstances."
                    
                    tone_items.append(ToneItem(**tone))
        
        # If no tones were found or conversion failed, add default tones
        if not tone_items:
            tone_items = [
                ToneItem(
                    name="fear", 
                    description="The dream exhibits elements of fear and anxiety.",
                    manifests="This fear may manifest as hesitation in taking risks in daily life.",
                    triggers="This fear may be triggered by situations of uncertainty or change."
                ),
                ToneItem(
                    name="uncertainty",
                    description="The dream shows signs of uncertainty and doubt.",
                    manifests="This uncertainty may manifest as indecision in important life choices.",
                    triggers="This uncertainty may be triggered by lack of clear direction or guidance."
                ),
                ToneItem(
                    name="introspection",
                    description="The dream has elements of self-reflection and introspection.",
                    manifests="This introspection may manifest as a desire to understand oneself better.",
                    triggers="This introspection may be triggered by moments of solitude or quiet contemplation."
                )
            ]
            
        if 'themes' not in analysis or not analysis['themes']:
            analysis['themes'] = ["Self-discovery", "Inner conflict", "Transformation"]
        if 'visualSymbols' not in analysis or not analysis['visualSymbols']:
            analysis['visualSymbols'] = ["Door", "Path", "Light"]
        
        response =  AnalysisResponse(
            statusCode=200,
            message="fetch sucessfully",
            data=AnalysisResponseData(
                title=analysis['title'],
                shortText=analysis['shortText'],
                dreamDescription=analysis['dreamDescription'],
                summary=analysis['summary'],
                tones=tone_items,
                themes=analysis['themes'],
                visualSymbols=analysis['visualSymbols']
            )
        )

        print("response ", response )
            
        return AnalysisResponse(
            statusCode=200,
            message="fetch sucessfully",
            data=AnalysisResponseData(
                title=analysis['title'],
                shortText=analysis['shortText'],
                dreamDescription=analysis['dreamDescription'],
                summary=analysis['summary'],
                tones=tone_items,
                themes=analysis['themes'],
                visualSymbols=analysis['visualSymbols']
            )
        )
        
    except Exception as e:
        print("Exception ", e)
        return {
            "statusCode": 400,
            "message": f"{e}",
            "data": {
                "title": 'NA',
                "shortText": 'NA',
                "dreamDescription": "NA",
                "summary": {
                    "dreamEntry": "NA",
                    "summarizedAnalysis": "NA",
                    "thoughtReflection": "NA",
                    "alignedAction": "NA"
                },
                "tones": [
                    ToneItem(
                        name="NA",
                        description="NA",
                        manifests="NA",
                        triggers="NA"
                    ),
                    ToneItem(
                        name="NA",
                        description="NA",
                        manifests="NA",
                        triggers="NA"
                    )
                ],
                "themes": [ToneItem(
                    name="NA",
                    description="NA",
                    manifests="NA",
                    triggers="NA"
                )],
                "visualSymbols": [ToneItem(
                    name="NA",
                    description="NA",
                    manifests="NA",
                    triggers="NA"
                )]
            }
        }


async def generate_profile_summary(payload: ProfileSummaryRequest) -> ProfileSummaryResponse:
    """Generate a summary of a dreamer's profile based on Q&A messages"""
    try:
        # Determine the model to use based on user type

        model = "openai/chatgpt-4o-latest"
        
        # Format the messages for the prompt
        formatted_messages = []
        for msg in payload.messages:
            if msg.isUser:
                formatted_messages.append(f"User: {msg.response}")
            else:
                formatted_messages.append(f"Question: {msg.query}")
        
        profile_content = "\n".join(formatted_messages)
        
        # Create the system prompt for profile summary
        system_prompt ="""You are a profile summarization assistant.
        Your task is to analyze a series of questions and answers about a person's profile and generate a concise, insightful summary that captures the essence of who they are.
        Provide your summary in valid JSON format with this field:
        - summary: A concise summary of the person's profile based on the Q&A
        Ensure your response is ONLY the JSON object, nothing else."""
        
        # Prepare the messages for the API request
        messages = [
            {
                "content": system_prompt,
                "role": "assistant"
            },
            {
                "content": f" Return ONLY a JSON object with a 'summary' field.\n\n{profile_content}",
                "role": "user"
            }
        ]
        
        # Make the API request
        response_data = await make_openrouter_request(
            model=model,
            messages=messages,
            temperature=0.48
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
DREAM_FREE_USER = """
Hi {name}! At {age} years old, your dream of {user_prompt} reflects your current journey. As a {gender} born on {birthdate}, you may be processing recent feelings about {home_page_summary_block}. ...
"""