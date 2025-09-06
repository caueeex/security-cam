"""
Endpoints para autenticação e autorização
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
import logging

from app.core.database import get_db
from app.schemas.user import User as UserSchema, UserCreate, UserLogin
from app.services.auth_service import AuthService
from app.core.exceptions import AuthenticationException, AuthorizationException

logger = logging.getLogger(__name__)
router = APIRouter()
security = HTTPBearer()


@router.post("/login")
async def login(
    user_credentials: UserLogin,
    db: Session = Depends(get_db)
):
    """Fazer login no sistema"""
    try:
        auth_service = AuthService(db)
        result = await auth_service.authenticate_user(
            username=user_credentials.username,
            password=user_credentials.password
        )
        
        if not result:
            raise AuthenticationException("Credenciais inválidas")
        
        return {
            "access_token": result["access_token"],
            "token_type": "bearer",
            "expires_in": result["expires_in"],
            "user": result["user"]
        }
    except AuthenticationException:
        raise
    except Exception as e:
        logger.error(f"Erro no login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )


@router.post("/register", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """Registrar novo usuário"""
    try:
        auth_service = AuthService(db)
        user = await auth_service.create_user(user_data)
        return user
    except Exception as e:
        logger.error(f"Erro no registro: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )


@router.get("/me", response_model=UserSchema)
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Obter informações do usuário atual"""
    try:
        auth_service = AuthService(db)
        user = await auth_service.get_current_user(credentials.credentials)
        
        if not user:
            raise AuthenticationException("Token inválido")
        
        return user
    except AuthenticationException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter usuário atual: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )


@router.post("/refresh")
async def refresh_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Renovar token de acesso"""
    try:
        auth_service = AuthService(db)
        result = await auth_service.refresh_token(credentials.credentials)
        
        if not result:
            raise AuthenticationException("Token inválido")
        
        return {
            "access_token": result["access_token"],
            "token_type": "bearer",
            "expires_in": result["expires_in"]
        }
    except AuthenticationException:
        raise
    except Exception as e:
        logger.error(f"Erro ao renovar token: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )


@router.post("/logout")
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Fazer logout do sistema"""
    try:
        auth_service = AuthService(db)
        await auth_service.logout_user(credentials.credentials)
        return {"message": "Logout realizado com sucesso"}
    except Exception as e:
        logger.error(f"Erro no logout: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )


@router.post("/change-password")
async def change_password(
    current_password: str,
    new_password: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Alterar senha do usuário"""
    try:
        auth_service = AuthService(db)
        success = await auth_service.change_password(
            token=credentials.credentials,
            current_password=current_password,
            new_password=new_password
        )
        
        if not success:
            raise AuthenticationException("Senha atual incorreta")
        
        return {"message": "Senha alterada com sucesso"}
    except AuthenticationException:
        raise
    except Exception as e:
        logger.error(f"Erro ao alterar senha: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )
