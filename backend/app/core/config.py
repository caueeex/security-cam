"""
Configurações da aplicação usando Pydantic Settings
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List, Optional
import os


class Settings(BaseSettings):
    """Configurações da aplicação"""
    
    # Configurações básicas
    APP_NAME: str = "Sistema de Segurança Inteligente"
    VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=False, env="DEBUG")
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    
    # API
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # CORS
    ALLOWED_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:3001"],
        env="ALLOWED_ORIGINS"
    )
    ALLOWED_HOSTS: List[str] = Field(
        default=["localhost", "127.0.0.1"],
        env="ALLOWED_HOSTS"
    )
    
    # Banco de dados PostgreSQL
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    
    # MongoDB
    MONGODB_URL: str = Field(..., env="MONGODB_URL")
    
    # Redis
    REDIS_URL: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    
    # Kafka
    KAFKA_BROKERS: str = Field(default="localhost:9092", env="KAFKA_BROKERS")
    
    # MinIO (Object Storage)
    MINIO_ENDPOINT: str = Field(default="localhost:9000", env="MINIO_ENDPOINT")
    MINIO_ACCESS_KEY: str = Field(default="minioadmin", env="MINIO_ACCESS_KEY")
    MINIO_SECRET_KEY: str = Field(default="minioadmin123", env="MINIO_SECRET_KEY")
    MINIO_BUCKET_NAME: str = Field(default="security-cam", env="MINIO_BUCKET_NAME")
    
    # Elasticsearch
    ELASTICSEARCH_URL: str = Field(default="http://localhost:9200", env="ELASTICSEARCH_URL")
    
    # MLflow
    MLFLOW_TRACKING_URI: str = Field(default="http://localhost:5000", env="MLFLOW_TRACKING_URI")
    
    # AI Engine
    AI_ENGINE_URL: str = Field(default="http://localhost:8001", env="AI_ENGINE_URL")
    
    # Configurações de vídeo
    VIDEO_STREAM_URL: Optional[str] = Field(default=None, env="VIDEO_STREAM_URL")
    VIDEO_FRAME_RATE: int = Field(default=30, env="VIDEO_FRAME_RATE")
    VIDEO_RESOLUTION: str = Field(default="1920x1080", env="VIDEO_RESOLUTION")
    
    # Configurações de detecção
    DETECTION_CONFIDENCE_THRESHOLD: float = Field(default=0.7, env="DETECTION_CONFIDENCE_THRESHOLD")
    ANOMALY_THRESHOLD: float = Field(default=0.5, env="ANOMALY_THRESHOLD")
    
    # Configurações de armazenamento
    MAX_VIDEO_RETENTION_DAYS: int = Field(default=30, env="MAX_VIDEO_RETENTION_DAYS")
    MAX_IMAGE_RETENTION_DAYS: int = Field(default=90, env="MAX_IMAGE_RETENTION_DAYS")
    
    # Configurações de notificação
    EMAIL_ENABLED: bool = Field(default=False, env="EMAIL_ENABLED")
    EMAIL_SMTP_HOST: Optional[str] = Field(default=None, env="EMAIL_SMTP_HOST")
    EMAIL_SMTP_PORT: Optional[int] = Field(default=None, env="EMAIL_SMTP_PORT")
    EMAIL_USERNAME: Optional[str] = Field(default=None, env="EMAIL_USERNAME")
    EMAIL_PASSWORD: Optional[str] = Field(default=None, env="EMAIL_PASSWORD")
    
    # WebSocket
    WS_HEARTBEAT_INTERVAL: int = Field(default=30, env="WS_HEARTBEAT_INTERVAL")
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Instância global das configurações
settings = Settings()
