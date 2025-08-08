from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from app.core.prompts import DREAMER_QUESTIONS_PROMPT,END_CHAT_PROMPT
from app.utils.openrouter import make_streaming_request
from app.core.config import get_openrouter_api_key
import httpx
import json
router = APIRouter()
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
                 

class DreamerQuestionsRequest(BaseModel):
    user_prompt: str
    temperature: float = 0.7
    last_messages: list[str]

# @router.post("/dream-questions")
# async def dreamer_questions_stream(payload: DreamerQuestionsRequest):
#     """
#     Stream an answer to the user's question using OpenRouter GPT-4.0.
#     """
#     api_key = get_openrouter_api_key()
#     messages = [{"role": "system", "content": DREAMER_QUESTIONS_PROMPT}]
#     messages.extend(payload.last_messages)
#
#
#     async def generate(messages: list[str]):
#         url = "https://openrouter.ai/api/v1/chat/completions"
#         headers = {
#             "Authorization": f"Bearer {api_key}",
#             "Content-Type": "application/json",
#         }
#         payload = {
#             "model": "openai/gpt-4o",
#             "messages": messages,
#             "stream": True
#         }
#         async with httpx.AsyncClient(timeout=None) as client:
#             async with client.stream("POST", url, headers=headers, json=payload) as response:
#                 async for line in response.aiter_lines():
#                     if line.strip() == "" or line.strip() == "data: [DONE]":
#                         continue
#                     if line.startswith("data: "):
#                         try:
#                             chunk = json.loads(line[len("data: "):])
#                             content = chunk.get("choices", [{}])[0].get("delta", {}).get("content")
#                             if content:
#                                 yield f"data: {json.dumps({
#                                     'statusCode': 200,
#                                     'message': 'fetch sucessfully',
#                                     'data': {'response': content}
#                                 })}\n\n"
#                         except Exception as e:
#                             continue
#
#     return StreamingResponse(generate(messages), media_type="text/event-stream")




@router.post("/dream-questions")
async def dreamer_questions_stream(payload: DreamerQuestionsRequest):
    """
    Stream an answer to the user's question using OpenRouter GPT-4.0.
    Also returns full final string at the end as a separate SSE message.
    """
    api_key = get_openrouter_api_key()
    messages = [{"role": "system", "content": DREAMER_QUESTIONS_PROMPT}]
    messages.append({"role": "user", "content": f"here is the user message : {payload.user_prompt}"})
    messages.append({"role": "user", "content": f" here are your asked questions and your responses {payload.last_messages}"})
    async def generate(messages: list[str]):
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "openai/chatgpt-4o-latest",
            "messages": messages,
            "temperature": 0.7,
            "stream": True
        }
        full_response = ""

        async with httpx.AsyncClient(timeout=None) as client:
            async with client.stream("POST", url, headers=headers, json=payload) as response:
                async for line in response.aiter_lines():
                    if line.strip() == "" or line.strip() == "data: [DONE]":
                        continue
                    if line.startswith("data: "):
                        try:
                            chunk = json.loads(line[len("data: "):])
                            content = chunk.get("choices", [{}])[0].get("delta", {}).get("content")
                            if content:
                                full_response += content
                                yield f"data: {json.dumps({
                                    'statusCode': 200,
                                    'message': 'fetch sucessfully',
                                    'data': {'response': content}
                                })}\n\n"
                        except Exception as e:
                            print("Issue with Stream : ", e)
                            continue

        # Send full response at the end
        yield f"data: {json.dumps({
            'statusCode': 200,
            'message': 'completed',
            'data': {'full_response': full_response}
        })}\n\n"

    return StreamingResponse(generate(messages), media_type="text/event-stream")
