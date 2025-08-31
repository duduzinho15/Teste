"""
Analisador de Conversões Geek vs Geral
Gera insights, tendências e recomendações baseadas nos dados de conversão
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import statistics
from decimal import Decimal

from .conversion_tracker import ConversionTracker, ConversionMetrics, ConversionEvent


@dataclass
class ConversionInsight:
    """Insight de conversão"""
    insight_type: str  # "trend", "anomaly", "opportunity", "warning"
    title: str
    description: str
    severity: str  # "low", "medium", "high", "critical"
    confidence: float  # 0.0 a 1.0
    recommendations: List[str]
    data_points: Dict[str, Any]
    timestamp: str


@dataclass
class ConversionTrend:
    """Tendência de conversão"""
    metric_name: str
    period: str
    trend_direction: str  # "up", "down", "stable"
    change_percentage: float
    significance: str  # "low", "medium", "high"
    description: str
    data_points: List[float]


@dataclass
class ConversionReport:
    """Relatório de análise de conversão"""
    timestamp: str
    period: str
    summary: str
    insights: List[ConversionInsight]
    trends: List[ConversionTrend]
    recommendations: List[str]
    performance_score: float  # 0.0 a 1.0
    geek_performance: Dict[str, Any]
    general_performance: Dict[str, Any]
    category_analysis: Dict[str, Any]


class ConversionAnalyzer:
    """
    Analisador de conversões que gera insights e tendências
    """
    
    def __init__(self, tracker: ConversionTracker):
        self.logger = logging.getLogger(__name__)
        self.tracker = tracker
        
        # Configurações de análise
        self.analysis_thresholds = {
            "significant_change": 0.15,  # 15% de mudança
            "anomaly_threshold": 2.0,    # 2 desvios padrão
            "trend_periods": 7,          # 7 períodos para análise de tendência
            "min_data_points": 10        # Mínimo de pontos para análise
        }
    
    async def analyze_conversions(self, period: str = "day") -> ConversionReport:
        """
        Analisa conversões e gera relatório completo
        """
        self.logger.info(f"Iniciando análise de conversões para período: {period}")
        
        try:
            # Calcular métricas atuais
            current_metrics = await self.tracker.calculate_conversion_metrics(period)
            
            # Gerar insights
            insights = await self._generate_insights(current_metrics, period)
            
            # Analisar tendências
            trends = await self._analyze_trends(period)
            
            # Calcular score de performance
            performance_score = self._calculate_performance_score(current_metrics)
            
            # Analisar performance geek vs geral
            geek_performance = self._analyze_geek_performance(current_metrics)
            general_performance = self._analyze_general_performance(current_metrics)
            
            # Analisar categorias
            category_analysis = self._analyze_categories(current_metrics)
            
            # Gerar recomendações
            recommendations = self._generate_recommendations(insights, trends, current_metrics)
            
            # Criar resumo
            summary = self._create_summary(current_metrics, insights, performance_score)
            
            report = ConversionReport(
                timestamp=datetime.now().isoformat(),
                period=period,
                summary=summary,
                insights=insights,
                trends=trends,
                recommendations=recommendations,
                performance_score=performance_score,
                geek_performance=geek_performance,
                general_performance=general_performance,
                category_analysis=category_analysis
            )
            
            self.logger.info(f"Análise concluída: {len(insights)} insights, {len(trends)} tendências")
            return report
            
        except Exception as e:
            self.logger.error(f"Erro na análise de conversões: {e}")
            return self._create_empty_report(period)
    
    async def _generate_insights(self, metrics: ConversionMetrics, period: str) -> List[ConversionInsight]:
        """Gera insights baseados nas métricas"""
        insights = []
        
        try:
            # Insight 1: Performance geek vs geral
            geek_ratio = metrics.geek_conversions / max(metrics.total_conversions, 1)
            if geek_ratio > 0.6:
                insights.append(ConversionInsight(
                    insight_type="opportunity",
                    title="Alto Engajamento Geek",
                    description=f"Conversões geek representam {geek_ratio:.1%} do total - excelente performance!",
                    severity="low",
                    confidence=0.9,
                    recommendations=[
                        "Manter foco em produtos geek",
                        "Expandir categorias geek populares",
                        "Otimizar campanhas para audiência geek"
                    ],
                    data_points={"geek_ratio": geek_ratio, "total_conversions": metrics.total_conversions},
                    timestamp=datetime.now().isoformat()
                ))
            elif geek_ratio < 0.3:
                insights.append(ConversionInsight(
                    insight_type="warning",
                    title="Baixo Engajamento Geek",
                    description=f"Conversões geek representam apenas {geek_ratio:.1%} do total",
                    severity="medium",
                    confidence=0.8,
                    recommendations=[
                        "Revisar estratégia de priorização geek",
                        "Analisar qualidade dos produtos geek",
                        "Investigar preferências da audiência"
                    ],
                    data_points={"geek_ratio": geek_ratio, "total_conversions": metrics.total_conversions},
                    timestamp=datetime.now().isoformat()
                ))
            
            # Insight 2: Taxa de conversão
            if metrics.geek_conversion_rate > metrics.general_conversion_rate * 1.5:
                insights.append(ConversionInsight(
                    insight_type="trend",
                    title="Geek Supera Conversão Geral",
                    description=f"Taxa de conversão geek ({metrics.geek_conversion_rate:.2%}) é {metrics.geek_conversion_rate/metrics.general_conversion_rate:.1f}x maior que geral",
                    severity="low",
                    confidence=0.85,
                    recommendations=[
                        "Aumentar oferta de produtos geek",
                        "Focar marketing em audiência geek",
                        "Otimizar experiência para usuários geek"
                    ],
                    data_points={
                        "geek_rate": metrics.geek_conversion_rate,
                        "general_rate": metrics.general_conversion_rate,
                        "ratio": metrics.geek_conversion_rate/metrics.general_conversion_rate
                    },
                    timestamp=datetime.now().isoformat()
                ))
            
            # Insight 3: Receita por conversão
            if metrics.geek_revenue > 0 and metrics.general_revenue > 0:
                geek_avg = metrics.geek_revenue / max(metrics.geek_conversions, 1)
                general_avg = metrics.general_revenue / max(metrics.general_conversions, 1)
                
                if geek_avg > general_avg * Decimal("1.3"):
                    insights.append(ConversionInsight(
                        insight_type="opportunity",
                        title="Maior Valor Geek",
                        description=f"Ticket médio geek (R$ {float(geek_avg):.2f}) é {float(geek_avg/general_avg):.1f}x maior que geral",
                        severity="low",
                        confidence=0.9,
                        recommendations=[
                            "Priorizar produtos geek de alto valor",
                            "Desenvolver estratégias de upselling para geek",
                            "Focar em produtos premium geek"
                        ],
                        data_points={
                            "geek_avg": float(geek_avg),
                            "general_avg": float(general_avg),
                            "ratio": float(geek_avg/general_avg)
                        },
                        timestamp=datetime.now().isoformat()
                    ))
            
            # Insight 4: Anomalias
            anomalies = self._detect_anomalies(metrics)
            insights.extend(anomalies)
            
            # Insight 5: Performance por categoria
            category_insights = self._analyze_category_insights(metrics)
            insights.extend(category_insights)
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar insights: {e}")
        
        return insights
    
    async def _analyze_trends(self, period: str) -> List[ConversionTrend]:
        """Analisa tendências de conversão"""
        trends = []
        
        try:
            # Obter histórico de métricas
            if len(self.tracker.metrics_history) < self.analysis_thresholds["min_data_points"]:
                return trends
            
            # Analisar tendência de conversões geek
            geek_conversions = [m.geek_conversions for m in self.tracker.metrics_history[-self.analysis_thresholds["trend_periods"]:]]
            if len(geek_conversions) >= 3:
                trend = self._calculate_trend("Conversões Geek", geek_conversions, period)
                trends.append(trend)
            
            # Analisar tendência de conversões gerais
            general_conversions = [m.general_conversions for m in self.tracker.metrics_history[-self.analysis_thresholds["trend_periods"]:]]
            if len(general_conversions) >= 3:
                trend = self._calculate_trend("Conversões Gerais", general_conversions, period)
                trends.append(trend)
            
            # Analisar tendência de receita
            total_revenue = [float(m.total_revenue) for m in self.tracker.metrics_history[-self.analysis_thresholds["trend_periods"]:]]
            if len(total_revenue) >= 3:
                trend = self._calculate_trend("Receita Total", total_revenue, period)
                trends.append(trend)
            
            # Analisar tendência de taxa de conversão
            conversion_rates = [m.overall_conversion_rate for m in self.tracker.metrics_history[-self.analysis_thresholds["trend_periods"]:]]
            if len(conversion_rates) >= 3:
                trend = self._calculate_trend("Taxa de Conversão", conversion_rates, period)
                trends.append(trend)
            
        except Exception as e:
            self.logger.error(f"Erro ao analisar tendências: {e}")
        
        return trends
    
    def _calculate_trend(self, metric_name: str, values: List[float], period: str) -> ConversionTrend:
        """Calcula tendência para uma métrica"""
        if len(values) < 3:
            return ConversionTrend(
                metric_name=metric_name,
                period=period,
                trend_direction="stable",
                change_percentage=0.0,
                significance="low",
                description="Dados insuficientes para análise",
                data_points=values
            )
        
        # Calcular mudança percentual
        first_value = values[0]
        last_value = values[-1]
        
        if first_value == 0:
            change_percentage = 100.0 if last_value > 0 else 0.0
        else:
            change_percentage = ((last_value - first_value) / first_value) * 100
        
        # Determinar direção
        if change_percentage > self.analysis_thresholds["significant_change"]:
            trend_direction = "up"
        elif change_percentage < -self.analysis_thresholds["significant_change"]:
            trend_direction = "down"
        else:
            trend_direction = "stable"
        
        # Determinar significância
        if abs(change_percentage) > 30:
            significance = "high"
        elif abs(change_percentage) > 15:
            significance = "medium"
        else:
            significance = "low"
        
        # Gerar descrição
        if trend_direction == "up":
            description = f"{metric_name} aumentou {abs(change_percentage):.1f}% no período"
        elif trend_direction == "down":
            description = f"{metric_name} diminuiu {abs(change_percentage):.1f}% no período"
        else:
            description = f"{metric_name} manteve-se estável ({change_percentage:.1f}% de mudança)"
        
        return ConversionTrend(
            metric_name=metric_name,
            period=period,
            trend_direction=trend_direction,
            change_percentage=change_percentage,
            significance=significance,
            description=description,
            data_points=values
        )
    
    def _detect_anomalies(self, metrics: ConversionMetrics) -> List[ConversionInsight]:
        """Detecta anomalias nos dados"""
        anomalies = []
        
        try:
            # Anomalia: Conversão zero
            if metrics.total_conversions == 0:
                anomalies.append(ConversionInsight(
                    insight_type="anomaly",
                    title="Sem Conversões",
                    description="Nenhuma conversão registrada no período",
                    severity="high",
                    confidence=1.0,
                    recommendations=[
                        "Verificar sistema de rastreamento",
                        "Investigar problemas técnicos",
                        "Revisar estratégia de marketing"
                    ],
                    data_points={"total_conversions": metrics.total_conversions},
                    timestamp=datetime.now().isoformat()
                ))
            
            # Anomalia: Taxa de conversão muito baixa
            if metrics.overall_conversion_rate < 0.001:  # Menos de 0.1%
                anomalies.append(ConversionInsight(
                    insight_type="anomaly",
                    title="Taxa de Conversão Muito Baixa",
                    description=f"Taxa de conversão de {metrics.overall_conversion_rate:.3%} está abaixo do esperado",
                    severity="medium",
                    confidence=0.8,
                    recommendations=[
                        "Revisar qualidade das ofertas",
                        "Otimizar experiência do usuário",
                        "Investigar problemas de UX"
                    ],
                    data_points={"conversion_rate": metrics.overall_conversion_rate},
                    timestamp=datetime.now().isoformat()
                ))
            
            # Anomalia: Receita zero com conversões
            if metrics.total_conversions > 0 and metrics.total_revenue == 0:
                anomalies.append(ConversionInsight(
                    insight_type="anomaly",
                    title="Conversões Sem Receita",
                    description="Conversões registradas mas sem receita associada",
                    severity="medium",
                    confidence=0.9,
                    recommendations=[
                        "Verificar rastreamento de receita",
                        "Investigar problemas de integração",
                        "Revisar configuração de comissões"
                    ],
                    data_points={
                        "conversions": metrics.total_conversions,
                        "revenue": float(metrics.total_revenue)
                    },
                    timestamp=datetime.now().isoformat()
                ))
            
        except Exception as e:
            self.logger.error(f"Erro ao detectar anomalias: {e}")
        
        return anomalies
    
    def _analyze_category_insights(self, metrics: ConversionMetrics) -> List[ConversionInsight]:
        """Analisa insights por categoria"""
        insights = []
        
        try:
            if not metrics.category_performance:
                return insights
            
            # Encontrar categoria com melhor performance
            best_category = None
            best_revenue = Decimal("0")
            
            for category, stats in metrics.category_performance.items():
                revenue = stats.get("revenue", Decimal("0"))
                if revenue > best_revenue:
                    best_revenue = revenue
                    best_category = category
            
            if best_category and best_revenue > 0:
                insights.append(ConversionInsight(
                    insight_type="opportunity",
                    title=f"Melhor Categoria: {best_category}",
                    description=f"Categoria {best_category} gerou R$ {best_revenue:.2f} em receita",
                    severity="low",
                    confidence=0.85,
                    recommendations=[
                        f"Aumentar oferta de produtos {best_category}",
                        f"Otimizar campanhas para {best_category}",
                        f"Expandir parcerias em {best_category}"
                    ],
                    data_points={
                        "category": best_category,
                        "revenue": float(best_revenue),
                        "conversions": metrics.category_performance[best_category].get("conversions", 0)
                    },
                    timestamp=datetime.now().isoformat()
                ))
            
            # Analisar categorias com baixa performance
            low_performance_categories = []
            for category, stats in metrics.category_performance.items():
                conversions = stats.get("conversions", 0)
                if conversions == 0:
                    low_performance_categories.append(category)
            
            if low_performance_categories:
                insights.append(ConversionInsight(
                    insight_type="warning",
                    title="Categorias Sem Conversões",
                    description=f"Categorias sem conversões: {', '.join(low_performance_categories)}",
                    severity="medium",
                    confidence=0.9,
                    recommendations=[
                        "Revisar qualidade dos produtos nessas categorias",
                        "Investigar demanda da audiência",
                        "Considerar remoção ou reformulação"
                    ],
                    data_points={"categories": low_performance_categories},
                    timestamp=datetime.now().isoformat()
                ))
            
        except Exception as e:
            self.logger.error(f"Erro ao analisar insights por categoria: {e}")
        
        return insights
    
    def _calculate_performance_score(self, metrics: ConversionMetrics) -> float:
        """Calcula score de performance geral"""
        try:
            score = 0.0
            factors = 0
            
            # Fator 1: Taxa de conversão (0-40 pontos)
            if metrics.overall_conversion_rate > 0.01:  # 1%
                score += 40
            elif metrics.overall_conversion_rate > 0.005:  # 0.5%
                score += 30
            elif metrics.overall_conversion_rate > 0.001:  # 0.1%
                score += 20
            else:
                score += 10
            factors += 1
            
            # Fator 2: Proporção geek (0-30 pontos)
            if metrics.total_conversions > 0:
                geek_ratio = metrics.geek_conversions / metrics.total_conversions
                if geek_ratio > 0.5:
                    score += 30
                elif geek_ratio > 0.3:
                    score += 20
                elif geek_ratio > 0.1:
                    score += 10
                else:
                    score += 5
                factors += 1
            
            # Fator 3: Receita (0-30 pontos)
            if metrics.total_revenue > Decimal("1000"):
                score += 30
            elif metrics.total_revenue > Decimal("500"):
                score += 20
            elif metrics.total_revenue > Decimal("100"):
                score += 10
            else:
                score += 5
            factors += 1
            
            return score / factors if factors > 0 else 0.0
            
        except Exception as e:
            self.logger.error(f"Erro ao calcular score de performance: {e}")
            return 0.0
    
    def _analyze_geek_performance(self, metrics: ConversionMetrics) -> Dict[str, Any]:
        """Analisa performance geek"""
        return {
            "conversions": metrics.geek_conversions,
            "revenue": float(metrics.geek_revenue),
            "commission": float(metrics.geek_commission),
            "conversion_rate": metrics.geek_conversion_rate,
            "trend": metrics.geek_trend,
            "ratio_of_total": metrics.geek_conversions / max(metrics.total_conversions, 1),
            "avg_order_value": float(metrics.geek_revenue / max(metrics.geek_conversions, 1))
        }
    
    def _analyze_general_performance(self, metrics: ConversionMetrics) -> Dict[str, Any]:
        """Analisa performance geral"""
        return {
            "conversions": metrics.general_conversions,
            "revenue": float(metrics.general_revenue),
            "commission": float(metrics.general_commission),
            "conversion_rate": metrics.general_conversion_rate,
            "trend": metrics.general_trend,
            "ratio_of_total": metrics.general_conversions / max(metrics.total_conversions, 1),
            "avg_order_value": float(metrics.general_revenue / max(metrics.general_conversions, 1))
        }
    
    def _analyze_categories(self, metrics: ConversionMetrics) -> Dict[str, Any]:
        """Analisa performance por categoria"""
        return {
            "total_categories": len(metrics.category_performance),
            "best_performing": self._get_best_performing_category(metrics),
            "worst_performing": self._get_worst_performing_category(metrics),
            "category_breakdown": metrics.category_performance
        }
    
    def _get_best_performing_category(self, metrics: ConversionMetrics) -> Optional[str]:
        """Retorna categoria com melhor performance"""
        if not metrics.category_performance:
            return None
        
        best_category = None
        best_revenue = Decimal("0")
        
        for category, stats in metrics.category_performance.items():
            revenue = stats.get("revenue", Decimal("0"))
            if revenue > best_revenue:
                best_revenue = revenue
                best_category = category
        
        return best_category
    
    def _get_worst_performing_category(self, metrics: ConversionMetrics) -> Optional[str]:
        """Retorna categoria com pior performance"""
        if not metrics.category_performance:
            return None
        
        worst_category = None
        worst_conversions = float('inf')
        
        for category, stats in metrics.category_performance.items():
            conversions = stats.get("conversions", 0)
            if conversions < worst_conversions:
                worst_conversions = conversions
                worst_category = category
        
        return worst_category
    
    def _generate_recommendations(self, insights: List[ConversionInsight], 
                                trends: List[ConversionTrend], 
                                metrics: ConversionMetrics) -> List[str]:
        """Gera recomendações baseadas em insights e tendências"""
        recommendations = []
        
        # Recomendações baseadas em insights
        for insight in insights:
            recommendations.extend(insight.recommendations)
        
        # Recomendações baseadas em tendências
        for trend in trends:
            if trend.trend_direction == "down" and trend.significance == "high":
                recommendations.append(f"Investigar queda em {trend.metric_name}")
            elif trend.trend_direction == "up" and trend.significance == "high":
                recommendations.append(f"Capitalizar crescimento em {trend.metric_name}")
        
        # Recomendações gerais baseadas em métricas
        if metrics.geek_conversion_rate < 0.005:  # Menos de 0.5%
            recommendations.append("Otimizar estratégia de conversão para produtos geek")
        
        if metrics.total_conversions < 10:
            recommendations.append("Aumentar volume de tráfego e ofertas")
        
        if metrics.total_revenue < Decimal("100"):
            recommendations.append("Focar em produtos de maior valor")
        
        # Remover duplicatas
        return list(set(recommendations))
    
    def _create_summary(self, metrics: ConversionMetrics, insights: List[ConversionInsight], 
                       performance_score: float) -> str:
        """Cria resumo da análise"""
        summary_parts = []
        
        # Resumo básico
        summary_parts.append(f"Total de {metrics.total_conversions} conversões")
        summary_parts.append(f"Receita de R$ {metrics.total_revenue:.2f}")
        summary_parts.append(f"Score de performance: {performance_score:.1f}/100")
        
        # Resumo geek vs geral
        if metrics.total_conversions > 0:
            geek_ratio = metrics.geek_conversions / metrics.total_conversions
            summary_parts.append(f"{geek_ratio:.1%} das conversões são geek")
        
        # Resumo de insights
        if insights:
            critical_insights = [i for i in insights if i.severity in ["high", "critical"]]
            if critical_insights:
                summary_parts.append(f"{len(critical_insights)} insights críticos identificados")
        
        return ". ".join(summary_parts) + "."
    
    def _create_empty_report(self, period: str) -> ConversionReport:
        """Cria relatório vazio"""
        return ConversionReport(
            timestamp=datetime.now().isoformat(),
            period=period,
            summary="Análise não disponível - dados insuficientes",
            insights=[],
            trends=[],
            recommendations=["Coletar mais dados para análise"],
            performance_score=0.0,
            geek_performance={},
            general_performance={},
            category_analysis={}
        )
