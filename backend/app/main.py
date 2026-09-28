"""
PCB Inspector FastAPI application.

Run locally:
    cd backend
    uvicorn app.main:app --reload --port 8000

Docs: http://localhost:8000/docs
"""
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routes import health, inspect
from app.services.detection_service import detection_service
from app.services.rag_service import rag_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("pcb_inspector")

app = FastAPI(
    title=settings.APP_NAME,
    description="CV -> ML -> RAG pipeline for PCB defect detection, severity grading, and explanation.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(health.router, tags=["health"])
app.include_router(inspect.router, tags=["inspection"])


@app.on_event("startup")
def load_everything():
    try:
        detection_service.load()
        logger.info(f"Detection model loaded from {settings.MODEL_PATH}")
    except FileNotFoundError as e:
        logger.error(str(e))

    if rag_service.check_index():
        logger.info(f"RAG index loaded (LLM provider: {rag_service.llm_provider})")
    else:
        logger.error("RAG index not found. Run: cd rag/src && python build_index.py")


@app.get("/")
def root():
    return {
        "message": "PCB Inspector API is running. See /docs for API documentation.",
        "health_check": "/health",
        "inspect_endpoint": "/inspect (POST, multipart/form-data, field name 'file')",
        "ask_endpoint": "/ask (POST, JSON: {question, defect_types})",
    }
