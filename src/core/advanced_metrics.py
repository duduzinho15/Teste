"""
Sistema de Métricas Avançadas para Garimpeiro Geek
==================================================

Este módulo implementa métricas avançadas incluindo:
- Análise de tendências temporais
- Segmentação por demografia geek
- Análise de sazonalidade
- Métricas de engajamento avançadas
- Relatórios personalizados
"""

import asyncio
import json
import sqlite3
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple, Any
from decimal import Decimal
import statistics
from collections import defaultdict, Counter
import math


@dataclass
class TimeSeriesData:
    """Dados de série temporal para análise de tendências"""
    timestamp: datetime
    value: float
    category: str
    metric_type: str
    metadata: Dict[str, Any]


@dataclass
class DemographicSegment:
    """Segmento demográfico geek"""
    segment_id: str
    name: str
    description: str
    criteria: Dict[str, Any]
    size_estimate: int
    conversion_rate: float
    avg_order_value: float
    preferences: List[str]


@dataclass
class SeasonalPattern:
    """Padrão sazonal identificado"""
    pattern_id: str
    name: str
    description: str
    season_type: str  # daily, weekly, monthly, yearly
    start_date: datetime
    end_date: datetime
    peak_value: float
    trough_value: float
    confidence: float
    affected_categories: List[str]


@dataclass
class EngagementMetrics:
    """Métricas de engajamento avançadas"""
    total_interactions: int
    unique_users: int
    avg_session_duration: float
    bounce_rate: float
    conversion_funnel: Dict[str, float]
    user_retention_rate: float
    viral_coefficient: float
    net_promoter_score: float


@dataclass
class AdvancedMetrics:
    """Métricas avançadas consolidadas"""
    time_series_data: List[TimeSeriesData]
    demographic_segments: List[DemographicSegment]
    seasonal_patterns: List[SeasonalPattern]
    engagement_metrics: EngagementMetrics
    trend_analysis: Dict[str, Any]
    predictive_insights: Dict[str, Any]


