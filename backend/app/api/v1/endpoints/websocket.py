"""
Endpoints para WebSocket - comunicação em tempo real
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from fastapi.websockets import WebSocketState
from typing import List, Dict, Any
import json
import logging
import asyncio
from datetime import datetime

from app.services.websocket_service import WebSocketService

logger = logging.getLogger(__name__)
router = APIRouter()

# Instância global do serviço WebSocket
websocket_service = WebSocketService()


@router.websocket("/live-feed")
async def websocket_live_feed(websocket: WebSocket):
    """WebSocket para feed de vídeo em tempo real"""
    await websocket_service.connect(websocket, "live_feed")
    
    try:
        while True:
            # Manter conexão viva
            await asyncio.sleep(1)
            
            # Verificar se a conexão ainda está ativa
            if websocket.client_state != WebSocketState.CONNECTED:
                break
                
    except WebSocketDisconnect:
        await websocket_service.disconnect(websocket, "live_feed")
    except Exception as e:
        logger.error(f"Erro no WebSocket live-feed: {e}")
        await websocket_service.disconnect(websocket, "live_feed")


@router.websocket("/alerts")
async def websocket_alerts(websocket: WebSocket):
    """WebSocket para alertas em tempo real"""
    await websocket_service.connect(websocket, "alerts")
    
    try:
        while True:
            # Manter conexão viva
            await asyncio.sleep(1)
            
            # Verificar se a conexão ainda está ativa
            if websocket.client_state != WebSocketState.CONNECTED:
                break
                
    except WebSocketDisconnect:
        await websocket_service.disconnect(websocket, "alerts")
    except Exception as e:
        logger.error(f"Erro no WebSocket alerts: {e}")
        await websocket_service.disconnect(websocket, "alerts")


@router.websocket("/detections")
async def websocket_detections(websocket: WebSocket):
    """WebSocket para detecções em tempo real"""
    await websocket_service.connect(websocket, "detections")
    
    try:
        while True:
            # Manter conexão viva
            await asyncio.sleep(1)
            
            # Verificar se a conexão ainda está ativa
            if websocket.client_state != WebSocketState.CONNECTED:
                break
                
    except WebSocketDisconnect:
        await websocket_service.disconnect(websocket, "detections")
    except Exception as e:
        logger.error(f"Erro no WebSocket detections: {e}")
        await websocket_service.disconnect(websocket, "detections")


@router.websocket("/camera-status")
async def websocket_camera_status(websocket: WebSocket):
    """WebSocket para status das câmeras em tempo real"""
    await websocket_service.connect(websocket, "camera_status")
    
    try:
        while True:
            # Manter conexão viva
            await asyncio.sleep(1)
            
            # Verificar se a conexão ainda está ativa
            if websocket.client_state != WebSocketState.CONNECTED:
                break
                
    except WebSocketDisconnect:
        await websocket_service.disconnect(websocket, "camera_status")
    except Exception as e:
        logger.error(f"Erro no WebSocket camera-status: {e}")
        await websocket_service.disconnect(websocket, "camera_status")


@router.websocket("/dashboard")
async def websocket_dashboard(websocket: WebSocket):
    """WebSocket para dados do dashboard em tempo real"""
    await websocket_service.connect(websocket, "dashboard")
    
    try:
        while True:
            # Manter conexão viva
            await asyncio.sleep(1)
            
            # Verificar se a conexão ainda está ativa
            if websocket.client_state != WebSocketState.CONNECTED:
                break
                
    except WebSocketDisconnect:
        await websocket_service.disconnect(websocket, "dashboard")
    except Exception as e:
        logger.error(f"Erro no WebSocket dashboard: {e}")
        await websocket_service.disconnect(websocket, "dashboard")


# Endpoints para enviar dados via WebSocket
@router.post("/broadcast/live-feed")
async def broadcast_live_feed_data(data: Dict[str, Any]):
    """Broadcast dados do feed de vídeo para todos os clientes conectados"""
    try:
        await websocket_service.broadcast_to_channel("live_feed", data)
        return {"status": "success", "message": "Dados enviados para live-feed"}
    except Exception as e:
        logger.error(f"Erro ao broadcast live-feed: {e}")
        return {"status": "error", "message": str(e)}


@router.post("/broadcast/alert")
async def broadcast_alert(alert_data: Dict[str, Any]):
    """Broadcast novo alerta para todos os clientes conectados"""
    try:
        await websocket_service.broadcast_to_channel("alerts", {
            "type": "new_alert",
            "data": alert_data,
            "timestamp": datetime.utcnow().isoformat()
        })
        return {"status": "success", "message": "Alerta enviado"}
    except Exception as e:
        logger.error(f"Erro ao broadcast alerta: {e}")
        return {"status": "error", "message": str(e)}


@router.post("/broadcast/detection")
async def broadcast_detection(detection_data: Dict[str, Any]):
    """Broadcast nova detecção para todos os clientes conectados"""
    try:
        await websocket_service.broadcast_to_channel("detections", {
            "type": "new_detection",
            "data": detection_data,
            "timestamp": datetime.utcnow().isoformat()
        })
        return {"status": "success", "message": "Detecção enviada"}
    except Exception as e:
        logger.error(f"Erro ao broadcast detecção: {e}")
        return {"status": "error", "message": str(e)}


@router.post("/broadcast/camera-status")
async def broadcast_camera_status(status_data: Dict[str, Any]):
    """Broadcast status da câmera para todos os clientes conectados"""
    try:
        await websocket_service.broadcast_to_channel("camera_status", {
            "type": "camera_status_update",
            "data": status_data,
            "timestamp": datetime.utcnow().isoformat()
        })
        return {"status": "success", "message": "Status da câmera enviado"}
    except Exception as e:
        logger.error(f"Erro ao broadcast status da câmera: {e}")
        return {"status": "error", "message": str(e)}
