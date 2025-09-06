"""
Modelo de dados para usuários do sistema
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Enum
from sqlalchemy.sql import func
from passlib.context import CryptContext
import enum
from app.core.database import Base

# Contexto para hash de senhas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserRole(str, enum.Enum):
    """Roles dos usuários"""
    ADMIN = "admin"
    OPERATOR = "operator"
    VIEWER = "viewer"


class User(Base):
    """Modelo para usuários do sistema"""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    full_name = Column(String(100), nullable=False)
    
    # Autenticação
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Permissões
    role = Column(Enum(UserRole), default=UserRole.VIEWER)
    permissions = Column(Text)  # JSON string com permissões específicas
    
    # Informações de sessão
    last_login = Column(DateTime(timezone=True))
    last_login_ip = Column(String(45))
    login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime(timezone=True))
    
    # Metadados
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def verify_password(self, password: str) -> bool:
        """Verificar senha do usuário"""
        return pwd_context.verify(password, self.hashed_password)
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Gerar hash da senha"""
        return pwd_context.hash(password)
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', role='{self.role}')>"
