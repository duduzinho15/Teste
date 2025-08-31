"""
Pesquisador de Mercado para Expansão de Categorias
Analisa tendências externas e oportunidades de mercado para expansão
"""

import asyncio
import json
import sqlite3
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from decimal import Decimal
from typing import Dict, List, Optional, Tuple
from enum import Enum
import random

from src.core.geek_prioritizer import GeekPrioritizer


class ResearchType(Enum):
    """Tipos de pesquisa de mercado"""
    TREND_ANALYSIS = "trend_analysis"
    COMPETITOR_ANALYSIS = "competitor_analysis"
    SEASONAL_ANALYSIS = "seasonal_analysis"
    DEMOGRAPHIC_ANALYSIS = "demographic_analysis"
    SOCIAL_MEDIA_ANALYSIS = "social_media_analysis"


@dataclass
class MarketTrend:
    """Tendência de mercado"""
    category: str
    trend_name: str
    trend_score: float
    growth_potential: float
    market_size: str  # "small", "medium", "large"
    competition_level: str  # "low", "medium", "high"
    seasonality: str  # "year_round", "seasonal", "event_based"
    research_date: datetime
    data_sources: List[str]


@dataclass
class ProductCategory:
    """Categoria de produto no mercado"""
    name: str
    market_volume: int
    average_price: float
    growth_rate: float
    geek_relevance: float
    competition_level: str
    entry_barrier: str  # "low", "medium", "high"
    created_at: datetime


