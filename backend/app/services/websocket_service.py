"""
Serviço para gerenciamento de WebSocket
"""

from fastapi import WebSocket
from typing import Dict, List, Any
import json
import logging
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)


class WebSocketService:
    """Serviço para gerenciamento de conexões WebSocket"""
    
    def __init__(self):
        # Dicionário para armazenar conexões por canal
        self.active_connections: Dict[str, List[WebSocket]] = {
            "live_feed": [],
            "alerts": [],
            "detections": [],
            "camera_status": [],
            "dashboard": []
        }
        
        # Dicionário para armazenar informações dos clientes
        self.client_info: Dict[WebSocket, Dict[str, Any]] = {}
    
    async def connect(self, websocket: WebSocket, channel: str):
        """Conectar cliente ao canal WebSocket"""
        await websocket.accept()
        
        if channel in self.active_connections:
            self.active_connections[channel].append(websocket)
            
            # Armazenar informações do cliente
            self.client_info[websocket] = {
                "channel": channel,
                "connected_at": datetime.utcnow(),
                "last_ping": datetime.utcnow()
            }
            
            logger.info(f"Cliente conectado ao canal {channel}. Total: {len(self.active_connections[channel])}")
            
            # Enviar mensagem de boas-vindas
            await self.send_personal_message({
                "type": "connection_established",
                "channel": channel,
                "timestamp": datetime.utcnow().isoformat(),
                "message": "Conectado com sucesso"
            }, websocket)
        else:
            logger.error(f"Canal {channel} não existe")
            await websocket.close()
    
    async def disconnect(self, websocket: WebSocket, channel: str):
        """Desconectar cliente do canal WebSocket"""
        if channel in self.active_connections:
            if websocket in self.active_connections[channel]:
                self.active_connections[channel].remove(websocket)
                
                # Remover informações do cliente
                if websocket in self.client_info:
                    del self.client_info[websocket]
                
                logger.info(f"Cliente desconectado do canal {channel}. Total: {len(self.active_connections[channel])}")
    
    async def send_personal_message(self, message: Dict[str, Any], websocket: WebSocket):
        """Enviar mensagem para um cliente específico"""
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem pessoal: {e}")
    
    async def broadcast_to_channel(self, channel: str, message: Dict[str, Any]):
        """Broadcast mensagem para todos os clientes de um canal"""
        if channel not in self.active_connections:
            logger.error(f"Canal {channel} não existe")
            return
        
        # Preparar mensagem
        full_message = {
            **message,
            "timestamp": datetime.utcnow().isoformat(),
            "channel": channel
        }
        
        # Enviar para todos os clientes conectados
        disconnected_clients = []
        
        for websocket in self.active_connections[channel]:
            try:
                await websocket.send_text(json.dumps(full_message))
            except Exception as e:
                logger.error(f"Erro ao enviar mensagem para cliente: {e}")
                disconnected_clients.append(websocket)
        
        # Remover clientes desconectados
        for websocket in disconnected_clients:
            await self.disconnect(websocket, channel)
        
        logger.info(f"Mensagem enviada para {len(self.active_connections[channel])} clientes no canal {channel}")
    
    async def broadcast_to_all_channels(self, message: Dict[str, Any]):
        """Broadcast mensagem para todos os canais"""
        for channel in self.active_connections.keys():
            await self.broadcast_to_channel(channel, message)
    
    async def send_heartbeat(self):
        """Enviar heartbeat para todos os clientes"""
        heartbeat_message = {
            "type": "heartbeat",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await self.broadcast_to_all_channels(heartbeat_message)
    
    async def get_connection_stats(self) -> Dict[str, Any]:
        """Obter estatísticas das conexões"""
        stats = {
            "total_connections": sum(len(connections) for connections in self.active_connections.values()),
            "connections_by_channel": {
                channel: len(connections) 
                for channel, connections in self.active_connections.items()
            },
            "active_clients": len(self.client_info)
        }
        
        return stats
    
    async def cleanup_disconnected_clients(self):
        """Limpar clientes desconectados"""
        disconnected_clients = []
        
        for websocket, info in self.client_info.items():
            try:
                # Tentar enviar ping para verificar se ainda está conectado
                await websocket.ping()
            except Exception:
                disconnected_clients.append((websocket, info["channel"]))
        
        # Remover clientes desconectados
        for websocket, channel in disconnected_clients:
            await self.disconnect(websocket, channel)
        
        if disconnected_clients:
            logger.info(f"Removidos {len(disconnected_clients)} clientes desconectados")
    
    async def send_live_feed_frame(self, camera_id: int, frame_data: str, metadata: Dict[str, Any]):
        """Enviar frame de vídeo para o canal live_feed"""
        message = {
            "type": "video_frame",
            "camera_id": camera_id,
            "frame_data": frame_data,
            "metadata": metadata
        }
        
        await self.broadcast_to_channel("live_feed", message)
    
    async def send_new_alert(self, alert_data: Dict[str, Any]):
        """Enviar novo alerta para o canal alerts"""
        message = {
            "type": "new_alert",
            "data": alert_data
        }
        
        await self.broadcast_to_channel("alerts", message)
    
    async def send_new_detection(self, detection_data: Dict[str, Any]):
        """Enviar nova detecção para o canal detections"""
        message = {
            "type": "new_detection",
            "data": detection_data
        }
        
        await self.broadcast_to_channel("detections", message)
    
    async def send_camera_status_update(self, camera_id: int, status_data: Dict[str, Any]):
        """Enviar atualização de status da câmera"""
        message = {
            "type": "camera_status_update",
            "camera_id": camera_id,
            "data": status_data
        }
        
        await self.broadcast_to_channel("camera_status", message)
    
    async def send_dashboard_update(self, dashboard_data: Dict[str, Any]):
        """Enviar atualização do dashboard"""
        message = {
            "type": "dashboard_update",
            "data": dashboard_data
        }
        
        await self.broadcast_to_channel("dashboard", message)
    
    async def start_heartbeat_task(self):
        """Iniciar tarefa de heartbeat"""
        async def heartbeat_loop():
            while True:
                try:
                    await self.send_heartbeat()
                    await self.cleanup_disconnected_clients()
                    await asyncio.sleep(30)  # Heartbeat a cada 30 segundos
                except Exception as e:
                    logger.error(f"Erro no heartbeat: {e}")
                    await asyncio.sleep(30)
        
        # Executar heartbeat em background
        asyncio.create_task(heartbeat_loop())
