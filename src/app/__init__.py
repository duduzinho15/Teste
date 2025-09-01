"""
app package for Garimpeiro Geek
Sistema de Recomendações de Ofertas via Telegram
"""

__version__ = "1.0.0"
__author__ = "Garimpeiro Geek Team"

# Sistemas implementados
from .production_testing import ProductionTestRunner
from .conversion_monitoring import ConversionTracker, ConversionAnalyzer, ConversionDashboard
from .user_feedback import FeedbackCollector, FeedbackAnalyzer, ScoreAdjuster, FeedbackDashboard
from .category_expansion import CategoryAnalyzer, CategoryExpander, MarketResearcher, CategoryOptimizer
from .ai_optimization import AIOptimizer, DataCollector, ModelTrainer, PredictionEngine, OptimizationDashboard
from .unified_dashboard import UnifiedDashboard, unified_dashboard

__all__ = [
    # Sistemas principais
    'ProductionTestRunner',
    'ConversionTracker', 'ConversionAnalyzer', 'ConversionDashboard',
    'FeedbackCollector', 'FeedbackAnalyzer', 'ScoreAdjuster', 'FeedbackDashboard',
    'CategoryAnalyzer', 'CategoryExpander', 'MarketResearcher', 'CategoryOptimizer',
    'AIOptimizer', 'DataCollector', 'ModelTrainer', 'PredictionEngine', 'OptimizationDashboard',
    # Sistema unificado
    'UnifiedDashboard', 'unified_dashboard'
]
