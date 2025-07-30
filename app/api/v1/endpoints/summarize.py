from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
import os
import requests

router = APIRouter()

class SummaryRequest(BaseModel):
    texts: List[str]

class SummaryResponse(BaseModel):
    summary: str

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "your-api-key-here")
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
CLAUDE_MODEL = "google/gemma-3-27b-it"

def get_summary_from_openrouter(prompt: str, texts: List[str]) -> str:
    """
    Calls OpenRouter Claude model with a system prompt and user content, returns summary string.
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
    response = requests.post(OPENROUTER_API_URL, headers=headers, json=data)
    if response.status_code == 200:
        result = response.json()
        # Claude/Anthropic returns the result in choices[0]['message']['content']
        return result.get("choices", [{}])[0].get("message", {}).get("content", "No summary returned.")
    else:
        raise HTTPException(status_code=500, detail=f"Failed to get summary from OpenRouter: {response.text}")

@router.post("/summarize/memory-bank")
def summarize_memory_bank(request: SummaryRequest):
    prompt = (
        "You are an expert summarizer. Summarize the following memory bank entries in a concise paragraph, "
        "highlighting key themes and important details."
    )
    summary = get_summary_from_openrouter(prompt, request.texts)
    return {
        "statusCode": 200,
        "message": "fetch sucessfully",
        "data": {"summary": summary}
    }

@router.post("/summarize/dream-logs")
def summarize_dream_logs(request: SummaryRequest):
    prompt = (
        "You are an expert dream analyst. Summarize the following dream logs, focusing on main events, "
        "emotions, and recurring patterns."
    )
    summary = get_summary_from_openrouter(prompt, request.texts)
    return {
        "statusCode": 200,
        "message": "fetch sucessfully",
        "data": {"summary": summary}
    }
