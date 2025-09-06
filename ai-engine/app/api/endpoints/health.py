"""
Endpoints de health check para o AI Engine
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import logging
from datetime import datetime

from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/")
async def health_check() -> Dict[str, Any]:
    """Health check básico"""
    return {
        "status": "healthy",
        "service": "AI Engine",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/detailed")
async def detailed_health_check() -> Dict[str, Any]:
    """Health check detalhado"""
    try:
        # Verificar componentes principais
        health_status = {
            "status": "healthy",
            "service": "AI Engine",
            "version": settings.VERSION,
            "environment": settings.ENVIRONMENT,
            "timestamp": datetime.utcnow().isoformat(),
            "components": {}
        }
        
        # Verificar GPU
        try:
            import torch
            health_status["components"]["gpu"] = {
                "available": torch.cuda.is_available(),
                "device_count": torch.cuda.device_count() if torch.cuda.is_available() else 0,
                "current_device": torch.cuda.current_device() if torch.cuda.is_available() else None
            }
        except Exception as e:
            health_status["components"]["gpu"] = {"error": str(e)}
        
        # Verificar OpenCV
        try:
            import cv2
            health_status["components"]["opencv"] = {
                "version": cv2.__version__,
                "available": True
            }
        except Exception as e:
            health_status["components"]["opencv"] = {"error": str(e)}
        
        # Verificar PyTorch
        try:
            import torch
            health_status["components"]["pytorch"] = {
                "version": torch.__version__,
                "available": True
            }
        except Exception as e:
            health_status["components"]["pytorch"] = {"error": str(e)}
        
        # Verificar configurações
        health_status["components"]["config"] = {
            "gpu_enabled": settings.GPU_ENABLED,
            "batch_size": settings.BATCH_SIZE,
            "max_workers": settings.MAX_WORKERS,
            "processing_interval": settings.PROCESSING_INTERVAL
        }
        
        return health_status
        
    except Exception as e:
        logger.error(f"Erro no health check detalhado: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ready")
async def readiness_check() -> Dict[str, Any]:
    """Verificar se o serviço está pronto para receber requisições"""
    try:
        # Verificar se todos os componentes essenciais estão funcionando
        ready = True
        issues = []
        
        # Verificar PyTorch
        try:
            import torch
            if not torch.cuda.is_available() and settings.GPU_ENABLED:
                issues.append("GPU não disponível mas habilitada nas configurações")
        except Exception as e:
            ready = False
            issues.append(f"PyTorch não disponível: {e}")
        
        # Verificar OpenCV
        try:
            import cv2
        except Exception as e:
            ready = False
            issues.append(f"OpenCV não disponível: {e}")
        
        return {
            "ready": ready,
            "issues": issues,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erro no readiness check: {e}")
        return {
            "ready": False,
            "issues": [str(e)],
            "timestamp": datetime.utcnow().isoformat()
        }


@router.get("/live")
async def liveness_check() -> Dict[str, Any]:
    """Verificar se o serviço está vivo"""
    return {
        "alive": True,
        "timestamp": datetime.utcnow().isoformat()
    }
