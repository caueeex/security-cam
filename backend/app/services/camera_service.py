"""
Serviço para gerenciamento de câmeras
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
import logging
import cv2
import requests
from datetime import datetime

from app.models.camera import Camera
from app.schemas.camera import CameraCreate, CameraUpdate, CameraStatus, CameraStats
from app.core.exceptions import ValidationException, NotFoundException

logger = logging.getLogger(__name__)


class CameraService:
    """Serviço para operações com câmeras"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def get_cameras(
        self,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = False
    ) -> List[Camera]:
        """Obter lista de câmeras"""
        query = self.db.query(Camera)
        
        if active_only:
            query = query.filter(Camera.is_active == True)
        
        return query.offset(skip).limit(limit).all()
    
    async def get_camera_by_id(self, camera_id: int) -> Optional[Camera]:
        """Obter câmera por ID"""
        return self.db.query(Camera).filter(Camera.id == camera_id).first()
    
    async def create_camera(self, camera_data: CameraCreate) -> Camera:
        """Criar nova câmera"""
        # Verificar se IP já existe
        existing_camera = self.db.query(Camera).filter(
            Camera.ip_address == camera_data.ip_address
        ).first()
        
        if existing_camera:
            raise ValidationException("Câmera com este IP já existe")
        
        # Criar nova câmera
        camera = Camera(**camera_data.dict())
        self.db.add(camera)
        self.db.commit()
        self.db.refresh(camera)
        
        logger.info(f"Câmera criada: {camera.name} ({camera.ip_address})")
        return camera
    
    async def update_camera(
        self,
        camera_id: int,
        camera_data: CameraUpdate
    ) -> Optional[Camera]:
        """Atualizar câmera"""
        camera = await self.get_camera_by_id(camera_id)
        if not camera:
            return None
        
        # Verificar se novo IP já existe (se fornecido)
        if camera_data.ip_address and camera_data.ip_address != camera.ip_address:
            existing_camera = self.db.query(Camera).filter(
                and_(
                    Camera.ip_address == camera_data.ip_address,
                    Camera.id != camera_id
                )
            ).first()
            
            if existing_camera:
                raise ValidationException("Câmera com este IP já existe")
        
        # Atualizar campos
        update_data = camera_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(camera, field, value)
        
        camera.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(camera)
        
        logger.info(f"Câmera atualizada: {camera.name}")
        return camera
    
    async def delete_camera(self, camera_id: int) -> bool:
        """Deletar câmera"""
        camera = await self.get_camera_by_id(camera_id)
        if not camera:
            return False
        
        self.db.delete(camera)
        self.db.commit()
        
        logger.info(f"Câmera deletada: {camera.name}")
        return True
    
    async def get_camera_status(self, camera_id: int) -> Optional[CameraStatus]:
        """Obter status da câmera"""
        camera = await self.get_camera_by_id(camera_id)
        if not camera:
            return None
        
        return CameraStatus(
            id=camera.id,
            name=camera.name,
            is_online=camera.is_online,
            last_heartbeat=camera.last_heartbeat,
            last_error=camera.last_error,
            detection_enabled=camera.detection_enabled
        )
    
    async def get_camera_stats(self, camera_id: int) -> Optional[CameraStats]:
        """Obter estatísticas da câmera"""
        camera = await self.get_camera_by_id(camera_id)
        if not camera:
            return None
        
        # Calcular estatísticas (implementar consultas específicas)
        # Por enquanto, valores mock
        stats = CameraStats(
            id=camera.id,
            name=camera.name,
            total_detections=0,
            total_alerts=0,
            false_positives=0,
            accuracy_rate=0.0,
            uptime_percentage=100.0,
            last_detection=None
        )
        
        return stats
    
    async def test_camera_connection(self, camera_id: int) -> bool:
        """Testar conexão com a câmera"""
        camera = await self.get_camera_by_id(camera_id)
        if not camera:
            return False
        
        try:
            # Testar conexão HTTP/RTSP
            if camera.stream_url.startswith('rtsp://'):
                # Teste RTSP usando OpenCV
                cap = cv2.VideoCapture(camera.stream_url)
                if cap.isOpened():
                    ret, frame = cap.read()
                    cap.release()
                    if ret:
                        camera.is_online = True
                        camera.last_heartbeat = datetime.utcnow()
                        camera.last_error = None
                        self.db.commit()
                        return True
            else:
                # Teste HTTP
                response = requests.get(camera.stream_url, timeout=5)
                if response.status_code == 200:
                    camera.is_online = True
                    camera.last_heartbeat = datetime.utcnow()
                    camera.last_error = None
                    self.db.commit()
                    return True
            
            # Se chegou aqui, conexão falhou
            camera.is_online = False
            camera.last_error = "Falha na conexão"
            self.db.commit()
            return False
            
        except Exception as e:
            camera.is_online = False
            camera.last_error = str(e)
            self.db.commit()
            logger.error(f"Erro ao testar conexão da câmera {camera_id}: {e}")
            return False
    
    async def update_camera_heartbeat(self, camera_id: int) -> bool:
        """Atualizar heartbeat da câmera"""
        camera = await self.get_camera_by_id(camera_id)
        if not camera:
            return False
        
        camera.last_heartbeat = datetime.utcnow()
        camera.is_online = True
        camera.last_error = None
        
        self.db.commit()
        return True
    
    async def get_online_cameras(self) -> List[Camera]:
        """Obter câmeras online"""
        return self.db.query(Camera).filter(
            and_(
                Camera.is_active == True,
                Camera.is_online == True
            )
        ).all()
    
    async def get_cameras_by_location(self, location: str) -> List[Camera]:
        """Obter câmeras por localização"""
        return self.db.query(Camera).filter(
            and_(
                Camera.location.ilike(f"%{location}%"),
                Camera.is_active == True
            )
        ).all()
