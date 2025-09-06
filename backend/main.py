"""
Sistema de Segurança Inteligente - Backend API
FastAPI application com arquitetura modular para detecção de intrusões
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import HTTPBearer
from contextlib import asynccontextmanager
import uvicorn
import logging
from prometheus_client import Counter, Histogram, generate_latest
from fastapi.responses import Response

from app.core.config import settings
from app.core.database import init_db
from app.core.middleware import LoggingMiddleware, MetricsMiddleware
from app.api.v1.api import api_router
from app.core.exceptions import SecurityCamException, security_cam_exception_handler

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Métricas Prometheus
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerenciar ciclo de vida da aplicação"""
    # Startup
    logger.info("Iniciando Sistema de Segurança Inteligente...")
    await init_db()
    logger.info("Banco de dados inicializado")
    
    yield
    
    # Shutdown
    logger.info("Finalizando Sistema de Segurança Inteligente...")

def create_application() -> FastAPI:
    """Criar e configurar aplicação FastAPI"""
    
    app = FastAPI(
        title="Sistema de Segurança Inteligente",
        description="API para monitoramento de perímetros e detecção automática de intrusões",
        version="1.0.0",
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
        lifespan=lifespan
    )

    # Middleware de segurança
    app.add_middleware(
        TrustedHostMiddleware, 
        allowed_hosts=settings.ALLOWED_HOSTS
    )
    
    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Middleware customizado
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(MetricsMiddleware)

    # Incluir rotas da API
    app.include_router(api_router, prefix=settings.API_V1_STR)

    # Handler de exceções customizadas
    app.add_exception_handler(SecurityCamException, security_cam_exception_handler)

    # Endpoint de health check
    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        return {
            "status": "healthy",
            "version": "1.0.0",
            "environment": settings.ENVIRONMENT
        }

    # Endpoint de métricas Prometheus
    @app.get("/metrics")
    async def metrics():
        """Endpoint para métricas Prometheus"""
        return Response(generate_latest(), media_type="text/plain")

    return app

# Criar instância da aplicação
app = create_application()

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    )
