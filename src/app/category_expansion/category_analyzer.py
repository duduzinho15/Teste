"""
Analisador de Categorias para Expansão
Identifica tendências e insights para expansão de categorias geek
"""

import asyncio
import json
import sqlite3
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from decimal import Decimal
from typing import Dict, List, Optional, Tuple
from enum import Enum
import statistics

from src.core.geek_prioritizer import GeekPrioritizer


class AnalysisType(Enum):
    """Tipos de análise de categoria"""
    TREND_ANALYSIS = "trend_analysis"
    PERFORMANCE_ANALYSIS = "performance_analysis"
    USER_PREFERENCE_ANALYSIS = "user_preference_analysis"
    MARKET_GAP_ANALYSIS = "market_gap_analysis"


@dataclass
class CategoryTrend:
    """Tendência de categoria"""
    category: str
    trend_score: float
    growth_rate: float
    period_days: int
    sample_size: int
    confidence_level: float
    trend_direction: str  # "increasing", "decreasing", "stable"
    analysis_date: datetime


@dataclass
class CategoryInsight:
    """Insight sobre categoria"""
    category: str
    insight_type: str
    description: str
    confidence_score: float
    data_points: int
    recommendation: str
    priority_level: str  # "high", "medium", "low"
    created_at: datetime


class CategoryAnalyzer:
    """Analisador de categorias para expansão"""
    
    def __init__(self, db_path: str = "category_analysis.db"):
        self.db_path = db_path
        self.geek_prioritizer = GeekPrioritizer()
        self._init_database()
    
    def _init_database(self) -> None:
        """Inicializa o banco de dados"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Tabela de tendências
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS category_trends (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        category TEXT NOT NULL,
                        trend_score REAL NOT NULL,
                        growth_rate REAL NOT NULL,
                        period_days INTEGER NOT NULL,
                        sample_size INTEGER NOT NULL,
                        confidence_level REAL NOT NULL,
                        trend_direction TEXT NOT NULL,
                        analysis_date TEXT NOT NULL,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Tabela de insights
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS category_insights (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        category TEXT NOT NULL,
                        insight_type TEXT NOT NULL,
                        description TEXT NOT NULL,
                        confidence_score REAL NOT NULL,
                        data_points INTEGER NOT NULL,
                        recommendation TEXT NOT NULL,
                        priority_level TEXT NOT NULL,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Tabela de dados de performance
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS category_performance (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        category TEXT NOT NULL,
                        conversion_rate REAL NOT NULL,
                        click_rate REAL NOT NULL,
                        revenue_generated REAL NOT NULL,
                        user_engagement REAL NOT NULL,
                        sample_size INTEGER NOT NULL,
                        date_recorded TEXT NOT NULL,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                conn.commit()
                print(f"✅ Banco de dados de análise de categorias inicializado: {self.db_path}")
                
        except Exception as e:
            print(f"❌ Erro ao inicializar banco de dados: {e}")
    
    async def analyze_category_trends(self, days_back: int = 30) -> List[CategoryTrend]:
        """Analisa tendências de categorias"""
        try:
            trends = []
            
            # Simular dados de tendência (em produção viria de dados reais)
            categories = [
                "gaming", "anime", "tech", "nerd", "otaku", "cosplay",
                "board_games", "collectibles", "electronics", "smart_home"
            ]
            
            for category in categories:
                # Simular análise de tendência
                trend_score = self._simulate_trend_score(category)
                growth_rate = self._simulate_growth_rate(category)
                sample_size = self._simulate_sample_size(category)
                confidence_level = min(0.95, sample_size / 1000)
                
                trend_direction = "increasing" if growth_rate > 0.05 else "decreasing" if growth_rate < -0.05 else "stable"
                
                trend = CategoryTrend(
                    category=category,
                    trend_score=trend_score,
                    growth_rate=growth_rate,
                    period_days=days_back,
                    sample_size=sample_size,
                    confidence_level=confidence_level,
                    trend_direction=trend_direction,
                    analysis_date=datetime.now()
                )
                
                trends.append(trend)
                await self._save_trend(trend)
            
            print(f"📊 Analisadas tendências de {len(trends)} categorias")
            return trends
            
        except Exception as e:
            print(f"❌ Erro ao analisar tendências: {e}")
            return []
    
    async def generate_category_insights(self, trends: List[CategoryTrend]) -> List[CategoryInsight]:
        """Gera insights baseados nas tendências"""
        try:
            insights = []
            
            for trend in trends:
                # Análise de performance
                if trend.growth_rate > 0.1 and trend.confidence_level > 0.8:
                    insight = CategoryInsight(
                        category=trend.category,
                        insight_type="high_growth_opportunity",
                        description=f"Categoria {trend.category} mostra crescimento forte de {trend.growth_rate:.1%}",
                        confidence_score=trend.confidence_level,
                        data_points=trend.sample_size,
                        recommendation="Expandir produtos nesta categoria",
                        priority_level="high",
                        created_at=datetime.now()
                    )
                    insights.append(insight)
                
                # Análise de declínio
                elif trend.growth_rate < -0.05 and trend.confidence_level > 0.7:
                    insight = CategoryInsight(
                        category=trend.category,
                        insight_type="declining_performance",
                        description=f"Categoria {trend.category} mostra declínio de {trend.growth_rate:.1%}",
                        confidence_score=trend.confidence_level,
                        data_points=trend.sample_size,
                        recommendation="Revisar estratégia para esta categoria",
                        priority_level="medium",
                        created_at=datetime.now()
                    )
                    insights.append(insight)
                
                # Análise de oportunidade
                elif trend.sample_size < 100 and trend.trend_score > 0.6:
                    insight = CategoryInsight(
                        category=trend.category,
                        insight_type="untapped_potential",
                        description=f"Categoria {trend.category} tem potencial não explorado",
                        confidence_score=trend.confidence_level,
                        data_points=trend.sample_size,
                        recommendation="Investir em mais produtos desta categoria",
                        priority_level="medium",
                        created_at=datetime.now()
                    )
                    insights.append(insight)
            
            # Salvar insights
            for insight in insights:
                await self._save_insight(insight)
            
            print(f"💡 Gerados {len(insights)} insights de categoria")
            return insights
            
        except Exception as e:
            print(f"❌ Erro ao gerar insights: {e}")
            return []
    
    async def analyze_user_preferences(self, feedback_data: List[Dict]) -> Dict[str, float]:
        """Analisa preferências dos usuários por categoria"""
        try:
            category_preferences = {}
            
            for feedback in feedback_data:
                category = feedback.get('category', '')
                rating = feedback.get('rating', 0)
                
                if category and rating > 0:
                    if category not in category_preferences:
                        category_preferences[category] = []
                    category_preferences[category].append(rating)
            
            # Calcular scores médios
            category_scores = {}
            for category, ratings in category_preferences.items():
                if len(ratings) >= 3:  # Mínimo de 3 avaliações
                    avg_rating = statistics.mean(ratings)
                    category_scores[category] = avg_rating
            
            print(f"📈 Analisadas preferências de {len(category_scores)} categorias")
            return category_scores
            
        except Exception as e:
            print(f"❌ Erro ao analisar preferências: {e}")
            return {}
    
    async def identify_expansion_opportunities(self, 
                                            trends: List[CategoryTrend],
                                            insights: List[CategoryInsight],
                                            user_preferences: Dict[str, float]) -> List[str]:
        """Identifica oportunidades de expansão"""
        try:
            opportunities = []
            
            # Critérios para expansão
            for trend in trends:
                score = 0
                
                # Critério 1: Crescimento forte
                if trend.growth_rate > 0.08:
                    score += 3
                elif trend.growth_rate > 0.05:
                    score += 2
                
                # Critério 2: Alta confiança
                if trend.confidence_level > 0.8:
                    score += 2
                elif trend.confidence_level > 0.6:
                    score += 1
                
                # Critério 3: Preferência dos usuários
                user_score = user_preferences.get(trend.category, 0)
                if user_score > 4.0:
                    score += 3
                elif user_score > 3.5:
                    score += 2
                
                # Critério 4: Tamanho da amostra
                if trend.sample_size > 500:
                    score += 1
                
                # Se score >= 6, é uma oportunidade
                if score >= 6:
                    opportunities.append(trend.category)
            
            print(f"🎯 Identificadas {len(opportunities)} oportunidades de expansão")
            return opportunities
            
        except Exception as e:
            print(f"❌ Erro ao identificar oportunidades: {e}")
            return []
    
    def _simulate_trend_score(self, category: str) -> float:
        """Simula score de tendência para uma categoria"""
        import random
        base_scores = {
            "gaming": 0.85,
            "anime": 0.78,
            "tech": 0.92,
            "nerd": 0.73,
            "otaku": 0.81,
            "cosplay": 0.67,
            "board_games": 0.76,
            "collectibles": 0.82,
            "electronics": 0.88,
            "smart_home": 0.79
        }
        base = base_scores.get(category, 0.5)
        return base + random.uniform(-0.1, 0.1)
    
    def _simulate_growth_rate(self, category: str) -> float:
        """Simula taxa de crescimento para uma categoria"""
        import random
        growth_rates = {
            "gaming": 0.12,
            "anime": 0.08,
            "tech": 0.15,
            "nerd": 0.06,
            "otaku": 0.09,
            "cosplay": 0.04,
            "board_games": 0.07,
            "collectibles": 0.11,
            "electronics": 0.13,
            "smart_home": 0.10
        }
        base = growth_rates.get(category, 0.05)
        return base + random.uniform(-0.03, 0.03)
    
    def _simulate_sample_size(self, category: str) -> int:
        """Simula tamanho da amostra para uma categoria"""
        import random
        base_sizes = {
            "gaming": 1200,
            "anime": 800,
            "tech": 1500,
            "nerd": 600,
            "otaku": 900,
            "cosplay": 400,
            "board_games": 700,
            "collectibles": 1000,
            "electronics": 1300,
            "smart_home": 950
        }
        base = base_sizes.get(category, 500)
        return base + random.randint(-100, 100)
    
    async def _save_trend(self, trend: CategoryTrend) -> None:
        """Salva tendência no banco de dados"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO category_trends 
                    (category, trend_score, growth_rate, period_days, sample_size, 
                     confidence_level, trend_direction, analysis_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    trend.category, trend.trend_score, trend.growth_rate,
                    trend.period_days, trend.sample_size, trend.confidence_level,
                    trend.trend_direction, trend.analysis_date.isoformat()
                ))
                conn.commit()
        except Exception as e:
            print(f"❌ Erro ao salvar tendência: {e}")
    
    async def _save_insight(self, insight: CategoryInsight) -> None:
        """Salva insight no banco de dados"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO category_insights 
                    (category, insight_type, description, confidence_score, 
                     data_points, recommendation, priority_level)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    insight.category, insight.insight_type, insight.description,
                    insight.confidence_score, insight.data_points, insight.recommendation,
                    insight.priority_level
                ))
                conn.commit()
        except Exception as e:
            print(f"❌ Erro ao salvar insight: {e}")
    
    async def get_analysis_summary(self) -> Dict:
        """Retorna resumo da análise"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Contar tendências
                cursor.execute("SELECT COUNT(*) FROM category_trends")
                trends_count = cursor.fetchone()[0]
                
                # Contar insights
                cursor.execute("SELECT COUNT(*) FROM category_insights")
                insights_count = cursor.fetchone()[0]
                
                # Categorias mais promissoras
                cursor.execute("""
                    SELECT category, AVG(trend_score) as avg_score 
                    FROM category_trends 
                    GROUP BY category 
                    ORDER BY avg_score DESC 
                    LIMIT 5
                """)
                top_categories = cursor.fetchall()
                
                return {
                    "total_trends": trends_count,
                    "total_insights": insights_count,
                    "top_categories": [{"category": cat, "score": score} for cat, score in top_categories],
                    "last_analysis": datetime.now().isoformat()
                }
                
        except Exception as e:
            print(f"❌ Erro ao gerar resumo: {e}")
            return {}