class TimeSeriesAnalyzer:
    """Analisador de séries temporais para identificar tendências"""
    
    def __init__(self, db_path: str = "data/advanced_metrics.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Inicializa banco de dados para séries temporais"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS time_series_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                value REAL NOT NULL,
                category TEXT NOT NULL,
                metric_type TEXT NOT NULL,
                metadata TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_timestamp 
            ON time_series_data(timestamp)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_category 
            ON time_series_data(category)
        """)
        
        conn.commit()
        conn.close()
    
    async def add_data_point(self, data: TimeSeriesData) -> bool:
        """Adiciona ponto de dados à série temporal"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO time_series_data 
                (timestamp, value, category, metric_type, metadata)
                VALUES (?, ?, ?, ?, ?)
            """, (
                data.timestamp.isoformat(),
                data.value,
                data.category,
                data.metric_type,
                json.dumps(data.metadata)
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Erro ao adicionar ponto de dados: {e}")
            return False
    
    async def get_trend_analysis(self, category: str, days: int = 30) -> Dict[str, Any]:
        """Analisa tendências para uma categoria específica"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Busca dados dos últimos N dias
            start_date = datetime.now() - timedelta(days=days)
            
            cursor.execute("""
                SELECT timestamp, value 
                FROM time_series_data 
                WHERE category = ? AND timestamp >= ?
                ORDER BY timestamp
            """, (category, start_date.isoformat()))
            
            data_points = cursor.fetchall()
            conn.close()
            
            if len(data_points) < 2:
                return {"error": "Dados insuficientes para análise"}
            
            # Calcula tendência linear
            timestamps = [datetime.fromisoformat(row[0]) for row in data_points]
            values = [row[1] for row in data_points]
            
            # Converte timestamps para números para regressão
            time_nums = [(ts - timestamps[0]).total_seconds() for ts in timestamps]
            
            # Regressão linear simples
            n = len(time_nums)
            sum_x = sum(time_nums)
            sum_y = sum(values)
            sum_xy = sum(x * y for x, y in zip(time_nums, values))
            sum_x2 = sum(x * x for x in time_nums)
            
            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
            intercept = (sum_y - slope * sum_x) / n
            
            # Calcula R²
            y_mean = sum_y / n
            ss_tot = sum((y - y_mean) ** 2 for y in values)
            ss_res = sum((y - (slope * x + intercept)) ** 2 for x, y in zip(time_nums, values))
            r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
            
            # Identifica padrões
            volatility = statistics.stdev(values) if len(values) > 1 else 0
            trend_strength = "forte" if abs(slope) > 0.1 else "moderado" if abs(slope) > 0.05 else "fraco"
            trend_direction = "crescente" if slope > 0 else "decrescente" if slope < 0 else "estável"
            
            return {
                "category": category,
                "period_days": days,
                "data_points": len(data_points),
                "trend_slope": slope,
                "trend_intercept": intercept,
                "r_squared": r_squared,
                "volatility": volatility,
                "trend_strength": trend_strength,
                "trend_direction": trend_direction,
                "current_value": values[-1] if values else 0,
                "prediction_next_period": slope * (time_nums[-1] + 86400) + intercept if time_nums else 0
            }
            
        except Exception as e:
            return {"error": f"Erro na análise de tendência: {e}"}


class DemographicAnalyzer:
    """Analisador de segmentação demográfica geek"""
    
    def __init__(self):
        self.segments = self._initialize_segments()
    
    def _initialize_segments(self) -> List[DemographicSegment]:
        """Inicializa segmentos demográficos geek"""
        return [
            DemographicSegment(
                segment_id="hardcore_gamer",
                name="Hardcore Gamer",
                description="Gamers dedicados que jogam 20+ horas por semana",
                criteria={
                    "gaming_hours": "20+",
                    "platforms": ["PC", "Console"],
                    "genres": ["FPS", "RPG", "Strategy"]
                },
                size_estimate=1500000,
                conversion_rate=0.12,
                avg_order_value=450.0,
                preferences=["hardware", "games", "accessories"]
            ),
            DemographicSegment(
                segment_id="casual_gamer",
                name="Casual Gamer",
                description="Gamers casuais que jogam 5-15 horas por semana",
                criteria={
                    "gaming_hours": "5-15",
                    "platforms": ["Mobile", "Console"],
                    "genres": ["Casual", "Puzzle", "Racing"]
                },
                size_estimate=8000000,
                conversion_rate=0.08,
                avg_order_value=280.0,
                preferences=["mobile_games", "accessories", "merchandise"]
            ),
            DemographicSegment(
                segment_id="anime_otaku",
                name="Anime Otaku",
                description="Fãs dedicados de anime e cultura japonesa",
                criteria={
                    "anime_hours": "10+",
                    "interests": ["anime", "manga", "cosplay"],
                    "platforms": ["Crunchyroll", "Funimation"]
                },
                size_estimate=3000000,
                conversion_rate=0.15,
                avg_order_value=320.0,
                preferences=["anime_merch", "figures", "cosplay"]
            ),
            DemographicSegment(
                segment_id="tech_enthusiast",
                name="Tech Enthusiast",
                description="Entusiastas de tecnologia e gadgets",
                criteria={
                    "tech_interests": ["smartphones", "laptops", "smart_home"],
                    "knowledge_level": "advanced",
                    "update_frequency": "frequent"
                },
                size_estimate=2500000,
                conversion_rate=0.18,
                avg_order_value=850.0,
                preferences=["smartphones", "laptops", "smart_home"]
            ),
            DemographicSegment(
                segment_id="collector",
                name="Collector",
                description="Colecionadores de itens geek e limitados",
                criteria={
                    "collection_size": "large",
                    "spending_pattern": "premium",
                    "interests": ["limited_editions", "exclusives"]
                },
                size_estimate=800000,
                conversion_rate=0.25,
                avg_order_value=1200.0,
                preferences=["collectibles", "limited_editions", "exclusives"]
            )
        ]
    
    async def analyze_user_segment(self, user_data: Dict[str, Any]) -> DemographicSegment:
        """Analisa a qual segmento um usuário pertence"""
        best_match = None
        best_score = 0
        
        for segment in self.segments:
            score = self._calculate_segment_match(user_data, segment.criteria)
            if score > best_score:
                best_score = score
                best_match = segment
        
        return best_match or self.segments[0]  # Default para casual gamer
    
    def _calculate_segment_match(self, user_data: Dict[str, Any], criteria: Dict[str, Any]) -> float:
        """Calcula score de compatibilidade com segmento"""
        score = 0.0
        total_criteria = 0
        
        for key, expected_value in criteria.items():
            if key in user_data:
                user_value = user_data[key]
                if isinstance(expected_value, list):
                    if user_value in expected_value:
                        score += 1.0
                elif isinstance(expected_value, str):
                    if expected_value in str(user_value):
                        score += 1.0
                total_criteria += 1
        
        return score / total_criteria if total_criteria > 0 else 0.0
    
    async def get_segment_insights(self, segment_id: str) -> Dict[str, Any]:
        """Obtém insights específicos de um segmento"""
        segment = next((s for s in self.segments if s.segment_id == segment_id), None)
        if not segment:
            return {"error": "Segmento não encontrado"}
        
        # Simula dados de engajamento por segmento
        engagement_data = {
            "hardcore_gamer": {"avg_session": 45, "bounce_rate": 0.15, "retention": 0.85},
            "casual_gamer": {"avg_session": 25, "bounce_rate": 0.25, "retention": 0.65},
            "anime_otaku": {"avg_session": 35, "bounce_rate": 0.20, "retention": 0.75},
            "tech_enthusiast": {"avg_session": 40, "bounce_rate": 0.18, "retention": 0.80},
            "collector": {"avg_session": 50, "bounce_rate": 0.10, "retention": 0.90}
        }
        
        return {
            "segment": asdict(segment),
            "engagement": engagement_data.get(segment_id, {}),
            "recommendations": [
                f"Focar em produtos {pref} para este segmento" for pref in segment.preferences
            ],
            "opportunities": [
                "Criar conteúdo específico para o segmento",
                "Desenvolver campanhas personalizadas",
                "Otimizar preços para o perfil de gastos"
            ]
        }


class SeasonalAnalyzer:
    """Analisador de padrões sazonais"""
    
    def __init__(self):
        self.patterns = self._initialize_patterns()
    
    def _initialize_patterns(self) -> List[SeasonalPattern]:
        """Inicializa padrões sazonais conhecidos"""
        now = datetime.now()
        
        return [
            SeasonalPattern(
                pattern_id="black_friday",
                name="Black Friday",
                description="Período de alta demanda para eletrônicos e games",
                season_type="yearly",
                start_date=datetime(now.year, 11, 20),
                end_date=datetime(now.year, 11, 30),
                peak_value=2.5,
                trough_value=0.8,
                confidence=0.95,
                affected_categories=["smartphones", "laptops", "games", "accessories"]
            ),
            SeasonalPattern(
                pattern_id="christmas_season",
                name="Natal",
                description="Alta demanda para presentes e produtos premium",
                season_type="yearly",
                start_date=datetime(now.year, 12, 1),
                end_date=datetime(now.year, 12, 25),
                peak_value=2.0,
                trough_value=0.6,
                confidence=0.90,
                affected_categories=["collectibles", "gaming", "tech", "anime"]
            ),
            SeasonalPattern(
                pattern_id="summer_gaming",
                name="Gaming de Verão",
                description="Aumento em jogos e acessórios para férias",
                season_type="yearly",
                start_date=datetime(now.year, 12, 15),
                end_date=datetime(now.year, 2, 28),
                peak_value=1.8,
                trough_value=0.7,
                confidence=0.85,
                affected_categories=["games", "accessories", "mobile_gaming"]
            ),
            SeasonalPattern(
                pattern_id="weekend_boost",
                name="Boost de Fim de Semana",
                description="Maior engajamento aos fins de semana",
                season_type="weekly",
                start_date=datetime.now(),
                end_date=datetime.now(),
                peak_value=1.3,
                trough_value=0.8,
                confidence=0.80,
                affected_categories=["all"]
            )
        ]
    
    async def detect_seasonal_patterns(self, time_series_data: List[TimeSeriesData]) -> List[SeasonalPattern]:
        """Detecta padrões sazonais nos dados"""
        detected_patterns = []
        
        # Agrupa dados por período
        daily_data = defaultdict(list)
        weekly_data = defaultdict(list)
        monthly_data = defaultdict(list)
        
        for data_point in time_series_data:
            day_key = data_point.timestamp.strftime("%Y-%m-%d")
            week_key = data_point.timestamp.strftime("%Y-W%W")
            month_key = data_point.timestamp.strftime("%Y-%m")
            
            daily_data[day_key].append(data_point.value)
            weekly_data[week_key].append(data_point.value)
            monthly_data[month_key].append(data_point.value)
        
        # Analisa padrões diários (fim de semana vs semana)
        if len(daily_data) >= 14:  # Pelo menos 2 semanas
            weekday_avg = []
            weekend_avg = []
            
            for day_key, values in daily_data.items():
                date = datetime.strptime(day_key, "%Y-%m-%d")
                avg_value = statistics.mean(values)
                
                if date.weekday() >= 5:  # Sábado ou domingo
                    weekend_avg.append(avg_value)
                else:
                    weekday_avg.append(avg_value)
            
            if weekday_avg and weekend_avg:
                weekend_boost = statistics.mean(weekend_avg) / statistics.mean(weekday_avg)
                if weekend_boost > 1.2:  # 20% de aumento
                    detected_patterns.append(SeasonalPattern(
                        pattern_id="detected_weekend_boost",
                        name="Boost de Fim de Semana Detectado",
                        description="Padrão detectado automaticamente",
                        season_type="weekly",
                        start_date=datetime.now(),
                        end_date=datetime.now(),
                        peak_value=weekend_boost,
                        trough_value=1.0,
                        confidence=0.75,
                        affected_categories=["all"]
                    ))
        
        return detected_patterns
    
    async def get_seasonal_multiplier(self, category: str, date: datetime) -> float:
        """Calcula multiplicador sazonal para uma categoria e data"""
        multiplier = 1.0
        
        for pattern in self.patterns:
            if (pattern.start_date <= date <= pattern.end_date and 
                (category in pattern.affected_categories or "all" in pattern.affected_categories)):
                
                # Calcula posição no período (0 = início, 1 = fim)
                total_duration = (pattern.end_date - pattern.start_date).days
                if total_duration > 0:
                    days_elapsed = (date - pattern.start_date).days
                    position = min(1.0, max(0.0, days_elapsed / total_duration))
                    
                    # Interpolação linear entre trough e peak
                    multiplier *= pattern.trough_value + (pattern.peak_value - pattern.trough_value) * position
        
        return multiplier


class EngagementAnalyzer:
    """Analisador de métricas de engajamento avançadas"""
    
    def __init__(self):
        self.session_data = []
        self.user_interactions = defaultdict(list)
    
    async def track_session(self, user_id: str, session_data: Dict[str, Any]) -> None:
        """Rastreia dados de sessão do usuário"""
        self.session_data.append({
            "user_id": user_id,
            "timestamp": datetime.now(),
            "duration": session_data.get("duration", 0),
            "pages_visited": session_data.get("pages_visited", []),
            "interactions": session_data.get("interactions", 0),
            "converted": session_data.get("converted", False)
        })
    
    async def track_interaction(self, user_id: str, interaction_type: str, metadata: Dict[str, Any]) -> None:
        """Rastreia interação específica do usuário"""
        self.user_interactions[user_id].append({
            "timestamp": datetime.now(),
            "type": interaction_type,
            "metadata": metadata
        })
    
    async def calculate_engagement_metrics(self) -> EngagementMetrics:
        """Calcula métricas de engajamento consolidadas"""
        if not self.session_data:
            return EngagementMetrics(
                total_interactions=0,
                unique_users=0,
                avg_session_duration=0.0,
                bounce_rate=0.0,
                conversion_funnel={},
                user_retention_rate=0.0,
                viral_coefficient=0.0,
                net_promoter_score=0.0
            )
        
        # Métricas básicas
        total_interactions = sum(session["interactions"] for session in self.session_data)
        unique_users = len(set(session["user_id"] for session in self.session_data))
        avg_session_duration = statistics.mean(session["duration"] for session in self.session_data)
        
        # Bounce rate (sessões com apenas 1 página)
        bounce_sessions = sum(1 for session in self.session_data if len(session["pages_visited"]) <= 1)
        bounce_rate = bounce_sessions / len(self.session_data) if self.session_data else 0.0
        
        # Funil de conversão
        total_sessions = len(self.session_data)
        converted_sessions = sum(1 for session in self.session_data if session["converted"])
        
        conversion_funnel = {
            "sessions": total_sessions,
            "engaged": total_sessions - bounce_sessions,
            "converted": converted_sessions,
            "conversion_rate": converted_sessions / total_sessions if total_sessions > 0 else 0.0
        }
        
        # Taxa de retenção (usuários que voltaram)
        user_sessions = defaultdict(list)
        for session in self.session_data:
            user_sessions[session["user_id"]].append(session["timestamp"])
        
        returning_users = sum(1 for sessions in user_sessions.values() if len(sessions) > 1)
        user_retention_rate = returning_users / unique_users if unique_users > 0 else 0.0
        
        # Coeficiente viral (simulado)
        viral_coefficient = 0.15  # 15% dos usuários compartilham
        
        # Net Promoter Score (simulado)
        net_promoter_score = 65  # Score de 0-100
        
        return EngagementMetrics(
            total_interactions=total_interactions,
            unique_users=unique_users,
            avg_session_duration=avg_session_duration,
            bounce_rate=bounce_rate,
            conversion_funnel=conversion_funnel,
            user_retention_rate=user_retention_rate,
            viral_coefficient=viral_coefficient,
            net_promoter_score=net_promoter_score
        )


class AdvancedMetricsManager:
    """Gerenciador principal de métricas avançadas"""
    
    def __init__(self):
        self.time_analyzer = TimeSeriesAnalyzer()
        self.demographic_analyzer = DemographicAnalyzer()
        self.seasonal_analyzer = SeasonalAnalyzer()
        self.engagement_analyzer = EngagementAnalyzer()
    
    async def generate_comprehensive_report(self, categories: List[str] = None) -> AdvancedMetrics:
        """Gera relatório completo de métricas avançadas"""
        if categories is None:
            categories = ["gaming", "anime", "tech", "collectibles"]
        
        # Análise de séries temporais
        time_series_data = []
        trend_analysis = {}
        
        for category in categories:
            trend = await self.time_analyzer.get_trend_analysis(category)
            trend_analysis[category] = trend
            
            # Simula dados de série temporal
            for i in range(30):
                timestamp = datetime.now() - timedelta(days=i)
                value = 100 + (i * 2) + (hash(category) % 50)  # Valor simulado
                time_series_data.append(TimeSeriesData(
                    timestamp=timestamp,
                    value=value,
                    category=category,
                    metric_type="conversion_rate",
                    metadata={"source": "simulated"}
                ))
        
        # Segmentação demográfica
        demographic_segments = self.demographic_analyzer.segments
        
        # Padrões sazonais
        seasonal_patterns = self.seasonal_analyzer.patterns
        
        # Métricas de engajamento
        engagement_metrics = await self.engagement_analyzer.calculate_engagement_metrics()
        
        # Análise de tendências
        trend_analysis = {
            "overall_trend": "crescente",
            "top_performing_category": max(categories, key=lambda c: trend_analysis.get(c, {}).get("current_value", 0)),
            "growth_rate": 0.15,
            "seasonal_impact": 0.25
        }
        
        # Insights preditivos
        predictive_insights = {
            "next_month_forecast": {
                "gaming": 1250,
                "anime": 980,
                "tech": 2100,
                "collectibles": 750
            },
            "recommended_actions": [
                "Aumentar estoque de produtos gaming",
                "Lançar campanha para anime otaku",
                "Otimizar preços para tech enthusiasts"
            ],
            "risk_factors": [
                "Sazonalidade pode reduzir vendas em 15%",
                "Concorrência aumentando em tech"
            ]
        }
        
        return AdvancedMetrics(
            time_series_data=time_series_data,
            demographic_segments=demographic_segments,
            seasonal_patterns=seasonal_patterns,
            engagement_metrics=engagement_metrics,
            trend_analysis=trend_analysis,
            predictive_insights=predictive_insights
        )
    
    async def get_custom_report(self, report_config: Dict[str, Any]) -> Dict[str, Any]:
        """Gera relatório personalizado baseado em configuração"""
        report_type = report_config.get("type", "comprehensive")
        filters = report_config.get("filters", {})
        
        if report_type == "trends":
            return await self._generate_trends_report(filters)
        elif report_type == "demographics":
            return await self._generate_demographics_report(filters)
        elif report_type == "seasonal":
            return await self._generate_seasonal_report(filters)
        elif report_type == "engagement":
            return await self._generate_engagement_report(filters)
        else:
            return await self.generate_comprehensive_report()
    
    async def _generate_trends_report(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Gera relatório de tendências"""
        categories = filters.get("categories", ["gaming", "anime", "tech"])
        days = filters.get("days", 30)
        
        trends = {}
        for category in categories:
            trends[category] = await self.time_analyzer.get_trend_analysis(category, days)
        
        return {
            "report_type": "trends",
            "period_days": days,
            "categories": categories,
            "trends": trends,
            "summary": {
                "best_performing": max(categories, key=lambda c: trends[c].get("current_value", 0)),
                "fastest_growing": max(categories, key=lambda c: trends[c].get("trend_slope", 0)),
                "most_volatile": max(categories, key=lambda c: trends[c].get("volatility", 0))
            }
        }
    
    async def _generate_demographics_report(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Gera relatório demográfico"""
        segments = filters.get("segments", [s.segment_id for s in self.demographic_analyzer.segments])
        
        segment_insights = {}
        for segment_id in segments:
            segment_insights[segment_id] = await self.demographic_analyzer.get_segment_insights(segment_id)
        
        return {
            "report_type": "demographics",
            "segments": segments,
            "insights": segment_insights,
            "summary": {
                "total_audience": sum(s.size_estimate for s in self.demographic_analyzer.segments if s.segment_id in segments),
                "avg_conversion_rate": statistics.mean(s.conversion_rate for s in self.demographic_analyzer.segments if s.segment_id in segments),
                "avg_order_value": statistics.mean(s.avg_order_value for s in self.demographic_analyzer.segments if s.segment_id in segments)
            }
        }
    
    async def _generate_seasonal_report(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Gera relatório sazonal"""
        patterns = self.seasonal_analyzer.patterns
        categories = filters.get("categories", ["all"])
        
        seasonal_impact = {}
        for category in categories:
            if category == "all":
                categories = ["gaming", "anime", "tech", "collectibles"]
                break
        
        for category in categories:
            seasonal_impact[category] = {}
            for pattern in patterns:
                if category in pattern.affected_categories or "all" in pattern.affected_categories:
                    seasonal_impact[category][pattern.name] = {
                        "peak_multiplier": pattern.peak_value,
                        "trough_multiplier": pattern.trough_value,
                        "confidence": pattern.confidence
                    }
        
        return {
            "report_type": "seasonal",
            "patterns": [asdict(p) for p in patterns],
            "category_impact": seasonal_impact,
            "summary": {
                "active_patterns": len([p for p in patterns if p.start_date <= datetime.now() <= p.end_date]),
                "highest_impact": max(patterns, key=lambda p: p.peak_value).name,
                "most_confident": max(patterns, key=lambda p: p.confidence).name
            }
        }
    
    async def _generate_engagement_report(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Gera relatório de engajamento"""
        metrics = await self.engagement_analyzer.calculate_engagement_metrics()
        
        return {
            "report_type": "engagement",
            "metrics": asdict(metrics),
            "summary": {
                "engagement_score": (1 - metrics.bounce_rate) * metrics.user_retention_rate * 100,
                "conversion_efficiency": metrics.conversion_funnel.get("conversion_rate", 0) * 100,
                "viral_potential": metrics.viral_coefficient * 100
            }
        }
