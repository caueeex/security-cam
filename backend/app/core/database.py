"""
Configuração e inicialização dos bancos de dados
"""

from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from motor.motor_asyncio import AsyncIOMotorClient
import redis.asyncio as redis
import logging
from typing import AsyncGenerator

from app.core.config import settings

logger = logging.getLogger(__name__)

# SQLAlchemy
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=settings.DEBUG
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# MongoDB
mongodb_client: AsyncIOMotorClient = None
mongodb_database = None

# Redis
redis_client: redis.Redis = None


async def init_db():
    """Inicializar conexões com bancos de dados"""
    global mongodb_client, mongodb_database, redis_client
    
    try:
        # MongoDB
        mongodb_client = AsyncIOMotorClient(settings.MONGODB_URL)
        mongodb_database = mongodb_client.get_default_database()
        await mongodb_client.admin.command('ping')
        logger.info("MongoDB conectado com sucesso")
        
        # Redis
        redis_client = redis.from_url(settings.REDIS_URL)
        await redis_client.ping()
        logger.info("Redis conectado com sucesso")
        
    except Exception as e:
        logger.error(f"Erro ao conectar com bancos de dados: {e}")
        raise


async def get_mongodb():
    """Obter instância do MongoDB"""
    return mongodb_database


async def get_redis():
    """Obter instância do Redis"""
    return redis_client


def get_db():
    """Dependency para obter sessão do banco de dados"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def close_db_connections():
    """Fechar conexões com bancos de dados"""
    global mongodb_client, redis_client
    
    if mongodb_client:
        mongodb_client.close()
        logger.info("Conexão MongoDB fechada")
    
    if redis_client:
        await redis_client.close()
        logger.info("Conexão Redis fechada")
