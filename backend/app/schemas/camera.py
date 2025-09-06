"""
Schemas Pydantic para câmeras
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any
from datetime import datetime


class CameraBase(BaseModel):
    """Schema base para câmera"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    location: str = Field(..., min_length=1, max_length=200)
    ip_address: str = Field(..., regex=r'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$')
    port: int = Field(default=554, ge=1, le=65535)
    stream_url: str = Field(..., min_length=1, max_length=500)
    username: Optional[str] = Field(None, max_length=100)
    password: Optional[str] = Field(None, max_length=100)
    resolution: str = Field(default="1920x1080")
    frame_rate: int = Field(default=30, ge=1, le=60)
    codec: str = Field(default="H.264")
    detection_enabled: bool = Field(default=True)
    confidence_threshold: float = Field(default=0.7, ge=0.0, le=1.0)
    motion_sensitivity: float = Field(default=0.5, ge=0.0, le=1.0)


class CameraCreate(CameraBase):
    """Schema para criação de câmera"""
    pass


class CameraUpdate(BaseModel):
    """Schema para atualização de câmera"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    location: Optional[str] = Field(None, min_length=1, max_length=200)
    ip_address: Optional[str] = Field(None, regex=r'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$')
    port: Optional[int] = Field(None, ge=1, le=65535)
    stream_url: Optional[str] = Field(None, min_length=1, max_length=500)
    username: Optional[str] = Field(None, max_length=100)
    password: Optional[str] = Field(None, max_length=100)
    resolution: Optional[str] = None
    frame_rate: Optional[int] = Field(None, ge=1, le=60)
    codec: Optional[str] = None
    detection_enabled: Optional[bool] = None
    confidence_threshold: Optional[float] = Field(None, ge=0.0, le=1.0)
    motion_sensitivity: Optional[float] = Field(None, ge=0.0, le=1.0)
    is_active: Optional[bool] = None


class CameraInDB(CameraBase):
    """Schema para câmera no banco de dados"""
    id: int
    is_active: bool
    is_online: bool
    last_heartbeat: Optional[datetime]
    last_error: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class Camera(CameraInDB):
    """Schema para resposta da API"""
    pass


class CameraStatus(BaseModel):
    """Schema para status da câmera"""
    id: int
    name: str
    is_online: bool
    last_heartbeat: Optional[datetime]
    last_error: Optional[str]
    detection_enabled: bool


class CameraStats(BaseModel):
    """Schema para estatísticas da câmera"""
    id: int
    name: str
    total_detections: int
    total_alerts: int
    false_positives: int
    accuracy_rate: float
    uptime_percentage: float
    last_detection: Optional[datetime]
