import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "PCB Inspector API"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    _repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    MODEL_PATH: str = os.getenv("MODEL_PATH", os.path.join(_repo_root, "models", "pcb_yolov8_best.pt"))
    CONFIDENCE_THRESHOLD: float = float(os.getenv("CONFIDENCE_THRESHOLD", "0.25"))

    MAX_UPLOAD_SIZE_MB: int = int(os.getenv("MAX_UPLOAD_SIZE_MB", "10"))
    ALLOWED_CONTENT_TYPES: tuple = ("image/jpeg", "image/png", "image/jpg", "image/bmp")

    CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")

    class Config:
        env_file = ".env"


settings = Settings()
