from pydantic import BaseModel
from typing import Optional

class PromptConfigSchema(BaseModel):
    feature: str
    system_prompt: Optional[str]
    model: Optional[str]
    temperature: Optional[float]
    top_p: Optional[float]
    max_tokens: Optional[int]

    class Config:
        orm_mode = True