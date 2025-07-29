import re
import json
import requests
import aiohttp
import asyncio
from typing import Dict, List, Any, AsyncGenerator
from app.core.config import get_openrouter_api_key, get_openrouter_gemini_key

def extract_json_from_text(text: str) -> Dict[str, Any]:
    """Extract JSON from text that may contain markdown or other formatting"""
    # Sometimes the model might wrap the JSON in markdown code blocks or add text before/after
    json_match = re.search(r'\{.*\}', text, re.DOTALL)
    if json_match:
        text = json_match.group(0)
    
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {}

def make_openrouter_request(model: str, messages: List[Dict[str, str]], temperature: float = 0.7) -> Dict[str, Any]:
    """Make a request to the OpenRouter API"""
    api_key = get_openrouter_api_key()
    
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}"
        },
        json={
            "model": model,
            "messages": messages,
            "temperature": temperature
        },
    )
    
    response.raise_for_status()
    return response.json()

async def make_streaming_request(model: str, messages: List[Dict[str, str]], temperature: float = 0.7) -> AsyncGenerator[bytes, None]:
    """Make a streaming request to the OpenRouter API"""
    if model == "google/gemini-2.5-pro":
        api_key = get_openrouter_gemini_key()
    else:
        api_key = get_openrouter_api_key()
    print("api_key:", api_key)
    
    # Set up headers
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "text/event-stream"
    }
    
    request_data = {
        "model": model,
        "messages": messages,
        "stream": True,
        "temperature": temperature
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
                yield f"data: {json.dumps({'statusCode': response.status, 'message': error_msg, 'data': None})}\n\n".encode('utf-8')
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
                                yield f"data: {json.dumps({'statusCode': 200, 'message': 'fetch sucessfully', 'data': {'response': content}})}\n\n".encode('utf-8')
                                # Small delay to avoid overwhelming the client
                                await asyncio.sleep(0.01)
                    except json.JSONDecodeError as e:
                        print(f"Error parsing JSON: {e} - Line: {line}")
                        continue
            
            # Send a final event to indicate the end of the stream
            yield f"data: [DONE]\n\n".encode('utf-8')
