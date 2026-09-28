from typing import List, Optional
from pydantic import BaseModel


class BBox(BaseModel):
    xmin: float
    ymin: float
    xmax: float
    ymax: float


class Severity(BaseModel):
    score: float
    level: str


class Source(BaseModel):
    section: str
    source_doc: str


class Explanation(BaseModel):
    explanation: str
    sources: List[Source]
    backend_used: str


class Detection(BaseModel):
    class_name: str
    confidence: float
    bbox: BBox
    severity: Severity
    explanation: Optional[Explanation] = None


class BoardSummary(BaseModel):
    overall_level: str
    counts: dict
    total_defects: int


class InspectionResponse(BaseModel):
    detections: List[Detection]
    board_summary: BoardSummary
    annotated_image_base64: str
    image_size: dict
    inference_time_ms: float
    model_name: str


class BoardQuestionRequest(BaseModel):
    question: str
    defect_types: List[str]


class BoardQuestionResponse(BaseModel):
    answer: str
    sources: List[Source]
    backend_used: str


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    rag_index_loaded: bool
    llm_provider: str
