"""
Processador de vídeo para captura e processamento de streams
"""

import cv2
import numpy as np
import asyncio
import logging
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
import threading
import queue
import time
from collections import deque

from app.core.config import settings

logger = logging.getLogger(__name__)


class VideoProcessor:
    """Processador de vídeo para captura e processamento"""
    
    def __init__(self):
        self.cameras: Dict[int, Dict[str, Any]] = {}
        self.active_streams: Dict[int, cv2.VideoCapture] = {}
        self.frame_buffers: Dict[int, deque] = {}
        self.processing_tasks: Dict[int, asyncio.Task] = {}
        self.frame_callbacks: Dict[int, List[Callable]] = {}
        
        # Configurações
        self.frame_rate = settings.VIDEO_FRAME_RATE
        self.buffer_size = settings.VIDEO_BUFFER_SIZE
        self.processing_interval = settings.PROCESSING_INTERVAL
        
        # Estatísticas
        self.total_frames_processed = 0
        self.total_processing_time = 0.0
        
        logger.info("VideoProcessor inicializado")
    
    async def add_camera(self, camera_id: int, stream_url: str, **kwargs) -> bool:
        """Adicionar câmera para processamento"""
        try:
            # Configurações da câmera
            camera_config = {
                "id": camera_id,
                "stream_url": stream_url,
                "frame_rate": kwargs.get("frame_rate", self.frame_rate),
                "resolution": kwargs.get("resolution", settings.VIDEO_RESOLUTION),
                "enabled": kwargs.get("enabled", True),
                "last_frame_time": None,
                "frame_count": 0,
                "error_count": 0,
                **kwargs
            }
            
            self.cameras[camera_id] = camera_config
            
            # Inicializar buffer de frames
            self.frame_buffers[camera_id] = deque(maxlen=self.buffer_size)
            
            # Inicializar callbacks
            self.frame_callbacks[camera_id] = []
            
            logger.info(f"Câmera {camera_id} adicionada: {stream_url}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao adicionar câmera {camera_id}: {e}")
            return False
    
    async def remove_camera(self, camera_id: int) -> bool:
        """Remover câmera do processamento"""
        try:
            # Parar stream se estiver ativo
            await self.stop_camera_stream(camera_id)
            
            # Remover das estruturas de dados
            if camera_id in self.cameras:
                del self.cameras[camera_id]
            
            if camera_id in self.frame_buffers:
                del self.frame_buffers[camera_id]
            
            if camera_id in self.frame_callbacks:
                del self.frame_callbacks[camera_id]
            
            logger.info(f"Câmera {camera_id} removida")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao remover câmera {camera_id}: {e}")
            return False
    
    async def start_camera_stream(self, camera_id: int) -> bool:
        """Iniciar stream da câmera"""
        try:
            if camera_id not in self.cameras:
                logger.error(f"Câmera {camera_id} não encontrada")
                return False
            
            camera_config = self.cameras[camera_id]
            
            if not camera_config["enabled"]:
                logger.info(f"Câmera {camera_id} está desabilitada")
                return False
            
            # Criar VideoCapture
            cap = cv2.VideoCapture(camera_config["stream_url"])
            
            if not cap.isOpened():
                logger.error(f"Não foi possível abrir stream da câmera {camera_id}")
                return False
            
            # Configurar propriedades
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, self._parse_resolution(camera_config["resolution"])[0])
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self._parse_resolution(camera_config["resolution"])[1])
            cap.set(cv2.CAP_PROP_FPS, camera_config["frame_rate"])
            
            self.active_streams[camera_id] = cap
            
            # Iniciar tarefa de processamento
            task = asyncio.create_task(self._process_camera_stream(camera_id))
            self.processing_tasks[camera_id] = task
            
            logger.info(f"Stream da câmera {camera_id} iniciado")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao iniciar stream da câmera {camera_id}: {e}")
            return False
    
    async def stop_camera_stream(self, camera_id: int) -> bool:
        """Parar stream da câmera"""
        try:
            # Cancelar tarefa de processamento
            if camera_id in self.processing_tasks:
                task = self.processing_tasks[camera_id]
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
                del self.processing_tasks[camera_id]
            
            # Liberar VideoCapture
            if camera_id in self.active_streams:
                cap = self.active_streams[camera_id]
                cap.release()
                del self.active_streams[camera_id]
            
            logger.info(f"Stream da câmera {camera_id} parado")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao parar stream da câmera {camera_id}: {e}")
            return False
    
    async def _process_camera_stream(self, camera_id: int):
        """Processar stream da câmera"""
        try:
            cap = self.active_streams[camera_id]
            camera_config = self.cameras[camera_id]
            
            logger.info(f"Iniciando processamento do stream da câmera {camera_id}")
            
            while True:
                start_time = time.time()
                
                # Capturar frame
                ret, frame = cap.read()
                
                if not ret:
                    logger.warning(f"Falha ao capturar frame da câmera {camera_id}")
                    camera_config["error_count"] += 1
                    
                    # Tentar reconectar após muitos erros
                    if camera_config["error_count"] > 10:
                        logger.error(f"Muitos erros na câmera {camera_id}, tentando reconectar...")
                        await self._reconnect_camera(camera_id)
                    
                    await asyncio.sleep(1)
                    continue
                
                # Resetar contador de erros
                camera_config["error_count"] = 0
                
                # Atualizar estatísticas
                camera_config["frame_count"] += 1
                camera_config["last_frame_time"] = datetime.utcnow()
                
                # Adicionar frame ao buffer
                self.frame_buffers[camera_id].append({
                    "frame": frame.copy(),
                    "timestamp": datetime.utcnow(),
                    "frame_number": camera_config["frame_count"]
                })
                
                # Chamar callbacks
                await self._call_frame_callbacks(camera_id, frame)
                
                # Controlar taxa de frames
                processing_time = time.time() - start_time
                sleep_time = max(0, self.processing_interval - processing_time)
                
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)
                
                self.total_frames_processed += 1
                self.total_processing_time += processing_time
                
        except asyncio.CancelledError:
            logger.info(f"Processamento da câmera {camera_id} cancelado")
        except Exception as e:
            logger.error(f"Erro no processamento da câmera {camera_id}: {e}")
    
    async def _reconnect_camera(self, camera_id: int):
        """Reconectar câmera"""
        try:
            logger.info(f"Tentando reconectar câmera {camera_id}")
            
            # Parar stream atual
            await self.stop_camera_stream(camera_id)
            
            # Aguardar um pouco
            await asyncio.sleep(5)
            
            # Tentar reconectar
            success = await self.start_camera_stream(camera_id)
            
            if success:
                logger.info(f"Câmera {camera_id} reconectada com sucesso")
            else:
                logger.error(f"Falha ao reconectar câmera {camera_id}")
                
        except Exception as e:
            logger.error(f"Erro ao reconectar câmera {camera_id}: {e}")
    
    async def _call_frame_callbacks(self, camera_id: int, frame: np.ndarray):
        """Chamar callbacks registrados para o frame"""
        try:
            if camera_id in self.frame_callbacks:
                for callback in self.frame_callbacks[camera_id]:
                    try:
                        await callback(camera_id, frame)
                    except Exception as e:
                        logger.error(f"Erro no callback da câmera {camera_id}: {e}")
                        
        except Exception as e:
            logger.error(f"Erro ao chamar callbacks da câmera {camera_id}: {e}")
    
    def add_frame_callback(self, camera_id: int, callback: Callable):
        """Adicionar callback para frames"""
        if camera_id not in self.frame_callbacks:
            self.frame_callbacks[camera_id] = []
        
        self.frame_callbacks[camera_id].append(callback)
        logger.info(f"Callback adicionado para câmera {camera_id}")
    
    def remove_frame_callback(self, camera_id: int, callback: Callable):
        """Remover callback para frames"""
        if camera_id in self.frame_callbacks and callback in self.frame_callbacks[camera_id]:
            self.frame_callbacks[camera_id].remove(callback)
            logger.info(f"Callback removido da câmera {camera_id}")
    
    async def get_latest_frame(self, camera_id: int) -> Optional[np.ndarray]:
        """Obter último frame da câmera"""
        try:
            if camera_id in self.frame_buffers and self.frame_buffers[camera_id]:
                latest_frame_data = self.frame_buffers[camera_id][-1]
                return latest_frame_data["frame"]
            return None
            
        except Exception as e:
            logger.error(f"Erro ao obter frame da câmera {camera_id}: {e}")
            return None
    
    async def get_frame_history(self, camera_id: int, count: int = 10) -> List[Dict[str, Any]]:
        """Obter histórico de frames da câmera"""
        try:
            if camera_id in self.frame_buffers:
                frames = list(self.frame_buffers[camera_id])
                return frames[-count:] if count > 0 else frames
            return []
            
        except Exception as e:
            logger.error(f"Erro ao obter histórico da câmera {camera_id}: {e}")
            return []
    
    async def capture_snapshot(self, camera_id: int) -> Optional[Dict[str, Any]]:
        """Capturar snapshot da câmera"""
        try:
            frame = await self.get_latest_frame(camera_id)
            if frame is not None:
                # Codificar frame como JPEG
                _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
                frame_bytes = buffer.tobytes()
                
                return {
                    "camera_id": camera_id,
                    "frame": frame_bytes,
                    "timestamp": datetime.utcnow().isoformat(),
                    "format": "jpeg"
                }
            return None
            
        except Exception as e:
            logger.error(f"Erro ao capturar snapshot da câmera {camera_id}: {e}")
            return None
    
    async def get_camera_status(self, camera_id: int) -> Dict[str, Any]:
        """Obter status da câmera"""
        try:
            if camera_id not in self.cameras:
                return {"error": "Câmera não encontrada"}
            
            camera_config = self.cameras[camera_id]
            is_streaming = camera_id in self.active_streams
            
            return {
                "camera_id": camera_id,
                "is_streaming": is_streaming,
                "enabled": camera_config["enabled"],
                "frame_count": camera_config["frame_count"],
                "error_count": camera_config["error_count"],
                "last_frame_time": camera_config["last_frame_time"].isoformat() if camera_config["last_frame_time"] else None,
                "buffer_size": len(self.frame_buffers.get(camera_id, [])),
                "stream_url": camera_config["stream_url"]
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter status da câmera {camera_id}: {e}")
            return {"error": str(e)}
    
    async def get_all_cameras_status(self) -> Dict[str, Any]:
        """Obter status de todas as câmeras"""
        try:
            status = {}
            for camera_id in self.cameras.keys():
                status[camera_id] = await self.get_camera_status(camera_id)
            
            return {
                "cameras": status,
                "total_cameras": len(self.cameras),
                "active_streams": len(self.active_streams),
                "total_frames_processed": self.total_frames_processed,
                "average_processing_time": self.total_processing_time / max(self.total_frames_processed, 1),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter status das câmeras: {e}")
            return {"error": str(e)}
    
    def _parse_resolution(self, resolution_str: str) -> tuple:
        """Parsear string de resolução para tupla"""
        try:
            width, height = map(int, resolution_str.split('x'))
            return (width, height)
        except:
            return (1920, 1080)  # Resolução padrão
    
    async def start_all_cameras(self):
        """Iniciar todas as câmeras habilitadas"""
        try:
            tasks = []
            for camera_id in self.cameras.keys():
                if self.cameras[camera_id]["enabled"]:
                    task = asyncio.create_task(self.start_camera_stream(camera_id))
                    tasks.append(task)
            
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
                logger.info(f"Iniciadas {len(tasks)} câmeras")
            
        except Exception as e:
            logger.error(f"Erro ao iniciar câmeras: {e}")
    
    async def stop_all_cameras(self):
        """Parar todas as câmeras"""
        try:
            tasks = []
            for camera_id in list(self.active_streams.keys()):
                task = asyncio.create_task(self.stop_camera_stream(camera_id))
                tasks.append(task)
            
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
                logger.info(f"Paradas {len(tasks)} câmeras")
            
        except Exception as e:
            logger.error(f"Erro ao parar câmeras: {e}")
    
    async def cleanup(self):
        """Limpeza de recursos"""
        try:
            await self.stop_all_cameras()
            logger.info("VideoProcessor limpo")
        except Exception as e:
            logger.error(f"Erro na limpeza do VideoProcessor: {e}")
