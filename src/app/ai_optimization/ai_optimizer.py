"""
Otimizador Principal de IA para Priorização
Coordena todo o sistema de IA para otimização automática de scores
"""

import asyncio
import json
import sqlite3
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional, Union
import logging
from pathlib import Path
from decimal import Decimal

from src.core.models import Offer
from src.core.geek_prioritizer import GeekPrioritizer
from .data_collector import DataCollector, FeatureSet, TrainingData
from .model_trainer import ModelTrainer, TrainingResult, ModelMetrics
from .prediction_engine import PredictionEngine, PredictionResult, ConfidenceScore


@dataclass
class OptimizationModel:
    """Modelo de otimização"""
    model_name: str
    version: str
    performance_score: float
    last_updated: datetime
    is_active: bool


@dataclass
class ModelConfig:
    """Configuração do modelo"""
    auto_retrain: bool
    retrain_interval_days: int
    min_data_points: int
    confidence_threshold: float
    batch_size: int


class AIOptimizer:
    """Otimizador principal de IA"""
    
    def __init__(self, config: Optional[ModelConfig] = None):
        self.config = config or ModelConfig(
            auto_retrain=True,
            retrain_interval_days=7,
            min_data_points=1000,
            confidence_threshold=0.7,
            batch_size=100
        )
        
        self.logger = logging.getLogger(__name__)
        self.geek_prioritizer = GeekPrioritizer()
        
        # Componentes do sistema
        self.data_collector = DataCollector()
        self.model_trainer = ModelTrainer()
        self.prediction_engine = PredictionEngine(self.model_trainer)
        
        # Estado do sistema
        self.is_initialized = False
        self.last_training = None
        self.current_model = None
        
        self._init_database()
    
    def _init_database(self):
        """Inicializa banco de dados do otimizador"""
        try:
            db_path = Path("data/ai_optimizer.db")
            db_path.parent.mkdir(parents=True, exist_ok=True)
            
            with sqlite3.connect(db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS optimization_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        offer_id TEXT NOT NULL,
                        original_score REAL NOT NULL,
                        optimized_score REAL NOT NULL,
                        confidence REAL NOT NULL,
                        model_used TEXT NOT NULL,
                        optimization_date TIMESTAMP NOT NULL
                    )
                """)
                
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS model_performance (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        model_name TEXT NOT NULL,
                        performance_score REAL NOT NULL,
                        total_optimizations INTEGER NOT NULL,
                        avg_improvement REAL NOT NULL,
                        last_updated TIMESTAMP NOT NULL
                    )
                """)
                
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS system_status (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        is_initialized BOOLEAN NOT NULL,
                        current_model TEXT,
                        last_training TIMESTAMP,
                        total_optimizations INTEGER NOT NULL,
                        last_updated TIMESTAMP NOT NULL
                    )
                """)
                
                conn.commit()
                self.logger.info("Banco de dados do otimizador inicializado")
                
        except Exception as e:
            self.logger.error(f"Erro ao inicializar banco do otimizador: {e}")
    
    async def initialize(self) -> bool:
        """Inicializa o sistema de IA"""
        try:
            self.logger.info("Inicializando sistema de IA para otimização...")
            
            # Verificar se há dados suficientes
            training_data = await self.data_collector.load_training_data()
            if len(training_data.features) < self.config.min_data_points:
                self.logger.info("Dados insuficientes, coletando dados históricos...")
                await self._collect_initial_data()
            
            # Verificar se há modelos treinados
            best_model = await self.model_trainer.get_best_model()
            if not best_model:
                self.logger.info("Nenhum modelo encontrado, treinando modelos...")
                await self._train_initial_models()
            
            # Carregar melhor modelo
            await self.prediction_engine.load_best_model()
            
            # Atualizar status
            self.is_initialized = True
            await self._update_system_status()
            
            self.logger.info("Sistema de IA inicializado com sucesso")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao inicializar sistema de IA: {e}")
            return False
    
    async def _collect_initial_data(self):
        """Coleta dados iniciais para treinamento"""
        try:
            # Coletar dados históricos
            historical_data = await self.data_collector.collect_historical_data(days_back=30)
            
            # Gerar target scores (simulados)
            target_scores = []
            for feature in historical_data:
                # Score baseado em performance simulada
                base_score = feature.geek_score
                performance_bonus = feature.conversion_rate * 0.3 + feature.engagement_rate * 0.2
                target_score = min(1.0, base_score + performance_bonus)
                target_scores.append(target_score)
            
            # Salvar dados
            await self.data_collector.save_training_data(historical_data, target_scores)
            
        except Exception as e:
            self.logger.error(f"Erro ao coletar dados iniciais: {e}")
    
    async def _train_initial_models(self):
        """Treina modelos iniciais"""
        try:
            training_data = await self.data_collector.load_training_data()
            if len(training_data.features) < self.config.min_data_points:
                raise ValueError("Dados insuficientes para treinamento")
            
            # Treinar todos os modelos
            results = await self.model_trainer.train_all_models(training_data)
            
            if results:
                self.last_training = datetime.now()
                self.logger.info(f"Treinados {len(results)} modelos com sucesso")
            
        except Exception as e:
            self.logger.error(f"Erro ao treinar modelos iniciais: {e}")
    
    async def optimize_offer(self, offer: Offer, 
                           conversion_data: Optional[Dict] = None) -> PredictionResult:
        """Otimiza score de uma oferta específica"""
        try:
            if not self.is_initialized:
                await self.initialize()
            
            # Fazer predição
            prediction = await self.prediction_engine.predict_from_offer(offer, conversion_data)
            
            # Verificar confiança
            if prediction.confidence.confidence < self.config.confidence_threshold:
                self.logger.warning(f"Baixa confiança na predição: {prediction.confidence.confidence}")
            
            # Salvar histórico
            await self._save_optimization_history(prediction)
            
            return prediction
            
        except Exception as e:
            self.logger.error(f"Erro ao otimizar oferta: {e}")
            raise
    
    async def optimize_batch(self, offers: List[Offer], 
                           conversion_data: Optional[Dict] = None) -> List[PredictionResult]:
        """Otimiza scores de múltiplas ofertas"""
        try:
            if not self.is_initialized:
                await self.initialize()
            
            results = []
            
            # Processar em lotes
            for i in range(0, len(offers), self.config.batch_size):
                batch = offers[i:i + self.config.batch_size]
                
                batch_results = []
                for offer in batch:
                    try:
                        result = await self.optimize_offer(offer, conversion_data)
                        batch_results.append(result)
                    except Exception as e:
                        self.logger.error(f"Erro ao otimizar oferta {offer.url}: {e}")
                        continue
                
                results.extend(batch_results)
                
                # Pequena pausa entre lotes
                await asyncio.sleep(0.1)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Erro ao otimizar lote de ofertas: {e}")
            return []
    
    async def auto_retrain_if_needed(self) -> bool:
        """Retreina modelos automaticamente se necessário"""
        try:
            if not self.config.auto_retrain:
                return False
            
            # Verificar se é necessário retreinar
            if self.last_training:
                days_since_training = (datetime.now() - self.last_training).days
                if days_since_training < self.config.retrain_interval_days:
                    return False
            
            # Verificar se há novos dados suficientes
            training_data = await self.data_collector.load_training_data()
            if len(training_data.features) < self.config.min_data_points:
                self.logger.info("Dados insuficientes para retreinamento")
                return False
            
            self.logger.info("Iniciando retreinamento automático...")
            
            # Retreinar modelos
            results = await self.model_trainer.train_all_models(training_data)
            
            if results:
                self.last_training = datetime.now()
                await self._update_system_status()
                
                # Recarregar melhor modelo
                await self.prediction_engine.load_best_model()
                
                self.logger.info("Retreinamento concluído com sucesso")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Erro no retreinamento automático: {e}")
            return False
    
    async def get_optimization_insights(self, prediction: PredictionResult) -> Dict[str, Any]:
        """Obtém insights sobre uma otimização"""
        try:
            insights = await self.prediction_engine.get_prediction_insights(prediction)
            
            # Adicionar insights específicos do otimizador
            optimization_stats = await self._get_optimization_stats()
            
            insights.update({
                'system_stats': optimization_stats,
                'optimization_date': prediction.created_at.isoformat(),
                'model_version': await self._get_model_version(prediction.model_used)
            })
            
            return insights
            
        except Exception as e:
            self.logger.error(f"Erro ao obter insights de otimização: {e}")
            return {}
    
    async def _save_optimization_history(self, prediction: PredictionResult):
        """Salva histórico de otimização"""
        try:
            db_path = Path("data/ai_optimizer.db")
            with sqlite3.connect(db_path) as conn:
                conn.execute("""
                    INSERT INTO optimization_history (
                        offer_id, original_score, optimized_score, confidence,
                        model_used, optimization_date
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    prediction.offer_id,
                    prediction.original_score,
                    prediction.predicted_score,
                    prediction.confidence.confidence,
                    prediction.model_used,
                    prediction.created_at
                ))
                
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"Erro ao salvar histórico de otimização: {e}")
    
    async def _update_system_status(self):
        """Atualiza status do sistema"""
        try:
            db_path = Path("data/ai_optimizer.db")
            with sqlite3.connect(db_path) as conn:
                # Obter total de otimizações
                cursor = conn.execute("SELECT COUNT(*) FROM optimization_history")
                total_optimizations = cursor.fetchone()[0]
                
                # Atualizar ou inserir status
                conn.execute("""
                    INSERT OR REPLACE INTO system_status (
                        id, is_initialized, current_model, last_training,
                        total_optimizations, last_updated
                    ) VALUES (1, ?, ?, ?, ?, ?)
                """, (
                    self.is_initialized,
                    self.prediction_engine.current_model_name,
                    self.last_training,
                    total_optimizations,
                    datetime.now()
                ))
                
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"Erro ao atualizar status do sistema: {e}")
    
    async def _get_optimization_stats(self) -> Dict[str, Any]:
        """Obtém estatísticas de otimização"""
        try:
            db_path = Path("data/ai_optimizer.db")
            with sqlite3.connect(db_path) as conn:
                # Estatísticas gerais
                cursor = conn.execute("""
                    SELECT 
                        COUNT(*) as total_optimizations,
                        AVG(optimized_score - original_score) as avg_improvement,
                        AVG(confidence) as avg_confidence
                    FROM optimization_history
                """)
                
                row = cursor.fetchone()
                if row:
                    return {
                        'total_optimizations': row[0],
                        'avg_improvement': row[1] or 0.0,
                        'avg_confidence': row[2] or 0.0
                    }
                
                return {}
                
        except Exception as e:
            self.logger.error(f"Erro ao obter estatísticas de otimização: {e}")
            return {}
    
    async def _get_model_version(self, model_name: str) -> str:
        """Obtém versão do modelo"""
        try:
            metrics = await self.model_trainer.get_model_metrics(model_name)
            if metrics:
                return f"{model_name}_v{len(metrics)}"
            return f"{model_name}_v1"
            
        except Exception as e:
            self.logger.error(f"Erro ao obter versão do modelo: {e}")
            return f"{model_name}_v1"
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Obtém status completo do sistema"""
        try:
            db_path = Path("data/ai_optimizer.db")
            with sqlite3.connect(db_path) as conn:
                cursor = conn.execute("""
                    SELECT is_initialized, current_model, last_training,
                           total_optimizations, last_updated
                    FROM system_status
                    WHERE id = 1
                """)
                
                row = cursor.fetchone()
                if row:
                    return {
                        'is_initialized': bool(row[0]),
                        'current_model': row[1],
                        'last_training': row[2],
                        'total_optimizations': row[3],
                        'last_updated': row[4],
                        'config': asdict(self.config)
                    }
                
                return {
                    'is_initialized': self.is_initialized,
                    'current_model': None,
                    'last_training': None,
                    'total_optimizations': 0,
                    'last_updated': datetime.now().isoformat(),
                    'config': asdict(self.config)
                }
                
        except Exception as e:
            self.logger.error(f"Erro ao obter status do sistema: {e}")
            return {}
    
    async def update_config(self, new_config: ModelConfig):
        """Atualiza configuração do sistema"""
        try:
            self.config = new_config
            self.logger.info("Configuração atualizada")
            
        except Exception as e:
            self.logger.error(f"Erro ao atualizar configuração: {e}")
    
    async def get_optimization_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Obtém histórico de otimizações"""
        try:
            db_path = Path("data/ai_optimizer.db")
            with sqlite3.connect(db_path) as conn:
                cursor = conn.execute("""
                    SELECT offer_id, original_score, optimized_score, confidence,
                           model_used, optimization_date
                    FROM optimization_history
                    ORDER BY optimization_date DESC
                    LIMIT ?
                """, (limit,))
                
                history = []
                for row in cursor.fetchall():
                    history.append({
                        'offer_id': row[0],
                        'original_score': row[1],
                        'optimized_score': row[2],
                        'confidence': row[3],
                        'model_used': row[4],
                        'optimization_date': row[5]
                    })
                
                return history
                
        except Exception as e:
            self.logger.error(f"Erro ao obter histórico de otimizações: {e}")
            return []
