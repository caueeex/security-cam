"""
Serviço para gerenciamento de alertas
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime, timedelta

from app.models.alert import Alert, AlertStatus, AlertPriority
from app.models.camera import Camera
from app.models.detection import Detection
from app.schemas.alert import (
    AlertCreate,
    AlertUpdate,
    AlertSummary,
    AlertStats,
    AlertFilter,
    AlertNotification
)
from app.core.exceptions import ValidationException, NotFoundException

logger = logging.getLogger(__name__)


class AlertService:
    """Serviço para operações com alertas"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def get_alerts(
        self,
        skip: int = 0,
        limit: int = 100,
        filter_data: Optional[AlertFilter] = None
    ) -> List[AlertSummary]:
        """Obter lista de alertas com filtros"""
        query = self.db.query(Alert)
        
        if filter_data:
            if filter_data.camera_id:
                query = query.filter(Alert.camera_id == filter_data.camera_id)
            
            if filter_data.alert_type:
                query = query.filter(Alert.alert_type == filter_data.alert_type)
            
            if filter_data.priority:
                query = query.filter(Alert.priority == filter_data.priority)
            
            if filter_data.status:
                query = query.filter(Alert.status == filter_data.status)
            
            if filter_data.start_date:
                query = query.filter(Alert.created_at >= filter_data.start_date)
            
            if filter_data.end_date:
                query = query.filter(Alert.created_at <= filter_data.end_date)
            
            if filter_data.location:
                query = query.filter(Alert.location.ilike(f"%{filter_data.location}%"))
        
        # Ordenar por data de criação mais recente
        query = query.order_by(desc(Alert.created_at))
        
        alerts = query.offset(skip).limit(limit).all()
        
        # Converter para AlertSummary
        return [
            AlertSummary(
                id=a.id,
                camera_id=a.camera_id,
                alert_type=a.alert_type,
                title=a.title,
                priority=a.priority,
                status=a.status,
                created_at=a.created_at,
                location=a.location
            )
            for a in alerts
        ]
    
    async def get_alert_by_id(self, alert_id: int) -> Optional[Alert]:
        """Obter alerta por ID"""
        return self.db.query(Alert).filter(Alert.id == alert_id).first()
    
    async def create_alert(self, alert_data: AlertCreate) -> Alert:
        """Criar novo alerta"""
        # Verificar se a câmera existe
        camera = self.db.query(Camera).filter(Camera.id == alert_data.camera_id).first()
        if not camera:
            raise ValidationException("Câmera não encontrada")
        
        # Verificar se a detecção existe (se fornecida)
        if alert_data.detection_id:
            detection = self.db.query(Detection).filter(
                Detection.id == alert_data.detection_id
            ).first()
            if not detection:
                raise ValidationException("Detecção não encontrada")
        
        # Criar novo alerta
        alert = Alert(**alert_data.dict())
        self.db.add(alert)
        self.db.commit()
        self.db.refresh(alert)
        
        logger.info(f"Alerta criado: {alert.title} (ID: {alert.id})")
        
        # Enviar notificações (implementar lógica de notificação)
        await self._send_alert_notifications(alert)
        
        return alert
    
    async def update_alert(
        self,
        alert_id: int,
        alert_data: AlertUpdate
    ) -> Optional[Alert]:
        """Atualizar alerta"""
        alert = await self.get_alert_by_id(alert_id)
        if not alert:
            return None
        
        # Atualizar campos
        update_data = alert_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(alert, field, value)
        
        # Se status foi alterado para resolved, definir resolved_at
        if alert_data.status == AlertStatus.RESOLVED and not alert.resolved_at:
            alert.resolved_at = datetime.utcnow()
        
        alert.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(alert)
        
        logger.info(f"Alerta atualizado: {alert.id}")
        return alert
    
    async def delete_alert(self, alert_id: int) -> bool:
        """Deletar alerta"""
        alert = await self.get_alert_by_id(alert_id)
        if not alert:
            return False
        
        self.db.delete(alert)
        self.db.commit()
        
        logger.info(f"Alerta deletado: {alert.id}")
        return True
    
    async def acknowledge_alert(self, alert_id: int) -> Optional[Alert]:
        """Reconhecer alerta"""
        alert = await self.get_alert_by_id(alert_id)
        if not alert:
            return None
        
        alert.status = AlertStatus.ACKNOWLEDGED
        alert.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(alert)
        
        logger.info(f"Alerta reconhecido: {alert.id}")
        return alert
    
    async def resolve_alert(
        self,
        alert_id: int,
        resolution_notes: Optional[str] = None,
        resolved_by: Optional[str] = None
    ) -> Optional[Alert]:
        """Resolver alerta"""
        alert = await self.get_alert_by_id(alert_id)
        if not alert:
            return None
        
        alert.status = AlertStatus.RESOLVED
        alert.resolved_at = datetime.utcnow()
        alert.resolved_by = resolved_by
        alert.resolution_notes = resolution_notes
        alert.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(alert)
        
        logger.info(f"Alerta resolvido: {alert.id}")
        return alert
    
    async def get_alert_stats(
        self,
        camera_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> AlertStats:
        """Obter estatísticas de alertas"""
        query = self.db.query(Alert)
        
        if camera_id:
            query = query.filter(Alert.camera_id == camera_id)
        
        if start_date:
            query = query.filter(Alert.created_at >= start_date)
        
        if end_date:
            query = query.filter(Alert.created_at <= end_date)
        
        # Estatísticas básicas
        total_alerts = query.count()
        pending_alerts = query.filter(Alert.status == AlertStatus.PENDING).count()
        resolved_alerts = query.filter(Alert.status == AlertStatus.RESOLVED).count()
        false_positive_alerts = query.filter(
            Alert.status == AlertStatus.FALSE_POSITIVE
        ).count()
        
        # Alertas por prioridade
        alerts_by_priority = {}
        priority_counts = query.with_entities(
            Alert.priority,
            func.count(Alert.id)
        ).group_by(Alert.priority).all()
        
        for priority, count in priority_counts:
            alerts_by_priority[priority.value] = count
        
        # Alertas por status
        alerts_by_status = {}
        status_counts = query.with_entities(
            Alert.status,
            func.count(Alert.id)
        ).group_by(Alert.status).all()
        
        for status, count in status_counts:
            alerts_by_status[status.value] = count
        
        # Alertas por tipo
        alerts_by_type = {}
        type_counts = query.with_entities(
            Alert.alert_type,
            func.count(Alert.id)
        ).group_by(Alert.alert_type).all()
        
        for alert_type, count in type_counts:
            alerts_by_type[alert_type] = count
        
        # Tempo médio de resolução
        resolved_query = query.filter(Alert.status == AlertStatus.RESOLVED)
        avg_resolution_time = None
        
        resolved_alerts_with_time = resolved_query.filter(
            Alert.resolved_at.isnot(None)
        ).all()
        
        if resolved_alerts_with_time:
            total_time = sum([
                (alert.resolved_at - alert.created_at).total_seconds()
                for alert in resolved_alerts_with_time
            ])
            avg_resolution_time = total_time / len(resolved_alerts_with_time) / 60  # em minutos
        
        # Alertas nas últimas 24h
        last_24h = datetime.utcnow() - timedelta(hours=24)
        alerts_last_24h = query.filter(Alert.created_at >= last_24h).count()
        
        # Alertas na última semana
        last_7d = datetime.utcnow() - timedelta(days=7)
        alerts_last_7d = query.filter(Alert.created_at >= last_7d).count()
        
        return AlertStats(
            total_alerts=total_alerts,
            pending_alerts=pending_alerts,
            resolved_alerts=resolved_alerts,
            false_positive_alerts=false_positive_alerts,
            alerts_by_priority=alerts_by_priority,
            alerts_by_status=alerts_by_status,
            alerts_by_type=alerts_by_type,
            average_resolution_time_minutes=avg_resolution_time,
            alerts_last_24h=alerts_last_24h,
            alerts_last_7d=alerts_last_7d
        )
    
    async def get_alert_notifications(self, alert_id: int) -> Optional[List[AlertNotification]]:
        """Obter histórico de notificações do alerta"""
        alert = await self.get_alert_by_id(alert_id)
        if not alert:
            return None
        
        # Implementar lógica para obter histórico de notificações
        # Por enquanto, retornar dados mock baseados no alerta
        notifications = []
        
        if alert.email_sent:
            notifications.append(AlertNotification(
                alert_id=alert.id,
                title=f"Email: {alert.title}",
                message=f"Alerta enviado por email",
                priority=alert.priority,
                image_url=alert.image_url,
                video_url=alert.video_url,
                location=alert.location,
                timestamp=alert.created_at
            ))
        
        if alert.sms_sent:
            notifications.append(AlertNotification(
                alert_id=alert.id,
                title=f"SMS: {alert.title}",
                message=f"Alerta enviado por SMS",
                priority=alert.priority,
                image_url=alert.image_url,
                video_url=alert.video_url,
                location=alert.location,
                timestamp=alert.created_at
            ))
        
        if alert.push_notification_sent:
            notifications.append(AlertNotification(
                alert_id=alert.id,
                title=f"Push: {alert.title}",
                message=f"Notificação push enviada",
                priority=alert.priority,
                image_url=alert.image_url,
                video_url=alert.video_url,
                location=alert.location,
                timestamp=alert.created_at
            ))
        
        return notifications
    
    async def _send_alert_notifications(self, alert: Alert):
        """Enviar notificações do alerta"""
        try:
            # Implementar lógica de envio de notificações
            # Email, SMS, Push notifications, etc.
            
            # Por enquanto, apenas log
            logger.info(f"Enviando notificações para alerta {alert.id}")
            
            # Simular envio de notificações
            alert.email_sent = True
            alert.push_notification_sent = True
            
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Erro ao enviar notificações do alerta {alert.id}: {e}")
    
    async def get_critical_alerts(self, limit: int = 10) -> List[Alert]:
        """Obter alertas críticos"""
        return self.db.query(Alert).filter(
            and_(
                Alert.priority == AlertPriority.CRITICAL,
                Alert.status == AlertStatus.PENDING
            )
        ).order_by(desc(Alert.created_at)).limit(limit).all()
    
    async def get_recent_alerts(
        self,
        camera_id: Optional[int] = None,
        limit: int = 10
    ) -> List[Alert]:
        """Obter alertas recentes"""
        query = self.db.query(Alert)
        
        if camera_id:
            query = query.filter(Alert.camera_id == camera_id)
        
        return query.order_by(desc(Alert.created_at)).limit(limit).all()
