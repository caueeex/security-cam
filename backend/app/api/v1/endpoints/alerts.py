"""
Endpoints para gerenciamento de alertas
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import logging

from app.core.database import get_db
from app.schemas.alert import (
    Alert as AlertSchema,
    AlertCreate,
    AlertUpdate,
    AlertSummary,
    AlertStats,
    AlertFilter,
    AlertNotification
)
from app.services.alert_service import AlertService
from app.core.exceptions import NotFoundException, ValidationException

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/", response_model=List[AlertSummary])
async def get_alerts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    camera_id: Optional[int] = Query(None),
    alert_type: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db)
):
    """Listar alertas com filtros"""
    try:
        alert_service = AlertService(db)
        
        # Criar filtro
        filter_data = AlertFilter(
            camera_id=camera_id,
            alert_type=alert_type,
            priority=priority,
            status=status,
            start_date=start_date,
            end_date=end_date
        )
        
        alerts = await alert_service.get_alerts(
            skip=skip,
            limit=limit,
            filter_data=filter_data
        )
        return alerts
    except Exception as e:
        logger.error(f"Erro ao listar alertas: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )


@router.get("/{alert_id}", response_model=AlertSchema)
async def get_alert(
    alert_id: int,
    db: Session = Depends(get_db)
):
    """Obter alerta por ID"""
    try:
        alert_service = AlertService(db)
        alert = await alert_service.get_alert_by_id(alert_id)
        if not alert:
            raise NotFoundException(f"Alerta com ID {alert_id} não encontrado")
        return alert
    except NotFoundException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter alerta {alert_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )


@router.post("/", response_model=AlertSchema, status_code=status.HTTP_201_CREATED)
async def create_alert(
    alert_data: AlertCreate,
    db: Session = Depends(get_db)
):
    """Criar novo alerta"""
    try:
        alert_service = AlertService(db)
        alert = await alert_service.create_alert(alert_data)
        return alert
    except ValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Erro ao criar alerta: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )


@router.put("/{alert_id}", response_model=AlertSchema)
async def update_alert(
    alert_id: int,
    alert_data: AlertUpdate,
    db: Session = Depends(get_db)
):
    """Atualizar alerta"""
    try:
        alert_service = AlertService(db)
        alert = await alert_service.update_alert(alert_id, alert_data)
        if not alert:
            raise NotFoundException(f"Alerta com ID {alert_id} não encontrado")
        return alert
    except NotFoundException:
        raise
    except ValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Erro ao atualizar alerta {alert_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )


@router.delete("/{alert_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_alert(
    alert_id: int,
    db: Session = Depends(get_db)
):
    """Deletar alerta"""
    try:
        alert_service = AlertService(db)
        success = await alert_service.delete_alert(alert_id)
        if not success:
            raise NotFoundException(f"Alerta com ID {alert_id} não encontrado")
    except NotFoundException:
        raise
    except Exception as e:
        logger.error(f"Erro ao deletar alerta {alert_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )


@router.get("/stats/overview", response_model=AlertStats)
async def get_alert_stats(
    camera_id: Optional[int] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db)
):
    """Obter estatísticas de alertas"""
    try:
        alert_service = AlertService(db)
        stats = await alert_service.get_alert_stats(
            camera_id=camera_id,
            start_date=start_date,
            end_date=end_date
        )
        return stats
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas de alertas: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )


@router.post("/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: int,
    db: Session = Depends(get_db)
):
    """Reconhecer alerta"""
    try:
        alert_service = AlertService(db)
        alert = await alert_service.acknowledge_alert(alert_id)
        if not alert:
            raise NotFoundException(f"Alerta com ID {alert_id} não encontrado")
        return {"status": "success", "message": "Alerta reconhecido com sucesso"}
    except NotFoundException:
        raise
    except Exception as e:
        logger.error(f"Erro ao reconhecer alerta {alert_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )


@router.post("/{alert_id}/resolve")
async def resolve_alert(
    alert_id: int,
    resolution_notes: Optional[str] = Query(None),
    resolved_by: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Resolver alerta"""
    try:
        alert_service = AlertService(db)
        alert = await alert_service.resolve_alert(
            alert_id=alert_id,
            resolution_notes=resolution_notes,
            resolved_by=resolved_by
        )
        if not alert:
            raise NotFoundException(f"Alerta com ID {alert_id} não encontrado")
        return {"status": "success", "message": "Alerta resolvido com sucesso"}
    except NotFoundException:
        raise
    except Exception as e:
        logger.error(f"Erro ao resolver alerta {alert_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )


@router.get("/{alert_id}/notifications", response_model=List[AlertNotification])
async def get_alert_notifications(
    alert_id: int,
    db: Session = Depends(get_db)
):
    """Obter histórico de notificações do alerta"""
    try:
        alert_service = AlertService(db)
        notifications = await alert_service.get_alert_notifications(alert_id)
        if notifications is None:
            raise NotFoundException(f"Alerta com ID {alert_id} não encontrado")
        return notifications
    except NotFoundException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter notificações do alerta {alert_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )
