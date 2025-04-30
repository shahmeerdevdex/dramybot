from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.prompt_config import PromptConfigSchema
from app.crud import prompt_config as crud
from app.dependencies import get_db

router = APIRouter()

@router.get("/{feature}", response_model=PromptConfigSchema)
async def get_prompt_config(feature: str, db: AsyncSession = Depends(get_db)):
    return await crud.get_prompt_config(db, feature)

@router.post("/", response_model=PromptConfigSchema)
async def upsert_config(config: PromptConfigSchema, db: AsyncSession = Depends(get_db)):
    return await crud.upsert_prompt_config(db, config)