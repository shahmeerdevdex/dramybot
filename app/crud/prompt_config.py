from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.models.prompt_config import PromptConfig
from app.schemas.prompt_config import PromptConfigSchema

async def get_prompt_config(db: AsyncSession, feature: str):
    result = await db.execute(select(PromptConfig).where(PromptConfig.feature == feature))
    return result.scalar_one_or_none()

async def upsert_prompt_config(db: AsyncSession, config: PromptConfigSchema):
    existing = await get_prompt_config(db, config.feature)
    if existing:
        for key, value in config.dict(exclude_unset=True).items():
            setattr(existing, key, value)
    else:
        existing = PromptConfig(**config.dict())
        db.add(existing)
    await db.commit()
    await db.refresh(existing)
    return existing