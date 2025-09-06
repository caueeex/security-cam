"""
Sistema de Segurança Inteligente - AI Engine
Motor de IA para detecção de anomalias em vídeo em tempo real
"""

import asyncio
import logging
import signal
import sys
from contextlib import asynccontextmanager
from typing import Dict, Any, Optional
import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import redis.asyncio as redis
from kafka import KafkaProducer, KafkaConsumer
import json
from datetime import datetime

from app.core.config import settings
from app.core.detection_pipeline import DetectionPipeline
from app.core.model_manager import ModelManager
from app.core.video_processor import VideoProcessor
from app.core.anomaly_detector import AnomalyDetector
from app.core.websocket_client import WebSocketClient
from app.api.endpoints import detection, health, models

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/ai_engine.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Instâncias globais
detection_pipeline: Optional[DetectionPipeline] = None
model_manager: Optional[ModelManager] = None
video_processor: Optional[VideoProcessor] = None
anomaly_detector: Optional[AnomalyDetector] = None
websocket_client: Optional[WebSocketClient] = None
redis_client: Optional[redis.Redis] = None
kafka_producer: Optional[KafkaProducer] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerenciar ciclo de vida da aplicação"""
    global detection_pipeline, model_manager, video_processor, anomaly_detector
    global websocket_client, redis_client, kafka_producer
    
    # Startup
    logger.info("Iniciando AI Engine...")
    
    try:
        # Inicializar Redis
        redis_client = redis.from_url(settings.REDIS_URL)
        await redis_client.ping()
        logger.info("Redis conectado")
        
        # Inicializar Kafka Producer
        kafka_producer = KafkaProducer(
            bootstrap_servers=settings.KAFKA_BROKERS.split(','),
            value_serializer=lambda x: json.dumps(x).encode('utf-8'),
            key_serializer=lambda x: x.encode('utf-8') if x else None
        )
        logger.info("Kafka Producer conectado")
        
        # Inicializar componentes de IA
        model_manager = ModelManager()
        await model_manager.initialize()
        logger.info("Model Manager inicializado")
        
        video_processor = VideoProcessor()
        logger.info("Video Processor inicializado")
        
        anomaly_detector = AnomalyDetector(model_manager)
        await anomaly_detector.initialize()
        logger.info("Anomaly Detector inicializado")
        
        # Inicializar pipeline de detecção
        detection_pipeline = DetectionPipeline(
            video_processor=video_processor,
            anomaly_detector=anomaly_detector,
            redis_client=redis_client,
            kafka_producer=kafka_producer
        )
        logger.info("Detection Pipeline inicializado")
        
        # Inicializar WebSocket client
        websocket_client = WebSocketClient(settings.BACKEND_WS_URL)
        await websocket_client.connect()
        logger.info("WebSocket Client conectado")
        
        # Iniciar processamento em background
        asyncio.create_task(detection_pipeline.start_processing())
        logger.info("Processamento iniciado")
        
        logger.info("AI Engine iniciado com sucesso!")
        
    except Exception as e:
        logger.error(f"Erro ao inicializar AI Engine: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Finalizando AI Engine...")
    
    try:
        if detection_pipeline:
            await detection_pipeline.stop_processing()
        
        if websocket_client:
            await websocket_client.disconnect()
        
        if kafka_producer:
            kafka_producer.close()
        
        if redis_client:
            await redis_client.close()
        
        logger.info("AI Engine finalizado")
        
    except Exception as e:
        logger.error(f"Erro ao finalizar AI Engine: {e}")


def create_application() -> FastAPI:
    """Criar e configurar aplicação FastAPI"""
    
    app = FastAPI(
        title="AI Engine - Sistema de Segurança Inteligente",
        description="Motor de IA para detecção de anomalias em vídeo",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Incluir rotas
    app.include_router(health.router, prefix="/health", tags=["health"])
    app.include_router(detection.router, prefix="/detection", tags=["detection"])
    app.include_router(models.router, prefix="/models", tags=["models"])

    return app


# Criar instância da aplicação
app = create_application()


# Handlers de sinal para shutdown graceful
def signal_handler(signum, frame):
    """Handler para sinais de shutdown"""
    logger.info(f"Recebido sinal {signum}, iniciando shutdown...")
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=False,
        log_level="info"
    )
