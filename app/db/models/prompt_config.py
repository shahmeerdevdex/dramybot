from sqlalchemy import Column, String, Text, Float
from app.db.base_class import Base

class PromptConfig(Base):
    __tablename__ = "prompt_configs"

    feature = Column(String, primary_key=True, index=True)  # e.g., guest_chat
    system_prompt = Column(Text, nullable=True)
    model = Column(String, default="openrouter/gemma-7b")
    temperature = Column(Float, default=0.7)
    top_p = Column(Float, default=1.0)
    max_tokens = Column(Float, default=500)
