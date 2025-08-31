"""
Sistema de Monitoramento de Performance para Teste em Produção
Monitora métricas em tempo real e gera relatórios de performance
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import statistics
from pathlib import Path

from src.core.models import Offer
from src.core.geek_prioritizer import GeekPrioritizer


@dataclass
class PerformanceMetric:
    """Métrica de performance individual"""
    timestamp: str
    metric_name: str
    value: float
    unit: str
    category: str
    description: str


@dataclass
class PerformanceSnapshot:
    """Snapshot completo de performance"""
    timestamp: str
    total_offers: int
    geek_offers_count: int
    general_offers_count: int
    average_geek_score: float
    average_processing_time: float
    offers_per_second: float
    memory_usage_mb: float
    cpu_usage_percent: float
    error_rate: float
    category_distribution: Dict[str, int]
    top_performing_categories: List[str]
    alerts_generated: int
    conversion_metrics: Dict[str, float]


class PerformanceMonitor:
    """
    Monitor de performance em tempo real para o sistema geek
    """
    
    def __init__(self, log_file: str = "performance_monitor.log"):
        self.logger = logging.getLogger(__name__)
        self.log_file = log_file
        self.metrics_history: List[PerformanceMetric] = []
        self.snapshots: List[PerformanceSnapshot] = []
        self.start_time = datetime.now()
        
        # Configurações de monitoramento
        self.monitoring_interval_seconds = 30
        self.max_history_size = 1000
        self.alert_thresholds = {
            "error_rate": 0.05,  # 5%
            "processing_time": 2.0,  # 2 segundos
            "memory_usage": 512.0,  # 512 MB
            "cpu_usage": 80.0  # 80%
        }
        
        # Métricas acumuladas
        self.total_offers_processed = 0
        self.total_errors = 0
        self.total_processing_time = 0.0
        self.total_geek_scores = []
        
    async def start_monitoring(self):
        """Inicia o monitoramento contínuo"""
        self.logger.info("Iniciando monitoramento de performance...")
        
        try:
            while True:
                await self.capture_performance_snapshot()
                await asyncio.sleep(self.monitoring_interval_seconds)
        except KeyboardInterrupt:
            self.logger.info("Monitoramento interrompido pelo usuário")
        except Exception as e:
            self.logger.error(f"Erro no monitoramento: {e}")
    
    async def capture_performance_snapshot(self):
        """Captura snapshot de performance atual"""
        try:
            # Simular métricas do sistema (em produção, estas viriam do sistema real)
            snapshot = await self._generate_performance_snapshot()
            self.snapshots.append(snapshot)
            
            # Manter histórico limitado
            if len(self.snapshots) > self.max_history_size:
                self.snapshots = self.snapshots[-self.max_history_size:]
            
            # Verificar alertas
            await self._check_performance_alerts(snapshot)
            
            # Log da snapshot
            self.logger.info(f"Snapshot capturado: {snapshot.total_offers} ofertas, "
                           f"Score médio: {snapshot.average_geek_score:.3f}")
            
        except Exception as e:
            self.logger.error(f"Erro ao capturar snapshot: {e}")
    
    async def _generate_performance_snapshot(self) -> PerformanceSnapshot:
        """Gera snapshot de performance baseado no estado atual"""
        current_time = datetime.now()
        
        # Calcular métricas baseadas no histórico
        if self.snapshots:
            last_snapshot = self.snapshots[-1]
            offers_since_last = max(0, self.total_offers_processed - last_snapshot.total_offers)
            time_since_last = (current_time - datetime.fromisoformat(last_snapshot.timestamp)).total_seconds()
            
            if time_since_last > 0:
                offers_per_second = offers_since_last / time_since_last
            else:
                offers_per_second = 0.0
        else:
            offers_per_second = 0.0
        
        # Calcular distribuição de categorias (simulado)
        category_distribution = {
            "gaming_consoles": len([s for s in self.total_geek_scores if s > 0.8]),
            "pc_gaming": len([s for s in self.total_geek_scores if 0.6 <= s <= 0.8]),
            "smart_home_tech": len([s for s in self.total_geek_scores if 0.4 <= s < 0.6]),
            "audio_tech": len([s for s in self.total_geek_scores if 0.2 <= s < 0.4]),
            "general": len([s for s in self.total_geek_scores if s < 0.2])
        }
        
        # Top categorias performando
        top_categories = sorted(category_distribution.items(), key=lambda x: x[1], reverse=True)[:3]
        top_performing_categories = [cat for cat, count in top_categories if count > 0]
        
        # Métricas de conversão (simuladas)
        conversion_metrics = {
            "geek_to_general_ratio": len([s for s in self.total_geek_scores if s > 0.5]) / max(len(self.total_geek_scores), 1),
            "high_priority_rate": len([s for s in self.total_geek_scores if s > 0.8]) / max(len(self.total_geek_scores), 1),
            "average_discount": 25.0,  # Simulado
            "stock_availability": 0.85  # Simulado
        }
        
        snapshot = PerformanceSnapshot(
            timestamp=current_time.isoformat(),
            total_offers=self.total_offers_processed,
            geek_offers_count=len([s for s in self.total_geek_scores if s > 0.5]),
            general_offers_count=len([s for s in self.total_geek_scores if s <= 0.5]),
            average_geek_score=statistics.mean(self.total_geek_scores) if self.total_geek_scores else 0.0,
            average_processing_time=self.total_processing_time / max(self.total_offers_processed, 1),
            offers_per_second=offers_per_second,
            memory_usage_mb=150.0,  # Simulado
            cpu_usage_percent=45.0,  # Simulado
            error_rate=self.total_errors / max(self.total_offers_processed, 1),
            category_distribution=category_distribution,
            top_performing_categories=top_performing_categories,
            alerts_generated=len([s for s in self.snapshots if s.error_rate > self.alert_thresholds["error_rate"]]),
            conversion_metrics=conversion_metrics
        )
        
        return snapshot
    
    async def _check_performance_alerts(self, snapshot: PerformanceSnapshot):
        """Verifica se há alertas de performance"""
        alerts = []
        
        if snapshot.error_rate > self.alert_thresholds["error_rate"]:
            alerts.append(f"Taxa de erro alta: {snapshot.error_rate:.2%}")
        
        if snapshot.average_processing_time > self.alert_thresholds["processing_time"]:
            alerts.append(f"Tempo de processamento alto: {snapshot.average_processing_time:.2f}s")
        
        if snapshot.memory_usage_mb > self.alert_thresholds["memory_usage"]:
            alerts.append(f"Uso de memória alto: {snapshot.memory_usage_mb:.1f}MB")
        
        if snapshot.cpu_usage_percent > self.alert_thresholds["cpu_usage"]:
            alerts.append(f"Uso de CPU alto: {snapshot.cpu_usage_percent:.1f}%")
        
        if alerts:
            for alert in alerts:
                self.logger.warning(f"ALERTA DE PERFORMANCE: {alert}")
    
    def record_offer_processing(self, offer: Offer, geek_score: float, processing_time: float):
        """Registra processamento de uma oferta"""
        self.total_offers_processed += 1
        self.total_processing_time += processing_time
        self.total_geek_scores.append(geek_score)
        
        # Criar métrica individual
        metric = PerformanceMetric(
            timestamp=datetime.now().isoformat(),
            metric_name="offer_processing",
            value=processing_time,
            unit="seconds",
            category="processing",
            description=f"Processamento da oferta: {getattr(offer, 'title', 'Sem título')[:50]}..."
        )
        
        self.metrics_history.append(metric)
        
        # Manter histórico limitado
        if len(self.metrics_history) > self.max_history_size:
            self.metrics_history = self.metrics_history[-self.max_history_size:]
    
    def record_error(self, error_message: str):
        """Registra um erro"""
        self.total_errors += 1
        
        metric = PerformanceMetric(
            timestamp=datetime.now().isoformat(),
            metric_name="error",
            value=1.0,
            unit="count",
            category="errors",
            description=error_message
        )
        
        self.metrics_history.append(metric)
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Retorna resumo de performance"""
        if not self.snapshots:
            return {"status": "Nenhum dado disponível"}
        
        latest = self.snapshots[-1]
        
        # Calcular tendências
        if len(self.snapshots) > 1:
            previous = self.snapshots[-2]
            score_trend = latest.average_geek_score - previous.average_geek_score
            processing_trend = latest.average_processing_time - previous.average_processing_time
        else:
            score_trend = 0.0
            processing_trend = 0.0
        
        summary = {
            "current_status": {
                "total_offers_processed": latest.total_offers,
                "geek_offers_ratio": latest.geek_offers_count / max(latest.total_offers, 1),
                "average_geek_score": latest.average_geek_score,
                "average_processing_time": latest.average_processing_time,
                "offers_per_second": latest.offers_per_second,
                "error_rate": latest.error_rate
            },
            "trends": {
                "score_trend": score_trend,
                "processing_trend": processing_trend
            },
            "category_performance": latest.category_distribution,
            "top_categories": latest.top_performing_categories,
            "conversion_metrics": latest.conversion_metrics,
            "alerts": latest.alerts_generated,
            "uptime_hours": (datetime.now() - self.start_time).total_seconds() / 3600
        }
        
        return summary
    
    def export_performance_report(self, output_file: str = None) -> str:
        """Exporta relatório completo de performance"""
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"performance_report_{timestamp}.json"
        
        report = {
            "report_info": {
                "generated_at": datetime.now().isoformat(),
                "monitoring_start": self.start_time.isoformat(),
                "total_snapshots": len(self.snapshots),
                "total_metrics": len(self.metrics_history)
            },
            "performance_summary": self.get_performance_summary(),
            "detailed_snapshots": [asdict(snapshot) for snapshot in self.snapshots[-100:]],  # Últimas 100
            "metrics_history": [asdict(metric) for metric in self.metrics_history[-500:]]  # Últimas 500
        }
        
        # Salvar arquivo
        output_path = Path(output_file)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Relatório exportado para: {output_path}")
        return str(output_path)
    
    def get_real_time_metrics(self) -> Dict[str, Any]:
        """Retorna métricas em tempo real para dashboard"""
        if not self.snapshots:
            return {"status": "aguardando dados"}
        
        latest = self.snapshots[-1]
        
        # Calcular métricas de tendência (últimos 5 snapshots)
        if len(self.snapshots) >= 5:
            recent_scores = [s.average_geek_score for s in self.snapshots[-5:]]
            score_trend = "↗️" if recent_scores[-1] > recent_scores[0] else "↘️" if recent_scores[-1] < recent_scores[0] else "→"
        else:
            score_trend = "→"
        
        return {
            "current_metrics": {
                "total_offers": latest.total_offers,
                "geek_ratio": f"{latest.geek_offers_count / max(latest.total_offers, 1):.1%}",
                "avg_score": f"{latest.average_geek_score:.3f}",
                "processing_time": f"{latest.average_processing_time:.2f}s",
                "throughput": f"{latest.offers_per_second:.1f}/s",
                "error_rate": f"{latest.error_rate:.2%}"
            },
            "trends": {
                "score_trend": score_trend,
                "performance_status": "🟢" if latest.error_rate < 0.02 else "🟡" if latest.error_rate < 0.05 else "🔴"
            },
            "top_categories": latest.top_performing_categories,
            "last_update": latest.timestamp
        }
    
    async def generate_performance_insights(self) -> List[str]:
        """Gera insights baseados na performance atual"""
        insights = []
        
        if not self.snapshots:
            return ["Sistema ainda não possui dados suficientes para análise"]
        
        latest = self.snapshots[-1]
        
        # Análise de performance
        if latest.average_geek_score > 0.7:
            insights.append("🎯 Sistema geek funcionando excepcionalmente bem - scores altos consistentes")
        elif latest.average_geek_score > 0.5:
            insights.append("✅ Sistema geek funcionando adequadamente")
        else:
            insights.append("⚠️ Sistema geek pode precisar de ajustes - scores baixos")
        
        # Análise de throughput
        if latest.offers_per_second > 10:
            insights.append("🚀 Alto throughput de processamento - sistema muito eficiente")
        elif latest.offers_per_second > 5:
            insights.append("⚡ Throughput adequado para produção")
        else:
            insights.append("🐌 Throughput baixo - pode indicar gargalos")
        
        # Análise de erros
        if latest.error_rate < 0.01:
            insights.append("🟢 Taxa de erro muito baixa - sistema estável")
        elif latest.error_rate < 0.05:
            insights.append("🟡 Taxa de erro aceitável")
        else:
            insights.append("🔴 Taxa de erro alta - investigar problemas")
        
        # Análise de categorias
        if latest.top_performing_categories:
            top_cat = latest.top_performing_categories[0]
            insights.append(f"🏆 Categoria {top_cat} liderando em performance")
        
        return insights
