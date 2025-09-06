"""
Serviço para gerenciamento de detecções
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from typing import List, Optional, Dict, Any
import logging
import base64
from datetime import datetime, timedelta

from app.models.detection import Detection
from app.models.camera import Camera
from app.schemas.detection import (
    DetectionCreate,
    DetectionUpdate,
    DetectionSummary,
    DetectionStats,
    DetectionFilter
)
from app.core.exceptions import ValidationException, NotFoundException

logger = logging.getLogger(__name__)


class DetectionService:
    """Serviço para operações com detecções"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def get_detections(
        self,
        skip: int = 0,
        limit: int = 100,
        filter_data: Optional[DetectionFilter] = None
    ) -> List[DetectionSummary]:
        """Obter lista de detecções com filtros"""
        query = self.db.query(Detection)
        
        if filter_data:
            if filter_data.camera_id:
                query = query.filter(Detection.camera_id == filter_data.camera_id)
            
            if filter_data.detection_type:
                query = query.filter(Detection.detection_type == filter_data.detection_type)
            
            if filter_data.risk_level:
                query = query.filter(Detection.risk_level == filter_data.risk_level)
            
            if filter_data.object_class:
                query = query.filter(Detection.object_class == filter_data.object_class)
            
            if filter_data.is_verified is not None:
                query = query.filter(Detection.is_verified == filter_data.is_verified)
            
            if filter_data.is_false_positive is not None:
                query = query.filter(Detection.is_false_positive == filter_data.is_false_positive)
            
            if filter_data.start_date:
                query = query.filter(Detection.frame_timestamp >= filter_data.start_date)
            
            if filter_data.end_date:
                query = query.filter(Detection.frame_timestamp <= filter_data.end_date)
            
            if filter_data.min_confidence:
                query = query.filter(Detection.confidence_score >= filter_data.min_confidence)
            
            if filter_data.max_confidence:
                query = query.filter(Detection.confidence_score <= filter_data.max_confidence)
        
        # Ordenar por timestamp mais recente
        query = query.order_by(desc(Detection.frame_timestamp))
        
        detections = query.offset(skip).limit(limit).all()
        
        # Converter para DetectionSummary
        return [
            DetectionSummary(
                id=d.id,
                camera_id=d.camera_id,
                detection_type=d.detection_type,
                confidence_score=d.confidence_score,
                risk_level=d.risk_level,
                frame_timestamp=d.frame_timestamp,
                object_class=d.object_class,
                is_verified=d.is_verified,
                is_false_positive=d.is_false_positive
            )
            for d in detections
        ]
    
    async def get_detection_by_id(self, detection_id: int) -> Optional[Detection]:
        """Obter detecção por ID"""
        return self.db.query(Detection).filter(Detection.id == detection_id).first()
    
    async def create_detection(self, detection_data: DetectionCreate) -> Detection:
        """Criar nova detecção"""
        # Verificar se a câmera existe
        camera = self.db.query(Camera).filter(Camera.id == detection_data.camera_id).first()
        if not camera:
            raise ValidationException("Câmera não encontrada")
        
        # Criar nova detecção
        detection = Detection(**detection_data.dict())
        self.db.add(detection)
        self.db.commit()
        self.db.refresh(detection)
        
        logger.info(f"Detecção criada: {detection.detection_type} (ID: {detection.id})")
        return detection
    
    async def update_detection(
        self,
        detection_id: int,
        detection_data: DetectionUpdate
    ) -> Optional[Detection]:
        """Atualizar detecção"""
        detection = await self.get_detection_by_id(detection_id)
        if not detection:
            return None
        
        # Atualizar campos
        update_data = detection_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(detection, field, value)
        
        detection.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(detection)
        
        logger.info(f"Detecção atualizada: {detection.id}")
        return detection
    
    async def delete_detection(self, detection_id: int) -> bool:
        """Deletar detecção"""
        detection = await self.get_detection_by_id(detection_id)
        if not detection:
            return False
        
        self.db.delete(detection)
        self.db.commit()
        
        logger.info(f"Detecção deletada: {detection.id}")
        return True
    
    async def verify_detection(
        self,
        detection_id: int,
        is_false_positive: bool,
        notes: Optional[str] = None
    ) -> Optional[Detection]:
        """Verificar detecção"""
        detection = await self.get_detection_by_id(detection_id)
        if not detection:
            return None
        
        detection.is_verified = True
        detection.is_false_positive = is_false_positive
        detection.verification_notes = notes
        detection.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(detection)
        
        logger.info(f"Detecção verificada: {detection.id} (FP: {is_false_positive})")
        return detection
    
    async def get_detection_image(self, detection_id: int) -> Optional[Dict[str, Any]]:
        """Obter imagem da detecção"""
        detection = await self.get_detection_by_id(detection_id)
        if not detection or not detection.image_path:
            return None
        
        try:
            # Implementar lógica para obter imagem do storage
            # Por enquanto, retornar dados mock
            return {
                "image_path": detection.image_path,
                "image_url": f"/api/v1/detections/{detection_id}/image",
                "bounding_box": detection.bounding_box,
                "center_point": detection.center_point
            }
        except Exception as e:
            logger.error(f"Erro ao obter imagem da detecção {detection_id}: {e}")
            return None
    
    async def get_detection_stats(
        self,
        camera_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> DetectionStats:
        """Obter estatísticas de detecções"""
        query = self.db.query(Detection)
        
        if camera_id:
            query = query.filter(Detection.camera_id == camera_id)
        
        if start_date:
            query = query.filter(Detection.frame_timestamp >= start_date)
        
        if end_date:
            query = query.filter(Detection.frame_timestamp <= end_date)
        
        # Estatísticas básicas
        total_detections = query.count()
        verified_detections = query.filter(Detection.is_verified == True).count()
        false_positives = query.filter(Detection.is_false_positive == True).count()
        
        # Taxa de precisão
        accuracy_rate = 0.0
        if verified_detections > 0:
            accuracy_rate = (verified_detections - false_positives) / verified_detections
        
        # Detecções por tipo
        detections_by_type = {}
        type_counts = query.with_entities(
            Detection.detection_type,
            func.count(Detection.id)
        ).group_by(Detection.detection_type).all()
        
        for detection_type, count in type_counts:
            detections_by_type[detection_type] = count
        
        # Detecções por nível de risco
        detections_by_risk_level = {}
        risk_counts = query.with_entities(
            Detection.risk_level,
            func.count(Detection.id)
        ).group_by(Detection.risk_level).all()
        
        for risk_level, count in risk_counts:
            detections_by_risk_level[risk_level] = count
        
        # Confiança média
        avg_confidence = query.with_entities(
            func.avg(Detection.confidence_score)
        ).scalar() or 0.0
        
        # Detecções nas últimas 24h
        last_24h = datetime.utcnow() - timedelta(hours=24)
        detections_last_24h = query.filter(
            Detection.frame_timestamp >= last_24h
        ).count()
        
        # Detecções na última semana
        last_7d = datetime.utcnow() - timedelta(days=7)
        detections_last_7d = query.filter(
            Detection.frame_timestamp >= last_7d
        ).count()
        
        return DetectionStats(
            total_detections=total_detections,
            verified_detections=verified_detections,
            false_positives=false_positives,
            accuracy_rate=accuracy_rate,
            detections_by_type=detections_by_risk_level,
            detections_by_risk_level=detections_by_risk_level,
            average_confidence=float(avg_confidence),
            detections_last_24h=detections_last_24h,
            detections_last_7d=detections_last_7d
        )
    
    async def get_recent_detections(
        self,
        camera_id: Optional[int] = None,
        limit: int = 10
    ) -> List[Detection]:
        """Obter detecções recentes"""
        query = self.db.query(Detection)
        
        if camera_id:
            query = query.filter(Detection.camera_id == camera_id)
        
        return query.order_by(desc(Detection.frame_timestamp)).limit(limit).all()
    
    async def get_detections_by_time_range(
        self,
        start_date: datetime,
        end_date: datetime,
        camera_id: Optional[int] = None
    ) -> List[Detection]:
        """Obter detecções por intervalo de tempo"""
        query = self.db.query(Detection).filter(
            and_(
                Detection.frame_timestamp >= start_date,
                Detection.frame_timestamp <= end_date
            )
        )
        
        if camera_id:
            query = query.filter(Detection.camera_id == camera_id)
        
        return query.order_by(desc(Detection.frame_timestamp)).all()
