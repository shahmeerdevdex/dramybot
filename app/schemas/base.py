from pydantic import BaseModel

class StandardResponse(BaseModel):
    """Base response model for all API responses"""
    statusCode: int = 200
    message: str = "fetch sucessfully"
    data: dict = None
