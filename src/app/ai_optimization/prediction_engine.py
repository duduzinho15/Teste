"""
Motor de Predição para IA de Otimização
Faz predições usando modelos treinados para otimizar scores de priorização
"""

import asyncio
import json
import numpy as np
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional, Union
import logging
from pathlib import Path

from src.core.models import Offer
from .data_collector import FeatureSet
from .model_trainer import ModelTrainer


@dataclass
class ConfidenceScore:
    """Score de confiança da predição"""
    confidence: float
    uncertainty: float
    model_agreement: float
    created_at: datetime


@dataclass
class PredictionResult:
    """Resultado de uma predição"""
    offer_id: str
    original_score: float
    predicted_score: float
    confidence: ConfidenceScore
    model_used: str
    features_used: List[str]
    created_at: datetime


class PredictionEngine:
    """Motor de predição para IA"""
    
    def __init__(self, model_trainer: ModelTrainer):
        self.model_trainer = model_trainer
        self.logger = logging.getLogger(__name__)
        self.current_model = None
        self.current_model_name = None
        
    async def load_best_model(self) -> bool:
        """Carrega o melhor modelo disponível"""
        try:
            best_model_name = await self.model_trainer.get_best_model()
            if not best_model_name:
                self.logger.warning("Nenhum modelo treinado encontrado")
                return False
            
            self.current_model = self.model_trainer.load_model(best_model_name)
            self.current_model_name = best_model_name
            self.logger.info(f"Modelo {best_model_name} carregado com sucesso")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao carregar melhor modelo: {e}")
            return False
    
    async def load_specific_model(self, model_name: str) -> bool:
        """Carrega um modelo específico"""
        try:
            self.current_model = self.model_trainer.load_model(model_name)
            self.current_model_name = model_name
            self.logger.info(f"Modelo {model_name} carregado com sucesso")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao carregar modelo {model_name}: {e}")
            return False
    
    def _prepare_single_features(self, feature_set: FeatureSet) -> np.ndarray:
        """Prepara features de uma única oferta para predição"""
        try:
            # Features numéricas
            numerical_features = [
                feature_set.price,
                feature_set.geek_score,
                feature_set.conversion_rate,
                feature_set.click_rate,
                feature_set.engagement_rate,
                feature_set.time_of_day,
                feature_set.day_of_week,
                feature_set.category_popularity,
                feature_set.store_reputation,
                feature_set.title_length,
                float(feature_set.has_discount),
                feature_set.discount_percentage
            ]
            
            # Features categóricas
            categorical_features = [
                feature_set.season,
                feature_set.price_range,
                feature_set.category,
                feature_set.store
            ]
            
            # Normalizar features numéricas
            numerical_scaled = self.model_trainer.scaler.transform([numerical_features])
            
            # Codificar features categóricas
            categorical_encoded = []
            for i, col in enumerate(['season', 'price_range', 'category', 'store']):
                if col in self.model_trainer.label_encoders:
                    encoder = self.model_trainer.label_encoders[col]
                    # Tratar valores não vistos
                    try:
                        encoded_value = encoder.transform([categorical_features[i]])[0]
                    except ValueError:
                        # Se valor não foi visto no treinamento, usar -1
                        encoded_value = -1
                    categorical_encoded.append(encoded_value)
                else:
                    categorical_encoded.append(0)
            
            # Combinar features
            X_combined = np.hstack([numerical_scaled, [categorical_encoded]])
            
            return X_combined
            
        except Exception as e:
            self.logger.error(f"Erro ao preparar features para predição: {e}")
            raise
    
    async def predict_score(self, feature_set: FeatureSet) -> PredictionResult:
        """Faz predição de score para uma oferta"""
        try:
            if not self.current_model:
                await self.load_best_model()
                if not self.current_model:
                    raise ValueError("Nenhum modelo disponível para predição")
            
            # Preparar features
            X = self._prepare_single_features(feature_set)
            
            # Fazer predição
            predicted_score = self.current_model.predict(X)[0]
            
            # Calcular confiança (simulada - em produção seria baseada na incerteza do modelo)
            confidence = 0.8 + (np.random.random() * 0.2)  # 80-100%
            uncertainty = 1.0 - confidence
            model_agreement = 0.85 + (np.random.random() * 0.15)  # 85-100%
            
            confidence_score = ConfidenceScore(
                confidence=confidence,
                uncertainty=uncertainty,
                model_agreement=model_agreement,
                created_at=datetime.now()
            )
            
            # Features usadas
            features_used = [
                'price', 'geek_score', 'conversion_rate', 'click_rate',
                'engagement_rate', 'time_of_day', 'day_of_week',
                'category_popularity', 'store_reputation', 'title_length',
                'has_discount', 'discount_percentage', 'season', 'price_range',
                'category', 'store'
            ]
            
            return PredictionResult(
                offer_id=feature_set.offer_id,
                original_score=feature_set.geek_score,
                predicted_score=predicted_score,
                confidence=confidence_score,
                model_used=self.current_model_name,
                features_used=features_used,
                created_at=datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"Erro ao fazer predição: {e}")
            raise
    
    async def predict_batch(self, feature_sets: List[FeatureSet]) -> List[PredictionResult]:
        """Faz predições em lote"""
        try:
            if not self.current_model:
                await self.load_best_model()
                if not self.current_model:
                    raise ValueError("Nenhum modelo disponível para predição")
            
            results = []
            
            for feature_set in feature_sets:
                try:
                    result = await self.predict_score(feature_set)
                    results.append(result)
                except Exception as e:
                    self.logger.error(f"Erro ao predizer {feature_set.offer_id}: {e}")
                    continue
            
            return results
            
        except Exception as e:
            self.logger.error(f"Erro ao fazer predições em lote: {e}")
            return []
    
    async def predict_from_offer(self, offer: Offer, 
                               conversion_data: Optional[Dict] = None) -> PredictionResult:
        """Faz predição a partir de uma oferta"""
        try:
            from .data_collector import DataCollector
            
            # Criar coletor de dados
            data_collector = DataCollector()
            
            # Extrair features da oferta
            feature_set = await data_collector.extract_features_from_offer(offer, conversion_data)
            
            # Fazer predição
            return await self.predict_score(feature_set)
            
        except Exception as e:
            self.logger.error(f"Erro ao predizer a partir da oferta: {e}")
            raise
    
    async def get_prediction_insights(self, prediction: PredictionResult) -> Dict[str, Any]:
        """Obtém insights sobre uma predição"""
        try:
            score_change = prediction.predicted_score - prediction.original_score
            improvement_percentage = (score_change / prediction.original_score) * 100 if prediction.original_score > 0 else 0
            
            insights = {
                'score_change': score_change,
                'improvement_percentage': improvement_percentage,
                'confidence_level': 'Alta' if prediction.confidence.confidence > 0.8 else 'Média' if prediction.confidence.confidence > 0.6 else 'Baixa',
                'recommendation': self._get_recommendation(score_change, prediction.confidence.confidence),
                'key_factors': await self._get_key_factors(prediction),
                'model_performance': await self._get_model_performance()
            }
            
            return insights
            
        except Exception as e:
            self.logger.error(f"Erro ao obter insights da predição: {e}")
            return {}
    
    def _get_recommendation(self, score_change: float, confidence: float) -> str:
        """Gera recomendação baseada na mudança de score"""
        if confidence < 0.6:
            return "Manter score original (baixa confiança)"
        
        if score_change > 0.1:
            return "Aumentar significativamente o score"
        elif score_change > 0.05:
            return "Aumentar moderadamente o score"
        elif score_change > -0.05:
            return "Manter score atual"
        elif score_change > -0.1:
            return "Diminuir moderadamente o score"
        else:
            return "Diminuir significativamente o score"
    
    async def _get_key_factors(self, prediction: PredictionResult) -> List[str]:
        """Identifica fatores-chave que influenciaram a predição"""
        try:
            feature_importance = await self.model_trainer.get_feature_importance(self.current_model_name)
            
            # Ordenar por importância
            sorted_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
            
            # Retornar top 5 fatores
            return [feature for feature, importance in sorted_features[:5]]
            
        except Exception as e:
            self.logger.error(f"Erro ao obter fatores-chave: {e}")
            return []
    
    async def _get_model_performance(self) -> Dict[str, Any]:
        """Obtém performance do modelo atual"""
        try:
            metrics = await self.model_trainer.get_model_metrics(self.current_model_name)
            if metrics:
                latest_metrics = metrics[0]
                return {
                    'r2_score': latest_metrics.r2_score,
                    'mse': latest_metrics.mse,
                    'mae': latest_metrics.mae,
                    'cross_val_score': latest_metrics.cross_val_score,
                    'training_time': latest_metrics.training_time
                }
            
            return {}
            
        except Exception as e:
            self.logger.error(f"Erro ao obter performance do modelo: {e}")
            return {}
    
    async def compare_models(self, feature_set: FeatureSet) -> Dict[str, float]:
        """Compara predições de diferentes modelos"""
        try:
            model_names = ['random_forest', 'gradient_boosting', 'linear_regression']
            predictions = {}
            
            for model_name in model_names:
                try:
                    # Carregar modelo específico
                    await self.load_specific_model(model_name)
                    
                    # Fazer predição
                    result = await self.predict_score(feature_set)
                    predictions[model_name] = result.predicted_score
                    
                except Exception as e:
                    self.logger.error(f"Erro ao comparar modelo {model_name}: {e}")
                    continue
            
            return predictions
            
        except Exception as e:
            self.logger.error(f"Erro ao comparar modelos: {e}")
            return {}
    
    async def get_prediction_history(self, offer_id: str) -> List[PredictionResult]:
        """Obtém histórico de predições para uma oferta"""
        try:
            # Em produção, isso viria de um banco de dados
            # Por enquanto, retorna lista vazia
            return []
            
        except Exception as e:
            self.logger.error(f"Erro ao obter histórico de predições: {e}")
            return []
