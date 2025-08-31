#!/usr/bin/env python3
"""Sistema de Métricas Avançadas para Dashboard"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import sqlite3
import json

@dataclass
class MetricValue:
    """Valor de uma métrica com contexto temporal"""
    value: float
    timestamp: datetime
    period: str  # 7d, 30d, 90d
    trend: float  # variação percentual
    status: str  # "good", "warning", "critical"

@dataclass
class AlertDefinition:
    """Definição de um alerta inteligente"""
    id: str
    name: str
    description: str
    metric: str
    threshold: float
    severity: str  # "critical", "warning", "info"
    action_required: bool
    auto_resolve: bool = False

class AdvancedMetricsEngine:
    """Motor de métricas avançadas e alertas inteligentes"""
    
    def __init__(self, db_path: str = "src/db/analytics.sqlite"):
        self.db_path = Path(db_path)
        self.logger = logging.getLogger(__name__)
        
        # Definições de alertas
        self.alert_definitions = [
            AlertDefinition(
                id="asin_quality_low",
                name="Qualidade ASIN Baixa",
                description="Percentual de ofertas Amazon com ASIN válido abaixo da meta",
                metric="asin_quality",
                threshold=95.0,
                severity="critical",
                action_required=True
            ),
            AlertDefinition(
                id="asin_url_extraction_low",
                name="Extração ASIN via URL Baixa",
                description="Percentual de extração ASIN via URL abaixo do ideal",
                metric="asin_url_extraction",
                threshold=70.0,
                severity="warning",
                action_required=False
            ),
            AlertDefinition(
                id="posts_blocked_high",
                name="Posts Bloqueados Elevados",
                description="Número de posts bloqueados por afiliação acima do normal",
                metric="posts_blocked_7d",
                threshold=50.0,
                severity="critical",
                action_required=True
            ),
            AlertDefinition(
                id="revenue_zero",
                name="Receita Zero",
                description="Receita total zero com posts publicados",
                metric="revenue_total",
                threshold=0.01,
                severity="critical",
                action_required=True
            ),
            AlertDefinition(
                id="latency_high",
                name="Latência Elevada",
                description="Latência média do sistema acima do aceitável",
                metric="latency_avg",
                threshold=5.0,
                severity="warning",
                action_required=False
            )
        ]
    
    def get_overview_metrics(self, period: str = "7d") -> Dict:
        """Obtém métricas da visão geral"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                # Calcular período
                days = int(period.replace("d", ""))
                start_date = datetime.now() - timedelta(days=days)
                
                # ASIN Quality
                asin_quality = self._calculate_asin_quality(conn, start_date)
                
                # Posts Bloqueados
                posts_blocked = self._calculate_posts_blocked(conn, start_date)
                
                # Receita
                revenue_metrics = self._calculate_revenue_metrics(conn, start_date)
                
                # Performance
                performance_metrics = self._calculate_performance_metrics(conn, start_date)
                
                return {
                    "asin_quality": asin_quality,
                    "posts_blocked": posts_blocked,
                    "revenue_total": revenue_metrics["total"],
                    "revenue_per_post": revenue_metrics["per_post"],
                    "latency_avg": performance_metrics["latency_avg"],
                    "freshness_hours": performance_metrics["freshness_hours"],
                    "period": period,
                    "last_updated": datetime.now().isoformat()
                }
                
        except Exception as e:
            self.logger.error(f"Erro ao obter métricas de overview: {e}")
            return self._get_fallback_metrics(period)
    
    def get_asin_metrics(self, period: str = "7d") -> Dict:
        """Obtém métricas específicas de ASIN"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                days = int(period.replace("d", ""))
                start_date = datetime.now() - timedelta(days=days)
                
                # Contar ofertas com/sem ASIN
                cursor = conn.execute("""
                    SELECT 
                        COUNT(CASE WHEN asin IS NOT NULL AND asin != '' THEN 1 END) as with_asin,
                        COUNT(CASE WHEN asin IS NULL OR asin = '' THEN 1 END) as without_asin,
                        COUNT(*) as total
                    FROM offers_posted 
                    WHERE platform = 'amazon' 
                    AND created_at >= ?
                """, (start_date.isoformat(),))
                
                row = cursor.fetchone()
                with_asin = row["with_asin"] if row else 0
                without_asin = row["without_asin"] if row else 0
                total = row["total"] if row else 0
                
                # Estratégias de extração
                strategy_cursor = conn.execute("""
                    SELECT 
                        asin_source,
                        COUNT(*) as count
                    FROM offers_posted 
                    WHERE platform = 'amazon' 
                    AND created_at >= ?
                    AND asin_source IS NOT NULL
                    GROUP BY asin_source
                """, (start_date.isoformat(),))
                
                strategies = {}
                for strategy_row in strategy_cursor.fetchall():
                    strategies[strategy_row["asin_source"]] = strategy_row["count"]
                
                return {
                    "with_asin": with_asin,
                    "without_asin": without_asin,
                    "total_offers": total,
                    "strategy": strategies,
                    "period": period
                }
                
        except Exception as e:
            self.logger.error(f"Erro ao obter métricas ASIN: {e}")
            return {
                "with_asin": 0,
                "without_asin": 0,
                "total_offers": 0,
                "strategy": {"url": 0, "html": 0, "api": 0},
                "period": period
            }
    
    def get_affiliation_blocks(self, period: str = "7d", platform: Optional[str] = None) -> List[Dict]:
        """Obtém detalhes de posts bloqueados por afiliação"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                days = int(period.replace("d", ""))
                start_date = datetime.now() - timedelta(days=days)
                
                query = """
                    SELECT 
                        platform,
                        reason,
                        COUNT(*) as quantidade
                    FROM perf 
                    WHERE status = 'blocked' 
                    AND created_at >= ?
                """
                params = [start_date.isoformat()]
                
                if platform:
                    query += " AND platform = ?"
                    params.append(platform)
                
                query += " GROUP BY platform, reason ORDER BY quantidade DESC"
                
                cursor = conn.execute(query, params)
                
                blocks = []
                for row in cursor.fetchall():
                    blocks.append({
                        "plataforma": row["platform"],
                        "motivo": row["reason"],
                        "quantidade": row["quantidade"]
                    })
                
                return blocks
                
        except Exception as e:
            self.logger.error(f"Erro ao obter bloqueios de afiliação: {e}")
            return []
    
    def get_alerts(self, period: str = "7d") -> Dict:
        """Obtém alertas ativos baseados nas métricas"""
        try:
            overview = self.get_overview_metrics(period)
            
            alerts = []
            critical_count = 0
            action_required = 0
            
            for alert_def in self.alert_definitions:
                metric_value = overview.get(alert_def.metric, 0)
                
                # Verificar se o alerta deve ser disparado
                if self._should_trigger_alert(alert_def, metric_value):
                    alert = {
                        "id": alert_def.id,
                        "name": alert_def.name,
                        "description": alert_def.description,
                        "severity": alert_def.severity,
                        "metric_value": metric_value,
                        "threshold": alert_def.threshold,
                        "action_required": alert_def.action_required,
                        "detected_at": datetime.now().isoformat(),
                        "status": "open"
                    }
                    
                    alerts.append(alert)
                    
                    if alert_def.severity == "critical":
                        critical_count += 1
                    
                    if alert_def.action_required:
                        action_required += 1
            
            return {
                "total": len(alerts),
                "critical": critical_count,
                "action": action_required,
                "alerts": alerts,
                "period": period
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar alertas: {e}")
            return {"total": 0, "critical": 0, "action": 0, "alerts": [], "period": period}
    
    def _calculate_asin_quality(self, conn: sqlite3.Connection, start_date: datetime) -> float:
        """Calcula qualidade do ASIN"""
        cursor = conn.execute("""
            SELECT 
                COUNT(CASE WHEN asin IS NOT NULL AND asin != '' THEN 1 END) as valid,
                COUNT(*) as total
            FROM offers_posted 
            WHERE platform = 'amazon' 
            AND created_at >= ?
        """, (start_date.isoformat(),))
        
        row = cursor.fetchone()
        if row and row["total"] > 0:
            return (row["valid"] / row["total"]) * 100
        return 0.0
    
    def _calculate_posts_blocked(self, conn: sqlite3.Connection, start_date: datetime) -> int:
        """Calcula posts bloqueados no período"""
        cursor = conn.execute("""
            SELECT COUNT(*) as count
            FROM perf 
            WHERE status = 'blocked' 
            AND created_at >= ?
        """, (start_date.isoformat(),))
        
        row = cursor.fetchone()
        return row["count"] if row else 0
    
    def _calculate_revenue_metrics(self, conn: sqlite3.Connection, start_date: datetime) -> Dict:
        """Calcula métricas de receita"""
        cursor = conn.execute("""
            SELECT 
                COALESCE(SUM(amount), 0) as total_revenue,
                COUNT(*) as total_orders
            FROM revenue 
            WHERE created_at >= ?
        """, (start_date.isoformat(),))
        
        row = cursor.fetchone()
        total_revenue = row["total_revenue"] if row else 0.0
        total_orders = row["total_orders"] if row else 0
        
        # Posts publicados no período
        posts_cursor = conn.execute("""
            SELECT COUNT(*) as count
            FROM perf 
            WHERE status = 'published' 
            AND created_at >= ?
        """, (start_date.isoformat(),))
        
        posts_row = posts_cursor.fetchone()
        total_posts = posts_row["count"] if posts_row else 0
        
        revenue_per_post = total_revenue / total_posts if total_posts > 0 else 0.0
        
        return {
            "total": total_revenue,
            "per_post": revenue_per_post,
            "total_orders": total_orders,
            "total_posts": total_posts
        }
    
    def _calculate_performance_metrics(self, conn: sqlite3.Connection, start_date: datetime) -> Dict:
        """Calcula métricas de performance"""
        # Latência média (simulado por enquanto)
        latency_avg = 2.5  # segundos
        
        # Freshness - horas desde último evento
        cursor = conn.execute("""
            SELECT MAX(created_at) as last_event
            FROM offers_posted
        """)
        
        row = cursor.fetchone()
        if row and row["last_event"]:
            last_event = datetime.fromisoformat(row["last_event"])
            freshness_hours = (datetime.now() - last_event).total_seconds() / 3600
        else:
            freshness_hours = 24.0  # fallback
        
        return {
            "latency_avg": latency_avg,
            "freshness_hours": freshness_hours
        }
    
    def _should_trigger_alert(self, alert_def: AlertDefinition, metric_value: float) -> bool:
        """Verifica se um alerta deve ser disparado"""
        if alert_def.metric in ["asin_quality", "asin_url_extraction"]:
            # Para percentuais, alerta se estiver abaixo do threshold
            return metric_value < alert_def.threshold
        elif alert_def.metric in ["posts_blocked_7d"]:
            # Para contadores, alerta se estiver acima do threshold
            return metric_value > alert_def.threshold
        elif alert_def.metric in ["revenue_total"]:
            # Para receita, alerta se estiver abaixo do threshold
            return metric_value < alert_def.threshold
        elif alert_def.metric in ["latency_avg"]:
            # Para latência, alerta se estiver acima do threshold
            return metric_value > alert_def.threshold
        
        return False
    
    def _get_fallback_metrics(self, period: str) -> Dict:
        """Retorna métricas de fallback quando há erro"""
        return {
            "asin_quality": 0.0,
            "posts_blocked": 0,
            "revenue_total": 0.0,
            "revenue_per_post": 0.0,
            "latency_avg": 0.0,
            "freshness_hours": 24.0,
            "period": period,
            "last_updated": datetime.now().isoformat()
        }
    
    def export_metrics_csv(self, period: str = "7d") -> str:
        """Exporta métricas para CSV"""
        try:
            overview = self.get_overview_metrics(period)
            asin_metrics = self.get_asin_metrics(period)
            affiliation_blocks = self.get_affiliation_blocks(period)
            
            csv_lines = [
                "Métrica,Valor,Período,Status",
                f"ASIN Quality,{overview['asin_quality']:.2f}%,{period},{'✅' if overview['asin_quality'] >= 95 else '❌'}",
                f"Posts Bloqueados,{overview['posts_blocked']},{period},⚠️",
                f"Receita Total,R$ {overview['revenue_total']:.2f},{period},{'✅' if overview['revenue_total'] > 0 else '❌'}",
                f"Receita/Post,R$ {overview['revenue_per_post']:.2f},{period},📊",
                f"Latência Média,{overview['latency_avg']:.2f}s,{period},{'✅' if overview['latency_avg'] < 5 else '⚠️'}",
                f"Freshness,{overview['freshness_hours']:.1f}h,{period},{'✅' if overview['freshness_hours'] < 6 else '⚠️'}",
                "",
                "Estratégias ASIN,Quantidade,Período",
            ]
            
            for strategy, count in asin_metrics["strategy"].items():
                csv_lines.append(f"{strategy},{count},{period}")
            
            csv_lines.extend([
                "",
                "Bloqueios por Plataforma,Motivo,Quantidade,Período"
            ])
            
            for block in affiliation_blocks:
                csv_lines.append(f"{block['plataforma']},{block['motivo']},{block['quantidade']},{period}")
            
            return "\n".join(csv_lines)
            
        except Exception as e:
            self.logger.error(f"Erro ao exportar CSV: {e}")
            return "Erro ao gerar relatório CSV"
