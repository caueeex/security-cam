"""
Modelo de dados para detecções de anomalias
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Detection(Base):
    """Modelo para detecções de anomalias"""
    
    __tablename__ = "detections"
    
    id = Column(Integer, primary_key=True, index=True)
    camera_id = Column(Integer, ForeignKey("cameras.id"), nullable=False)
    
    # Informações da detecção
    detection_type = Column(String(50), nullable=False)  # anomaly, intrusion, motion, etc.
    confidence_score = Column(Float, nullable=False)
    anomaly_score = Column(Float)
    
    # Coordenadas da detecção
    bounding_box = Column(JSON)  # {"x": 100, "y": 200, "width": 300, "height": 400}
    center_point = Column(JSON)  # {"x": 250, "y": 400}
    
    # Metadados da imagem/vídeo
    frame_timestamp = Column(DateTime(timezone=True), nullable=False)
    frame_number = Column(Integer)
    image_path = Column(String(500))
    video_path = Column(String(500))
    
    # Informações técnicas
    model_version = Column(String(50))
    processing_time_ms = Column(Integer)
    
    # Classificação e análise
    object_class = Column(String(100))  # person, vehicle, animal, etc.
    behavior_type = Column(String(100))  # walking, running, loitering, etc.
    risk_level = Column(String(20), default="medium")  # low, medium, high, critical
    
    # Status da detecção
    is_verified = Column(Boolean, default=False)
    is_false_positive = Column(Boolean, default=False)
    verification_notes = Column(Text)
    
    # Metadados
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relacionamentos
    camera = relationship("Camera", back_populates="detections")
    alerts = relationship("Alert", back_populates="detection")
    
    def __repr__(self):
        return f"<Detection(id={self.id}, type='{self.detection_type}', confidence={self.confidence_score})>"
