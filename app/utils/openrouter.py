import re
import json
from sys import exception

import aiohttp
import asyncio
from typing import Dict, List, Any, AsyncGenerator
from app.core.config import get_openrouter_api_key, get_openrouter_gemini_key
import httpx
import traceback

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

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


async def make_openrouter_request(
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        retries: int = 3,
        timeout: float = 50.0,
        memory: str = False,
) -> Dict[str, Any]:
    """Make an async request to OpenRouter API using httpx"""
    api_key = get_openrouter_api_key()

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = ""
    if memory:
        payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "top_p": 1.0,  # 0.0 to 1.0, default 1.0
        "top_k": 0,  # 0 or above, default 0
        "frequency_penalty": 0.0,  # -2.0 to 2.0, default 0.0
        "presence_penalty": 0.0,  # -2.0 to 2.0, default 0.0
        "repetition_penalty": 0.0,  # 0.0 to 2.0, default 1.0
        "min_p": 0.0,  # 0.0 to 1.0, default 0.0
        "top_a": 0.0,  # 0.0 to 1.0, default 0.0
    }
    else:
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature, # optional integer limit
        }
        

    for attempt in range(1, retries + 1):
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(OPENROUTER_API_URL, headers=headers, json=payload)
                response.raise_for_status()
                return response.json()

        except httpx.HTTPStatusError as e:
            print(f"[Attempt {attempt}] HTTP error: {e.response.status_code} - {e.response.text}")
        except httpx.RequestError as e:
            print(f"[Attempt {attempt}] Network error: {str(e)}")
        except httpx.ReadError as e:
            print(f"[Attempt {attempt}] Read error: {str(e)}")

        await asyncio.sleep(2)  # backoff between retries

    raise RuntimeError("Failed to fetch response from OpenRouter after retries.")

async def make_streaming_request(model: str, messages: List[Dict[str, str]], temperature: float = 0.5) -> AsyncGenerator[str, None]:
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
        "temperature": temperature,
        "top_p": 1.0,  # 0.0 to 1.0, default 1.0
        "top_k": 0,  # 0 or above, default 0
        "frequency_penalty": 0.0,  # -2.0 to 2.0, default 0.0
        "presence_penalty": 0.0,  # -2.0 to 2.0, default 0.0
        "repetition_penalty": 1.0,  # 0.0 to 2.0, default 1.0
        "min_p": 0.0,  # 0.0 to 1.0, default 0.0
        "top_a": 0.0,  # 0.0 to 1.0, default 0.0
        "max_tokens": 0,  # optional integer limit
    }
    full_response = ""
    buffer = ""
    async with httpx.AsyncClient(timeout=None) as client:
        async with client.stream(
            "POST",
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=request_data,
        ) as response:
            async for chunk in response.aiter_bytes(chunk_size=1024):
                buffer += chunk.decode("utf-8", errors="ignore")

                while True:
                    line_end = buffer.find('\n')
                    if line_end == -1:
                        break

                    line = buffer[:line_end].strip()
                    buffer = buffer[line_end + 1:]

                    if not line or line == "data: [DONE]":
                        continue

                    if line.startswith("data: "):
                        try:
                            data = json.loads(line[6:])
                            content = data.get("choices", [{}])[0].get("delta", {}).get("content")
                            if content:
                                yield f"data: {json.dumps({
                                    'statusCode': 200,
                                    'message': 'fetch successfully',
                                    'data': {'response': content}
                                })}\n\n"
                        except json.JSONDecodeError:
                            continue
    # Use aiohttp for async HTTP requests
    # async with aiohttp.ClientSession() as session:
    #     try:
    #         async with session.post(
    #             "https://openrouter.ai/api/v1/chat/completions",
    #             headers=headers,
    #             json=request_data,
    #         ) as response:
    #             # Check if the request was successful
    #             if response.status != 200:
    #                 error_text = await response.text()
    #                 error_msg = f"Error from OpenRouter API: {response.status} - {error_text}"
    #                 yield f"data: {json.dumps({'statusCode': response.status, 'message': error_msg, 'data': None})}\n\n".encode('utf-8')
    #                 return
    #
    #             # Process the streaming response
    #             async for line in response.content:
    #                 line = line.decode('utf-8').strip()
    #                 if not line:
    #                     continue
    #
    #                 # OpenRouter sends "data: [DONE]" to indicate the end of the stream
    #                 if line == "data: [DONE]":
    #                     break
    #
    #                 # Lines start with "data: " - remove this prefix
    #                 if line.startswith("data: "):
    #                     json_str = line[6:]  # Remove "data: " prefix
    #                     try:
    #                         data = json.loads(json_str)
    #                         if "choices" in data and len(data["choices"]) > 0:
    #                             delta = data["choices"][0].get("delta", {})
    #                             content = delta.get("content", "")
    #                             if content:
    #                                 # Format as SSE event
    #                                 yield f"data: {json.dumps({'statusCode': 200, 'message': 'fetch sucessfully', 'data': {'response': content}})}\n\n".encode('utf-8')
    #                                 # Small delay to avoid overwhelming the client
    #                                 await asyncio.sleep(0.01)
    #                     except json.JSONDecodeError as e:
    #                         print(f"Error parsing JSON: {e} - Line: {line}")
    #                         continue
    #
    #             # Send a final event to indicate the end of the stream
    #             yield f"data: [DONE]\n\n".encode('utf-8')
    #     except Exception as e:
    #
    #         print(f"Issue with Stream : {traceback.print_exc()}")
