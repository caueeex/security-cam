"""
Router principal da API v1
"""

from fastapi import APIRouter
from app.api.v1.endpoints import cameras, detections, alerts, auth, websocket

api_router = APIRouter()

# Incluir todos os endpoints
api_router.include_router(
    cameras.router,
    prefix="/cameras",
    tags=["cameras"]
)

api_router.include_router(
    detections.router,
    prefix="/detections",
    tags=["detections"]
)

api_router.include_router(
    alerts.router,
    prefix="/alerts",
    tags=["alerts"]
)

api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["authentication"]
)

api_router.include_router(
    websocket.router,
    prefix="/ws",
    tags=["websocket"]
)
