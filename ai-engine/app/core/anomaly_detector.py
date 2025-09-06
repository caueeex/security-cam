"""
Detector de anomalias baseado em deep learning
Implementa técnicas de detecção de anomalias em vídeo
"""

import torch
import torch.nn as nn
import cv2
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
import logging
from collections import deque
import asyncio
from datetime import datetime
import json

from app.core.config import settings
from app.core.model_manager import ModelManager

logger = logging.getLogger(__name__)


class AnomalyDetector:
    """Detector de anomalias em vídeo"""
    
    def __init__(self, model_manager: ModelManager):
        self.model_manager = model_manager
        self.device = torch.device("cuda" if torch.cuda.is_available() and settings.GPU_ENABLED else "cpu")
        
        # Buffer para frames anteriores (para detecção temporal)
        self.frame_buffer = deque(maxlen=settings.VIDEO_BUFFER_SIZE)
        self.anomaly_buffer = deque(maxlen=10)
        
        # Modelos específicos para anomalia
        self.autoencoder = None
        self.lstm_model = None
        self.attention_model = None
        
        # Estatísticas
        self.total_frames_processed = 0
        self.total_anomalies_detected = 0
        self.false_positive_count = 0
        
        logger.info("AnomalyDetector inicializado")
    
    async def initialize(self):
        """Inicializar modelos de anomalia"""
        try:
            # Carregar autoencoder para reconstrução
            await self._load_autoencoder()
            
            # Carregar modelo LSTM para sequências temporais
            await self._load_lstm_model()
            
            # Carregar modelo de atenção
            await self._load_attention_model()
            
            logger.info("Modelos de anomalia inicializados")
            
        except Exception as e:
            logger.error(f"Erro ao inicializar modelos de anomalia: {e}")
            # Continuar com modelos padrão se houver erro
    
    async def _load_autoencoder(self):
        """Carregar autoencoder para detecção de anomalias"""
        try:
            # Criar autoencoder padrão se não existir modelo treinado
            self.autoencoder = self._create_autoencoder()
            self.autoencoder.to(self.device)
            self.autoencoder.eval()
            
            logger.info("Autoencoder carregado")
            
        except Exception as e:
            logger.error(f"Erro ao carregar autoencoder: {e}")
            self.autoencoder = self._create_autoencoder()
    
    async def _load_lstm_model(self):
        """Carregar modelo LSTM para sequências temporais"""
        try:
            self.lstm_model = self._create_lstm_model()
            self.lstm_model.to(self.device)
            self.lstm_model.eval()
            
            logger.info("Modelo LSTM carregado")
            
        except Exception as e:
            logger.error(f"Erro ao carregar modelo LSTM: {e}")
            self.lstm_model = self._create_lstm_model()
    
    async def _load_attention_model(self):
        """Carregar modelo de atenção"""
        try:
            self.attention_model = self._create_attention_model()
            self.attention_model.to(self.device)
            self.attention_model.eval()
            
            logger.info("Modelo de atenção carregado")
            
        except Exception as e:
            logger.error(f"Erro ao carregar modelo de atenção: {e}")
            self.attention_model = self._create_attention_model()
    
    def _create_autoencoder(self) -> nn.Module:
        """Criar autoencoder para reconstrução de frames"""
        class VideoAutoencoder(nn.Module):
            def __init__(self):
                super().__init__()
                
                # Encoder
                self.encoder = nn.Sequential(
                    nn.Conv2d(3, 64, 4, 2, 1),  # 192x192 -> 96x96
                    nn.ReLU(),
                    nn.Conv2d(64, 128, 4, 2, 1),  # 96x96 -> 48x48
                    nn.ReLU(),
                    nn.Conv2d(128, 256, 4, 2, 1),  # 48x48 -> 24x24
                    nn.ReLU(),
                    nn.Conv2d(256, 512, 4, 2, 1),  # 24x24 -> 12x12
                    nn.ReLU(),
                    nn.Conv2d(512, 1024, 4, 2, 1),  # 12x12 -> 6x6
                    nn.ReLU(),
                )
                
                # Decoder
                self.decoder = nn.Sequential(
                    nn.ConvTranspose2d(1024, 512, 4, 2, 1),  # 6x6 -> 12x12
                    nn.ReLU(),
                    nn.ConvTranspose2d(512, 256, 4, 2, 1),  # 12x12 -> 24x24
                    nn.ReLU(),
                    nn.ConvTranspose2d(256, 128, 4, 2, 1),  # 24x24 -> 48x48
                    nn.ReLU(),
                    nn.ConvTranspose2d(128, 64, 4, 2, 1),  # 48x48 -> 96x96
                    nn.ReLU(),
                    nn.ConvTranspose2d(64, 3, 4, 2, 1),  # 96x96 -> 192x192
                    nn.Sigmoid(),
                )
            
            def forward(self, x):
                encoded = self.encoder(x)
                decoded = self.decoder(encoded)
                return decoded
        
        return VideoAutoencoder()
    
    def _create_lstm_model(self) -> nn.Module:
        """Criar modelo LSTM para sequências temporais"""
        class TemporalAnomalyDetector(nn.Module):
            def __init__(self, input_size=1024, hidden_size=512, num_layers=2):
                super().__init__()
                self.hidden_size = hidden_size
                self.num_layers = num_layers
                
                self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
                self.attention = nn.MultiheadAttention(hidden_size, num_heads=8)
                self.classifier = nn.Sequential(
                    nn.Linear(hidden_size, 256),
                    nn.ReLU(),
                    nn.Dropout(0.3),
                    nn.Linear(256, 64),
                    nn.ReLU(),
                    nn.Dropout(0.3),
                    nn.Linear(64, 1),
                    nn.Sigmoid()
                )
            
            def forward(self, x):
                # x shape: (batch_size, sequence_length, input_size)
                lstm_out, _ = self.lstm(x)
                
                # Aplicar atenção
                attended, _ = self.attention(lstm_out, lstm_out, lstm_out)
                
                # Usar último timestep
                last_output = attended[:, -1, :]
                
                # Classificação
                anomaly_score = self.classifier(last_output)
                
                return anomaly_score
        
        return TemporalAnomalyDetector()
    
    def _create_attention_model(self) -> nn.Module:
        """Criar modelo de atenção para detecção de anomalias"""
        class AttentionAnomalyDetector(nn.Module):
            def __init__(self, input_size=1024, hidden_size=512):
                super().__init__()
                self.input_projection = nn.Linear(input_size, hidden_size)
                self.attention = nn.MultiheadAttention(hidden_size, num_heads=8)
                self.norm = nn.LayerNorm(hidden_size)
                self.classifier = nn.Sequential(
                    nn.Linear(hidden_size, 256),
                    nn.ReLU(),
                    nn.Dropout(0.3),
                    nn.Linear(256, 1),
                    nn.Sigmoid()
                )
            
            def forward(self, x):
                # Projetar entrada
                projected = self.input_projection(x)
                
                # Aplicar atenção
                attended, attention_weights = self.attention(projected, projected, projected)
                
                # Residual connection
                output = self.norm(projected + attended)
                
                # Classificação
                anomaly_score = self.classifier(output.mean(dim=1))
                
                return anomaly_score, attention_weights
        
        return AttentionAnomalyDetector()
    
    async def detect_anomaly(self, frame: np.ndarray, camera_id: int) -> Dict[str, Any]:
        """Detectar anomalias em um frame"""
        try:
            self.total_frames_processed += 1
            
            # Pré-processar frame
            processed_frame = self._preprocess_frame(frame)
            
            # Adicionar ao buffer
            self.frame_buffer.append(processed_frame)
            
            # Detectar anomalias usando diferentes métodos
            results = {}
            
            # 1. Detecção baseada em reconstrução (autoencoder)
            reconstruction_score = await self._detect_reconstruction_anomaly(processed_frame)
            results["reconstruction"] = reconstruction_score
            
            # 2. Detecção baseada em sequência temporal (LSTM)
            temporal_score = await self._detect_temporal_anomaly()
            results["temporal"] = temporal_score
            
            # 3. Detecção baseada em atenção
            attention_score = await self._detect_attention_anomaly(processed_frame)
            results["attention"] = attention_score
            
            # 4. Detecção baseada em movimento
            motion_score = await self._detect_motion_anomaly(frame)
            results["motion"] = motion_score
            
            # Combinar scores
            combined_score = self._combine_anomaly_scores(results)
            
            # Determinar se é anomalia
            is_anomaly = combined_score > settings.ANOMALY_THRESHOLD
            
            if is_anomaly:
                self.total_anomalies_detected += 1
            
            # Adicionar ao buffer de anomalias
            self.anomaly_buffer.append({
                "timestamp": datetime.utcnow(),
                "camera_id": camera_id,
                "score": combined_score,
                "is_anomaly": is_anomaly,
                "details": results
            })
            
            return {
                "is_anomaly": is_anomaly,
                "anomaly_score": combined_score,
                "confidence": combined_score,
                "details": results,
                "timestamp": datetime.utcnow().isoformat(),
                "camera_id": camera_id
            }
            
        except Exception as e:
            logger.error(f"Erro na detecção de anomalia: {e}")
            return {
                "is_anomaly": False,
                "anomaly_score": 0.0,
                "confidence": 0.0,
                "details": {},
                "timestamp": datetime.utcnow().isoformat(),
                "camera_id": camera_id
            }
    
    def _preprocess_frame(self, frame: np.ndarray) -> np.ndarray:
        """Pré-processar frame para detecção de anomalia"""
        # Redimensionar para tamanho padrão
        resized = cv2.resize(frame, (192, 192))
        
        # Normalizar
        normalized = resized.astype(np.float32) / 255.0
        
        # Converter para tensor
        tensor = torch.FloatTensor(normalized).permute(2, 0, 1)  # HWC -> CHW
        
        return tensor
    
    async def _detect_reconstruction_anomaly(self, frame_tensor: torch.Tensor) -> float:
        """Detectar anomalia baseada em reconstrução"""
        try:
            if self.autoencoder is None:
                return 0.0
            
            with torch.no_grad():
                # Adicionar dimensão de batch
                input_tensor = frame_tensor.unsqueeze(0).to(self.device)
                
                # Reconstruir frame
                reconstructed = self.autoencoder(input_tensor)
                
                # Calcular erro de reconstrução
                mse = torch.nn.functional.mse_loss(input_tensor, reconstructed)
                
                # Converter para score de anomalia (maior erro = maior anomalia)
                anomaly_score = min(mse.item() * 10, 1.0)  # Normalizar para [0, 1]
                
                return anomaly_score
                
        except Exception as e:
            logger.error(f"Erro na detecção de reconstrução: {e}")
            return 0.0
    
    async def _detect_temporal_anomaly(self) -> float:
        """Detectar anomalia baseada em sequência temporal"""
        try:
            if self.lstm_model is None or len(self.frame_buffer) < 5:
                return 0.0
            
            # Preparar sequência temporal
            sequence = []
            for frame_tensor in list(self.frame_buffer)[-5:]:  # Últimos 5 frames
                # Extrair features (simplificado)
                features = self._extract_frame_features(frame_tensor)
                sequence.append(features)
            
            # Converter para tensor
            sequence_tensor = torch.FloatTensor(sequence).unsqueeze(0).to(self.device)
            
            with torch.no_grad():
                anomaly_score = self.lstm_model(sequence_tensor)
                return anomaly_score.item()
                
        except Exception as e:
            logger.error(f"Erro na detecção temporal: {e}")
            return 0.0
    
    async def _detect_attention_anomaly(self, frame_tensor: torch.Tensor) -> float:
        """Detectar anomalia baseada em atenção"""
        try:
            if self.attention_model is None:
                return 0.0
            
            # Extrair features do frame
            features = self._extract_frame_features(frame_tensor)
            features_tensor = torch.FloatTensor(features).unsqueeze(0).to(self.device)
            
            with torch.no_grad():
                anomaly_score, attention_weights = self.attention_model(features_tensor)
                return anomaly_score.item()
                
        except Exception as e:
            logger.error(f"Erro na detecção de atenção: {e}")
            return 0.0
    
    async def _detect_motion_anomaly(self, frame: np.ndarray) -> float:
        """Detectar anomalia baseada em movimento"""
        try:
            if len(self.frame_buffer) < 2:
                return 0.0
            
            # Converter frame atual para escala de cinza
            current_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Obter frame anterior do buffer
            previous_tensor = list(self.frame_buffer)[-2]
            previous_frame = previous_tensor.permute(1, 2, 0).cpu().numpy()
            previous_gray = cv2.cvtColor((previous_frame * 255).astype(np.uint8), cv2.COLOR_RGB2GRAY)
            
            # Calcular diferença
            diff = cv2.absdiff(current_gray, previous_gray)
            
            # Aplicar threshold
            _, thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)
            
            # Calcular área de movimento
            motion_area = np.sum(thresh > 0)
            total_area = thresh.shape[0] * thresh.shape[1]
            motion_percentage = motion_area / total_area
            
            # Detectar movimento anômalo (muito rápido ou muito lento)
            if motion_percentage > 0.3:  # Movimento excessivo
                return min(motion_percentage * 2, 1.0)
            elif motion_percentage < 0.001:  # Movimento muito baixo (possível anomalia)
                return 0.5
            else:
                return 0.0
                
        except Exception as e:
            logger.error(f"Erro na detecção de movimento: {e}")
            return 0.0
    
    def _extract_frame_features(self, frame_tensor: torch.Tensor) -> np.ndarray:
        """Extrair features de um frame"""
        try:
            # Simplificado: usar média e desvio padrão dos canais
            features = []
            
            for channel in range(frame_tensor.shape[0]):
                channel_data = frame_tensor[channel].flatten()
                features.extend([
                    channel_data.mean().item(),
                    channel_data.std().item(),
                    channel_data.min().item(),
                    channel_data.max().item()
                ])
            
            # Adicionar features de textura (simplificado)
            gray = frame_tensor.mean(dim=0)
            features.extend([
                gray.mean().item(),
                gray.std().item()
            ])
            
            return np.array(features)
            
        except Exception as e:
            logger.error(f"Erro na extração de features: {e}")
            return np.zeros(18)  # Retornar array de zeros com tamanho fixo
    
    def _combine_anomaly_scores(self, scores: Dict[str, float]) -> float:
        """Combinar diferentes scores de anomalia"""
        try:
            # Pesos para diferentes métodos
            weights = {
                "reconstruction": 0.3,
                "temporal": 0.3,
                "attention": 0.2,
                "motion": 0.2
            }
            
            # Calcular score combinado
            combined_score = 0.0
            total_weight = 0.0
            
            for method, score in scores.items():
                if method in weights:
                    combined_score += score * weights[method]
                    total_weight += weights[method]
            
            if total_weight > 0:
                combined_score /= total_weight
            
            return min(combined_score, 1.0)
            
        except Exception as e:
            logger.error(f"Erro ao combinar scores: {e}")
            return 0.0
    
    async def get_anomaly_statistics(self) -> Dict[str, Any]:
        """Obter estatísticas de detecção de anomalias"""
        return {
            "total_frames_processed": self.total_frames_processed,
            "total_anomalies_detected": self.total_anomalies_detected,
            "false_positive_count": self.false_positive_count,
            "anomaly_rate": self.total_anomalies_detected / max(self.total_frames_processed, 1),
            "buffer_size": len(self.frame_buffer),
            "recent_anomalies": len(self.anomaly_buffer),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def update_threshold(self, new_threshold: float):
        """Atualizar threshold de detecção"""
        settings.ANOMALY_THRESHOLD = new_threshold
        logger.info(f"Threshold de anomalia atualizado para: {new_threshold}")
    
    async def add_false_positive_feedback(self, frame_data: Dict[str, Any]):
        """Adicionar feedback de falso positivo para melhoria do modelo"""
        try:
            self.false_positive_count += 1
            
            # Aqui seria implementada a lógica para retreinamento
            # ou ajuste do modelo baseado no feedback
            
            logger.info("Feedback de falso positivo registrado")
            
        except Exception as e:
            logger.error(f"Erro ao processar feedback: {e}")
