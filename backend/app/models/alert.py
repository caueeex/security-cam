"""
Modelo de dados para alertas de segurança
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class AlertStatus(str, enum.Enum):
    """Status dos alertas"""
    PENDING = "pending"
    ACKNOWLEDGED = "acknowledged"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"
    FALSE_POSITIVE = "false_positive"


class AlertPriority(str, enum.Enum):
    """Prioridade dos alertas"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Alert(Base):
    """Modelo para alertas de segurança"""
    
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    camera_id = Column(Integer, ForeignKey("cameras.id"), nullable=False)
    detection_id = Column(Integer, ForeignKey("detections.id"), nullable=True)
    
    # Informações do alerta
    alert_type = Column(String(50), nullable=False)  # intrusion, motion, anomaly, etc.
    title = Column(String(200), nullable=False)
    description = Column(Text)
    priority = Column(Enum(AlertPriority), default=AlertPriority.MEDIUM)
    status = Column(Enum(AlertStatus), default=AlertStatus.PENDING)
    
    # Dados da detecção
    detection_data = Column(JSON)  # Dados completos da detecção
    image_url = Column(String(500))
    video_url = Column(String(500))
    
    # Localização e contexto
    location = Column(String(200))
    coordinates = Column(JSON)  # {"lat": -23.5505, "lng": -46.6333}
    
    # Notificações
    email_sent = Column(Boolean, default=False)
    sms_sent = Column(Boolean, default=False)
    push_notification_sent = Column(Boolean, default=False)
    
    # Resolução do alerta
    resolved_at = Column(DateTime(timezone=True))
    resolved_by = Column(String(100))
    resolution_notes = Column(Text)
    
    # Metadados
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relacionamentos
    camera = relationship("Camera", back_populates="alerts")
    detection = relationship("Detection", back_populates="alerts")
    
    def __repr__(self):
        return f"<Alert(id={self.id}, type='{self.alert_type}', priority='{self.priority}')>"
