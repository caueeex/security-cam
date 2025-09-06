"""
Serviço para autenticação e autorização
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional, Dict, Any
import logging
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
import secrets

from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserLogin
from app.core.config import settings
from app.core.exceptions import AuthenticationException, ValidationException

logger = logging.getLogger(__name__)

# Contexto para hash de senhas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Serviço para operações de autenticação"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def _create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None):
        """Criar token de acesso JWT"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
        return encoded_jwt
    
    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verificar senha"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def _get_password_hash(self, password: str) -> str:
        """Gerar hash da senha"""
        return pwd_context.hash(password)
    
    async def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Autenticar usuário"""
        user = self.db.query(User).filter(
            and_(
                User.username == username,
                User.is_active == True
            )
        ).first()
        
        if not user or not self._verify_password(password, user.hashed_password):
            return None
        
        # Atualizar último login
        user.last_login = datetime.utcnow()
        user.login_attempts = 0
        self.db.commit()
        
        # Criar token de acesso
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = self._create_access_token(
            data={"sub": str(user.id), "username": user.username},
            expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role.value,
                "is_active": user.is_active
            }
        }
    
    async def create_user(self, user_data: UserCreate) -> User:
        """Criar novo usuário"""
        # Verificar se username já existe
        existing_user = self.db.query(User).filter(User.username == user_data.username).first()
        if existing_user:
            raise ValidationException("Username já existe")
        
        # Verificar se email já existe
        existing_email = self.db.query(User).filter(User.email == user_data.email).first()
        if existing_email:
            raise ValidationException("Email já existe")
        
        # Criar novo usuário
        hashed_password = self._get_password_hash(user_data.password)
        
        user = User(
            username=user_data.username,
            email=user_data.email,
            full_name=user_data.full_name,
            hashed_password=hashed_password,
            role=user_data.role or UserRole.VIEWER,
            is_active=True,
            is_verified=False
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        logger.info(f"Usuário criado: {user.username}")
        return user
    
    async def get_current_user(self, token: str) -> Optional[User]:
        """Obter usuário atual pelo token"""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id: str = payload.get("sub")
            username: str = payload.get("username")
            
            if user_id is None or username is None:
                return None
            
            user = self.db.query(User).filter(
                and_(
                    User.id == int(user_id),
                    User.username == username,
                    User.is_active == True
                )
            ).first()
            
            return user
            
        except JWTError:
            return None
        except Exception as e:
            logger.error(f"Erro ao obter usuário atual: {e}")
            return None
    
    async def refresh_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Renovar token de acesso"""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id: str = payload.get("sub")
            username: str = payload.get("username")
            
            if user_id is None or username is None:
                return None
            
            user = self.db.query(User).filter(
                and_(
                    User.id == int(user_id),
                    User.username == username,
                    User.is_active == True
                )
            ).first()
            
            if not user:
                return None
            
            # Criar novo token
            access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = self._create_access_token(
                data={"sub": str(user.id), "username": user.username},
                expires_delta=access_token_expires
            )
            
            return {
                "access_token": access_token,
                "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
            }
            
        except JWTError:
            return None
        except Exception as e:
            logger.error(f"Erro ao renovar token: {e}")
            return None
    
    async def logout_user(self, token: str) -> bool:
        """Fazer logout do usuário"""
        try:
            # Implementar lógica de logout (blacklist de tokens, etc.)
            # Por enquanto, apenas log
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id: str = payload.get("sub")
            username: str = payload.get("username")
            
            logger.info(f"Logout realizado: {username} (ID: {user_id})")
            return True
            
        except JWTError:
            return False
        except Exception as e:
            logger.error(f"Erro no logout: {e}")
            return False
    
    async def change_password(
        self,
        token: str,
        current_password: str,
        new_password: str
    ) -> bool:
        """Alterar senha do usuário"""
        try:
            user = await self.get_current_user(token)
            if not user:
                return False
            
            # Verificar senha atual
            if not self._verify_password(current_password, user.hashed_password):
                return False
            
            # Atualizar senha
            user.hashed_password = self._get_password_hash(new_password)
            user.updated_at = datetime.utcnow()
            
            self.db.commit()
            
            logger.info(f"Senha alterada para usuário: {user.username}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao alterar senha: {e}")
            return False
    
    async def verify_user(self, user_id: int) -> bool:
        """Verificar usuário (ativar conta)"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        
        user.is_verified = True
        user.updated_at = datetime.utcnow()
        
        self.db.commit()
        
        logger.info(f"Usuário verificado: {user.username}")
        return True
    
    async def deactivate_user(self, user_id: int) -> bool:
        """Desativar usuário"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        
        user.is_active = False
        user.updated_at = datetime.utcnow()
        
        self.db.commit()
        
        logger.info(f"Usuário desativado: {user.username}")
        return True
    
    async def update_user_role(self, user_id: int, new_role: UserRole) -> bool:
        """Atualizar role do usuário"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        
        user.role = new_role
        user.updated_at = datetime.utcnow()
        
        self.db.commit()
        
        logger.info(f"Role atualizado para {user.username}: {new_role.value}")
        return True
    
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Obter usuário por ID"""
        return self.db.query(User).filter(User.id == user_id).first()
    
    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Obter usuário por username"""
        return self.db.query(User).filter(User.username == username).first()
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Obter usuário por email"""
        return self.db.query(User).filter(User.email == email).first()
    
    async def get_all_users(self, skip: int = 0, limit: int = 100) -> list[User]:
        """Obter todos os usuários"""
        return self.db.query(User).offset(skip).limit(limit).all()
    
    async def increment_login_attempts(self, username: str) -> bool:
        """Incrementar tentativas de login"""
        user = self.db.query(User).filter(User.username == username).first()
        if not user:
            return False
        
        user.login_attempts += 1
        
        # Bloquear usuário após 5 tentativas
        if user.login_attempts >= 5:
            user.locked_until = datetime.utcnow() + timedelta(minutes=30)
        
        self.db.commit()
        return True
    
    async def reset_login_attempts(self, username: str) -> bool:
        """Resetar tentativas de login"""
        user = self.db.query(User).filter(User.username == username).first()
        if not user:
            return False
        
        user.login_attempts = 0
        user.locked_until = None
        
        self.db.commit()
        return True
