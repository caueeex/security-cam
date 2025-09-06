"""
Endpoints para gerenciamento de câmeras
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from app.core.database import get_db
from app.models.camera import Camera
from app.schemas.camera import (
    Camera as CameraSchema,
    CameraCreate,
    CameraUpdate,
    CameraStatus,
    CameraStats
)
from app.services.camera_service import CameraService
from app.core.exceptions import NotFoundException, ValidationException

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/", response_model=List[CameraSchema])
async def get_cameras(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    active_only: bool = Query(False),
    db: Session = Depends(get_db)
):
    """Listar todas as câmeras"""
    try:
        camera_service = CameraService(db)
        cameras = await camera_service.get_cameras(
            skip=skip,
            limit=limit,
            active_only=active_only
        )
        return cameras
    except Exception as e:
        logger.error(f"Erro ao listar câmeras: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )


@router.get("/{camera_id}", response_model=CameraSchema)
async def get_camera(
    camera_id: int,
    db: Session = Depends(get_db)
):
    """Obter câmera por ID"""
    try:
        camera_service = CameraService(db)
        camera = await camera_service.get_camera_by_id(camera_id)
        if not camera:
            raise NotFoundException(f"Câmera com ID {camera_id} não encontrada")
        return camera
    except NotFoundException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter câmera {camera_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )


@router.post("/", response_model=CameraSchema, status_code=status.HTTP_201_CREATED)
async def create_camera(
    camera_data: CameraCreate,
    db: Session = Depends(get_db)
):
    """Criar nova câmera"""
    try:
        camera_service = CameraService(db)
        camera = await camera_service.create_camera(camera_data)
        return camera
    except ValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Erro ao criar câmera: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )


@router.put("/{camera_id}", response_model=CameraSchema)
async def update_camera(
    camera_id: int,
    camera_data: CameraUpdate,
    db: Session = Depends(get_db)
):
    """Atualizar câmera"""
    try:
        camera_service = CameraService(db)
        camera = await camera_service.update_camera(camera_id, camera_data)
        if not camera:
            raise NotFoundException(f"Câmera com ID {camera_id} não encontrada")
        return camera
    except NotFoundException:
        raise
    except ValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Erro ao atualizar câmera {camera_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )


@router.delete("/{camera_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_camera(
    camera_id: int,
    db: Session = Depends(get_db)
):
    """Deletar câmera"""
    try:
        camera_service = CameraService(db)
        success = await camera_service.delete_camera(camera_id)
        if not success:
            raise NotFoundException(f"Câmera com ID {camera_id} não encontrada")
    except NotFoundException:
        raise
    except Exception as e:
        logger.error(f"Erro ao deletar câmera {camera_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )


@router.get("/{camera_id}/status", response_model=CameraStatus)
async def get_camera_status(
    camera_id: int,
    db: Session = Depends(get_db)
):
    """Obter status da câmera"""
    try:
        camera_service = CameraService(db)
        status = await camera_service.get_camera_status(camera_id)
        if not status:
            raise NotFoundException(f"Câmera com ID {camera_id} não encontrada")
        return status
    except NotFoundException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter status da câmera {camera_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )


@router.get("/{camera_id}/stats", response_model=CameraStats)
async def get_camera_stats(
    camera_id: int,
    db: Session = Depends(get_db)
):
    """Obter estatísticas da câmera"""
    try:
        camera_service = CameraService(db)
        stats = await camera_service.get_camera_stats(camera_id)
        if not stats:
            raise NotFoundException(f"Câmera com ID {camera_id} não encontrada")
        return stats
    except NotFoundException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas da câmera {camera_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )


@router.post("/{camera_id}/test-connection")
async def test_camera_connection(
    camera_id: int,
    db: Session = Depends(get_db)
):
    """Testar conexão com a câmera"""
    try:
        camera_service = CameraService(db)
        result = await camera_service.test_camera_connection(camera_id)
        if not result:
            raise NotFoundException(f"Câmera com ID {camera_id} não encontrada")
        return {"status": "success", "message": "Conexão testada com sucesso"}
    except NotFoundException:
        raise
    except Exception as e:
        logger.error(f"Erro ao testar conexão da câmera {camera_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )
