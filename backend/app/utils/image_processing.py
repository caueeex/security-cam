"""
Utilitários para processamento de imagens
"""

import cv2
import numpy as np
from PIL import Image
import base64
import io
from typing import Tuple, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


def resize_image(image: np.ndarray, target_size: Tuple[int, int]) -> np.ndarray:
    """Redimensionar imagem mantendo proporção"""
    height, width = image.shape[:2]
    target_width, target_height = target_size
    
    # Calcular nova dimensão mantendo proporção
    aspect_ratio = width / height
    
    if target_width / target_height > aspect_ratio:
        new_width = int(target_height * aspect_ratio)
        new_height = target_height
    else:
        new_width = target_width
        new_height = int(target_width / aspect_ratio)
    
    # Redimensionar
    resized = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
    
    # Criar imagem com padding se necessário
    if new_width != target_width or new_height != target_height:
        padded = np.zeros((target_height, target_width, 3), dtype=np.uint8)
        y_offset = (target_height - new_height) // 2
        x_offset = (target_width - new_width) // 2
        padded[y_offset:y_offset+new_height, x_offset:x_offset+new_width] = resized
        return padded
    
    return resized


def crop_bounding_box(image: np.ndarray, bbox: Dict[str, int]) -> np.ndarray:
    """Cortar região da imagem baseada no bounding box"""
    x = bbox.get('x', 0)
    y = bbox.get('y', 0)
    width = bbox.get('width', image.shape[1])
    height = bbox.get('height', image.shape[0])
    
    # Garantir que as coordenadas estão dentro da imagem
    x = max(0, min(x, image.shape[1] - 1))
    y = max(0, min(y, image.shape[0] - 1))
    width = min(width, image.shape[1] - x)
    height = min(height, image.shape[0] - y)
    
    return image[y:y+height, x:x+width]


def apply_blur(image: np.ndarray, blur_type: str = "gaussian", kernel_size: int = 15) -> np.ndarray:
    """Aplicar blur na imagem"""
    if blur_type == "gaussian":
        return cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)
    elif blur_type == "median":
        return cv2.medianBlur(image, kernel_size)
    elif blur_type == "bilateral":
        return cv2.bilateralFilter(image, kernel_size, 80, 80)
    else:
        return image


def enhance_image(image: np.ndarray) -> np.ndarray:
    """Melhorar qualidade da imagem"""
    # Converter para LAB
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    
    # Separar canais
    l, a, b = cv2.split(lab)
    
    # Aplicar CLAHE no canal L
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    l = clahe.apply(l)
    
    # Recombinar canais
    enhanced = cv2.merge([l, a, b])
    
    # Converter de volta para BGR
    return cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)


def detect_faces(image: np.ndarray) -> list:
    """Detectar faces na imagem"""
    # Carregar classificador Haar para faces
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    # Converter para escala de cinza
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Detectar faces
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)
    
    # Converter para formato padrão
    face_list = []
    for (x, y, w, h) in faces:
        face_list.append({
            'x': int(x),
            'y': int(y),
            'width': int(w),
            'height': int(h),
            'confidence': 1.0  # Haar não retorna confiança
        })
    
    return face_list


def detect_motion(frame1: np.ndarray, frame2: np.ndarray, threshold: float = 30) -> Dict[str, Any]:
    """Detectar movimento entre dois frames"""
    # Converter para escala de cinza
    gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
    
    # Calcular diferença
    diff = cv2.absdiff(gray1, gray2)
    
    # Aplicar threshold
    _, thresh = cv2.threshold(diff, threshold, 255, cv2.THRESH_BINARY)
    
    # Encontrar contornos
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Calcular área total de movimento
    motion_area = sum(cv2.contourArea(contour) for contour in contours)
    total_area = frame1.shape[0] * frame1.shape[1]
    motion_percentage = (motion_area / total_area) * 100
    
    # Encontrar bounding box do movimento
    motion_bbox = None
    if contours:
        # Combinar todos os contornos
        all_points = np.vstack(contours)
        x, y, w, h = cv2.boundingRect(all_points)
        motion_bbox = {'x': x, 'y': y, 'width': w, 'height': h}
    
    return {
        'has_motion': motion_percentage > 0.1,  # Threshold de 0.1%
        'motion_percentage': motion_percentage,
        'motion_area': motion_area,
        'contours_count': len(contours),
        'motion_bbox': motion_bbox
    }


def image_to_base64(image: np.ndarray, format: str = "JPEG", quality: int = 95) -> str:
    """Converter imagem OpenCV para base64"""
    # Converter BGR para RGB
    if len(image.shape) == 3:
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    else:
        image_rgb = image
    
    # Converter para PIL Image
    pil_image = Image.fromarray(image_rgb)
    
    # Converter para base64
    buffer = io.BytesIO()
    pil_image.save(buffer, format=format, quality=quality)
    buffer.seek(0)
    
    image_base64 = base64.b64encode(buffer.getvalue()).decode()
    return f"data:image/{format.lower()};base64,{image_base64}"


def base64_to_image(base64_string: str) -> np.ndarray:
    """Converter base64 para imagem OpenCV"""
    # Remover prefixo data URL se presente
    if ',' in base64_string:
        base64_string = base64_string.split(',')[1]
    
    # Decodificar base64
    image_data = base64.b64decode(base64_string)
    
    # Converter para PIL Image
    pil_image = Image.open(io.BytesIO(image_data))
    
    # Converter para OpenCV
    image_cv = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
    
    return image_cv


def calculate_image_similarity(image1: np.ndarray, image2: np.ndarray) -> float:
    """Calcular similaridade entre duas imagens"""
    # Redimensionar para o mesmo tamanho
    height = min(image1.shape[0], image2.shape[0])
    width = min(image1.shape[1], image2.shape[1])
    
    img1_resized = cv2.resize(image1, (width, height))
    img2_resized = cv2.resize(image2, (width, height))
    
    # Converter para escala de cinza
    gray1 = cv2.cvtColor(img1_resized, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(img2_resized, cv2.COLOR_BGR2GRAY)
    
    # Calcular correlação
    correlation = cv2.matchTemplate(gray1, gray2, cv2.TM_CCOEFF_NORMED)[0][0]
    
    return float(correlation)


def extract_image_features(image: np.ndarray) -> Dict[str, Any]:
    """Extrair características da imagem"""
    features = {}
    
    # Dimensões
    features['width'] = image.shape[1]
    features['height'] = image.shape[0]
    features['channels'] = image.shape[2] if len(image.shape) == 3 else 1
    
    # Estatísticas de cor
    if len(image.shape) == 3:
        mean_color = np.mean(image, axis=(0, 1))
        features['mean_color'] = {
            'b': float(mean_color[0]),
            'g': float(mean_color[1]),
            'r': float(mean_color[2])
        }
        
        std_color = np.std(image, axis=(0, 1))
        features['std_color'] = {
            'b': float(std_color[0]),
            'g': float(std_color[1]),
            'r': float(std_color[2])
        }
    
    # Brilho médio
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
    features['brightness'] = float(np.mean(gray))
    features['contrast'] = float(np.std(gray))
    
    # Histograma
    hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
    features['histogram'] = hist.flatten().tolist()
    
    return features


def create_thumbnail(image: np.ndarray, size: Tuple[int, int] = (150, 150)) -> np.ndarray:
    """Criar thumbnail da imagem"""
    return resize_image(image, size)


def watermark_image(image: np.ndarray, text: str, position: str = "bottom-right") -> np.ndarray:
    """Adicionar marca d'água na imagem"""
    # Criar cópia da imagem
    watermarked = image.copy()
    
    # Configurar texto
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.7
    color = (255, 255, 255)  # Branco
    thickness = 2
    
    # Obter tamanho do texto
    text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
    
    # Calcular posição
    if position == "bottom-right":
        x = image.shape[1] - text_size[0] - 10
        y = image.shape[0] - 10
    elif position == "bottom-left":
        x = 10
        y = image.shape[0] - 10
    elif position == "top-right":
        x = image.shape[1] - text_size[0] - 10
        y = text_size[1] + 10
    elif position == "top-left":
        x = 10
        y = text_size[1] + 10
    else:
        x = 10
        y = image.shape[0] - 10
    
    # Adicionar texto
    cv2.putText(watermarked, text, (x, y), font, font_scale, color, thickness)
    
    return watermarked
