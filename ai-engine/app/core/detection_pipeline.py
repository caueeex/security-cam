"""
Pipeline de detecção que coordena todos os componentes de IA
"""

import asyncio
import logging
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
import numpy as np
import cv2
import base64
import io
from PIL import Image

from app.core.config import settings
from app.core.video_processor import VideoProcessor
from app.core.anomaly_detector import AnomalyDetector
from app.core.model_manager import ModelManager

logger = logging.getLogger(__name__)


class DetectionPipeline:
    """Pipeline principal de detecção de anomalias"""
    
    def __init__(self, video_processor: VideoProcessor, anomaly_detector: AnomalyDetector, 
                 redis_client, kafka_producer):
        self.video_processor = video_processor
        self.anomaly_detector = anomaly_detector
        self.redis_client = redis_client
        self.kafka_producer = kafka_producer
        
        # Estado do pipeline
        self.is_running = False
        self.processing_tasks: Dict[int, asyncio.Task] = {}
        
        # Estatísticas
        self.total_detections = 0
        self.total_anomalies = 0
        self.total_objects = 0
        
        # Configurações
        self.batch_size = settings.BATCH_SIZE
        self.processing_interval = settings.PROCESSING_INTERVAL
        
        logger.info("DetectionPipeline inicializado")
    
    async def start_processing(self):
        """Iniciar processamento do pipeline"""
        try:
            if self.is_running:
                logger.warning("Pipeline já está rodando")
                return
            
            self.is_running = True
            logger.info("Iniciando pipeline de detecção")
            
            # Registrar callbacks para frames
            await self._register_frame_callbacks()
            
            # Iniciar processamento de todas as câmeras
            await self.video_processor.start_all_cameras()
            
            logger.info("Pipeline de detecção iniciado com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao iniciar pipeline: {e}")
            self.is_running = False
            raise
    
    async def stop_processing(self):
        """Parar processamento do pipeline"""
        try:
            if not self.is_running:
                return
            
            self.is_running = False
            logger.info("Parando pipeline de detecção")
            
            # Cancelar todas as tarefas de processamento
            for task in self.processing_tasks.values():
                task.cancel()
            
            # Aguardar cancelamento
            if self.processing_tasks:
                await asyncio.gather(*self.processing_tasks.values(), return_exceptions=True)
            
            # Parar processamento de vídeo
            await self.video_processor.stop_all_cameras()
            
            logger.info("Pipeline de detecção parado")
            
        except Exception as e:
            logger.error(f"Erro ao parar pipeline: {e}")
    
    async def _register_frame_callbacks(self):
        """Registrar callbacks para processamento de frames"""
        try:
            # Obter lista de câmeras
            cameras_status = await self.video_processor.get_all_cameras_status()
            
            for camera_id in cameras_status.get("cameras", {}).keys():
                # Registrar callback para cada câmera
                self.video_processor.add_frame_callback(
                    camera_id, 
                    self._process_frame_callback
                )
                
                logger.info(f"Callback registrado para câmera {camera_id}")
                
        except Exception as e:
            logger.error(f"Erro ao registrar callbacks: {e}")
    
    async def _process_frame_callback(self, camera_id: int, frame: np.ndarray):
        """Callback para processamento de frames"""
        try:
            if not self.is_running:
                return
            
            # Criar tarefa assíncrona para processamento
            if camera_id not in self.processing_tasks:
                task = asyncio.create_task(self._process_camera_frames(camera_id))
                self.processing_tasks[camera_id] = task
            
        except Exception as e:
            logger.error(f"Erro no callback de frame da câmera {camera_id}: {e}")
    
    async def _process_camera_frames(self, camera_id: int):
        """Processar frames de uma câmera específica"""
        try:
            logger.info(f"Iniciando processamento de frames da câmera {camera_id}")
            
            while self.is_running:
                try:
                    # Obter último frame
                    frame = await self.video_processor.get_latest_frame(camera_id)
                    
                    if frame is None:
                        await asyncio.sleep(0.1)
                        continue
                    
                    # Processar frame
                    await self._process_single_frame(camera_id, frame)
                    
                    # Controlar taxa de processamento
                    await asyncio.sleep(self.processing_interval)
                    
                except Exception as e:
                    logger.error(f"Erro no processamento da câmera {camera_id}: {e}")
                    await asyncio.sleep(1)
            
        except asyncio.CancelledError:
            logger.info(f"Processamento da câmera {camera_id} cancelado")
        except Exception as e:
            logger.error(f"Erro no processamento da câmera {camera_id}: {e}")
        finally:
            # Remover tarefa da lista
            if camera_id in self.processing_tasks:
                del self.processing_tasks[camera_id]
    
    async def _process_single_frame(self, camera_id: int, frame: np.ndarray):
        """Processar um único frame"""
        try:
            start_time = datetime.utcnow()
            
            # 1. Detecção de objetos
            object_detections = await self._detect_objects(frame)
            
            # 2. Detecção de anomalias
            anomaly_result = await self.anomaly_detector.detect_anomaly(frame, camera_id)
            
            # 3. Detecção de faces
            face_detections = await self._detect_faces(frame)
            
            # 4. Análise de movimento
            motion_analysis = await self._analyze_motion(camera_id, frame)
            
            # 5. Combinar resultados
            detection_result = await self._combine_detection_results(
                camera_id, frame, object_detections, anomaly_result, 
                face_detections, motion_analysis
            )
            
            # 6. Processar resultado
            if detection_result["has_detection"]:
                await self._handle_detection(detection_result)
            
            # Atualizar estatísticas
            self._update_statistics(detection_result)
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Log de performance
            if processing_time > 0.1:  # Log se processamento demorou mais que 100ms
                logger.warning(f"Processamento lento da câmera {camera_id}: {processing_time:.3f}s")
            
        except Exception as e:
            logger.error(f"Erro no processamento do frame da câmera {camera_id}: {e}")
    
    async def _detect_objects(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """Detectar objetos no frame"""
        try:
            # Usar modelo YOLO do ModelManager
            if hasattr(self.anomaly_detector, 'model_manager'):
                detections = await self.anomaly_detector.model_manager.predict_objects(frame)
                return detections
            return []
            
        except Exception as e:
            logger.error(f"Erro na detecção de objetos: {e}")
            return []
    
    async def _detect_faces(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """Detectar faces no frame"""
        try:
            # Usar modelo de faces do ModelManager
            if hasattr(self.anomaly_detector, 'model_manager'):
                detections = await self.anomaly_detector.model_manager.detect_faces(frame)
                return detections
            return []
            
        except Exception as e:
            logger.error(f"Erro na detecção de faces: {e}")
            return []
    
    async def _analyze_motion(self, camera_id: int, frame: np.ndarray) -> Dict[str, Any]:
        """Analisar movimento no frame"""
        try:
            # Obter frame anterior
            frame_history = await self.video_processor.get_frame_history(camera_id, 2)
            
            if len(frame_history) < 2:
                return {"has_motion": False, "motion_score": 0.0}
            
            previous_frame = frame_history[0]["frame"]
            
            # Calcular diferença
            gray_current = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray_previous = cv2.cvtColor(previous_frame, cv2.COLOR_BGR2GRAY)
            
            diff = cv2.absdiff(gray_current, gray_previous)
            _, thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)
            
            # Calcular área de movimento
            motion_area = np.sum(thresh > 0)
            total_area = thresh.shape[0] * thresh.shape[1]
            motion_percentage = motion_area / total_area
            
            return {
                "has_motion": motion_percentage > 0.01,  # 1% de movimento
                "motion_score": motion_percentage,
                "motion_area": motion_area
            }
            
        except Exception as e:
            logger.error(f"Erro na análise de movimento: {e}")
            return {"has_motion": False, "motion_score": 0.0}
    
    async def _combine_detection_results(self, camera_id: int, frame: np.ndarray,
                                       object_detections: List[Dict[str, Any]],
                                       anomaly_result: Dict[str, Any],
                                       face_detections: List[Dict[str, Any]],
                                       motion_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Combinar resultados de todas as detecções"""
        try:
            # Determinar se há detecção significativa
            has_detection = (
                len(object_detections) > 0 or
                anomaly_result.get("is_anomaly", False) or
                len(face_detections) > 0 or
                motion_analysis.get("has_motion", False)
            )
            
            # Calcular score de confiança geral
            confidence_scores = []
            
            if object_detections:
                confidence_scores.extend([d.get("confidence", 0) for d in object_detections])
            
            if anomaly_result.get("is_anomaly"):
                confidence_scores.append(anomaly_result.get("confidence", 0))
            
            if face_detections:
                confidence_scores.extend([d.get("confidence", 0) for d in face_detections])
            
            if motion_analysis.get("has_motion"):
                confidence_scores.append(motion_analysis.get("motion_score", 0))
            
            overall_confidence = max(confidence_scores) if confidence_scores else 0.0
            
            # Determinar tipo de detecção
            detection_types = []
            if object_detections:
                detection_types.append("object")
            if anomaly_result.get("is_anomaly"):
                detection_types.append("anomaly")
            if face_detections:
                detection_types.append("face")
            if motion_analysis.get("has_motion"):
                detection_types.append("motion")
            
            # Determinar nível de risco
            risk_level = "low"
            if anomaly_result.get("is_anomaly") or len(object_detections) > 2:
                risk_level = "high"
            elif len(object_detections) > 0 or len(face_detections) > 0:
                risk_level = "medium"
            
            return {
                "camera_id": camera_id,
                "timestamp": datetime.utcnow().isoformat(),
                "has_detection": has_detection,
                "overall_confidence": overall_confidence,
                "detection_types": detection_types,
                "risk_level": risk_level,
                "object_detections": object_detections,
                "anomaly_result": anomaly_result,
                "face_detections": face_detections,
                "motion_analysis": motion_analysis,
                "frame_data": await self._encode_frame(frame)
            }
            
        except Exception as e:
            logger.error(f"Erro ao combinar resultados: {e}")
            return {
                "camera_id": camera_id,
                "timestamp": datetime.utcnow().isoformat(),
                "has_detection": False,
                "overall_confidence": 0.0,
                "detection_types": [],
                "risk_level": "low",
                "error": str(e)
            }
    
    async def _encode_frame(self, frame: np.ndarray) -> str:
        """Codificar frame como base64"""
        try:
            # Redimensionar frame para economizar espaço
            resized = cv2.resize(frame, (640, 480))
            
            # Codificar como JPEG
            _, buffer = cv2.imencode('.jpg', resized, [cv2.IMWRITE_JPEG_QUALITY, 85])
            
            # Converter para base64
            frame_base64 = base64.b64encode(buffer).decode('utf-8')
            
            return frame_base64
            
        except Exception as e:
            logger.error(f"Erro ao codificar frame: {e}")
            return ""
    
    async def _handle_detection(self, detection_result: Dict[str, Any]):
        """Processar resultado de detecção"""
        try:
            # Salvar no Redis para cache rápido
            await self._save_to_redis(detection_result)
            
            # Enviar para Kafka para processamento assíncrono
            await self._send_to_kafka(detection_result)
            
            # Log da detecção
            logger.info(f"Detecção na câmera {detection_result['camera_id']}: "
                       f"{detection_result['detection_types']} "
                       f"(confiança: {detection_result['overall_confidence']:.2f})")
            
        except Exception as e:
            logger.error(f"Erro ao processar detecção: {e}")
    
    async def _save_to_redis(self, detection_result: Dict[str, Any]):
        """Salvar detecção no Redis"""
        try:
            if self.redis_client:
                key = f"detection:{detection_result['camera_id']}:{detection_result['timestamp']}"
                await self.redis_client.setex(
                    key, 
                    3600,  # Expirar em 1 hora
                    json.dumps(detection_result)
                )
                
        except Exception as e:
            logger.error(f"Erro ao salvar no Redis: {e}")
    
    async def _send_to_kafka(self, detection_result: Dict[str, Any]):
        """Enviar detecção para Kafka"""
        try:
            if self.kafka_producer:
                topic = "detections"
                key = f"camera_{detection_result['camera_id']}"
                
                self.kafka_producer.send(topic, key=key, value=detection_result)
                
        except Exception as e:
            logger.error(f"Erro ao enviar para Kafka: {e}")
    
    def _update_statistics(self, detection_result: Dict[str, Any]):
        """Atualizar estatísticas"""
        try:
            self.total_detections += 1
            
            if detection_result.get("has_detection"):
                self.total_anomalies += 1
            
            if detection_result.get("object_detections"):
                self.total_objects += len(detection_result["object_detections"])
                
        except Exception as e:
            logger.error(f"Erro ao atualizar estatísticas: {e}")
    
    async def get_pipeline_status(self) -> Dict[str, Any]:
        """Obter status do pipeline"""
        try:
            return {
                "is_running": self.is_running,
                "total_detections": self.total_detections,
                "total_anomalies": self.total_anomalies,
                "total_objects": self.total_objects,
                "active_cameras": len(self.processing_tasks),
                "processing_tasks": list(self.processing_tasks.keys()),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter status do pipeline: {e}")
            return {"error": str(e)}
    
    async def add_camera(self, camera_id: int, stream_url: str, **kwargs) -> bool:
        """Adicionar câmera ao pipeline"""
        try:
            success = await self.video_processor.add_camera(camera_id, stream_url, **kwargs)
            
            if success and self.is_running:
                # Registrar callback se pipeline estiver rodando
                self.video_processor.add_frame_callback(
                    camera_id, 
                    self._process_frame_callback
                )
            
            return success
            
        except Exception as e:
            logger.error(f"Erro ao adicionar câmera {camera_id}: {e}")
            return False
    
    async def remove_camera(self, camera_id: int) -> bool:
        """Remover câmera do pipeline"""
        try:
            # Parar processamento da câmera
            if camera_id in self.processing_tasks:
                task = self.processing_tasks[camera_id]
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
                del self.processing_tasks[camera_id]
            
            # Remover do video processor
            success = await self.video_processor.remove_camera(camera_id)
            
            return success
            
        except Exception as e:
            logger.error(f"Erro ao remover câmera {camera_id}: {e}")
            return False
