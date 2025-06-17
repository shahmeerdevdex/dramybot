from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from app.core.prompts import DREAMER_QUESTIONS_PROMPT
from app.utils.openrouter import make_streaming_request

router = APIRouter()

class DreamerQuestionsRequest(BaseModel):
    user_prompt: str
    temperature: float = 0.7
    last_messages: list[str]

@router.post("/dream-questions")
async def dreamer_questions_stream(payload: DreamerQuestionsRequest):
    """
    Stream an answer to the user's question using OpenRouter GPT-4.0.
    """
    model = "openai/gpt-4o"
    messages = [
        {"role": "system", "content": DREAMER_QUESTIONS_PROMPT},
        {"role": "user", "content": payload.user_prompt},
        {"role": "assistant", "content": f"here are the previous messages you have asked with user : {payload.last_messages}"}
    ]
    print(messages)
    return StreamingResponse(
        stream_response_from_openrouter(model, messages, payload.temperature),
        media_type="text/event-stream"
    )

async def stream_response_from_openrouter(model, messages, temperature):
    try:
        async for chunk in make_streaming_request(model, messages, temperature):
            yield chunk
    except Exception as e:
        yield f"data: {{\"statusCode\": 500, \"message\": \"{str(e)}\", \"data\": null}}\n\n".encode('utf-8')
        yield f"data: [DONE]\n\n".encode('utf-8')
