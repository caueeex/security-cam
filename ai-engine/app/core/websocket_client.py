"""
Cliente WebSocket para comunicação com o backend
"""

import asyncio
import websockets
import json
import logging
from typing import Dict, Any, Optional, Callable
from datetime import datetime
import aiohttp

from app.core.config import settings

logger = logging.getLogger(__name__)


class WebSocketClient:
    """Cliente WebSocket para comunicação com o backend"""
    
    def __init__(self, backend_ws_url: str):
        self.backend_ws_url = backend_ws_url
        self.websocket = None
        self.is_connected = False
        self.reconnect_interval = 5  # segundos
        self.max_reconnect_attempts = 10
        self.reconnect_attempts = 0
        
        # Callbacks para diferentes tipos de mensagem
        self.message_callbacks: Dict[str, Callable] = {}
        
        # Tarefas em background
        self.heartbeat_task: Optional[asyncio.Task] = None
        self.reconnect_task: Optional[asyncio.Task] = None
        
        logger.info(f"WebSocketClient inicializado para {backend_ws_url}")
    
    async def connect(self) -> bool:
        """Conectar ao WebSocket do backend"""
        try:
            logger.info("Conectando ao WebSocket do backend...")
            
            self.websocket = await websockets.connect(
                self.backend_ws_url,
                ping_interval=30,
                ping_timeout=10,
                close_timeout=10
            )
            
            self.is_connected = True
            self.reconnect_attempts = 0
            
            # Iniciar heartbeat
            self.heartbeat_task = asyncio.create_task(self._heartbeat_loop())
            
            # Iniciar loop de recebimento de mensagens
            asyncio.create_task(self._message_loop())
            
            logger.info("Conectado ao WebSocket do backend")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao conectar ao WebSocket: {e}")
            self.is_connected = False
            return False
    
    async def disconnect(self):
        """Desconectar do WebSocket"""
        try:
            self.is_connected = False
            
            # Cancelar tarefas
            if self.heartbeat_task:
                self.heartbeat_task.cancel()
                try:
                    await self.heartbeat_task
                except asyncio.CancelledError:
                    pass
            
            if self.reconnect_task:
                self.reconnect_task.cancel()
                try:
                    await self.reconnect_task
                except asyncio.CancelledError:
                    pass
            
            # Fechar WebSocket
            if self.websocket:
                await self.websocket.close()
                self.websocket = None
            
            logger.info("Desconectado do WebSocket do backend")
            
        except Exception as e:
            logger.error(f"Erro ao desconectar: {e}")
    
    async def send_message(self, message: Dict[str, Any]) -> bool:
        """Enviar mensagem para o backend"""
        try:
            if not self.is_connected or not self.websocket:
                logger.warning("WebSocket não conectado, tentando reconectar...")
                await self._attempt_reconnect()
                return False
            
            message_str = json.dumps(message)
            await self.websocket.send(message_str)
            
            logger.debug(f"Mensagem enviada: {message.get('type', 'unknown')}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem: {e}")
            await self._handle_connection_error()
            return False
    
    async def send_detection_result(self, detection_data: Dict[str, Any]):
        """Enviar resultado de detecção"""
        try:
            message = {
                "type": "detection_result",
                "data": detection_data,
                "timestamp": datetime.utcnow().isoformat(),
                "source": "ai_engine"
            }
            
            await self.send_message(message)
            
        except Exception as e:
            logger.error(f"Erro ao enviar resultado de detecção: {e}")
    
    async def send_anomaly_alert(self, anomaly_data: Dict[str, Any]):
        """Enviar alerta de anomalia"""
        try:
            message = {
                "type": "anomaly_alert",
                "data": anomaly_data,
                "timestamp": datetime.utcnow().isoformat(),
                "source": "ai_engine"
            }
            
            await self.send_message(message)
            
        except Exception as e:
            logger.error(f"Erro ao enviar alerta de anomalia: {e}")
    
    async def send_model_status(self, model_data: Dict[str, Any]):
        """Enviar status dos modelos"""
        try:
            message = {
                "type": "model_status",
                "data": model_data,
                "timestamp": datetime.utcnow().isoformat(),
                "source": "ai_engine"
            }
            
            await self.send_message(message)
            
        except Exception as e:
            logger.error(f"Erro ao enviar status dos modelos: {e}")
    
    async def send_health_status(self, health_data: Dict[str, Any]):
        """Enviar status de saúde"""
        try:
            message = {
                "type": "health_status",
                "data": health_data,
                "timestamp": datetime.utcnow().isoformat(),
                "source": "ai_engine"
            }
            
            await self.send_message(message)
            
        except Exception as e:
            logger.error(f"Erro ao enviar status de saúde: {e}")
    
    def register_callback(self, message_type: str, callback: Callable):
        """Registrar callback para tipo de mensagem"""
        self.message_callbacks[message_type] = callback
        logger.info(f"Callback registrado para mensagens do tipo: {message_type}")
    
    async def _message_loop(self):
        """Loop para receber mensagens"""
        try:
            while self.is_connected and self.websocket:
                try:
                    message_str = await self.websocket.recv()
                    message = json.loads(message_str)
                    
                    await self._handle_message(message)
                    
                except websockets.exceptions.ConnectionClosed:
                    logger.warning("Conexão WebSocket fechada pelo servidor")
                    await self._handle_connection_error()
                    break
                    
                except Exception as e:
                    logger.error(f"Erro ao receber mensagem: {e}")
                    
        except asyncio.CancelledError:
            logger.info("Loop de mensagens cancelado")
        except Exception as e:
            logger.error(f"Erro no loop de mensagens: {e}")
    
    async def _handle_message(self, message: Dict[str, Any]):
        """Processar mensagem recebida"""
        try:
            message_type = message.get("type", "unknown")
            
            logger.debug(f"Mensagem recebida: {message_type}")
            
            # Chamar callback específico se registrado
            if message_type in self.message_callbacks:
                callback = self.message_callbacks[message_type]
                try:
                    await callback(message)
                except Exception as e:
                    logger.error(f"Erro no callback para {message_type}: {e}")
            
            # Processar tipos específicos de mensagem
            if message_type == "ping":
                await self._handle_ping(message)
            elif message_type == "config_update":
                await self._handle_config_update(message)
            elif message_type == "model_command":
                await self._handle_model_command(message)
            elif message_type == "camera_command":
                await self._handle_camera_command(message)
                
        except Exception as e:
            logger.error(f"Erro ao processar mensagem: {e}")
    
    async def _handle_ping(self, message: Dict[str, Any]):
        """Responder ao ping"""
        try:
            pong_message = {
                "type": "pong",
                "timestamp": datetime.utcnow().isoformat(),
                "source": "ai_engine"
            }
            
            await self.send_message(pong_message)
            
        except Exception as e:
            logger.error(f"Erro ao responder ping: {e}")
    
    async def _handle_config_update(self, message: Dict[str, Any]):
        """Processar atualização de configuração"""
        try:
            config_data = message.get("data", {})
            logger.info(f"Atualização de configuração recebida: {config_data}")
            
            # Aqui seria implementada a lógica para atualizar configurações
            # Por exemplo, thresholds de detecção, parâmetros de modelo, etc.
            
        except Exception as e:
            logger.error(f"Erro ao processar atualização de configuração: {e}")
    
    async def _handle_model_command(self, message: Dict[str, Any]):
        """Processar comando de modelo"""
        try:
            command_data = message.get("data", {})
            command = command_data.get("command")
            
            logger.info(f"Comando de modelo recebido: {command}")
            
            # Aqui seria implementada a lógica para comandos de modelo
            # Por exemplo, carregar/descarregar modelos, retreinar, etc.
            
        except Exception as e:
            logger.error(f"Erro ao processar comando de modelo: {e}")
    
    async def _handle_camera_command(self, message: Dict[str, Any]):
        """Processar comando de câmera"""
        try:
            command_data = message.get("data", {})
            command = command_data.get("command")
            camera_id = command_data.get("camera_id")
            
            logger.info(f"Comando de câmera recebido: {command} para câmera {camera_id}")
            
            # Aqui seria implementada a lógica para comandos de câmera
            # Por exemplo, iniciar/parar processamento, ajustar parâmetros, etc.
            
        except Exception as e:
            logger.error(f"Erro ao processar comando de câmera: {e}")
    
    async def _heartbeat_loop(self):
        """Loop de heartbeat"""
        try:
            while self.is_connected:
                try:
                    heartbeat_message = {
                        "type": "heartbeat",
                        "timestamp": datetime.utcnow().isoformat(),
                        "source": "ai_engine"
                    }
                    
                    await self.send_message(heartbeat_message)
                    
                    # Aguardar intervalo de heartbeat
                    await asyncio.sleep(30)  # Heartbeat a cada 30 segundos
                    
                except Exception as e:
                    logger.error(f"Erro no heartbeat: {e}")
                    await asyncio.sleep(30)
                    
        except asyncio.CancelledError:
            logger.info("Loop de heartbeat cancelado")
        except Exception as e:
            logger.error(f"Erro no loop de heartbeat: {e}")
    
    async def _handle_connection_error(self):
        """Lidar com erro de conexão"""
        try:
            self.is_connected = False
            
            if self.reconnect_attempts < self.max_reconnect_attempts:
                logger.info(f"Tentando reconectar... (tentativa {self.reconnect_attempts + 1})")
                
                self.reconnect_task = asyncio.create_task(self._attempt_reconnect())
            else:
                logger.error("Máximo de tentativas de reconexão atingido")
                
        except Exception as e:
            logger.error(f"Erro ao lidar com erro de conexão: {e}")
    
    async def _attempt_reconnect(self):
        """Tentar reconectar"""
        try:
            self.reconnect_attempts += 1
            
            # Aguardar antes de tentar reconectar
            await asyncio.sleep(self.reconnect_interval)
            
            # Tentar reconectar
            success = await self.connect()
            
            if success:
                logger.info("Reconexão bem-sucedida")
            else:
                logger.warning(f"Falha na reconexão (tentativa {self.reconnect_attempts})")
                
        except Exception as e:
            logger.error(f"Erro na tentativa de reconexão: {e}")
    
    async def get_connection_status(self) -> Dict[str, Any]:
        """Obter status da conexão"""
        return {
            "is_connected": self.is_connected,
            "backend_url": self.backend_ws_url,
            "reconnect_attempts": self.reconnect_attempts,
            "max_reconnect_attempts": self.max_reconnect_attempts,
            "registered_callbacks": list(self.message_callbacks.keys()),
            "timestamp": datetime.utcnow().isoformat()
        }
