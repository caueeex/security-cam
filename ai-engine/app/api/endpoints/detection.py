"""
Endpoints para detecção de anomalias
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from typing import Dict, Any, Optional, List
import logging
import json
import asyncio
from datetime import datetime
import io
import base64
from PIL import Image
import numpy as np
import cv2

from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/process-frame")
async def process_frame(
    camera_id: int,
    frame_data: str,  # Base64 encoded image
    background_tasks: BackgroundTasks
) -> Dict[str, Any]:
    """Processar um frame individual"""
    try:
        # Decodificar frame
        frame = await _decode_base64_frame(frame_data)
        
        if frame is None:
            raise HTTPException(status_code=400, detail="Frame inválido")
        
        # Processar frame (simulado - em produção seria com os modelos reais)
        result = await _process_single_frame(camera_id, frame)
        
        # Adicionar tarefa em background para salvar resultado
        background_tasks.add_task(_save_detection_result, result)
        
        return result
        
    except Exception as e:
        logger.error(f"Erro ao processar frame: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/process-video-stream")
async def process_video_stream(
    camera_id: int,
    stream_url: str,
    duration: Optional[int] = None  # segundos
) -> Dict[str, Any]:
    """Processar stream de vídeo"""
    try:
        # Simular processamento de stream
        result = {
            "camera_id": camera_id,
            "stream_url": stream_url,
            "status": "processing",
            "start_time": datetime.utcnow().isoformat(),
            "duration": duration,
            "detections": []
        }
        
        # Em produção, aqui seria iniciado o processamento real do stream
        logger.info(f"Iniciando processamento do stream da câmera {camera_id}")
        
        return result
        
    except Exception as e:
        logger.error(f"Erro ao processar stream: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/detections/{camera_id}")
async def get_detections(
    camera_id: int,
    limit: int = 10,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None
) -> Dict[str, Any]:
    """Obter detecções de uma câmera"""
    try:
        # Simular dados de detecção
        detections = await _get_simulated_detections(camera_id, limit)
        
        return {
            "camera_id": camera_id,
            "detections": detections,
            "count": len(detections),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erro ao obter detecções: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/detections/{camera_id}/latest")
async def get_latest_detection(camera_id: int) -> Dict[str, Any]:
    """Obter última detecção de uma câmera"""
    try:
        # Simular última detecção
        detection = await _get_simulated_latest_detection(camera_id)
        
        return detection
        
    except Exception as e:
        logger.error(f"Erro ao obter última detecção: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/detections/{detection_id}/verify")
async def verify_detection(
    detection_id: int,
    is_false_positive: bool,
    notes: Optional[str] = None
) -> Dict[str, Any]:
    """Verificar detecção (marcar como verdadeira ou falso positivo)"""
    try:
        # Simular verificação
        result = {
            "detection_id": detection_id,
            "verified": True,
            "is_false_positive": is_false_positive,
            "notes": notes,
            "verified_at": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Detecção {detection_id} verificada: FP={is_false_positive}")
        
        return result
        
    except Exception as e:
        logger.error(f"Erro ao verificar detecção: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_detection_stats() -> Dict[str, Any]:
    """Obter estatísticas de detecção"""
    try:
        # Simular estatísticas
        stats = {
            "total_detections": 1250,
            "total_anomalies": 45,
            "total_objects": 3200,
            "false_positives": 12,
            "accuracy_rate": 0.94,
            "detections_by_type": {
                "person": 800,
                "vehicle": 450,
                "animal": 120,
                "anomaly": 45
            },
            "detections_by_camera": {
                "1": 450,
                "2": 380,
                "3": 420
            },
            "last_24h": {
                "detections": 156,
                "anomalies": 8,
                "false_positives": 2
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return stats
        
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/camera/{camera_id}/status")
async def get_camera_status(camera_id: int) -> Dict[str, Any]:
    """Obter status de processamento de uma câmera"""
    try:
        # Simular status da câmera
        status = {
            "camera_id": camera_id,
            "is_processing": True,
            "frames_processed": 15420,
            "detections_found": 156,
            "last_detection": datetime.utcnow().isoformat(),
            "processing_rate": 30.0,  # FPS
            "error_count": 0,
            "uptime": "2h 15m 30s"
        }
        
        return status
        
    except Exception as e:
        logger.error(f"Erro ao obter status da câmera: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/camera/{camera_id}/start")
async def start_camera_processing(camera_id: int) -> Dict[str, Any]:
    """Iniciar processamento de uma câmera"""
    try:
        # Simular início de processamento
        result = {
            "camera_id": camera_id,
            "status": "started",
            "started_at": datetime.utcnow().isoformat(),
            "message": f"Processamento da câmera {camera_id} iniciado"
        }
        
        logger.info(f"Processamento da câmera {camera_id} iniciado")
        
        return result
        
    except Exception as e:
        logger.error(f"Erro ao iniciar processamento da câmera: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/camera/{camera_id}/stop")
async def stop_camera_processing(camera_id: int) -> Dict[str, Any]:
    """Parar processamento de uma câmera"""
    try:
        # Simular parada de processamento
        result = {
            "camera_id": camera_id,
            "status": "stopped",
            "stopped_at": datetime.utcnow().isoformat(),
            "message": f"Processamento da câmera {camera_id} parado"
        }
        
        logger.info(f"Processamento da câmera {camera_id} parado")
        
        return result
        
    except Exception as e:
        logger.error(f"Erro ao parar processamento da câmera: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Funções auxiliares

async def _decode_base64_frame(frame_data: str) -> Optional[np.ndarray]:
    """Decodificar frame base64 para OpenCV"""
    try:
        # Remover prefixo data URL se presente
        if ',' in frame_data:
            frame_data = frame_data.split(',')[1]
        
        # Decodificar base64
        image_data = base64.b64decode(frame_data)
        
        # Converter para PIL Image
        pil_image = Image.open(io.BytesIO(image_data))
        
        # Converter para OpenCV
        frame = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        
        return frame
        
    except Exception as e:
        logger.error(f"Erro ao decodificar frame: {e}")
        return None


async def _process_single_frame(camera_id: int, frame: np.ndarray) -> Dict[str, Any]:
    """Processar um frame individual"""
    try:
        # Simular processamento de IA
        # Em produção, aqui seria usado o pipeline real de detecção
        
        # Detecção simulada
        detections = []
        
        # Simular detecção de pessoa
        if np.random.random() > 0.7:  # 30% de chance de detectar algo
            detections.append({
                "class": "person",
                "confidence": 0.85,
                "bounding_box": {
                    "x": 100,
                    "y": 150,
                    "width": 200,
                    "height": 300
                },
                "center_point": {
                    "x": 200,
                    "y": 300
                }
            })
        
        # Simular detecção de anomalia
        anomaly_score = np.random.random()
        is_anomaly = anomaly_score > settings.ANOMALY_THRESHOLD
        
        result = {
            "camera_id": camera_id,
            "timestamp": datetime.utcnow().isoformat(),
            "has_detection": len(detections) > 0 or is_anomaly,
            "detections": detections,
            "anomaly": {
                "is_anomaly": is_anomaly,
                "score": anomaly_score,
                "confidence": anomaly_score
            },
            "processing_time_ms": np.random.randint(50, 200),
            "frame_size": {
                "width": frame.shape[1],
                "height": frame.shape[0]
            }
        }
        
        return result
        
    except Exception as e:
        logger.error(f"Erro no processamento do frame: {e}")
        return {
            "camera_id": camera_id,
            "timestamp": datetime.utcnow().isoformat(),
            "has_detection": False,
            "error": str(e)
        }


async def _save_detection_result(result: Dict[str, Any]):
    """Salvar resultado de detecção em background"""
    try:
        # Em produção, aqui seria salvo no banco de dados ou cache
        logger.info(f"Resultado de detecção salvo: {result['camera_id']}")
        
    except Exception as e:
        logger.error(f"Erro ao salvar resultado: {e}")


async def _get_simulated_detections(camera_id: int, limit: int) -> List[Dict[str, Any]]:
    """Obter detecções simuladas"""
    detections = []
    
    for i in range(min(limit, 5)):  # Máximo 5 detecções simuladas
        detection = {
            "id": f"{camera_id}_{i}",
            "camera_id": camera_id,
            "timestamp": datetime.utcnow().isoformat(),
            "detection_type": np.random.choice(["person", "vehicle", "anomaly"]),
            "confidence": np.random.uniform(0.7, 0.95),
            "bounding_box": {
                "x": np.random.randint(0, 500),
                "y": np.random.randint(0, 400),
                "width": np.random.randint(50, 200),
                "height": np.random.randint(50, 200)
            },
            "is_verified": np.random.choice([True, False]),
            "is_false_positive": np.random.choice([True, False], p=[0.1, 0.9])
        }
        detections.append(detection)
    
    return detections


async def _get_simulated_latest_detection(camera_id: int) -> Dict[str, Any]:
    """Obter última detecção simulada"""
    return {
        "id": f"{camera_id}_latest",
        "camera_id": camera_id,
        "timestamp": datetime.utcnow().isoformat(),
        "detection_type": "person",
        "confidence": 0.92,
        "bounding_box": {
            "x": 150,
            "y": 200,
            "width": 180,
            "height": 250
        },
        "is_verified": False,
        "is_false_positive": False
    }
