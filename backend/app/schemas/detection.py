"""
Schemas Pydantic para detecções
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any
from datetime import datetime


class DetectionBase(BaseModel):
    """Schema base para detecção"""
    camera_id: int
    detection_type: str = Field(..., min_length=1, max_length=50)
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    anomaly_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    bounding_box: Optional[Dict[str, Any]] = None
    center_point: Optional[Dict[str, Any]] = None
    frame_timestamp: datetime
    frame_number: Optional[int] = None
    image_path: Optional[str] = Field(None, max_length=500)
    video_path: Optional[str] = Field(None, max_length=500)
    model_version: Optional[str] = Field(None, max_length=50)
    processing_time_ms: Optional[int] = None
    object_class: Optional[str] = Field(None, max_length=100)
    behavior_type: Optional[str] = Field(None, max_length=100)
    risk_level: str = Field(default="medium", regex=r'^(low|medium|high|critical)$')


class DetectionCreate(DetectionBase):
    """Schema para criação de detecção"""
    pass


class DetectionUpdate(BaseModel):
    """Schema para atualização de detecção"""
    is_verified: Optional[bool] = None
    is_false_positive: Optional[bool] = None
    verification_notes: Optional[str] = None


class DetectionInDB(DetectionBase):
    """Schema para detecção no banco de dados"""
    id: int
    is_verified: bool
    is_false_positive: bool
    verification_notes: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class Detection(DetectionInDB):
    """Schema para resposta da API"""
    pass


class DetectionSummary(BaseModel):
    """Schema para resumo de detecção"""
    id: int
    camera_id: int
    detection_type: str
    confidence_score: float
    risk_level: str
    frame_timestamp: datetime
    object_class: Optional[str]
    is_verified: bool
    is_false_positive: bool


class DetectionStats(BaseModel):
    """Schema para estatísticas de detecção"""
    total_detections: int
    verified_detections: int
    false_positives: int
    accuracy_rate: float
    detections_by_type: Dict[str, int]
    detections_by_risk_level: Dict[str, int]
    average_confidence: float
    detections_last_24h: int
    detections_last_7d: int


class DetectionFilter(BaseModel):
    """Schema para filtros de detecção"""
    camera_id: Optional[int] = None
    detection_type: Optional[str] = None
    risk_level: Optional[str] = None
    object_class: Optional[str] = None
    is_verified: Optional[bool] = None
    is_false_positive: Optional[bool] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    min_confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    max_confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
