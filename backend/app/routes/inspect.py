import logging

from fastapi import APIRouter, UploadFile, File, HTTPException, Query

from app.models.schemas import InspectionResponse, BoardQuestionRequest, BoardQuestionResponse
from app.services.detection_service import detection_service
from app.services.rag_service import rag_service
from app.utils.image_utils import validate_and_open_image, bgr_image_to_base64_png

logger = logging.getLogger("pcb.inspect")
router = APIRouter()


@router.post("/inspect", response_model=InspectionResponse)
async def inspect_board(
    file: UploadFile = File(...),
    explain: bool = Query(True, description="If true, generate a RAG explanation for each detection"),
):
    """
    The full pipeline for one uploaded board image:
      1. CV/ML: YOLOv8 detects and localizes each defect, with confidence
      2. ML (rule engine): each detection is graded Low/Medium/High severity
      3. RAG: each detection is explained using the knowledge base + LLM
    """
    if not detection_service.loaded:
        raise HTTPException(status_code=503, detail="Detection model is not loaded. Check /health.")

    file_bytes = await file.read()
    bgr_image = validate_and_open_image(file_bytes, file.content_type)

    try:
        result = detection_service.inspect(bgr_image)
    except Exception:
        logger.exception("Detection failed")
        raise HTTPException(status_code=500, detail="Detection failed. Please try a different image.")

    detections = result["detections"]

    if explain and detections:
        if not rag_service.check_index():
            logger.warning("RAG index not available -- returning detections without explanations.")
        else:
            for d in detections:
                try:
                    d["explanation"] = rag_service.explain(
                        d["class_name"], d["confidence"],
                        d["severity"]["level"], d["severity"]["score"],
                    )
                except Exception:
                    logger.exception(f"RAG explanation failed for {d['class_name']}")
                    d["explanation"] = None

    return InspectionResponse(
        detections=detections,
        board_summary=result["board_summary"],
        annotated_image_base64=bgr_image_to_base64_png(result["annotated_image"]),
        image_size=result["image_size"],
        inference_time_ms=result.get("inference_time_ms", 0.0),
        model_name=detection_service.model_name,
    )


@router.post("/ask", response_model=BoardQuestionResponse)
async def ask_about_board(request: BoardQuestionRequest):
    """Free-text Q&A over a board's findings, e.g. 'is this safe to assemble?'
    Called by the frontend after an /inspect response, passing back the
    defect types that were found so the RAG layer can retrieve across them."""
    if not rag_service.check_index():
        raise HTTPException(status_code=503, detail="RAG index is not available. Check /health.")

    try:
        result = rag_service.answer(request.question, request.defect_types)
    except Exception:
        logger.exception("RAG Q&A failed")
        raise HTTPException(status_code=500, detail="Could not answer the question. Please try again.")

    return BoardQuestionResponse(**result)
