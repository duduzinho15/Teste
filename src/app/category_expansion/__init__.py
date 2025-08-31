"""
Sistema de Expansão de Categorias Geek
Expande automaticamente categorias baseado no feedback dos usuários e análise de mercado
"""

from .category_analyzer import CategoryAnalyzer, CategoryTrend, CategoryInsight
from .category_expander import CategoryExpander, ExpansionSuggestion, CategoryMapping
from .market_researcher import MarketResearcher, MarketTrend, ProductCategory
from .category_optimizer import CategoryOptimizer, OptimizationResult, CategoryScore

__all__ = [
    'CategoryAnalyzer',
    'CategoryExpander', 
    'MarketResearcher',
    'CategoryOptimizer',
    'CategoryTrend',
    'CategoryInsight',
    'ExpansionSuggestion',
    'CategoryMapping',
    'MarketTrend',
    'ProductCategory',
    'OptimizationResult',
    'CategoryScore'
]
