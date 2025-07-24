from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.models.summary import DreamLogSummary, MemoryBankSummary

# Dream Log Summary CRUD
async def create_or_update_dream_log_summary(db: AsyncSession, user_id: str, summary: str):
    result = await db.execute(select(DreamLogSummary).where(DreamLogSummary.user_id == user_id))
    obj = result.scalars().first()
    if obj:
        obj.summary = summary
    else:
        obj = DreamLogSummary(user_id=user_id, summary=summary)
        db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj

async def get_dream_log_summaries(db: AsyncSession, user_id: str):
    result = await db.execute(select(DreamLogSummary).where(DreamLogSummary.user_id == user_id))
    return result.scalars().all()

# Memory Bank Summary CRUD
async def create_or_update_memory_bank_summary(db: AsyncSession, user_id: str, summary: str):
    result = await db.execute(select(MemoryBankSummary).where(MemoryBankSummary.user_id == user_id))
    obj = result.scalars().first()
    if obj:
        obj.summary = summary
    else:
        obj = MemoryBankSummary(user_id=user_id, summary=summary)
        db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj

async def get_memory_bank_summaries(db: AsyncSession, user_id: str):
    result = await db.execute(select(MemoryBankSummary).where(MemoryBankSummary.user_id == user_id))
    return result.scalars().all() 