"""
Schemas Pydantic para alertas
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any
from datetime import datetime
from app.models.alert import AlertStatus, AlertPriority


class AlertBase(BaseModel):
    """Schema base para alerta"""
    camera_id: int
    detection_id: Optional[int] = None
    alert_type: str = Field(..., min_length=1, max_length=50)
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    priority: AlertPriority = AlertPriority.MEDIUM
    status: AlertStatus = AlertStatus.PENDING
    detection_data: Optional[Dict[str, Any]] = None
    image_url: Optional[str] = Field(None, max_length=500)
    video_url: Optional[str] = Field(None, max_length=500)
    location: Optional[str] = Field(None, max_length=200)
    coordinates: Optional[Dict[str, Any]] = None


class AlertCreate(AlertBase):
    """Schema para criação de alerta"""
    pass


class AlertUpdate(BaseModel):
    """Schema para atualização de alerta"""
    status: Optional[AlertStatus] = None
    priority: Optional[AlertPriority] = None
    description: Optional[str] = None
    resolved_by: Optional[str] = Field(None, max_length=100)
    resolution_notes: Optional[str] = None


class AlertInDB(AlertBase):
    """Schema para alerta no banco de dados"""
    id: int
    email_sent: bool
    sms_sent: bool
    push_notification_sent: bool
    resolved_at: Optional[datetime]
    resolved_by: Optional[str]
    resolution_notes: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class Alert(AlertInDB):
    """Schema para resposta da API"""
    pass


class AlertSummary(BaseModel):
    """Schema para resumo de alerta"""
    id: int
    camera_id: int
    alert_type: str
    title: str
    priority: AlertPriority
    status: AlertStatus
    created_at: datetime
    location: Optional[str]


class AlertStats(BaseModel):
    """Schema para estatísticas de alertas"""
    total_alerts: int
    pending_alerts: int
    resolved_alerts: int
    false_positive_alerts: int
    alerts_by_priority: Dict[str, int]
    alerts_by_status: Dict[str, int]
    alerts_by_type: Dict[str, int]
    average_resolution_time_minutes: Optional[float]
    alerts_last_24h: int
    alerts_last_7d: int


class AlertFilter(BaseModel):
    """Schema para filtros de alerta"""
    camera_id: Optional[int] = None
    alert_type: Optional[str] = None
    priority: Optional[AlertPriority] = None
    status: Optional[AlertStatus] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    location: Optional[str] = None


class AlertNotification(BaseModel):
    """Schema para notificação de alerta"""
    alert_id: int
    title: str
    message: str
    priority: AlertPriority
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    location: Optional[str] = None
    timestamp: datetime
