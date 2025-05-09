from fastapi import FastAPI
from app.api.api import api_router
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create FastAPI application
app = FastAPI(
    title="OpenRouter API",
    description="API for interacting with OpenRouter chat models",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Include API router
app.include_router(api_router)
