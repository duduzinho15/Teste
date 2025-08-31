"""
Sistema de IA para Otimização Automática de Priorização
Utiliza machine learning para otimizar automaticamente scores de priorização geek
"""

from .ai_optimizer import AIOptimizer, OptimizationModel, ModelConfig
from .data_collector import DataCollector, TrainingData, FeatureSet
from .model_trainer import ModelTrainer, TrainingResult, ModelMetrics
from .prediction_engine import PredictionEngine, PredictionResult, ConfidenceScore
from .optimization_dashboard import OptimizationDashboard

__all__ = [
    'AIOptimizer',
    'DataCollector', 
    'ModelTrainer',
    'PredictionEngine',
    'OptimizationDashboard',
    'OptimizationModel',
    'ModelConfig',
    'TrainingData',
    'FeatureSet',
    'TrainingResult',
    'ModelMetrics',
    'PredictionResult',
    'ConfidenceScore'
]
