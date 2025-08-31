"""
Sistema de Feedback dos Usuários para Ajuste de Scores
Permite coletar feedback e ajustar automaticamente scores de priorização geek
"""

from .feedback_collector import FeedbackCollector, FeedbackType, UserFeedback
from .feedback_analyzer import FeedbackAnalyzer, ScoreAdjustment
from .score_adjuster import ScoreAdjuster, AdjustmentConfig
from .feedback_dashboard import FeedbackDashboard

__all__ = [
    'FeedbackCollector',
    'FeedbackAnalyzer', 
    'ScoreAdjuster',
    'FeedbackDashboard',
    'FeedbackType',
    'UserFeedback',
    'ScoreAdjustment',
    'AdjustmentConfig'
]
