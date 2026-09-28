"""
Detection service singleton. Imports ml/src/inference.py directly (the
same PCBInspector class used for standalone CLI testing and result
generation) so the served model's behavior is guaranteed identical to
what was trained and evaluated -- one definition of the detection
pipeline, not a backend-side reimplementation.
"""
import os
import sys

_BACKEND_APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # backend/app
_REPO_ROOT = os.path.dirname(os.path.dirname(_BACKEND_APP_DIR))                   # repo root
_ML_SRC = os.path.join(_REPO_ROOT, "ml", "src")
if _ML_SRC not in sys.path:
    sys.path.insert(0, _ML_SRC)

from inference import PCBInspector  # noqa: E402  (ml/src/inference.py)

from app.config import settings


class DetectionService:
    def __init__(self):
        self.inspector = None
        self.loaded = False
        self.model_name = "YOLOv8 (PCB defect detection)"

    def load(self):
        if not os.path.exists(settings.MODEL_PATH):
            raise FileNotFoundError(
                f"No model checkpoint at {settings.MODEL_PATH}. "
                f"Train it first: cd ml/src && python train_yolo.py"
            )
        self.inspector = PCBInspector(
            weights_path=settings.MODEL_PATH,
            confidence_threshold=settings.CONFIDENCE_THRESHOLD,
        )
        self.loaded = True

    def inspect(self, bgr_image) -> dict:
        if not self.loaded:
            raise RuntimeError("Detection model not loaded.")
        return self.inspector.inspect(bgr_image)


detection_service = DetectionService()
