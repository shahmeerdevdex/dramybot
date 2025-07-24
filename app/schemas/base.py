from pydantic import BaseModel

class StandardResponse(BaseModel):
    """Base response model for all API responses"""
    statusCode: int = 200
    message: str = "fetch sucessfully"
    data: dict = None

class DreamLogSummarySchema(BaseModel):
    id: int | None = None
    user_id: str
    summary: str

    class Config:
        orm_mode = True

class MemoryBankSummarySchema(BaseModel):
    id: int | None = None
    user_id: str
    summary: str

    class Config:
        orm_mode = True
