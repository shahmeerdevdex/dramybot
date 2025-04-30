from fastapi import APIRouter
from app.api.v1.endpoints import prompt_config, openrouter_chat

api_router = APIRouter()

api_router.include_router(
    prompt_config.router, prefix="/prompt-config", tags=["Prompt Config"]
)
api_router.include_router(
    openrouter_chat.router, prefix="/chat", tags=["OpenRouter Chat"]
)
