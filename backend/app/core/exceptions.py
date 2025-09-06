"""
Exceções customizadas do sistema
"""

from fastapi import HTTPException, status
from typing import Any, Dict, Optional


class SecurityCamException(Exception):
    """Exceção base do sistema de segurança"""
    
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class DetectionException(SecurityCamException):
    """Exceção relacionada à detecção de anomalias"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details
        )


class VideoProcessingException(SecurityCamException):
    """Exceção relacionada ao processamento de vídeo"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details
        )


class StorageException(SecurityCamException):
    """Exceção relacionada ao armazenamento de dados"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_507_INSUFFICIENT_STORAGE,
            details=details
        )


class AuthenticationException(SecurityCamException):
    """Exceção relacionada à autenticação"""
    
    def __init__(self, message: str = "Falha na autenticação", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            details=details
        )


class AuthorizationException(SecurityCamException):
    """Exceção relacionada à autorização"""
    
    def __init__(self, message: str = "Acesso negado", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            details=details
        )


class ValidationException(SecurityCamException):
    """Exceção relacionada à validação de dados"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details
        )


class NotFoundException(SecurityCamException):
    """Exceção para recursos não encontrados"""
    
    def __init__(self, message: str = "Recurso não encontrado", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            details=details
        )


async def security_cam_exception_handler(request, exc: SecurityCamException):
    """Handler para exceções customizadas do sistema"""
    return HTTPException(
        status_code=exc.status_code,
        detail={
            "message": exc.message,
            "details": exc.details,
            "type": exc.__class__.__name__
        }
    )
