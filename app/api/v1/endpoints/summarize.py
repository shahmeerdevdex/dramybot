from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
import os
import httpx
from fastapi import HTTPException
import asyncio
router = APIRouter()

class SummaryRequest(BaseModel):
    texts: List[str]

class SummaryResponse(BaseModel):
    summary: str

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "your-api-key-here")
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
CLAUDE_MODEL = "google/gemma-3-27b-it"

async def get_summary_from_openrouter(prompt: str, texts: List[str]) -> str:
    """
    Asynchronously calls the OpenRouter Claude model with a system prompt and user content, and returns the summary.
    """
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": "\n".join(texts)}
    ]

    data = {
        "model": CLAUDE_MODEL,
        "messages": messages,
        "max_tokens": 512,
        "temperature": 0.3
    }

    retries = 3
    timeout = 50.0

    for attempt in range(1, retries + 1):
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(OPENROUTER_API_URL, headers=headers, json=data)
                response.raise_for_status()
                result = response.json()
                return result.get("choices", [{}])[0].get("message", {}).get("content", "No summary returned.")

        except httpx.HTTPStatusError as e:
            print(f"[Attempt {attempt}] HTTP error: {e.response.status_code} - {e.response.text}")
        except httpx.RequestError as e:
            print(f"[Attempt {attempt}] Network error: {str(e)}")
        except httpx.ReadError as e:
            print(f"[Attempt {attempt}] Read error: {str(e)}")
        except Exception as e:
            print(f"[Attempt {attempt}] Unknown error: {str(e)}")

        await asyncio.sleep(2)  # Exponential backoff can be added if needed

    raise HTTPException(status_code=500, detail="Failed to get summary from OpenRouter after retries.")
@router.post("/summarize/memory-bank")
async def summarize_memory_bank(request: SummaryRequest):
    prompt = (
        "You are an expert summarizer. Summarize the following memory bank entries in a concise paragraph, "
        "highlighting key themes and important details."
    )
    summary = await get_summary_from_openrouter(prompt, request.texts)
    return {
        "statusCode": 200,
        "message": "fetch sucessfully",
        "data": {"summary": summary}
    }

@router.post("/summarize/dream-logs")
async def summarize_dream_logs(request: SummaryRequest):
    prompt = (
        "You are an expert dream analyst. Summarize the following dream logs, focusing on main events, "
        "emotions, and recurring patterns."
    )
    summary = await get_summary_from_openrouter(prompt, request.texts)
    return {
        "statusCode": 200,
        "message": "fetch sucessfully",
        "data": {"summary": summary}
    }
