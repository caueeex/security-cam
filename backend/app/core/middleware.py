"""
Middleware customizado para logging e métricas
"""

import time
import logging
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from prometheus_client import Counter, Histogram, generate_latest

logger = logging.getLogger(__name__)

# Métricas Prometheus
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code']
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint']
)

RESPONSE_SIZE = Histogram(
    'http_response_size_bytes',
    'HTTP response size in bytes',
    ['method', 'endpoint']
)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware para logging de requisições"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Log da requisição
        logger.info(
            f"Request: {request.method} {request.url.path}",
            extra={
                "method": request.method,
                "path": request.url.path,
                "query_params": str(request.query_params),
                "client_ip": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent")
            }
        )
        
        # Processar requisição
        response = await call_next(request)
        
        # Calcular duração
        process_time = time.time() - start_time
        
        # Log da resposta
        logger.info(
            f"Response: {response.status_code} - {process_time:.4f}s",
            extra={
                "status_code": response.status_code,
                "process_time": process_time,
                "response_size": response.headers.get("content-length", 0)
            }
        )
        
        # Adicionar header com tempo de processamento
        response.headers["X-Process-Time"] = str(process_time)
        
        return response


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware para coleta de métricas Prometheus"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Processar requisição
        response = await call_next(request)
        
        # Calcular métricas
        duration = time.time() - start_time
        endpoint = request.url.path
        
        # Registrar métricas
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=endpoint,
            status_code=response.status_code
        ).inc()
        
        REQUEST_DURATION.labels(
            method=request.method,
            endpoint=endpoint
        ).observe(duration)
        
        # Tamanho da resposta (se disponível)
        content_length = response.headers.get("content-length")
        if content_length:
            RESPONSE_SIZE.labels(
                method=request.method,
                endpoint=endpoint
            ).observe(int(content_length))
        
        return response
