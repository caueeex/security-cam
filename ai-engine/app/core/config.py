"""
Configurações do AI Engine
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List, Optional
import os


class Settings(BaseSettings):
    """Configurações do AI Engine"""
    
    # Configurações básicas
    APP_NAME: str = "AI Engine - Sistema de Segurança Inteligente"
    VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=False, env="DEBUG")
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    
    # Redis
    REDIS_URL: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    
    # Kafka
    KAFKA_BROKERS: str = Field(default="localhost:9092", env="KAFKA_BROKERS")
    
    # Backend API
    BACKEND_API_URL: str = Field(default="http://localhost:8000", env="BACKEND_API_URL")
    BACKEND_WS_URL: str = Field(default="ws://localhost:8000/ws", env="BACKEND_WS_URL")
    
    # MLflow
    MLFLOW_TRACKING_URI: str = Field(default="http://localhost:5000", env="MLFLOW_TRACKING_URI")
    
    # Modelos de IA
    MODEL_PATH: str = Field(default="/app/models", env="MODEL_PATH")
    MODEL_CACHE_SIZE: int = Field(default=5, env="MODEL_CACHE_SIZE")
    
    # Configurações de detecção
    DETECTION_CONFIDENCE_THRESHOLD: float = Field(default=0.7, env="DETECTION_CONFIDENCE_THRESHOLD")
    ANOMALY_THRESHOLD: float = Field(default=0.5, env="ANOMALY_THRESHOLD")
    MOTION_THRESHOLD: float = Field(default=0.1, env="MOTION_THRESHOLD")
    
    # Configurações de vídeo
    VIDEO_FRAME_RATE: int = Field(default=30, env="VIDEO_FRAME_RATE")
    VIDEO_RESOLUTION: str = Field(default="1920x1080", env="VIDEO_RESOLUTION")
    VIDEO_BUFFER_SIZE: int = Field(default=10, env="VIDEO_BUFFER_SIZE")
    
    # Processamento
    BATCH_SIZE: int = Field(default=4, env="BATCH_SIZE")
    MAX_WORKERS: int = Field(default=4, env="MAX_WORKERS")
    PROCESSING_INTERVAL: float = Field(default=0.1, env="PROCESSING_INTERVAL")  # segundos
    
    # Configurações de modelo
    YOLO_MODEL_PATH: str = Field(default="yolov8n.pt", env="YOLO_MODEL_PATH")
    ANOMALY_MODEL_PATH: str = Field(default="anomaly_detector.pth", env="ANOMALY_MODEL_PATH")
    FACE_DETECTION_MODEL: str = Field(default="haarcascade_frontalface_default.xml", env="FACE_DETECTION_MODEL")
    
    # Configurações de armazenamento
    SAVE_DETECTIONS: bool = Field(default=True, env="SAVE_DETECTIONS")
    SAVE_IMAGES: bool = Field(default=True, env="SAVE_IMAGES")
    IMAGE_QUALITY: int = Field(default=95, env="IMAGE_QUALITY")
    
    # Configurações de performance
    GPU_ENABLED: bool = Field(default=True, env="GPU_ENABLED")
    MEMORY_FRACTION: float = Field(default=0.8, env="MEMORY_FRACTION")
    
    # Configurações de logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FILE: str = Field(default="logs/ai_engine.log", env="LOG_FILE")
    
    # Configurações de monitoramento
    METRICS_ENABLED: bool = Field(default=True, env="METRICS_ENABLED")
    HEALTH_CHECK_INTERVAL: int = Field(default=30, env="HEALTH_CHECK_INTERVAL")
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Instância global das configurações
settings = Settings()
