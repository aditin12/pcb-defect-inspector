from fastapi import APIRouter

from app.models.schemas import HealthResponse
from app.services.detection_service import detection_service
from app.services.rag_service import rag_service

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health_check():
    rag_service.check_index()
    return HealthResponse(
        status="ok" if (detection_service.loaded and rag_service.index_loaded) else "degraded",
        model_loaded=detection_service.loaded,
        rag_index_loaded=rag_service.index_loaded,
        llm_provider=rag_service.llm_provider,
    )
