import base64
import io

import cv2
import numpy as np
from PIL import Image, UnidentifiedImageError
from fastapi import HTTPException

from app.config import settings


def validate_and_open_image(file_bytes: bytes, content_type: str) -> np.ndarray:
    """Returns a BGR numpy array (OpenCV/Ultralytics' expected format)."""
    if content_type not in settings.ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{content_type}'. Allowed: {', '.join(settings.ALLOWED_CONTENT_TYPES)}",
        )

    size_mb = len(file_bytes) / (1024 * 1024)
    if size_mb > settings.MAX_UPLOAD_SIZE_MB:
        raise HTTPException(status_code=400, detail=f"File too large ({size_mb:.1f}MB). Max: {settings.MAX_UPLOAD_SIZE_MB}MB")

    if len(file_bytes) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    try:
        pil_image = Image.open(io.BytesIO(file_bytes))
        pil_image.verify()
        pil_image = Image.open(io.BytesIO(file_bytes)).convert("RGB")
    except UnidentifiedImageError:
        raise HTTPException(status_code=400, detail="Could not read the uploaded file as an image.")
    except Exception:
        raise HTTPException(status_code=400, detail="The uploaded image appears to be corrupted.")

    rgb_array = np.array(pil_image)
    bgr_array = cv2.cvtColor(rgb_array, cv2.COLOR_RGB2BGR)
    return bgr_array


def bgr_image_to_base64_png(bgr_array: np.ndarray) -> str:
    success, buffer = cv2.imencode(".png", bgr_array)
    if not success:
        raise RuntimeError("Failed to encode image to PNG.")
    return base64.b64encode(buffer).decode("utf-8")
