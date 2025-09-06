"""
Utilitários de segurança
"""

import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional
import logging

logger = logging.getLogger(__name__)


def generate_secure_token(length: int = 32) -> str:
    """Gerar token seguro"""
    return secrets.token_urlsafe(length)


def generate_api_key() -> str:
    """Gerar chave de API"""
    return f"sk_{secrets.token_urlsafe(32)}"


def hash_sensitive_data(data: str) -> str:
    """Hash de dados sensíveis"""
    return hashlib.sha256(data.encode()).hexdigest()


def validate_ip_address(ip: str) -> bool:
    """Validar endereço IP"""
    import ipaddress
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False


def sanitize_filename(filename: str) -> str:
    """Sanitizar nome de arquivo"""
    import re
    # Remover caracteres perigosos
    sanitized = re.sub(r'[^\w\-_\.]', '_', filename)
    # Limitar tamanho
    if len(sanitized) > 255:
        name, ext = sanitized.rsplit('.', 1) if '.' in sanitized else (sanitized, '')
        sanitized = name[:255-len(ext)-1] + ('.' + ext if ext else '')
    return sanitized


def check_password_strength(password: str) -> dict:
    """Verificar força da senha"""
    import re
    
    result = {
        "is_strong": False,
        "score": 0,
        "feedback": []
    }
    
    # Critérios de força
    if len(password) < 8:
        result["feedback"].append("Senha deve ter pelo menos 8 caracteres")
    else:
        result["score"] += 1
    
    if not re.search(r'[a-z]', password):
        result["feedback"].append("Senha deve conter pelo menos uma letra minúscula")
    else:
        result["score"] += 1
    
    if not re.search(r'[A-Z]', password):
        result["feedback"].append("Senha deve conter pelo menos uma letra maiúscula")
    else:
        result["score"] += 1
    
    if not re.search(r'\d', password):
        result["feedback"].append("Senha deve conter pelo menos um número")
    else:
        result["score"] += 1
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        result["feedback"].append("Senha deve conter pelo menos um caractere especial")
    else:
        result["score"] += 1
    
    # Senha forte se atender pelo menos 4 critérios
    result["is_strong"] = result["score"] >= 4
    
    return result


def generate_secure_filename(original_filename: str, prefix: str = "") -> str:
    """Gerar nome de arquivo seguro"""
    import os
    from datetime import datetime
    
    # Obter extensão
    _, ext = os.path.splitext(original_filename)
    
    # Gerar nome único
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    random_part = secrets.token_hex(8)
    
    filename = f"{prefix}_{timestamp}_{random_part}{ext}" if prefix else f"{timestamp}_{random_part}{ext}"
    
    return sanitize_filename(filename)


def validate_file_upload(file_content: bytes, max_size: int = 10 * 1024 * 1024) -> dict:
    """Validar upload de arquivo"""
    result = {
        "is_valid": True,
        "errors": [],
        "file_info": {}
    }
    
    # Verificar tamanho
    if len(file_content) > max_size:
        result["is_valid"] = False
        result["errors"].append(f"Arquivo muito grande. Máximo: {max_size / (1024*1024):.1f}MB")
    
    # Verificar tipo de arquivo (magic bytes)
    if len(file_content) >= 4:
        magic_bytes = file_content[:4]
        
        # Tipos de imagem suportados
        image_types = {
            b'\xff\xd8\xff\xe0': 'JPEG',
            b'\xff\xd8\xff\xe1': 'JPEG',
            b'\x89PNG': 'PNG',
            b'GIF8': 'GIF',
            b'RIFF': 'WEBP'
        }
        
        file_type = None
        for magic, file_format in image_types.items():
            if file_content.startswith(magic):
                file_type = file_format
                break
        
        if file_type:
            result["file_info"]["type"] = file_type
            result["file_info"]["size"] = len(file_content)
        else:
            result["is_valid"] = False
            result["errors"].append("Tipo de arquivo não suportado")
    
    return result


def create_audit_log(action: str, user_id: Optional[int], details: dict) -> dict:
    """Criar log de auditoria"""
    return {
        "action": action,
        "user_id": user_id,
        "timestamp": datetime.utcnow().isoformat(),
        "details": details,
        "ip_address": None,  # Será preenchido pelo middleware
        "user_agent": None   # Será preenchido pelo middleware
    }


def encrypt_sensitive_field(value: str) -> str:
    """Criptografar campo sensível"""
    # Implementar criptografia real em produção
    # Por enquanto, apenas base64
    import base64
    return base64.b64encode(value.encode()).decode()


def decrypt_sensitive_field(encrypted_value: str) -> str:
    """Descriptografar campo sensível"""
    # Implementar descriptografia real em produção
    # Por enquanto, apenas base64
    import base64
    return base64.b64decode(encrypted_value.encode()).decode()