class MarketResearcher:
    """Pesquisador de mercado para expansão de categorias"""
    
    def __init__(self, db_path: str = "market_research.db"):
        self.db_path = db_path
        self.geek_prioritizer = GeekPrioritizer()
        self._init_database()
        self._load_market_data()
    
    def _init_database(self) -> None:
        """Inicializa o banco de dados"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Tabela de tendências de mercado
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS market_trends (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        category TEXT NOT NULL,
                        trend_name TEXT NOT NULL,
                        trend_score REAL NOT NULL,
                        growth_potential REAL NOT NULL,
                        market_size TEXT NOT NULL,
                        competition_level TEXT NOT NULL,
                        seasonality TEXT NOT NULL,
                        research_date TEXT NOT NULL,
                        data_sources TEXT NOT NULL,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Tabela de categorias de produto
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS product_categories (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        market_volume INTEGER NOT NULL,
                        average_price REAL NOT NULL,
                        growth_rate REAL NOT NULL,
                        geek_relevance REAL NOT NULL,
                        competition_level TEXT NOT NULL,
                        entry_barrier TEXT NOT NULL,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Tabela de análise de competidores
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS competitor_analysis (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        category TEXT NOT NULL,
                        competitor_name TEXT NOT NULL,
                        market_share REAL NOT NULL,
                        strengths TEXT NOT NULL,
                        weaknesses TEXT NOT NULL,
                        opportunities TEXT NOT NULL,
                        analysis_date TEXT NOT NULL,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                conn.commit()
                print(f"✅ Banco de dados de pesquisa de mercado inicializado: {self.db_path}")
                
        except Exception as e:
            print(f"❌ Erro ao inicializar banco de dados: {e}")
    
    def _load_market_data(self) -> None:
        """Carrega dados de mercado pré-definidos"""
        self.market_data = {
            # Dados de mercado por categoria
            "gaming": {
                "market_volume": 2000000,
                "average_price": 150.0,
                "growth_rate": 0.15,
                "competition_level": "high",
                "entry_barrier": "medium"
            },
            "anime": {
                "market_volume": 800000,
                "average_price": 80.0,
                "growth_rate": 0.12,
                "competition_level": "medium",
                "entry_barrier": "low"
            },
            "tech": {
                "market_volume": 3500000,
                "average_price": 300.0,
                "growth_rate": 0.18,
                "competition_level": "high",
                "entry_barrier": "high"
            },
            "electronics": {
                "market_volume": 5000000,
                "average_price": 250.0,
                "growth_rate": 0.10,
                "competition_level": "high",
                "entry_barrier": "medium"
            },
            "smart_home": {
                "market_volume": 1200000,
                "average_price": 180.0,
                "growth_rate": 0.25,
                "competition_level": "medium",
                "entry_barrier": "medium"
            }
        }
    
    async def analyze_market_trends(self, categories: List[str]) -> List[MarketTrend]:
        """Analisa tendências de mercado para categorias específicas"""
        try:
            trends = []
            
            for category in categories:
                # Simular análise de tendências de mercado
                category_trends = await self._simulate_market_trends(category)
                trends.extend(category_trends)
                
                # Salvar tendências
                for trend in category_trends:
                    await self._save_market_trend(trend)
            
            print(f"📈 Analisadas {len(trends)} tendências de mercado")
            return trends
            
        except Exception as e:
            print(f"❌ Erro ao analisar tendências de mercado: {e}")
            return []
    
    async def research_product_categories(self, target_categories: List[str]) -> List[ProductCategory]:
        """Pesquisa categorias de produto no mercado"""
        try:
            categories = []
            
            for category in target_categories:
                if category in self.market_data:
                    data = self.market_data[category]
                    
                    # Calcular relevância geek
                    geek_relevance = self.geek_prioritizer.calculate_geek_score(category)
                    
                    product_category = ProductCategory(
                        name=category,
                        market_volume=data["market_volume"],
                        average_price=data["average_price"],
                        growth_rate=data["growth_rate"],
                        geek_relevance=geek_relevance,
                        competition_level=data["competition_level"],
                        entry_barrier=data["entry_barrier"],
                        created_at=datetime.now()
                    )
                    
                    categories.append(product_category)
                    await self._save_product_category(product_category)
            
            print(f"🔍 Pesquisadas {len(categories)} categorias de produto")
            return categories
            
        except Exception as e:
            print(f"❌ Erro ao pesquisar categorias: {e}")
            return []
    
    async def analyze_competitors(self, categories: List[str]) -> Dict[str, List[Dict]]:
        """Analisa competidores para categorias específicas"""
        try:
            competitor_analysis = {}
            
            for category in categories:
                competitors = await self._simulate_competitor_analysis(category)
                competitor_analysis[category] = competitors
                
                # Salvar análise
                for competitor in competitors:
                    await self._save_competitor_analysis(category, competitor)
            
            print(f"🏢 Analisados competidores para {len(categories)} categorias")
            return competitor_analysis
            
        except Exception as e:
            print(f"❌ Erro ao analisar competidores: {e}")
            return {}
    
    async def identify_market_opportunities(self, 
                                         trends: List[MarketTrend],
                                         categories: List[ProductCategory]) -> List[Dict]:
        """Identifica oportunidades de mercado"""
        try:
            opportunities = []
            
            for trend in trends:
                # Encontrar categoria correspondente
                category_data = next((cat for cat in categories if cat.name == trend.category), None)
                
                if category_data:
                    # Calcular score de oportunidade
                    opportunity_score = self._calculate_opportunity_score(trend, category_data)
                    
                    if opportunity_score > 0.7:  # Mínimo para considerar oportunidade
                        opportunity = {
                            "category": trend.category,
                            "trend_name": trend.trend_name,
                            "opportunity_score": opportunity_score,
                            "reasoning": self._generate_opportunity_reasoning(trend, category_data),
                            "expected_impact": "high" if opportunity_score > 0.8 else "medium",
                            "implementation_priority": 1 if opportunity_score > 0.9 else 2
                        }
                        opportunities.append(opportunity)
            
            print(f"🎯 Identificadas {len(opportunities)} oportunidades de mercado")
            return opportunities
            
        except Exception as e:
            print(f"❌ Erro ao identificar oportunidades: {e}")
            return []
    
    async def generate_seasonal_insights(self, categories: List[str]) -> Dict[str, List[Dict]]:
        """Gera insights sazonais para categorias"""
        try:
            seasonal_insights = {}
            
            for category in categories:
                insights = await self._analyze_seasonality(category)
                seasonal_insights[category] = insights
            
            print(f"📅 Gerados insights sazonais para {len(categories)} categorias")
            return seasonal_insights
            
        except Exception as e:
            print(f"❌ Erro ao gerar insights sazonais: {e}")
            return {}
    
    async def get_market_research_summary(self) -> Dict:
        """Retorna resumo da pesquisa de mercado"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Contar tendências
                cursor.execute("SELECT COUNT(*) FROM market_trends")
                trends_count = cursor.fetchone()[0]
                
                # Contar categorias
                cursor.execute("SELECT COUNT(*) FROM product_categories")
                categories_count = cursor.fetchone()[0]
                
                # Contar análises de competidores
                cursor.execute("SELECT COUNT(*) FROM competitor_analysis")
                competitors_count = cursor.fetchone()[0]
                
                # Top tendências
                cursor.execute("""
                    SELECT category, trend_name, trend_score 
                    FROM market_trends 
                    ORDER BY trend_score DESC 
                    LIMIT 5
                """)
                top_trends = cursor.fetchall()
                
                return {
                    "total_trends": trends_count,
                    "total_categories": categories_count,
                    "total_competitor_analyses": competitors_count,
                    "top_trends": [
                        {"category": cat, "trend": trend, "score": score} 
                        for cat, trend, score in top_trends
                    ],
                    "last_research": datetime.now().isoformat()
                }
                
        except Exception as e:
            print(f"❌ Erro ao gerar resumo: {e}")
            return {}
    
    async def _simulate_market_trends(self, category: str) -> List[MarketTrend]:
        """Simula tendências de mercado para uma categoria"""
        try:
            trends = []
            
            # Tendências específicas por categoria
            category_trends = {
                "gaming": [
                    ("Esports Growth", 0.85, 0.20, "large", "high", "year_round"),
                    ("VR Gaming", 0.75, 0.30, "medium", "medium", "year_round"),
                    ("Mobile Gaming", 0.90, 0.15, "large", "high", "year_round")
                ],
                "anime": [
                    ("Anime Merchandise", 0.80, 0.18, "medium", "medium", "year_round"),
                    ("Cosplay Culture", 0.70, 0.12, "small", "low", "seasonal"),
                    ("Manga Popularity", 0.85, 0.10, "medium", "medium", "year_round")
                ],
                "tech": [
                    ("AI Integration", 0.95, 0.35, "large", "high", "year_round"),
                    ("Smart Home", 0.88, 0.25, "large", "medium", "year_round"),
                    ("Wearable Tech", 0.82, 0.20, "medium", "high", "year_round")
                ],
                "electronics": [
                    ("Smart TVs", 0.90, 0.15, "large", "high", "year_round"),
                    ("Wireless Audio", 0.85, 0.18, "large", "medium", "year_round"),
                    ("Smart Appliances", 0.78, 0.22, "medium", "medium", "year_round")
                ]
            }
            
            if category in category_trends:
                for trend_name, score, growth, size, competition, seasonality in category_trends[category]:
                    trend = MarketTrend(
                        category=category,
                        trend_name=trend_name,
                        trend_score=score,
                        growth_potential=growth,
                        market_size=size,
                        competition_level=competition,
                        seasonality=seasonality,
                        research_date=datetime.now(),
                        data_sources=["market_analysis", "social_media", "sales_data"]
                    )
                    trends.append(trend)
            
            return trends
            
        except Exception as e:
            print(f"❌ Erro ao simular tendências: {e}")
            return []
    
    async def _simulate_competitor_analysis(self, category: str) -> List[Dict]:
        """Simula análise de competidores"""
        try:
            competitors = []
            
            # Competidores simulados por categoria
            category_competitors = {
                "gaming": [
                    {"name": "GameStore", "market_share": 0.25, "strengths": "Variedade", "weaknesses": "Preços altos"},
                    {"name": "GamerHub", "market_share": 0.20, "strengths": "Especialização", "weaknesses": "Pouca variedade"}
                ],
                "anime": [
                    {"name": "OtakuShop", "market_share": 0.30, "strengths": "Autenticidade", "weaknesses": "Preços altos"},
                    {"name": "AnimeWorld", "market_share": 0.25, "strengths": "Variedade", "weaknesses": "Qualidade"}
                ],
                "tech": [
                    {"name": "TechStore", "market_share": 0.35, "strengths": "Marcas", "weaknesses": "Preços altos"},
                    {"name": "GadgetHub", "market_share": 0.20, "strengths": "Inovação", "weaknesses": "Suporte"}
                ]
            }
            
            if category in category_competitors:
                for comp in category_competitors[category]:
                    competitor = {
                        "name": comp["name"],
                        "market_share": comp["market_share"],
                        "strengths": comp["strengths"],
                        "weaknesses": comp["weaknesses"],
                        "opportunities": "Expansão de nichos específicos"
                    }
                    competitors.append(competitor)
            
            return competitors
            
        except Exception as e:
            print(f"❌ Erro ao simular análise de competidores: {e}")
            return []
    
    async def _analyze_seasonality(self, category: str) -> List[Dict]:
        """Analisa sazonalidade de uma categoria"""
        try:
            insights = []
            
            # Análise sazonal por categoria
            seasonal_patterns = {
                "gaming": [
                    {"period": "Q4", "reason": "Natal e Black Friday", "impact": "high"},
                    {"period": "Q2", "reason": "Lançamentos de jogos", "impact": "medium"}
                ],
                "anime": [
                    {"period": "Q3", "reason": "Convenções de anime", "impact": "high"},
                    {"period": "Q4", "reason": "Presentes de Natal", "impact": "medium"}
                ],
                "tech": [
                    {"period": "Q4", "reason": "Black Friday e Cyber Monday", "impact": "high"},
                    {"period": "Q1", "reason": "Novos lançamentos", "impact": "medium"}
                ]
            }
            
            if category in seasonal_patterns:
                for pattern in seasonal_patterns[category]:
                    insight = {
                        "period": pattern["period"],
                        "reason": pattern["reason"],
                        "impact": pattern["impact"],
                        "recommendation": f"Preparar campanhas para {pattern['period']}"
                    }
                    insights.append(insight)
            
            return insights
            
        except Exception as e:
            print(f"❌ Erro ao analisar sazonalidade: {e}")
            return []
    
    def _calculate_opportunity_score(self, trend: MarketTrend, category: ProductCategory) -> float:
        """Calcula score de oportunidade"""
        try:
            score = 0.0
            
            # Fator 1: Score da tendência (30%)
            score += trend.trend_score * 0.3
            
            # Fator 2: Potencial de crescimento (25%)
            score += trend.growth_potential * 0.25
            
            # Fator 3: Relevância geek (20%)
            score += category.geek_relevance * 0.2
            
            # Fator 4: Barreira de entrada (15%)
            barrier_score = {"low": 1.0, "medium": 0.7, "high": 0.4}
            score += barrier_score.get(category.entry_barrier, 0.5) * 0.15
            
            # Fator 5: Tamanho do mercado (10%)
            market_score = {"small": 0.5, "medium": 0.7, "large": 1.0}
            score += market_score.get(trend.market_size, 0.5) * 0.1
            
            return min(1.0, score)
            
        except Exception as e:
            print(f"❌ Erro ao calcular score de oportunidade: {e}")
            return 0.0
    
    def _generate_opportunity_reasoning(self, trend: MarketTrend, category: ProductCategory) -> str:
        """Gera raciocínio para oportunidade"""
        try:
            reasoning = f"Tendência '{trend.trend_name}' em {trend.category} "
            reasoning += f"com score de {trend.trend_score:.2f} e potencial de crescimento de {trend.growth_potential:.1%}. "
            reasoning += f"Relevância geek: {category.geek_relevance:.2f}. "
            reasoning += f"Barreira de entrada: {category.entry_barrier}."
            
            return reasoning
            
        except Exception as e:
            print(f"❌ Erro ao gerar raciocínio: {e}")
            return "Oportunidade identificada baseada em análise de mercado."
    
    async def _save_market_trend(self, trend: MarketTrend) -> None:
        """Salva tendência de mercado"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO market_trends 
                    (category, trend_name, trend_score, growth_potential, market_size,
                     competition_level, seasonality, research_date, data_sources)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    trend.category, trend.trend_name, trend.trend_score,
                    trend.growth_potential, trend.market_size, trend.competition_level,
                    trend.seasonality, trend.research_date.isoformat(),
                    json.dumps(trend.data_sources)
                ))
                conn.commit()
        except Exception as e:
            print(f"❌ Erro ao salvar tendência: {e}")
    
    async def _save_product_category(self, category: ProductCategory) -> None:
        """Salva categoria de produto"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO product_categories 
                    (name, market_volume, average_price, growth_rate, geek_relevance,
                     competition_level, entry_barrier)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    category.name, category.market_volume, category.average_price,
                    category.growth_rate, category.geek_relevance, category.competition_level,
                    category.entry_barrier
                ))
                conn.commit()
        except Exception as e:
            print(f"❌ Erro ao salvar categoria: {e}")
    
    async def _save_competitor_analysis(self, category: str, competitor: Dict) -> None:
        """Salva análise de competidor"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO competitor_analysis 
                    (category, competitor_name, market_share, strengths, weaknesses, opportunities, analysis_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    category, competitor["name"], competitor["market_share"],
                    competitor["strengths"], competitor["weaknesses"],
                    competitor["opportunities"], datetime.now().isoformat()
                ))
                conn.commit()
        except Exception as e:
            print(f"❌ Erro ao salvar análise de competidor: {e}")
