"""
Sistema de Análise de Feedback dos Usuários
Analisa feedback coletado e gera insights para ajuste de scores
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any, Tuple
from decimal import Decimal
from enum import Enum
import sqlite3
from collections import defaultdict, Counter
import statistics

from .feedback_collector import FeedbackCollector, FeedbackType, UserFeedback
from src.core.geek_prioritizer import GeekPrioritizer


class AnalysisType(Enum):
    """Tipos de análise disponíveis"""
    USER_PREFERENCES = "user_preferences"
    CATEGORY_PERFORMANCE = "category_performance"
    PRODUCT_PERFORMANCE = "product_performance"
    TREND_ANALYSIS = "trend_analysis"
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    CONVERSION_ANALYSIS = "conversion_analysis"


@dataclass
class UserPreference:
    """Preferências de um usuário"""
    user_id: str
    category: str
    preference_score: float
    confidence: float
    sample_size: int
    last_updated: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        data = asdict(self)
        data['last_updated'] = self.last_updated.isoformat()
        return data


@dataclass
class CategoryPerformance:
    """Performance de uma categoria"""
    category: str
    total_feedback: int
    positive_feedback: int
    negative_feedback: int
    average_rating: float
    conversion_rate: float
    geek_score: float
    performance_score: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return asdict(self)


@dataclass
class FeedbackInsight:
    """Insight gerado a partir do feedback"""
    insight_type: str
    title: str
    description: str
    confidence: float
    data: Dict[str, Any]
    recommendations: List[str]
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data


@dataclass
class ScoreAdjustment:
    """Ajuste de score baseado no feedback"""
    category: str
    current_score: float
    suggested_score: float
    adjustment_factor: float
    confidence: float
    reasoning: str
    supporting_data: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return asdict(self)


class FeedbackAnalyzer:
    """Sistema de análise de feedback dos usuários"""
    
    def __init__(self, feedback_collector: FeedbackCollector):
        self.feedback_collector = feedback_collector
        self.geek_prioritizer = GeekPrioritizer()
        self.logger = logging.getLogger(__name__)
    
    async def analyze_user_preferences(
        self,
        user_id: str,
        days: int = 30
    ) -> List[UserPreference]:
        """Analisa preferências de um usuário específico"""
        try:
            # Obter histórico de feedback do usuário
            feedbacks = await self.feedback_collector.get_user_feedback_history(user_id, days)
            
            if not feedbacks:
                return []
            
            # Agrupar feedback por categoria
            category_feedback = defaultdict(list)
            
            for feedback in feedbacks:
                # Extrair categoria do metadata ou inferir do offer_id
                category = self._extract_category_from_feedback(feedback)
                if category:
                    category_feedback[category].append(feedback)
            
            # Calcular preferências por categoria
            preferences = []
            for category, category_feedbacks in category_feedback.items():
                preference = await self._calculate_category_preference(
                    user_id, category, category_feedbacks
                )
                if preference:
                    preferences.append(preference)
            
            # Ordenar por score de preferência
            preferences.sort(key=lambda x: x.preference_score, reverse=True)
            
            self.logger.info(f"Analisadas preferências para usuário {user_id}: {len(preferences)} categorias")
            return preferences
            
        except Exception as e:
            self.logger.error(f"Erro ao analisar preferências do usuário: {e}")
            return []
    
    async def analyze_category_performance(
        self,
        days: int = 30
    ) -> List[CategoryPerformance]:
        """Analisa performance de todas as categorias"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            with sqlite3.connect(self.feedback_collector.db_path) as conn:
                cursor = conn.cursor()
                
                # Obter todos os feedbacks do período
                cursor.execute("""
                    SELECT feedback_type, feedback_value, metadata
                    FROM user_feedback
                    WHERE timestamp >= ?
                """, (cutoff_date.isoformat(),))
                
                feedbacks = cursor.fetchall()
            
            # Agrupar por categoria
            category_data = defaultdict(lambda: {
                'total': 0,
                'positive': 0,
                'negative': 0,
                'ratings': [],
                'conversions': 0
            })
            
            for feedback_type, feedback_value, metadata in feedbacks:
                category = self._extract_category_from_metadata(metadata)
                if not category:
                    continue
                
                data = category_data[category]
                data['total'] += 1
                
                # Classificar feedback
                if feedback_type == FeedbackType.RATING.value:
                    try:
                        rating = float(feedback_value)
                        data['ratings'].append(rating)
                        if rating >= 4:
                            data['positive'] += 1
                        elif rating <= 2:
                            data['negative'] += 1
                    except ValueError:
                        pass
                
                elif feedback_type == FeedbackType.LIKE.value:
                    data['positive'] += 1
                
                elif feedback_type == FeedbackType.DISLIKE.value:
                    data['negative'] += 1
                
                elif feedback_type == FeedbackType.PURCHASE.value:
                    data['conversions'] += 1
            
            # Calcular performance por categoria
            performances = []
            for category, data in category_data.items():
                if data['total'] == 0:
                    continue
                
                # Calcular métricas
                positive_rate = data['positive'] / data['total'] if data['total'] > 0 else 0
                negative_rate = data['negative'] / data['total'] if data['total'] > 0 else 0
                avg_rating = statistics.mean(data['ratings']) if data['ratings'] else 0
                conversion_rate = data['conversions'] / data['total'] if data['total'] > 0 else 0
                
                # Calcular geek score
                geek_score = self.geek_prioritizer.calculate_geek_score(category)
                
                # Calcular performance score (média ponderada)
                performance_score = (
                    positive_rate * 0.3 +
                    avg_rating * 0.2 +
                    conversion_rate * 0.4 +
                    (1 - negative_rate) * 0.1
                )
                
                performance = CategoryPerformance(
                    category=category,
                    total_feedback=data['total'],
                    positive_feedback=data['positive'],
                    negative_feedback=data['negative'],
                    average_rating=avg_rating,
                    conversion_rate=conversion_rate,
                    geek_score=geek_score,
                    performance_score=performance_score
                )
                
                performances.append(performance)
            
            # Ordenar por performance score
            performances.sort(key=lambda x: x.performance_score, reverse=True)
            
            self.logger.info(f"Analisada performance de {len(performances)} categorias")
            return performances
            
        except Exception as e:
            self.logger.error(f"Erro ao analisar performance das categorias: {e}")
            return []
    
    async def generate_feedback_insights(
        self,
        days: int = 30
    ) -> List[FeedbackInsight]:
        """Gera insights a partir do feedback coletado"""
        try:
            insights = []
            
            # Analisar performance das categorias
            performances = await self.analyze_category_performance(days)
            
            # Insight 1: Categorias com melhor performance
            if performances:
                top_category = performances[0]
                insights.append(FeedbackInsight(
                    insight_type="top_performing_category",
                    title=f"Categoria com Melhor Performance: {top_category.category}",
                    description=f"A categoria {top_category.category} apresentou a melhor performance com score de {top_category.performance_score:.2f}",
                    confidence=0.8,
                    data=top_category.to_dict(),
                    recommendations=[
                        f"Aumentar priorização da categoria {top_category.category}",
                        "Considerar expandir produtos nesta categoria",
                        "Replicar estratégias de sucesso para outras categorias"
                    ],
                    timestamp=datetime.now()
                ))
            
            # Insight 2: Categorias com baixa performance
            low_performance = [p for p in performances if p.performance_score < 0.3]
            if low_performance:
                insights.append(FeedbackInsight(
                    insight_type="low_performing_categories",
                    title=f"{len(low_performance)} Categorias com Baixa Performance",
                    description=f"Identificadas {len(low_performance)} categorias com performance abaixo do esperado",
                    confidence=0.7,
                    data={"categories": [p.category for p in low_performance]},
                    recommendations=[
                        "Revisar estratégia de seleção de produtos",
                        "Considerar ajustar scores de priorização",
                        "Investigar feedback negativo específico"
                    ],
                    timestamp=datetime.now()
                ))
            
            # Insight 3: Análise de conversão
            high_conversion = [p for p in performances if p.conversion_rate > 0.1]
            if high_conversion:
                insights.append(FeedbackInsight(
                    insight_type="high_conversion_categories",
                    title=f"{len(high_conversion)} Categorias com Alta Conversão",
                    description=f"Identificadas {len(high_conversion)} categorias com taxa de conversão superior a 10%",
                    confidence=0.9,
                    data={"categories": [p.category for p in high_conversion]},
                    recommendations=[
                        "Priorizar produtos destas categorias",
                        "Aumentar exposição destas categorias",
                        "Replicar estratégias de preço e apresentação"
                    ],
                    timestamp=datetime.now()
                ))
            
            # Insight 4: Tendências de feedback
            trend_insight = await self._analyze_feedback_trends(days)
            if trend_insight:
                insights.append(trend_insight)
            
            self.logger.info(f"Gerados {len(insights)} insights de feedback")
            return insights
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar insights: {e}")
            return []
    
    async def suggest_score_adjustments(
        self,
        days: int = 30
    ) -> List[ScoreAdjustment]:
        """Sugere ajustes de score baseado no feedback"""
        try:
            adjustments = []
            
            # Analisar performance das categorias
            performances = await self.analyze_category_performance(days)
            
            for performance in performances:
                # Calcular score atual (usando geek_prioritizer)
                current_score = performance.geek_score
                
                # Calcular score sugerido baseado na performance
                performance_factor = performance.performance_score
                conversion_factor = min(performance.conversion_rate * 2, 1.0)  # Máximo 100%
                rating_factor = performance.average_rating / 5.0
                
                # Score sugerido (média ponderada)
                suggested_score = (
                    current_score * 0.4 +  # Manter 40% do score atual
                    performance_factor * 0.3 +  # 30% baseado na performance
                    conversion_factor * 0.2 +  # 20% baseado na conversão
                    rating_factor * 0.1  # 10% baseado na avaliação
                )
                
                # Calcular fator de ajuste
                adjustment_factor = suggested_score / current_score if current_score > 0 else 1.0
                
                # Calcular confiança baseada no tamanho da amostra
                confidence = min(performance.total_feedback / 50, 1.0)  # Máximo confiança com 50+ feedbacks
                
                # Gerar reasoning
                reasoning = self._generate_adjustment_reasoning(performance, adjustment_factor)
                
                adjustment = ScoreAdjustment(
                    category=performance.category,
                    current_score=current_score,
                    suggested_score=suggested_score,
                    adjustment_factor=adjustment_factor,
                    confidence=confidence,
                    reasoning=reasoning,
                    supporting_data=performance.to_dict()
                )
                
                adjustments.append(adjustment)
            
            # Ordenar por magnitude do ajuste
            adjustments.sort(key=lambda x: abs(x.adjustment_factor - 1.0), reverse=True)
            
            self.logger.info(f"Sugeridos {len(adjustments)} ajustes de score")
            return adjustments
            
        except Exception as e:
            self.logger.error(f"Erro ao sugerir ajustes de score: {e}")
            return []
    
    async def _calculate_category_preference(
        self,
        user_id: str,
        category: str,
        feedbacks: List[UserFeedback]
    ) -> Optional[UserPreference]:
        """Calcula preferência de um usuário por uma categoria"""
        try:
            if not feedbacks:
                return None
            
            # Calcular scores positivos e negativos
            positive_score = 0
            negative_score = 0
            total_weight = 0
            
            for feedback in feedbacks:
                weight = self._get_feedback_weight(feedback)
                total_weight += weight
                
                if feedback.feedback_type in [FeedbackType.LIKE, FeedbackType.RATING]:
                    if feedback.feedback_type == FeedbackType.RATING:
                        rating = float(feedback.feedback_value)
                        if rating >= 4:
                            positive_score += weight * (rating / 5)
                        elif rating <= 2:
                            negative_score += weight
                    else:
                        positive_score += weight
                
                elif feedback.feedback_type == FeedbackType.DISLIKE:
                    negative_score += weight
                
                elif feedback.feedback_type == FeedbackType.PURCHASE:
                    positive_score += weight * 2  # Compra tem peso maior
            
            if total_weight == 0:
                return None
            
            # Calcular score de preferência
            preference_score = (positive_score - negative_score) / total_weight
            preference_score = max(0, min(1, preference_score))  # Normalizar entre 0 e 1
            
            # Calcular confiança baseada no número de feedbacks
            confidence = min(len(feedbacks) / 10, 1.0)  # Máximo confiança com 10+ feedbacks
            
            return UserPreference(
                user_id=user_id,
                category=category,
                preference_score=preference_score,
                confidence=confidence,
                sample_size=len(feedbacks),
                last_updated=datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"Erro ao calcular preferência de categoria: {e}")
            return None
    
    def _get_feedback_weight(self, feedback: UserFeedback) -> float:
        """Calcula peso de um feedback baseado na idade e tipo"""
        # Peso baseado no tipo de feedback
        type_weights = {
            FeedbackType.CLICK: 1.0,
            FeedbackType.LIKE: 2.0,
            FeedbackType.DISLIKE: 2.0,
            FeedbackType.RATING: 3.0,
            FeedbackType.PURCHASE: 5.0,
            FeedbackType.SHARE: 2.5,
            FeedbackType.SAVE: 2.0
        }
        
        base_weight = type_weights.get(feedback.feedback_type, 1.0)
        
        # Aplicar decaimento temporal (feedback mais recente tem mais peso)
        days_old = (datetime.now() - feedback.timestamp).days
        time_decay = max(0.1, 1.0 - (days_old / 30))  # Mínimo 10% após 30 dias
        
        return base_weight * time_decay
    
    def _extract_category_from_feedback(self, feedback: UserFeedback) -> Optional[str]:
        """Extrai categoria de um feedback"""
        if feedback.metadata and 'category' in feedback.metadata:
            return feedback.metadata['category']
        
        # Tentar extrair do offer_id ou metadata
        if feedback.metadata and 'message_text' in feedback.metadata:
            text = feedback.metadata['message_text'].lower()
            return self._extract_category_from_text(text)
        
        return None
    
    def _extract_category_from_metadata(self, metadata: str) -> Optional[str]:
        """Extrai categoria de metadata JSON"""
        try:
            if metadata and isinstance(metadata, str):
                data = json.loads(metadata)
                return data.get('category')
        except (json.JSONDecodeError, TypeError):
            pass
        return None
    
    def _extract_category_from_text(self, text: str) -> Optional[str]:
        """Extrai categoria de texto"""
        # Mapeamento de palavras-chave para categorias
        category_keywords = {
            'games': ['jogo', 'game', 'gamer', 'console', 'playstation', 'xbox', 'nintendo'],
            'anime': ['anime', 'manga', 'otaku', 'japonês', 'japonesa'],
            'tech': ['tech', 'tecnologia', 'smartphone', 'notebook', 'pc', 'computador'],
            'geek': ['geek', 'nerd', 'cosplay', 'figurinha', 'action figure'],
            'electronics': ['eletrônico', 'eletrodoméstico', 'smart tv', 'microondas', 'fone']
        }
        
        for category, keywords in category_keywords.items():
            if any(keyword in text for keyword in keywords):
                return category
        
        return None
    
    def _generate_adjustment_reasoning(self, performance: CategoryPerformance, adjustment_factor: float) -> str:
        """Gera explicação para ajuste de score"""
        if adjustment_factor > 1.2:
            return f"Alta performance ({performance.performance_score:.2f}) e conversão ({performance.conversion_rate:.1%}) sugerem aumento de priorização"
        elif adjustment_factor < 0.8:
            return f"Baixa performance ({performance.performance_score:.2f}) e conversão ({performance.conversion_rate:.1%}) sugerem redução de priorização"
        else:
            return f"Performance equilibrada ({performance.performance_score:.2f}) - manter priorização atual"
    
    async def _analyze_feedback_trends(self, days: int) -> Optional[FeedbackInsight]:
        """Analisa tendências de feedback ao longo do tempo"""
        try:
            # Implementar análise de tendências temporais
            # Por enquanto, retorna None
            return None
        except Exception as e:
            self.logger.error(f"Erro ao analisar tendências: {e}")
            return None
