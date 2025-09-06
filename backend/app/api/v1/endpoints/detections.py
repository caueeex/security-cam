"""
Endpoints para gerenciamento de detecções
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import logging

from app.core.database import get_db
from app.schemas.detection import (
    Detection as DetectionSchema,
    DetectionCreate,
    DetectionUpdate,
    DetectionSummary,
    DetectionStats,
    DetectionFilter
)
from app.services.detection_service import DetectionService
from app.core.exceptions import NotFoundException, ValidationException

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/", response_model=List[DetectionSummary])
async def get_detections(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    camera_id: Optional[int] = Query(None),
    detection_type: Optional[str] = Query(None),
    risk_level: Optional[str] = Query(None),
    is_verified: Optional[bool] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db)
):
    """Listar detecções com filtros"""
    try:
        detection_service = DetectionService(db)
        
        # Criar filtro
        filter_data = DetectionFilter(
            camera_id=camera_id,
            detection_type=detection_type,
            risk_level=risk_level,
            is_verified=is_verified,
            start_date=start_date,
            end_date=end_date
        )
        
        detections = await detection_service.get_detections(
            skip=skip,
            limit=limit,
            filter_data=filter_data
        )
        return detections
    except Exception as e:
        logger.error(f"Erro ao listar detecções: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )


@router.get("/{detection_id}", response_model=DetectionSchema)
async def get_detection(
    detection_id: int,
    db: Session = Depends(get_db)
):
    """Obter detecção por ID"""
    try:
        detection_service = DetectionService(db)
        detection = await detection_service.get_detection_by_id(detection_id)
        if not detection:
            raise NotFoundException(f"Detecção com ID {detection_id} não encontrada")
        return detection
    except NotFoundException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter detecção {detection_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )


@router.post("/", response_model=DetectionSchema, status_code=status.HTTP_201_CREATED)
async def create_detection(
    detection_data: DetectionCreate,
    db: Session = Depends(get_db)
):
    """Criar nova detecção"""
    try:
        detection_service = DetectionService(db)
        detection = await detection_service.create_detection(detection_data)
        return detection
    except ValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Erro ao criar detecção: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )


@router.put("/{detection_id}", response_model=DetectionSchema)
async def update_detection(
    detection_id: int,
    detection_data: DetectionUpdate,
    db: Session = Depends(get_db)
):
    """Atualizar detecção"""
    try:
        detection_service = DetectionService(db)
        detection = await detection_service.update_detection(detection_id, detection_data)
        if not detection:
            raise NotFoundException(f"Detecção com ID {detection_id} não encontrada")
        return detection
    except NotFoundException:
        raise
    except ValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Erro ao atualizar detecção {detection_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )


@router.delete("/{detection_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_detection(
    detection_id: int,
    db: Session = Depends(get_db)
):
    """Deletar detecção"""
    try:
        detection_service = DetectionService(db)
        success = await detection_service.delete_detection(detection_id)
        if not success:
            raise NotFoundException(f"Detecção com ID {detection_id} não encontrada")
    except NotFoundException:
        raise
    except Exception as e:
        logger.error(f"Erro ao deletar detecção {detection_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )


@router.get("/stats/overview", response_model=DetectionStats)
async def get_detection_stats(
    camera_id: Optional[int] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db)
):
    """Obter estatísticas de detecções"""
    try:
        detection_service = DetectionService(db)
        stats = await detection_service.get_detection_stats(
            camera_id=camera_id,
            start_date=start_date,
            end_date=end_date
        )
        return stats
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas de detecções: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )


@router.post("/{detection_id}/verify")
async def verify_detection(
    detection_id: int,
    is_false_positive: bool = Query(False),
    notes: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Verificar detecção (marcar como verdadeira ou falso positivo)"""
    try:
        detection_service = DetectionService(db)
        detection = await detection_service.verify_detection(
            detection_id=detection_id,
            is_false_positive=is_false_positive,
            notes=notes
        )
        if not detection:
            raise NotFoundException(f"Detecção com ID {detection_id} não encontrada")
        return {"status": "success", "message": "Detecção verificada com sucesso"}
    except NotFoundException:
        raise
    except Exception as e:
        logger.error(f"Erro ao verificar detecção {detection_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )


@router.get("/{detection_id}/image")
async def get_detection_image(
    detection_id: int,
    db: Session = Depends(get_db)
):
    """Obter imagem da detecção"""
    try:
        detection_service = DetectionService(db)
        image_data = await detection_service.get_detection_image(detection_id)
        if not image_data:
            raise NotFoundException(f"Imagem da detecção {detection_id} não encontrada")
        return image_data
    except NotFoundException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter imagem da detecção {detection_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )
