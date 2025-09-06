"""
Gerenciador de modelos de IA
"""

import torch
import torch.nn as nn
import cv2
import numpy as np
from typing import Dict, Any, Optional, List
import logging
from pathlib import Path
import mlflow
import mlflow.pytorch
from ultralytics import YOLO
import pickle
import json
from datetime import datetime

from app.core.config import settings

logger = logging.getLogger(__name__)


class ModelManager:
    """Gerenciador de modelos de IA"""
    
    def __init__(self):
        self.models: Dict[str, Any] = {}
        self.model_cache: Dict[str, Any] = {}
        self.device = torch.device("cuda" if torch.cuda.is_available() and settings.GPU_ENABLED else "cpu")
        self.model_path = Path(settings.MODEL_PATH)
        self.model_path.mkdir(exist_ok=True)
        
        logger.info(f"ModelManager inicializado com device: {self.device}")
    
    async def initialize(self):
        """Inicializar todos os modelos"""
        try:
            # Carregar modelo YOLO para detecção de objetos
            await self.load_yolo_model()
            
            # Carregar modelo de detecção de anomalias
            await self.load_anomaly_model()
            
            # Carregar modelo de detecção de faces
            await self.load_face_detection_model()
            
            # Configurar MLflow
            mlflow.set_tracking_uri(settings.MLFLOW_TRACKING_URI)
            
            logger.info("Todos os modelos inicializados com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao inicializar modelos: {e}")
            raise
    
    async def load_yolo_model(self):
        """Carregar modelo YOLO"""
        try:
            model_path = self.model_path / settings.YOLO_MODEL_PATH
            
            if not model_path.exists():
                logger.info("Baixando modelo YOLO...")
                model_path = settings.YOLO_MODEL_PATH  # Baixar automaticamente
            
            self.models["yolo"] = YOLO(model_path)
            self.models["yolo"].to(self.device)
            
            logger.info(f"Modelo YOLO carregado: {model_path}")
            
        except Exception as e:
            logger.error(f"Erro ao carregar modelo YOLO: {e}")
            raise
    
    async def load_anomaly_model(self):
        """Carregar modelo de detecção de anomalias"""
        try:
            model_path = self.model_path / settings.ANOMALY_MODEL_PATH
            
            if model_path.exists():
                # Carregar modelo PyTorch
                self.models["anomaly"] = torch.load(model_path, map_location=self.device)
                self.models["anomaly"].eval()
                logger.info(f"Modelo de anomalia carregado: {model_path}")
            else:
                # Criar modelo padrão se não existir
                self.models["anomaly"] = self._create_default_anomaly_model()
                logger.info("Modelo de anomalia padrão criado")
            
        except Exception as e:
            logger.error(f"Erro ao carregar modelo de anomalia: {e}")
            # Usar modelo padrão em caso de erro
            self.models["anomaly"] = self._create_default_anomaly_model()
    
    async def load_face_detection_model(self):
        """Carregar modelo de detecção de faces"""
        try:
            # Usar Haar Cascade do OpenCV
            cascade_path = cv2.data.haarcascades + settings.FACE_DETECTION_MODEL
            self.models["face"] = cv2.CascadeClassifier(cascade_path)
            
            if self.models["face"].empty():
                raise Exception("Não foi possível carregar o classificador Haar")
            
            logger.info(f"Modelo de detecção de faces carregado: {cascade_path}")
            
        except Exception as e:
            logger.error(f"Erro ao carregar modelo de faces: {e}")
            raise
    
    def _create_default_anomaly_model(self) -> nn.Module:
        """Criar modelo de anomalia padrão"""
        class SimpleAnomalyDetector(nn.Module):
            def __init__(self):
                super().__init__()
                self.conv1 = nn.Conv2d(3, 32, 3, padding=1)
                self.conv2 = nn.Conv2d(32, 64, 3, padding=1)
                self.conv3 = nn.Conv2d(64, 128, 3, padding=1)
                self.pool = nn.MaxPool2d(2, 2)
                self.fc1 = nn.Linear(128 * 24 * 24, 512)
                self.fc2 = nn.Linear(512, 1)
                self.relu = nn.ReLU()
                self.sigmoid = nn.Sigmoid()
            
            def forward(self, x):
                x = self.pool(self.relu(self.conv1(x)))
                x = self.pool(self.relu(self.conv2(x)))
                x = self.pool(self.relu(self.conv3(x)))
                x = x.view(-1, 128 * 24 * 24)
                x = self.relu(self.fc1(x))
                x = self.sigmoid(self.fc2(x))
                return x
        
        model = SimpleAnomalyDetector()
        model.to(self.device)
        model.eval()
        return model
    
    async def predict_objects(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """Detectar objetos na imagem usando YOLO"""
        try:
            if "yolo" not in self.models:
                raise Exception("Modelo YOLO não carregado")
            
            results = self.models["yolo"](image, conf=settings.DETECTION_CONFIDENCE_THRESHOLD)
            
            detections = []
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        conf = box.conf[0].cpu().numpy()
                        cls = int(box.cls[0].cpu().numpy())
                        class_name = self.models["yolo"].names[cls]
                        
                        detections.append({
                            "class": class_name,
                            "confidence": float(conf),
                            "bounding_box": {
                                "x": int(x1),
                                "y": int(y1),
                                "width": int(x2 - x1),
                                "height": int(y2 - y1)
                            },
                            "center_point": {
                                "x": int((x1 + x2) / 2),
                                "y": int((y1 + y2) / 2)
                            }
                        })
            
            return detections
            
        except Exception as e:
            logger.error(f"Erro na detecção de objetos: {e}")
            return []
    
    async def predict_anomaly(self, image: np.ndarray) -> Dict[str, Any]:
        """Detectar anomalias na imagem"""
        try:
            if "anomaly" not in self.models:
                raise Exception("Modelo de anomalia não carregado")
            
            # Pré-processar imagem
            processed_image = self._preprocess_image_for_anomaly(image)
            
            # Fazer predição
            with torch.no_grad():
                tensor_image = torch.FloatTensor(processed_image).unsqueeze(0).to(self.device)
                anomaly_score = self.models["anomaly"](tensor_image).cpu().numpy()[0][0]
            
            return {
                "anomaly_score": float(anomaly_score),
                "is_anomaly": anomaly_score > settings.ANOMALY_THRESHOLD,
                "confidence": float(anomaly_score)
            }
            
        except Exception as e:
            logger.error(f"Erro na detecção de anomalia: {e}")
            return {
                "anomaly_score": 0.0,
                "is_anomaly": False,
                "confidence": 0.0
            }
    
    async def detect_faces(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """Detectar faces na imagem"""
        try:
            if "face" not in self.models:
                raise Exception("Modelo de faces não carregado")
            
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            faces = self.models["face"].detectMultiScale(gray, 1.1, 4)
            
            detections = []
            for (x, y, w, h) in faces:
                detections.append({
                    "class": "face",
                    "confidence": 1.0,  # Haar não retorna confiança
                    "bounding_box": {
                        "x": int(x),
                        "y": int(y),
                        "width": int(w),
                        "height": int(h)
                    },
                    "center_point": {
                        "x": int(x + w / 2),
                        "y": int(y + h / 2)
                    }
                })
            
            return detections
            
        except Exception as e:
            logger.error(f"Erro na detecção de faces: {e}")
            return []
    
    def _preprocess_image_for_anomaly(self, image: np.ndarray) -> np.ndarray:
        """Pré-processar imagem para detecção de anomalia"""
        # Redimensionar para 192x192 (assumindo modelo treinado com esse tamanho)
        resized = cv2.resize(image, (192, 192))
        
        # Normalizar para [0, 1]
        normalized = resized.astype(np.float32) / 255.0
        
        # Converter de BGR para RGB
        rgb = cv2.cvtColor(normalized, cv2.COLOR_BGR2RGB)
        
        # Transpor para formato PyTorch (C, H, W)
        tensor_format = np.transpose(rgb, (2, 0, 1))
        
        return tensor_format
    
    async def get_model_info(self) -> Dict[str, Any]:
        """Obter informações dos modelos"""
        info = {
            "device": str(self.device),
            "models_loaded": list(self.models.keys()),
            "model_cache_size": len(self.model_cache),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Informações específicas de cada modelo
        for model_name, model in self.models.items():
            if model_name == "yolo":
                info[f"{model_name}_info"] = {
                    "type": "YOLO",
                    "classes": len(model.names),
                    "class_names": list(model.names.values())
                }
            elif model_name == "anomaly":
                info[f"{model_name}_info"] = {
                    "type": "PyTorch",
                    "parameters": sum(p.numel() for p in model.parameters()),
                    "trainable": sum(p.numel() for p in model.parameters() if p.requires_grad)
                }
            elif model_name == "face":
                info[f"{model_name}_info"] = {
                    "type": "Haar Cascade",
                    "loaded": not model.empty()
                }
        
        return info
    
    async def save_model(self, model_name: str, model: Any, metadata: Dict[str, Any] = None):
        """Salvar modelo"""
        try:
            model_path = self.model_path / f"{model_name}.pth"
            
            if isinstance(model, nn.Module):
                torch.save(model.state_dict(), model_path)
            else:
                torch.save(model, model_path)
            
            # Salvar metadados
            if metadata:
                metadata_path = self.model_path / f"{model_name}_metadata.json"
                with open(metadata_path, 'w') as f:
                    json.dump(metadata, f, indent=2)
            
            logger.info(f"Modelo {model_name} salvo em {model_path}")
            
        except Exception as e:
            logger.error(f"Erro ao salvar modelo {model_name}: {e}")
            raise
    
    async def load_custom_model(self, model_name: str, model_path: str) -> bool:
        """Carregar modelo customizado"""
        try:
            path = Path(model_path)
            if not path.exists():
                logger.error(f"Arquivo de modelo não encontrado: {model_path}")
                return False
            
            # Carregar modelo baseado na extensão
            if path.suffix == '.pth':
                model = torch.load(model_path, map_location=self.device)
                if isinstance(model, nn.Module):
                    model.eval()
                self.models[model_name] = model
            elif path.suffix == '.pt':
                # Modelo YOLO
                self.models[model_name] = YOLO(model_path)
                self.models[model_name].to(self.device)
            else:
                logger.error(f"Formato de modelo não suportado: {path.suffix}")
                return False
            
            logger.info(f"Modelo customizado {model_name} carregado de {model_path}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao carregar modelo customizado {model_name}: {e}")
            return False
