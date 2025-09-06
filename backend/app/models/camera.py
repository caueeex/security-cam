"""
Modelo de dados para câmeras de segurança
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Camera(Base):
    """Modelo para câmeras de segurança"""
    
    __tablename__ = "cameras"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text)
    location = Column(String(200), nullable=False)
    ip_address = Column(String(45), nullable=False, unique=True)
    port = Column(Integer, default=554)
    stream_url = Column(String(500), nullable=False)
    username = Column(String(100))
    password = Column(String(100))
    
    # Configurações técnicas
    resolution = Column(String(20), default="1920x1080")
    frame_rate = Column(Integer, default=30)
    codec = Column(String(20), default="H.264")
    
    # Configurações de detecção
    detection_enabled = Column(Boolean, default=True)
    confidence_threshold = Column(Float, default=0.7)
    motion_sensitivity = Column(Float, default=0.5)
    
    # Status e monitoramento
    is_active = Column(Boolean, default=True)
    is_online = Column(Boolean, default=False)
    last_heartbeat = Column(DateTime(timezone=True))
    last_error = Column(Text)
    
    # Metadados
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relacionamentos
    detections = relationship("Detection", back_populates="camera")
    alerts = relationship("Alert", back_populates="camera")
    
    def __repr__(self):
        return f"<Camera(id={self.id}, name='{self.name}', location='{self.location}')>"
