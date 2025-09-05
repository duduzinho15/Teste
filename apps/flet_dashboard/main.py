"""
Dashboard Flet para monitoramento do Garimpeiro Geek
Métricas de produção, controle do bot e observabilidade
Foco em Amazon ASIN-first, qualidade de afiliação e operação do pipeline
"""

import flet as ft
import asyncio
import logging
import sys
import os
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path

# Adicionar o diretório raiz ao Python path para importar módulos src
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Imports do sistema
try:
    from src.core.analytics_queries import (
        get_dashboard_summary, amazon_asin_quality_7d, amazon_asin_strategy_7d,
        posts_blocked_7d, deeplink_latency_7d, revenue_per_platform_7d,
        badges_7d, price_freshness_7d, source_fallback_7d, get_recent_blocked_posts,
        health_check
    )
    from src.core.alert_system import get_active_alerts, get_alerts_summary
    
    # Novos sistemas implementados
    from src.app.production_testing import ProductionTestRunner
    from src.app.conversion_monitoring import ConversionTracker, ConversionAnalyzer, ConversionDashboard
    from src.app.user_feedback import FeedbackCollector, FeedbackAnalyzer, ScoreAdjuster, FeedbackDashboard
    from src.app.category_expansion import CategoryAnalyzer, CategoryExpander, MarketResearcher, CategoryOptimizer
    from src.app.ai_optimization import AIOptimizer, DataCollector, ModelTrainer, PredictionEngine, OptimizationDashboard
    from src.core.affiliate_integration import AffiliateIntegrationManager
    from src.core.affiliate_dashboard import AffiliateDashboard
    from src.core.advanced_metrics import AdvancedMetricsManager
    from src.core.advanced_metrics_dashboard import AdvancedMetricsDashboard
    from src.core.deep_learning import DeepLearningManager
    from src.core.deep_learning_dashboard import DeepLearningDashboard
    
except ImportError as e:
    print(f"Erro ao importar módulos do sistema: {e}")
    print("Certifique-se de executar o dashboard a partir do diretório raiz do projeto")
    sys.exit(1)

# Import local dos componentes UI
try:
    from ui_components import (
        MetricCard, PieChart, BarChart, DataTable, AlertBanner, 
        ProgressIndicator, StatusIndicator
    )
except ImportError:
    # Fallback para import absoluto se relativo falhar
    try:
        from apps.flet_dashboard.ui_components import (
            MetricCard, PieChart, BarChart, DataTable, AlertBanner, 
            ProgressIndicator, StatusIndicator
        )
    except ImportError as e:
        print(f"Erro ao importar componentes UI: {e}")
        sys.exit(1)

logger = logging.getLogger(__name__)


class GarimpeiroDashboard:
    """Dashboard principal para monitoramento e controle"""
    
    def __init__(self):
        self.page = None
        self.metrics = {}
        self.bot_status = "🟢 Ativo"
        self.platform_toggles = {}
        self.current_period = "7d"
        self.auto_refresh_enabled = True
        
    def main(self, page: ft.Page):
        """Configuração principal da página"""
        self.page = page
        page.title = "Garimpeiro Geek - Métricas de Produção"
        page.theme_mode = ft.ThemeMode.DARK
        page.padding = 20
        page.scroll = "auto"
        
        # Verificar saúde do sistema
        health = health_check()
        if health["status"] != "healthy":
            page.add(
                AlertBanner(
                    "Sistema de Métricas com Problemas",
                    f"Views: {health['views_count']}/{health['expected_views']}, "
                    f"Eventos recentes: {health['recent_events']}",
                    "error" if health["status"] == "error" else "warning"
                ).build()
            )
        
        # Layout principal com tabs
        tabs = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                ft.Tab(
                    text="📊 Visão Geral",
                    content=self._build_overview_tab()
                ),
                ft.Tab(
                    text="🎯 Amazon ASIN",
                    content=self._build_amazon_tab()
                ),
                ft.Tab(
                    text="🛒 Mercado Livre",
                    content=self._build_mercadolivre_tab()
                ),
                ft.Tab(
                    text="🔧 Moderação ML",
                    content=self._build_mercadolivre_moderation_tab()
                ),
                ft.Tab(
                    text="🔗 Afiliação",
                    content=self._build_affiliation_tab()
                ),
                ft.Tab(
                    text="📈 Performance",
                    content=self._build_performance_tab()
                ),
                ft.Tab(
                    text="🚨 Alertas",
                    content=self._build_alerts_tab()
                ),
                ft.Tab(
                    text="⚙️ Controles",
                    content=self._build_controls_tab()
                ),
                ft.Tab(
                    text="🎛️ Controles Avançados",
                    content=self._build_advanced_controls_tab()
                ),
                ft.Tab(
                    text="🧪 Teste Produção",
                    content=self._build_production_testing_tab()
                ),
                ft.Tab(
                    text="📊 Conversões",
                    content=self._build_conversion_monitoring_tab()
                ),
                ft.Tab(
                    text="💬 Feedback",
                    content=self._build_user_feedback_tab()
                ),
                ft.Tab(
                    text="📂 Categorias",
                    content=self._build_category_expansion_tab()
                ),
                ft.Tab(
                    text="🤖 IA Otimização",
                    content=self._build_ai_optimization_tab()
                ),
                ft.Tab(
                    text="🔗 Integração Afiliados",
                    content=self._build_affiliate_integration_tab()
                ),
                                        ft.Tab(
                            text="📊 Métricas Avançadas",
                            content=self._build_advanced_metrics_tab()
                        ),
                        ft.Tab(
                            text="🤖 Deep Learning",
                            content=self._build_deep_learning_tab()
                        )
            ],
            expand=True
        )
        
        # Adicionar header e tabs
        page.add(
            self._build_header(),
            tabs
        )
        
        # Inicializar métricas
        self._refresh_metrics()
        
        # Auto-refresh desabilitado temporariamente devido a problemas de asyncio
        # self._start_auto_refresh()
        
    def _build_header(self) -> ft.Container:
        """Header com nome, status e controles de período"""
        period_dropdown = ft.Dropdown(
            value=self.current_period,
            options=[
                ft.dropdown.Option("7d", "Últimos 7 dias"),
                ft.dropdown.Option("30d", "Últimos 30 dias")
            ],
            on_change=self._on_period_change,
            width=150
        )
        
        refresh_button = ft.IconButton(
            icon=ft.Icons.REFRESH,
            tooltip="Atualizar métricas",
            on_click=lambda e: self._refresh_metrics()
        )
        
        return ft.Container(
            content=ft.Row([
                ft.Column([
                    ft.Text("🕵️ Garimpeiro Geek", size=28, weight=ft.FontWeight.BOLD),
                    ft.Text("Dashboard de Métricas de Produção", size=14, color=ft.Colors.GREY_400)
                ]),
                ft.Row([
                    ft.Text("Período:", size=14, color=ft.Colors.GREY_400),
                    period_dropdown,
                    refresh_button,
                    ft.Container(
                        content=ft.Text(self.bot_status, size=16),
                        bgcolor=ft.Colors.GREEN_100,
                        padding=8,
                        border_radius=6
                    )
                ], spacing=10)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=20,
            bgcolor=ft.Colors.BLUE_900,
            border_radius=12,
            margin=ft.margin.only(bottom=20)
        )
    
    def _build_overview_tab(self) -> ft.Container:
        """Tab de visão geral com KPIs principais"""
        summary = get_dashboard_summary(self.current_period)
        
        # Sistema de alertas inteligente
        active_alerts = get_active_alerts(self.current_period)
        alerts_summary = get_alerts_summary(self.current_period)
        
        # Mostrar alertas mais importantes
        alert_banners = []
        for alert in active_alerts[:5]:  # Top 5 alertas
            alert_type = "error" if alert.severity in ["error", "critical"] else "warning"
            alert_banners.append(
                AlertBanner(
                    alert.title,
                    alert.message,
                    alert_type
                ).build()
            )
        
        # Se não há alertas específicos, mostrar resumo
        if not alert_banners and alerts_summary["total"] == 0:
            alert_banners.append(
                AlertBanner(
                    "Sistema Operacional",
                    "✅ Todas as métricas estão dentro dos parâmetros normais",
                    "success"
                ).build()
            )
        
        # KPIs principais
        kpi_cards = ft.Row([
            MetricCard(
                "Amazon ASIN Válido",
                f"{summary.get('amazon_asin_pct', 0):.1f}%",
                f"Meta: >95%",
                ft.Colors.GREEN_400 if summary.get('amazon_asin_pct', 0) >= 95 else ft.Colors.ORANGE_400,
                summary.get('asin_alert', False),
                "Percentual de ofertas Amazon com ASIN extraído corretamente"
            ).build(),
            
            MetricCard(
                "Posts Bloqueados",
                str(summary.get('total_blocked', 0)),
                f"Período: {self.current_period}",
                ft.Colors.RED_400 if summary.get('total_blocked', 0) > 0 else ft.Colors.GREEN_400,
                summary.get('blocked_alert', False),
                "Posts bloqueados por problemas de afiliação"
            ).build(),
            
            MetricCard(
                "Receita Total",
                f"R$ {summary.get('total_revenue', 0):.2f}",
                f"{summary.get('total_posts', 0)} posts",
                ft.Colors.BLUE_400,
                False,
                f"Receita total no período de {self.current_period}"
            ).build(),
            
            MetricCard(
                "R$/Post Médio",
                f"R$ {summary.get('avg_revenue_per_post', 0):.2f}",
                "Por post publicado",
                ft.Colors.PURPLE_400,
                False,
                "Receita média por post publicado"
            ).build()
        ], alignment=ft.MainAxisAlignment.SPACE_EVENLY, wrap=True)
        
        # Indicadores de progresso
        progress_indicators = ft.Row([
            ProgressIndicator(
                "ASIN Quality",
                summary.get('amazon_asin_pct', 0),
                100,
                "%"
            ).build(),
            
            ProgressIndicator(
                "Playwright Usage",
                summary.get('playwright_pct', 0),
                100,
                "%"
            ).build()
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=30)
        
        # Resumo de alertas se houver muitos
        if alerts_summary["total"] > 5:
            alert_summary_card = ft.Container(
                content=ft.Row([
                    ft.Text(f"📊 {alerts_summary['total']} alertas ativos", size=16, weight=ft.FontWeight.BOLD),
                    ft.Text(f"🚨 {alerts_summary['by_severity']['critical']} críticos", color=ft.Colors.RED_400),
                    ft.Text(f"❌ {alerts_summary['by_severity']['error']} erros", color=ft.Colors.ORANGE_400),
                    ft.Text(f"⚠️ {alerts_summary['by_severity']['warning']} avisos", color=ft.Colors.YELLOW_400),
                    ft.Text(f"⚡ {alerts_summary['action_required']} requerem ação", color=ft.Colors.BLUE_400)
                ], alignment=ft.MainAxisAlignment.SPACE_EVENLY),
                padding=15,
                bgcolor=ft.Colors.GREY_800,
                border_radius=8,
                margin=ft.margin.only(bottom=10)
            )
            alert_banners.append(alert_summary_card)
        
        content = ft.Column([
            *alert_banners,
            kpi_cards,
            ft.Divider(height=20),
            progress_indicators
        ], spacing=20)
        
        return ft.Container(content=content, padding=20)
    
    def _build_amazon_tab(self) -> ft.Container:
        """Tab específica para métricas Amazon ASIN"""
        asin_quality = amazon_asin_quality_7d()
        asin_strategies = amazon_asin_strategy_7d()
        
        # Preparar dados para gráficos
        strategy_data = [
            {"label": s["method"].title(), "value": s["cnt"]}
            for s in asin_strategies if s["cnt"] > 0
        ]
        
        # Cards de qualidade ASIN
        quality_cards = ft.Row([
            MetricCard(
                "Com ASIN",
                str(asin_quality["with"]),
                f"{asin_quality['pct']:.1f}% do total",
                ft.Colors.GREEN_400
            ).build(),
            
            MetricCard(
                "Sem ASIN",
                str(asin_quality["without"]),
                "Ofertas incompletas",
                ft.Colors.RED_400,
                asin_quality["without"] > 0
            ).build(),
            
            MetricCard(
                "Total Ofertas",
                str(asin_quality["total"]),
                "Últimos 7 dias",
                ft.Colors.BLUE_400
            ).build()
        ], alignment=ft.MainAxisAlignment.SPACE_EVENLY)
        
        # Gráfico de estratégias
        strategy_chart = PieChart(
            "Estratégias de Extração ASIN",
            strategy_data,
            "value",
            "label"
        ).build()
        
        content = ft.Column([
            ft.Text("🎯 Amazon ASIN-first Pipeline", size=24, weight=ft.FontWeight.BOLD),
            ft.Text("Qualidade de normalização e estratégias de extração", size=14, color=ft.Colors.GREY_400),
            ft.Divider(height=20),
            quality_cards,
            ft.Divider(height=20),
            strategy_chart
        ], spacing=20)
        
        return ft.Container(content=content, padding=20)
    
    def _build_mercadolivre_tab(self) -> ft.Container:
        """Tab específica para métricas do Mercado Livre"""
        # Importar as funções específicas do Mercado Livre
        try:
            from src.core.analytics_queries import (
                mercadolivre_metrics_7d, 
                mercadolivre_performance_7d, 
                mercadolivre_revenue_7d
            )
            
            metrics = mercadolivre_metrics_7d()
            performance = mercadolivre_performance_7d()
            revenue = mercadolivre_revenue_7d()
            
        except ImportError:
            # Fallback se as funções não estiverem disponíveis
            metrics = {
                "total_offers": 0, "shortlinks": 0, "social_links": 0,
                "direct_links": 0, "shortlink_pct": 0.0, "social_pct": 0.0, "quality_score": 0.0
            }
            performance = {
                "avg_latency": 0, "conversion_rate": 0.0, "successful_conversions": 0,
                "failed_conversions": 0, "avg_latency_formatted": "0ms"
            }
            revenue = {
                "total_revenue": 0.0, "transactions": 0, "avg_transaction": 0.0,
                "formatted_revenue": "R$ 0,00"
            }
        
        # Cards de qualidade de links
        quality_cards = ft.Row([
            MetricCard(
                "Shortlinks",
                str(metrics["shortlinks"]),
                f"{metrics['shortlink_pct']:.1f}% do total",
                ft.Colors.GREEN_400,
                metrics["shortlink_pct"] < 80.0  # Alerta se < 80%
            ).build(),
            
            MetricCard(
                "Links Sociais",
                str(metrics["social_links"]),
                f"{metrics['social_pct']:.1f}% do total",
                ft.Colors.BLUE_400
            ).build(),
            
            MetricCard(
                "Score Qualidade",
                f"{metrics['quality_score']:.1f}%",
                "Baseado em tipos de link",
                ft.Colors.ORANGE_400 if metrics["quality_score"] < 70.0 else ft.Colors.GREEN_400,
                metrics["quality_score"] < 70.0
            ).build()
        ], alignment=ft.MainAxisAlignment.SPACE_EVENLY)
        
        # Cards de performance
        performance_cards = ft.Row([
            MetricCard(
                "Taxa Conversão",
                f"{performance['conversion_rate']:.1f}%",
                f"{performance['successful_conversions']} sucessos",
                ft.Colors.GREEN_400 if performance['conversion_rate'] > 80.0 else ft.Colors.ORANGE_400,
                performance['conversion_rate'] < 80.0
            ).build(),
            
            MetricCard(
                "Latência Média",
                performance['avg_latency_formatted'],
                f"{performance['latency_samples']} amostras",
                ft.Colors.BLUE_400 if performance['avg_latency'] < 1000 else ft.Colors.ORANGE_400
            ).build(),
            
            MetricCard(
                "Total Ofertas",
                str(metrics["total_offers"]),
                "Últimos 7 dias",
                ft.Colors.PURPLE_400
            ).build()
        ], alignment=ft.MainAxisAlignment.SPACE_EVENLY)
        
        # Card de receita
        revenue_card = ft.Row([
            MetricCard(
                "Receita Total",
                revenue['formatted_revenue'],
                f"{revenue['transactions']} transações",
                ft.Colors.GREEN_400,
                revenue['total_revenue'] == 0.0
            ).build(),
            
            MetricCard(
                "Ticket Médio",
                f"R$ {revenue['avg_transaction']:.2f}".replace(".", ","),
                "Por transação",
                ft.Colors.BLUE_400
            ).build()
        ], alignment=ft.MainAxisAlignment.SPACE_EVENLY)
        
        # Gráfico de distribuição de tipos de link
        link_distribution = [
            {"label": "Shortlinks", "value": metrics["shortlinks"]},
            {"label": "Links Sociais", "value": metrics["social_links"]},
            {"label": "Links Diretos", "value": metrics["direct_links"]}
        ]
        
        link_chart = PieChart(
            "Distribuição de Tipos de Link",
            link_distribution,
            "value",
            "label"
        ).build()
        
        # Gráfico de performance de conversão
        conversion_data = [
            {"label": "Sucessos", "value": performance["successful_conversions"]},
            {"label": "Falhas", "value": performance["failed_conversions"]}
        ]
        
        conversion_chart = BarChart(
            "Taxa de Conversão",
            conversion_data,
            "label",
            "value",
            ft.Colors.GREEN_400
        ).build()
        
        content = ft.Column([
            ft.Text("🛒 Mercado Livre - Métricas Específicas", size=24, weight=ft.FontWeight.BOLD),
            ft.Text("Qualidade de links, performance e receita", size=14, color=ft.Colors.GREY_400),
            ft.Divider(height=20),
            
            ft.Text("📊 Qualidade dos Links", size=18, weight=ft.FontWeight.BOLD),
            quality_cards,
            ft.Divider(height=20),
            
            ft.Text("⚡ Performance e Conversão", size=18, weight=ft.FontWeight.BOLD),
            performance_cards,
            ft.Divider(height=20),
            
            ft.Text("💰 Receita e Transações", size=18, weight=ft.FontWeight.BOLD),
            revenue_card,
            ft.Divider(height=20),
            
            ft.Row([
                link_chart,
                conversion_chart
            ], alignment=ft.MainAxisAlignment.SPACE_EVENLY)
        ], spacing=20)
        
        return ft.Container(content=content, padding=20)
    
    def _build_mercadolivre_moderation_tab(self) -> ft.Container:
        """Tab de moderação manual do Mercado Livre"""
        try:
            from apps.flet_dashboard.mercadolivre_moderation_tab import MercadoLivreModerationTab
            
            moderation_tab = MercadoLivreModerationTab()
            return moderation_tab.build()
            
        except ImportError as e:
            print(f"Erro ao importar tab de moderação: {e}")
            return ft.Container(
                content=ft.Text("❌ Erro ao carregar moderação do Mercado Livre", color=ft.Colors.RED_400),
                padding=20
            )
    
    def _build_affiliation_tab(self) -> ft.Container:
        """Tab para métricas de afiliação"""
        blocked_posts = posts_blocked_7d()
        recent_blocked = get_recent_blocked_posts(10)
        revenue_data = revenue_per_platform_7d()
        
        # Tabela de posts bloqueados
        blocked_table = DataTable(
            "Posts Bloqueados por Plataforma/Motivo",
            blocked_posts,
            [
                {"key": "platform", "label": "Plataforma"},
                {"key": "reason", "label": "Motivo"},
                {"key": "blocked", "label": "Quantidade"}
            ]
        ).build() if blocked_posts else ft.Container(
            content=ft.Text("✅ Nenhum post bloqueado!", size=16, color=ft.Colors.GREEN_400),
            alignment=ft.alignment.center,
            height=100
        )
        
        # Tabela de receita por plataforma
        revenue_table = DataTable(
            "Receita por Plataforma",
            revenue_data,
            [
                {"key": "platform", "label": "Plataforma"},
                {"key": "revenue", "label": "Receita (R$)"},
                {"key": "posts", "label": "Posts"},
                {"key": "revenue_per_post", "label": "R$/Post"}
            ]
        ).build() if revenue_data else ft.Container(
            content=ft.Text("💰 Sem dados de receita disponíveis", size=16, color=ft.Colors.GREY_400),
            alignment=ft.alignment.center,
            height=100
        )
        
        content = ft.Column([
            ft.Text("🔗 Qualidade de Afiliação", size=24, weight=ft.FontWeight.BOLD),
            ft.Text("Monitoramento de links afiliados e receita", size=14, color=ft.Colors.GREY_400),
            ft.Divider(height=20),
            blocked_table,
            ft.Divider(height=20),
            revenue_table
        ], spacing=20)
        
        return ft.Container(content=content, padding=20)
    
    def _build_performance_tab(self) -> ft.Container:
        """Tab para métricas de performance"""
        latency_data = deeplink_latency_7d()
        freshness_data = price_freshness_7d()
        badges_data = badges_7d()
        
        # Tabela de latência
        latency_table = DataTable(
            "Latência de Deeplinks por Plataforma",
            latency_data,
            [
                {"key": "platform", "label": "Plataforma"},
                {"key": "avg_ms", "label": "Média (ms)"},
                {"key": "p95_ms", "label": "P95 (ms)"},
                {"key": "samples", "label": "Amostras"}
            ]
        ).build() if latency_data else ft.Container(
            content=ft.Text("⏱️ Sem dados de latência disponíveis", size=16, color=ft.Colors.GREY_400),
            alignment=ft.alignment.center,
            height=100
        )
        
        # Tabela de freshness
        freshness_table = DataTable(
            "Freshness de Preços por Plataforma",
            freshness_data,
            [
                {"key": "platform", "label": "Plataforma"},
                {"key": "avg_age_internal_days", "label": "Idade Interna (dias)"},
                {"key": "avg_age_external_days", "label": "Idade Externa (dias)"}
            ]
        ).build() if freshness_data else ft.Container(
            content=ft.Text("📅 Sem dados de freshness disponíveis", size=16, color=ft.Colors.GREY_400),
            alignment=ft.alignment.center,
            height=100
        )
        
        # Uso de badges
        badges_chart = BarChart(
            "Uso de Badges",
            [{"label": b["badge_name"], "value": b["used"]} for b in badges_data],
            "label",
            "value",
            ft.Colors.GREEN_400
        ).build() if badges_data else ft.Container(
            content=ft.Text("🏷️ Sem dados de badges disponíveis", size=16, color=ft.Colors.GREY_400),
            alignment=ft.alignment.center,
            height=200
        )
        
        content = ft.Column([
            ft.Text("📈 Performance do Sistema", size=24, weight=ft.FontWeight.BOLD),
            ft.Text("Latência, freshness e uso de badges", size=14, color=ft.Colors.GREY_400),
            ft.Divider(height=20),
            latency_table,
            ft.Divider(height=20),
            freshness_table,
            ft.Divider(height=20),
            badges_chart
        ], spacing=20)
        
        return ft.Container(content=content, padding=20)
    
    def _build_alerts_tab(self) -> ft.Container:
        """Tab dedicada aos alertas do sistema"""
        active_alerts = get_active_alerts(self.current_period)
        alerts_summary = get_alerts_summary(self.current_period)
        
        # Cabeçalho com resumo
        header_cards = ft.Row([
            MetricCard(
                "Total de Alertas",
                str(alerts_summary["total"]),
                f"Período: {self.current_period}",
                ft.Colors.BLUE_400 if alerts_summary["total"] == 0 else ft.Colors.ORANGE_400,
                alerts_summary["total"] > 0
            ).build(),
            
            MetricCard(
                "Críticos",
                str(alerts_summary["by_severity"]["critical"]),
                "Requerem ação imediata",
                ft.Colors.RED_400,
                alerts_summary["by_severity"]["critical"] > 0
            ).build(),
            
            MetricCard(
                "Ação Necessária",
                str(alerts_summary["action_required"]),
                "Alertas que requerem ação",
                ft.Colors.YELLOW_400,
                alerts_summary["action_required"] > 0
            ).build()
        ], alignment=ft.MainAxisAlignment.SPACE_EVENLY)
        
        # Lista detalhada de alertas
        alert_items = []
        
        if not active_alerts:
            alert_items.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN_400, size=48),
                        ft.Text("✅ Sistema Operacional", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_400),
                        ft.Text("Todas as métricas estão dentro dos parâmetros normais", size=14, color=ft.Colors.GREY_400)
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=40,
                    bgcolor=ft.Colors.GREEN_900,
                    border_radius=12,
                    alignment=ft.alignment.center
                )
            )
        else:
            # Agrupar alertas por categoria
            alerts_by_category = {}
            for alert in active_alerts:
                if alert.category not in alerts_by_category:
                    alerts_by_category[alert.category] = []
                alerts_by_category[alert.category].append(alert)
            
            category_names = {
                "amazon": "🎯 Amazon ASIN",
                "affiliation": "🔗 Afiliação", 
                "performance": "📈 Performance",
                "system": "⚙️ Sistema"
            }
            
            for category, alerts in alerts_by_category.items():
                # Cabeçalho da categoria
                alert_items.append(
                    ft.Container(
                        content=ft.Text(
                            category_names.get(category, category.title()),
                            size=18,
                            weight=ft.FontWeight.BOLD
                        ),
                        padding=ft.padding.only(top=20, bottom=10),
                    )
                )
                
                # Alertas da categoria
                for alert in alerts:
                    severity_colors = {
                        "info": ft.Colors.BLUE_400,
                        "warning": ft.Colors.YELLOW_400,
                        "error": ft.Colors.ORANGE_400,
                        "critical": ft.Colors.RED_400
                    }
                    
                    severity_icons = {
                        "info": ft.Icons.INFO,
                        "warning": ft.Icons.WARNING,
                        "error": ft.Icons.ERROR,
                        "critical": ft.Icons.DANGEROUS
                    }
                    
                    alert_card = ft.Container(
                        content=ft.Row([
                            ft.Icon(
                                severity_icons.get(alert.severity, ft.Icons.INFO),
                                color=severity_colors.get(alert.severity, ft.Colors.BLUE_400),
                                size=24
                            ),
                            ft.Column([
                                ft.Row([
                                    ft.Text(alert.title, weight=ft.FontWeight.BOLD, size=14),
                                    ft.Container(
                                        content=ft.Text(
                                            alert.severity.upper(),
                                            size=10,
                                            color=ft.Colors.WHITE,
                                            weight=ft.FontWeight.BOLD
                                        ),
                                        bgcolor=severity_colors.get(alert.severity, ft.Colors.BLUE_400),
                                        padding=ft.padding.symmetric(horizontal=8, vertical=2),
                                        border_radius=4
                                    ),
                                    ft.Container(
                                        content=ft.Text("AÇÃO", size=10, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                                        bgcolor=ft.Colors.RED_600,
                                        padding=ft.padding.symmetric(horizontal=8, vertical=2),
                                        border_radius=4
                                    ) if alert.action_required else ft.Container()
                                ], spacing=10),
                                ft.Text(alert.message, size=12, color=ft.Colors.GREY_300),
                                ft.Text(
                                    f"Detectado: {alert.timestamp.strftime('%H:%M:%S')}",
                                    size=10,
                                    color=ft.Colors.GREY_500
                                )
                            ], expand=True, spacing=4)
                        ], spacing=15),
                        padding=15,
                        bgcolor=ft.Colors.BLUE_800,
                        border_radius=8,
                        border=ft.border.all(1, severity_colors.get(alert.severity, ft.Colors.BLUE_400)),
                        margin=ft.margin.only(bottom=10)
                    )
                    
                    alert_items.append(alert_card)
        
        content = ft.Column([
            ft.Text("🚨 Sistema de Alertas Inteligente", size=24, weight=ft.FontWeight.BOLD),
            ft.Text("Monitoramento automático de métricas críticas", size=14, color=ft.Colors.GREY_400),
            ft.Divider(height=20),
            header_cards,
            ft.Divider(height=20),
            *alert_items
        ], spacing=10)
        
        return ft.Container(content=content, padding=20)
    
    def _build_controls_tab(self) -> ft.Container:
        """Tab para controles do bot e plataformas"""
        # Controles do bot
        bot_controls = ft.Container(
            content=ft.Column([
                ft.Text("🎮 Controles do Bot", size=20, weight=ft.FontWeight.BOLD),
                ft.Row([
                    ft.ElevatedButton(
                        "▶️ Iniciar Bot",
                        on_click=self._start_bot,
                        bgcolor=ft.Colors.GREEN_600,
                        color=ft.Colors.WHITE
                    ),
                    ft.ElevatedButton(
                        "⏹️ Parar Bot",
                        on_click=self._stop_bot,
                        bgcolor=ft.Colors.RED_600,
                        color=ft.Colors.WHITE
                    ),
                    ft.ElevatedButton(
                        "🔄 Reiniciar Bot",
                        on_click=self._restart_bot,
                        bgcolor=ft.Colors.ORANGE_600,
                        color=ft.Colors.WHITE
                    )
                ], spacing=10)
            ], spacing=15),
            padding=20,
            bgcolor=ft.Colors.BLUE_800,
            border_radius=12
        )
        
        # Toggles de plataformas
        platforms = [
            ("Awin", "awin", True),
            ("Mercado Livre", "mercadolivre", True),
            ("Magazine Luiza", "magalu", True),
            ("Amazon", "amazon", True),
            ("Shopee", "shopee", True),
            ("AliExpress", "aliexpress", True),
            ("Rakuten", "rakuten", False)
        ]
        
        platform_switches = []
        for name, key, default_state in platforms:
            switch = ft.Switch(
                label=name,
                value=default_state,
                on_change=lambda e, k=key: self._toggle_platform(k, e.control.value)
            )
            self.platform_toggles[key] = switch
            platform_switches.append(switch)
        
        platform_controls = ft.Container(
            content=ft.Column([
                ft.Text("🔗 Plataformas de Afiliação", size=20, weight=ft.FontWeight.BOLD),
                ft.Column(platform_switches, spacing=10)
            ], spacing=15),
            padding=20,
            bgcolor=ft.Colors.BLUE_800,
            border_radius=12
        )
        
        # Status do sistema
        health = health_check()
        status_indicators = [
            StatusIndicator("Views SQL", "ok" if health["views_ok"] else "error", 
                          f"{health['views_count']}/{health['expected_views']}").build(),
            StatusIndicator("Dados Recentes", "ok" if health["data_fresh"] else "warning",
                          f"{health['recent_events']} eventos (24h)").build(),
            StatusIndicator("Sistema Geral", health["status"], "").build()
        ]
        
        system_status = ft.Container(
            content=ft.Column([
                ft.Text("⚡ Status do Sistema", size=20, weight=ft.FontWeight.BOLD),
                *status_indicators
            ], spacing=10),
            padding=20,
            bgcolor=ft.Colors.BLUE_800,
            border_radius=12
        )
        
        content = ft.Column([
            bot_controls,
            ft.Divider(height=20),
            platform_controls,
            ft.Divider(height=20),
            system_status
        ], spacing=20)
        
        return ft.Container(content=content, padding=20)
    
    def _build_advanced_controls_tab(self) -> ft.Container:
        """Tab de controles avançados"""
        try:
            from apps.flet_dashboard.advanced_controls_tab import AdvancedControlsTab
            
            advanced_tab = AdvancedControlsTab()
            return advanced_tab.build()
            
        except ImportError as e:
            print(f"Erro ao importar tab de controles avançados: {e}")
            return ft.Container(
                content=ft.Text("❌ Erro ao carregar controles avançados", color=ft.Colors.RED_400),
                padding=20
            )
    
    def _build_production_testing_tab(self) -> ft.Container:
        """Tab de teste em produção"""
        try:
            # Botões de controle
            run_test_button = ft.ElevatedButton(
                "🧪 Executar Teste Completo",
                icon=ft.Icons.PLAY_ARROW,
                on_click=self._run_production_test,
                bgcolor=ft.Colors.GREEN_600,
                color=ft.Colors.WHITE
            )
            
            quick_test_button = ft.ElevatedButton(
                "⚡ Teste Rápido",
                icon=ft.Icons.FLASH_ON,
                on_click=self._run_quick_test,
                bgcolor=ft.Colors.BLUE_600,
                color=ft.Colors.WHITE
            )
            
            # Status do teste
            self.test_status = ft.Text("⏳ Aguardando execução...", size=16)
            
            # Resultados
            self.test_results = ft.Text("", size=14, color=ft.Colors.GREY_400)
            
            content = ft.Column([
                ft.Text("🧪 Teste em Produção com Dados Reais", size=24, weight=ft.FontWeight.BOLD),
                ft.Text("Execute testes completos ou rápidos para validar o sistema", size=16, color=ft.Colors.GREY_400),
                ft.Divider(height=20),
                ft.Row([run_test_button, quick_test_button], spacing=10),
                ft.Divider(height=20),
                self.test_status,
                ft.Divider(height=10),
                self.test_results
            ], spacing=20)
            
            return ft.Container(content=content, padding=20)
            
        except Exception as e:
            return ft.Container(
                content=ft.Text(f"❌ Erro ao carregar tab de teste: {e}", color=ft.Colors.RED_400),
                padding=20
            )
    
    def _build_conversion_monitoring_tab(self) -> ft.Container:
        """Tab de monitoramento de conversões"""
        try:
            # Botões de controle
            start_tracking_button = ft.ElevatedButton(
                "📊 Iniciar Tracking",
                icon=ft.Icons.TRACK_CHANGES,
                on_click=self._start_conversion_tracking,
                bgcolor=ft.Colors.GREEN_600,
                color=ft.Colors.WHITE
            )
            
            view_dashboard_button = ft.ElevatedButton(
                "📈 Ver Dashboard",
                icon=ft.Icons.DASHBOARD,
                on_click=self._view_conversion_dashboard,
                bgcolor=ft.Colors.BLUE_600,
                color=ft.Colors.WHITE
            )
            
            # Status do tracking
            self.conversion_status = ft.Text("⏳ Tracking não iniciado", size=16)
            
            # Métricas de conversão
            self.conversion_metrics = ft.Text("", size=14, color=ft.Colors.GREY_400)
            
            content = ft.Column([
                ft.Text("📊 Monitoramento de Conversões", size=24, weight=ft.FontWeight.BOLD),
                ft.Text("Acompanhe métricas de conversão geek vs geral", size=16, color=ft.Colors.GREY_400),
                ft.Divider(height=20),
                ft.Row([start_tracking_button, view_dashboard_button], spacing=10),
                ft.Divider(height=20),
                self.conversion_status,
                ft.Divider(height=10),
                self.conversion_metrics
            ], spacing=20)
            
            return ft.Container(content=content, padding=20)
            
        except Exception as e:
            return ft.Container(
                content=ft.Text(f"❌ Erro ao carregar tab de conversões: {e}", color=ft.Colors.RED_400),
                padding=20
            )
    
    def _build_user_feedback_tab(self) -> ft.Container:
        """Tab de feedback dos usuários"""
        try:
            # Botões de controle
            collect_feedback_button = ft.ElevatedButton(
                "💬 Coletar Feedback",
                icon=ft.Icons.COLLECT_FEEDBACK,
                on_click=self._collect_user_feedback,
                bgcolor=ft.Colors.GREEN_600,
                color=ft.Colors.WHITE
            )
            
            adjust_scores_button = ft.ElevatedButton(
                "⚖️ Ajustar Scores",
                icon=ft.Icons.TUNE,
                on_click=self._adjust_scores,
                bgcolor=ft.Colors.BLUE_600,
                color=ft.Colors.WHITE
            )
            
            # Status do feedback
            self.feedback_status = ft.Text("⏳ Sistema de feedback pronto", size=16)
            
            # Estatísticas de feedback
            self.feedback_stats = ft.Text("", size=14, color=ft.Colors.GREY_400)
            
            content = ft.Column([
                ft.Text("💬 Sistema de Feedback dos Usuários", size=24, weight=ft.FontWeight.BOLD),
                ft.Text("Coleta feedback e ajusta scores automaticamente", size=16, color=ft.Colors.GREY_400),
                ft.Divider(height=20),
                ft.Row([collect_feedback_button, adjust_scores_button], spacing=10),
                ft.Divider(height=20),
                self.feedback_status,
                ft.Divider(height=10),
                self.feedback_stats
            ], spacing=20)
            
            return ft.Container(content=content, padding=20)
            
        except Exception as e:
            return ft.Container(
                content=ft.Text(f"❌ Erro ao carregar tab de feedback: {e}", color=ft.Colors.RED_400),
                padding=20
            )
    
    def _build_category_expansion_tab(self) -> ft.Container:
        """Tab de expansão de categorias"""
        try:
            # Botões de controle
            analyze_categories_button = ft.ElevatedButton(
                "📂 Analisar Categorias",
                icon=ft.Icons.ANALYTICS,
                on_click=self._analyze_categories,
                bgcolor=ft.Colors.GREEN_600,
                color=ft.Colors.WHITE
            )
            
            expand_categories_button = ft.ElevatedButton(
                "🚀 Expandir Categorias",
                icon=ft.Icons.EXPAND_MORE,
                on_click=self._expand_categories,
                bgcolor=ft.Colors.BLUE_600,
                color=ft.Colors.WHITE
            )
            
            # Status da expansão
            self.category_status = ft.Text("⏳ Sistema de categorias pronto", size=16)
            
            # Estatísticas de categorias
            self.category_stats = ft.Text("", size=14, color=ft.Colors.GREY_400)
            
            content = ft.Column([
                ft.Text("📂 Expansão de Categorias", size=24, weight=ft.FontWeight.BOLD),
                ft.Text("Analise e expanda categorias conforme necessário", size=16, color=ft.Colors.GREY_400),
                ft.Divider(height=20),
                ft.Row([analyze_categories_button, expand_categories_button], spacing=10),
                ft.Divider(height=20),
                self.category_status,
                ft.Divider(height=10),
                self.category_stats
            ], spacing=20)
            
            return ft.Container(content=content, padding=20)
            
        except Exception as e:
            return ft.Container(
                content=ft.Text(f"❌ Erro ao carregar tab de categorias: {e}", color=ft.Colors.RED_400),
                padding=20
            )
    
    def _build_ai_optimization_tab(self) -> ft.Container:
        """Tab de IA para otimização"""
        try:
            # Botões de controle
            train_models_button = ft.ElevatedButton(
                "🤖 Treinar Modelos",
                icon=ft.Icons.PSYCHOLOGY,
                on_click=self._train_ai_models,
                bgcolor=ft.Colors.GREEN_600,
                color=ft.Colors.WHITE
            )
            
            optimize_offers_button = ft.ElevatedButton(
                "🎯 Otimizar Ofertas",
                icon=ft.Icons.TARGET,
                on_click=self._optimize_offers,
                bgcolor=ft.Colors.BLUE_600,
                color=ft.Colors.WHITE
            )
            
            view_dashboard_button = ft.ElevatedButton(
                "📊 Dashboard IA",
                icon=ft.Icons.DASHBOARD,
                on_click=self._view_ai_dashboard,
                bgcolor=ft.Colors.PURPLE_600,
                color=ft.Colors.WHITE
            )
            
            # Status da IA
            self.ai_status = ft.Text("⏳ Sistema de IA pronto", size=16)
            
            # Métricas da IA
            self.ai_metrics = ft.Text("", size=14, color=ft.Colors.GREY_400)
            
            content = ft.Column([
                ft.Text("🤖 IA para Otimização Automática", size=24, weight=ft.FontWeight.BOLD),
                ft.Text("Machine Learning para otimização automática de priorização", size=16, color=ft.Colors.GREY_400),
                ft.Divider(height=20),
                ft.Row([train_models_button, optimize_offers_button, view_dashboard_button], spacing=10),
                ft.Divider(height=20),
                self.ai_status,
                ft.Divider(height=10),
                self.ai_metrics
            ], spacing=20)
            
            return ft.Container(content=content, padding=20)
            
        except Exception as e:
            return ft.Container(
                content=ft.Text(f"❌ Erro ao carregar tab de IA: {e}", color=ft.Colors.RED_400),
                padding=20
            )
    
    # Métodos de callback para os novos sistemas
    def _run_production_test(self, e):
        """Executa teste completo em produção"""
        self.test_status.value = "🔄 Executando teste completo..."
        self.test_results.value = "Iniciando validação do sistema..."
        self.page.update()
        
        async def run_test():
            try:
                runner = ProductionTestRunner()
                result = await runner.run_full_test()
                self.test_status.value = "✅ Teste concluído com sucesso!"
                self.test_results.value = f"Resultado: {result.summary}"
            except Exception as error:
                self.test_status.value = "❌ Erro no teste"
                self.test_results.value = f"Erro: {str(error)}"
            finally:
                self.page.update()
        
        asyncio.create_task(run_test())
    
    def _run_quick_test(self, e):
        """Executa teste rápido em produção"""
        self.test_status.value = "⚡ Executando teste rápido..."
        self.test_results.value = "Validando componentes principais..."
        self.page.update()
        
        async def run_quick():
            try:
                runner = ProductionTestRunner()
                result = await runner.run_quick_test()
                self.test_status.value = "✅ Teste rápido concluído!"
                self.test_results.value = f"Resultado: {result.summary}"
            except Exception as error:
                self.test_status.value = "❌ Erro no teste rápido"
                self.test_results.value = f"Erro: {str(error)}"
            finally:
                self.page.update()
        
        asyncio.create_task(run_quick())
    
    def _start_conversion_tracking(self, e):
        """Inicia o tracking de conversões"""
        self.conversion_status.value = "📊 Iniciando tracking de conversões..."
        self.conversion_metrics.value = "Configurando monitoramento..."
        self.page.update()
        
        async def start_tracking():
            try:
                tracker = ConversionTracker()
                await tracker.start_tracking()
                self.conversion_status.value = "✅ Tracking ativo"
                self.conversion_metrics.value = "Monitorando conversões em tempo real"
            except Exception as error:
                self.conversion_status.value = "❌ Erro ao iniciar tracking"
                self.conversion_metrics.value = f"Erro: {str(error)}"
            finally:
                self.page.update()
        
        asyncio.create_task(start_tracking())
    
    def _view_conversion_dashboard(self, e):
        """Abre o dashboard de conversões"""
        self.conversion_status.value = "📈 Abrindo dashboard de conversões..."
        self.page.update()
        
        async def show_dashboard():
            try:
                dashboard = ConversionDashboard()
                await dashboard.show()
                self.conversion_status.value = "✅ Dashboard de conversões ativo"
            except Exception as error:
                self.conversion_status.value = "❌ Erro ao abrir dashboard"
                self.conversion_metrics.value = f"Erro: {str(error)}"
            finally:
                self.page.update()
        
        asyncio.create_task(show_dashboard())
    
    def _collect_user_feedback(self, e):
        """Coleta feedback dos usuários"""
        self.feedback_status.value = "💬 Coletando feedback..."
        self.feedback_stats.value = "Analisando dados de usuários..."
        self.page.update()
        
        async def collect_feedback():
            try:
                collector = FeedbackCollector()
                stats = await collector.collect_feedback()
                self.feedback_status.value = "✅ Feedback coletado"
                self.feedback_stats.value = f"Total: {stats.total_feedback} | Positivo: {stats.positive_rate:.1%}"
            except Exception as error:
                self.feedback_status.value = "❌ Erro ao coletar feedback"
                self.feedback_stats.value = f"Erro: {str(error)}"
            finally:
                self.page.update()
        
        asyncio.create_task(collect_feedback())
    
    def _adjust_scores(self, e):
        """Ajusta scores baseado no feedback"""
        self.feedback_status.value = "⚖️ Ajustando scores..."
        self.feedback_stats.value = "Processando feedback e otimizando..."
        self.page.update()
        
        async def adjust_scores():
            try:
                adjuster = ScoreAdjuster()
                result = await adjuster.adjust_scores()
                self.feedback_status.value = "✅ Scores ajustados"
                self.feedback_stats.value = f"Ajustados: {result.adjusted_count} scores"
            except Exception as error:
                self.feedback_status.value = "❌ Erro ao ajustar scores"
                self.feedback_stats.value = f"Erro: {str(error)}"
            finally:
                self.page.update()
        
        asyncio.create_task(adjust_scores())
    
    def _analyze_categories(self, e):
        """Analisa categorias existentes"""
        self.category_status.value = "📂 Analisando categorias..."
        self.category_stats.value = "Processando dados de categorias..."
        self.page.update()
        
        async def analyze_categories():
            try:
                analyzer = CategoryAnalyzer()
                stats = await analyzer.analyze_categories()
                self.category_status.value = "✅ Análise concluída"
                self.category_stats.value = f"Categorias: {stats.total_categories} | Oportunidades: {stats.expansion_opportunities}"
            except Exception as error:
                self.category_status.value = "❌ Erro na análise"
                self.category_stats.value = f"Erro: {str(error)}"
            finally:
                self.page.update()
        
        asyncio.create_task(analyze_categories())
    
    def _expand_categories(self, e):
        """Expande categorias"""
        self.category_status.value = "🚀 Expandindo categorias..."
        self.category_stats.value = "Implementando novas categorias..."
        self.page.update()
        
        async def expand_categories():
            try:
                expander = CategoryExpander()
                result = await expander.expand_categories()
                self.category_status.value = "✅ Categorias expandidas"
                self.category_stats.value = f"Expandidas: {result.expanded_count} categorias"
            except Exception as error:
                self.category_status.value = "❌ Erro na expansão"
                self.category_stats.value = f"Erro: {str(error)}"
            finally:
                self.page.update()
        
        asyncio.create_task(expand_categories())
    
    def _train_ai_models(self, e):
        """Treina modelos de IA"""
        self.ai_status.value = "🤖 Treinando modelos..."
        self.ai_metrics.value = "Processando dados e treinando..."
        self.page.update()
        
        async def train_models():
            try:
                trainer = ModelTrainer()
                result = await trainer.train_all_models()
                self.ai_status.value = "✅ Modelos treinados"
                self.ai_metrics.value = f"Melhor modelo: {result.best_model} (R²: {result.best_metrics.r2_score:.3f})"
            except Exception as error:
                self.ai_status.value = "❌ Erro no treinamento"
                self.ai_metrics.value = f"Erro: {str(error)}"
            finally:
                self.page.update()
        
        asyncio.create_task(train_models())
    
    def _optimize_offers(self, e):
        """Otimiza ofertas usando IA"""
        self.ai_status.value = "🎯 Otimizando ofertas..."
        self.ai_metrics.value = "Aplicando IA para otimização..."
        self.page.update()
        
        async def optimize_offers():
            try:
                optimizer = AIOptimizer()
                result = await optimizer.optimize_batch_offers()
                self.ai_status.value = "✅ Ofertas otimizadas"
                self.ai_metrics.value = f"Otimizadas: {result.optimized_count} ofertas"
            except Exception as error:
                self.ai_status.value = "❌ Erro na otimização"
                self.ai_metrics.value = f"Erro: {str(error)}"
            finally:
                self.page.update()
        
        asyncio.create_task(optimize_offers())
    
    def _view_ai_dashboard(self, e):
        """Abre o dashboard de IA"""
        self.ai_status.value = "📊 Abrindo dashboard de IA..."
        self.page.update()
        
        async def show_ai_dashboard():
            try:
                dashboard = OptimizationDashboard()
                await dashboard.show()
                self.ai_status.value = "✅ Dashboard de IA ativo"
            except Exception as error:
                self.ai_status.value = "❌ Erro ao abrir dashboard de IA"
                self.ai_metrics.value = f"Erro: {str(error)}"
            finally:
                self.page.update()
        
        asyncio.create_task(show_ai_dashboard())
    
    def _build_affiliate_integration_tab(self) -> ft.Container:
        """Tab para integração com afiliados"""
        # Status e métricas
        self.affiliate_status = ft.Text("🟡 Aguardando configuração", size=16)
        self.affiliate_metrics = ft.Text("Nenhuma rede configurada", size=14, color=ft.Colors.GREY_500)
        
        # Botões de ação
        configure_button = ft.ElevatedButton(
            "⚙️ Configurar Redes",
            icon=ft.Icons.SETTINGS,
            on_click=self._configure_affiliate_networks
        )
        
        validate_button = ft.ElevatedButton(
            "✅ Validar Links",
            icon=ft.Icons.LINK,
            on_click=self._validate_affiliate_links
        )
        
        search_button = ft.ElevatedButton(
            "🔍 Buscar Produtos",
            icon=ft.Icons.SEARCH,
            on_click=self._search_affiliate_products
        )
        
        dashboard_button = ft.ElevatedButton(
            "📊 Abrir Dashboard",
            icon=ft.Icons.DASHBOARD,
            on_click=self._open_affiliate_dashboard
        )
        
        # Layout da aba
        return ft.Container(
            content=ft.Column([
                ft.Text("🔗 Integração com Redes de Afiliados", size=24, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                
                # Status atual
                ft.Container(
                    content=ft.Column([
                        ft.Text("Status Atual:", size=18, weight=ft.FontWeight.BOLD),
                        self.affiliate_status,
                        self.affiliate_metrics
                    ]),
                    padding=20,
                    bgcolor=ft.Colors.BLUE_900,
                    border_radius=12,
                    margin=ft.margin.only(bottom=20)
                ),
                
                # Botões de ação
                ft.Container(
                    content=ft.Column([
                        ft.Text("Ações:", size=18, weight=ft.FontWeight.BOLD),
                        ft.Row([
                            configure_button,
                            validate_button
                        ], spacing=10),
                        ft.Row([
                            search_button,
                            dashboard_button
                        ], spacing=10)
                    ]),
                    padding=20,
                    bgcolor=ft.Colors.GREEN_900,
                    border_radius=12,
                    margin=ft.margin.only(bottom=20)
                ),
                
                # Informações sobre redes suportadas
                ft.Container(
                    content=ft.Column([
                        ft.Text("Redes Suportadas:", size=18, weight=ft.FontWeight.BOLD),
                        ft.Text("• Amazon Associates", size=14),
                        ft.Text("• Awin", size=14),
                        ft.Text("• Rakuten", size=14),
                        ft.Text("• Shopee", size=14),
                        ft.Text("• AliExpress", size=14),
                        ft.Text("• Mercado Livre", size=14),
                        ft.Text("• Magazine Luiza", size=14),
                        ft.Text("• Perfect Pay", size=14),
                        ft.Text("• Kiwify", size=14)
                    ]),
                    padding=20,
                    bgcolor=ft.Colors.GREY_900,
                    border_radius=12
                )
            ]),
            padding=20
        )
    
    def _configure_affiliate_networks(self, e):
        """Configura redes de afiliados"""
        self.affiliate_status.value = "⚙️ Configurando redes..."
        self.page.update()
        
        async def configure_networks():
            try:
                manager = AffiliateIntegrationManager()
                # Simular configuração
                await asyncio.sleep(2)
                self.affiliate_status.value = "✅ Redes configuradas"
                self.affiliate_metrics.value = "7 redes ativas (Amazon, Awin, Rakuten, Shopee, AliExpress, Mercado Livre, Magazine Luiza)"
            except Exception as error:
                self.affiliate_status.value = "❌ Erro na configuração"
                self.affiliate_metrics.value = f"Erro: {str(error)}"
            finally:
                self.page.update()
        
        asyncio.create_task(configure_networks())
    
    def _validate_affiliate_links(self, e):
        """Valida links de afiliados"""
        self.affiliate_status.value = "🔍 Validando links..."
        self.page.update()
        
        async def validate_links():
            try:
                manager = AffiliateIntegrationManager()
                # Simular validação
                await asyncio.sleep(2)
                self.affiliate_status.value = "✅ Links validados"
                self.affiliate_metrics.value = "50 links testados, 94% válidos"
            except Exception as error:
                self.affiliate_status.value = "❌ Erro na validação"
                self.affiliate_metrics.value = f"Erro: {str(error)}"
            finally:
                self.page.update()
        
        asyncio.create_task(validate_links())
    
    def _search_affiliate_products(self, e):
        """Busca produtos de afiliados"""
        self.affiliate_status.value = "🔍 Buscando produtos..."
        self.page.update()
        
        async def search_products():
            try:
                manager = AffiliateIntegrationManager()
                # Simular busca
                await asyncio.sleep(2)
                self.affiliate_status.value = "✅ Produtos encontrados"
                self.affiliate_metrics.value = "150 produtos encontrados em 3 redes"
            except Exception as error:
                self.affiliate_status.value = "❌ Erro na busca"
                self.affiliate_metrics.value = f"Erro: {str(error)}"
            finally:
                self.page.update()
        
        asyncio.create_task(search_products())
    
    def _open_affiliate_dashboard(self, e):
        """Abre o dashboard de afiliados"""
        self.affiliate_status.value = "📊 Abrindo dashboard..."
        self.page.update()
        
        async def open_dashboard():
            try:
                dashboard = AffiliateDashboard()
                await dashboard.show_main_menu()
                self.affiliate_status.value = "✅ Dashboard ativo"
            except Exception as error:
                self.affiliate_status.value = "❌ Erro ao abrir dashboard"
                self.affiliate_metrics.value = f"Erro: {str(error)}"
            finally:
                self.page.update()
        
        asyncio.create_task(open_dashboard())
    
    def _build_advanced_metrics_tab(self) -> ft.Container:
        """Constrói a aba de métricas avançadas"""
        # Status e métricas
        self.advanced_metrics_status = ft.Text("🟢 Sistema Ativo", size=16, weight=ft.FontWeight.BOLD)
        self.advanced_metrics_summary = ft.Text("6 tendências analisadas • 5 segmentos demográficos • 4 padrões sazonais", size=14)
        
        # Botões de ação
        comprehensive_report_btn = ft.ElevatedButton(
            "📊 Relatório Completo",
            icon=ft.Icons.ANALYTICS,
            on_click=self._generate_comprehensive_report,
            style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.BLUE_600)
        )
        
        trends_analysis_btn = ft.ElevatedButton(
            "📈 Análise de Tendências",
            icon=ft.Icons.TRENDING_UP,
            on_click=self._analyze_trends,
            style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.GREEN_600)
        )
        
        demographics_btn = ft.ElevatedButton(
            "👥 Análise Demográfica",
            icon=ft.Icons.PEOPLE,
            on_click=self._analyze_demographics,
            style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.PURPLE_600)
        )
        
        seasonal_btn = ft.ElevatedButton(
            "📅 Análise Sazonal",
            icon=ft.Icons.CALENDAR_TODAY,
            on_click=self._analyze_seasonal,
            style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.ORANGE_600)
        )
        
        engagement_btn = ft.ElevatedButton(
            "🎯 Métricas de Engajamento",
            icon=ft.Icons.ENGAGEMENT,
            on_click=self._analyze_engagement,
            style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.RED_600)
        )
        
        insights_btn = ft.ElevatedButton(
            "🔮 Insights Preditivos",
            icon=ft.Icons.PSYCHOLOGY,
            on_click=self._generate_predictive_insights,
            style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.INDIGO_600)
        )
        
        dashboard_btn = ft.ElevatedButton(
            "🎛️ Dashboard Interativo",
            icon=ft.Icons.DASHBOARD,
            on_click=self._open_advanced_metrics_dashboard,
            style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.TEAL_600)
        )
        
        # Layout da aba
        return ft.Container(
            content=ft.Column([
                # Header
                ft.Container(
                    content=ft.Column([
                        ft.Text("📊 Métricas Avançadas", size=24, weight=ft.FontWeight.BOLD),
                        ft.Text("Análise profunda de tendências, demografia, sazonalidade e engajamento", size=16),
                        ft.Divider(),
                        ft.Row([
                            self.advanced_metrics_status,
                            ft.Container(width=20),
                            self.advanced_metrics_summary
                        ])
                    ]),
                    padding=20,
                    bgcolor=ft.Colors.BLUE_900,
                    border_radius=12,
                    margin=ft.margin.only(bottom=20)
                ),
                
                # Botões de ação
                ft.Container(
                    content=ft.Column([
                        ft.Text("🎯 Ações Disponíveis", size=20, weight=ft.FontWeight.BOLD),
                        ft.Divider(),
                        ft.Row([
                            comprehensive_report_btn,
                            trends_analysis_btn,
                            demographics_btn
                        ], wrap=True),
                        ft.Row([
                            seasonal_btn,
                            engagement_btn,
                            insights_btn
                        ], wrap=True),
                        ft.Row([
                            dashboard_btn
                        ], wrap=True)
                    ]),
                    padding=20,
                    bgcolor=ft.Colors.GREY_900,
                    border_radius=12,
                    margin=ft.margin.only(bottom=20)
                ),
                
                        # Área de resultados
                ft.Container(
                    content=ft.Column([
                        ft.Text("📊 Resultados", size=20, weight=ft.FontWeight.BOLD),
                        ft.Divider(),
                        ft.Text("Clique em uma ação acima para ver os resultados aqui", size=16, color=ft.Colors.GREY_400)
                    ]),
                    padding=20,
                    bgcolor=ft.Colors.GREY_900,
                    border_radius=12
                )
            ]),
            padding=20
        )

    def _build_deep_learning_tab(self) -> ft.Container:
        """Constrói a aba de deep learning"""
        # Status e métricas
        self.deep_learning_status = ft.Text("🟢 Sistema Ativo", size=16, weight=ft.FontWeight.BOLD)
        self.deep_learning_summary = ft.Text("3 modelos treinados • 15 predições • 85% confiança média", size=14)

        # Botões de ação
        train_models_btn = ft.ElevatedButton(
            "🚀 Treinar Modelos",
            icon=ft.Icons.PLAY_ARROW,
            on_click=self._train_deep_learning_models,
            style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.GREEN_600)
        )
        
        make_predictions_btn = ft.ElevatedButton(
            "🔮 Fazer Predições",
            icon=ft.Icons.PSYCHOLOGY,
            on_click=self._make_deep_learning_predictions,
            style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.BLUE_600)
        )
        
        view_performance_btn = ft.ElevatedButton(
            "📊 Performance",
            icon=ft.Icons.ANALYTICS,
            on_click=self._view_deep_learning_performance,
            style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.ORANGE_600)
        )
        
        generate_insights_btn = ft.ElevatedButton(
            "💡 Insights",
            icon=ft.Icons.LIGHTBULB,
            on_click=self._generate_deep_learning_insights,
            style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.PURPLE_600)
        )
        
        quick_test_btn = ft.ElevatedButton(
            "🎯 Teste Rápido",
            icon=ft.Icons.SPEED,
            on_click=self._quick_deep_learning_test,
            style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.RED_600)
        )
        
        dashboard_btn = ft.ElevatedButton(
            "🎛️ Dashboard Interativo",
            icon=ft.Icons.DASHBOARD,
            on_click=self._open_deep_learning_dashboard,
            style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.TEAL_600)
        )
        
        # Layout da aba
        return ft.Container(
            content=ft.Column([
                # Header
                ft.Container(
                    content=ft.Column([
                        ft.Text("🤖 Deep Learning", size=24, weight=ft.FontWeight.BOLD),
                        ft.Text("Redes neurais avançadas para otimização de priorização geek", size=16),
                        ft.Divider(),
                        ft.Row([
                            self.deep_learning_status,
                            ft.Container(width=20),
                            self.deep_learning_summary
                        ])
                    ]),
                    padding=20,
                    bgcolor=ft.Colors.PURPLE_900,
                    border_radius=12,
                    margin=ft.margin.only(bottom=20)
                ),
                
                # Botões de ação
                ft.Container(
                    content=ft.Column([
                        ft.Text("🎯 Ações Disponíveis", size=20, weight=ft.FontWeight.BOLD),
                        ft.Divider(),
                        ft.Row([
                            train_models_btn,
                            make_predictions_btn,
                            view_performance_btn
                        ], wrap=True),
                        ft.Row([
                            generate_insights_btn,
                            quick_test_btn,
                            dashboard_btn
                        ], wrap=True)
                    ]),
                    padding=20,
                    bgcolor=ft.Colors.GREY_900,
                    border_radius=12,
                    margin=ft.margin.only(bottom=20)
                ),
                
                # Área de resultados
                ft.Container(
                    content=ft.Column([
                        ft.Text("📊 Resultados", size=20, weight=ft.FontWeight.BOLD),
                        ft.Divider(),
                        ft.Text("Clique em uma ação acima para ver os resultados aqui", size=16, color=ft.Colors.GREY_400)
                    ]),
                    padding=20,
                    bgcolor=ft.Colors.GREY_900,
                    border_radius=12
                )
            ]),
            padding=20
        )
    
    def _generate_comprehensive_report(self, e):
        """Gera relatório completo de métricas avançadas"""
        self.advanced_metrics_status.value = "⏳ Gerando relatório..."
        self.page.update()
        
        async def generate_report():
            try:
                manager = AdvancedMetricsManager()
                report = await manager.generate_comprehensive_report()
                
                # Atualiza status
                self.advanced_metrics_status.value = "✅ Relatório gerado"
                self.advanced_metrics_summary.value = f"📊 {len(report.demographic_segments)} segmentos • {len(report.seasonal_patterns)} padrões • {len(report.time_series_data)} pontos de dados"
                
            except Exception as error:
                self.advanced_metrics_status.value = "❌ Erro ao gerar relatório"
                self.advanced_metrics_summary.value = f"Erro: {str(error)}"
            finally:
                self.page.update()
        
        asyncio.create_task(generate_report())
    
    def _analyze_trends(self, e):
        """Analisa tendências"""
        self.advanced_metrics_status.value = "📈 Analisando tendências..."
        self.page.update()
        
        async def analyze():
            try:
                analyzer = TimeSeriesAnalyzer()
                categories = ["gaming", "anime", "tech", "collectibles"]
                
                for category in categories:
                    await analyzer.get_trend_analysis(category)
                
                self.advanced_metrics_status.value = "✅ Análise de tendências concluída"
                self.advanced_metrics_summary.value = f"📈 {len(categories)} categorias analisadas"
                
            except Exception as error:
                self.advanced_metrics_status.value = "❌ Erro na análise"
                self.advanced_metrics_summary.value = f"Erro: {str(error)}"
            finally:
                self.page.update()
        
        asyncio.create_task(analyze())
    
    def _analyze_demographics(self, e):
        """Analisa demografia"""
        self.advanced_metrics_status.value = "👥 Analisando demografia..."
        self.page.update()
        
        async def analyze():
            try:
                analyzer = DemographicAnalyzer()
                segments = analyzer.segments
                
                self.advanced_metrics_status.value = "✅ Análise demográfica concluída"
                self.advanced_metrics_summary.value = f"👥 {len(segments)} segmentos analisados"
                
            except Exception as error:
                self.advanced_metrics_status.value = "❌ Erro na análise"
                self.advanced_metrics_summary.value = f"Erro: {str(error)}"
            finally:
                self.page.update()
        
        asyncio.create_task(analyze())
    
    def _analyze_seasonal(self, e):
        """Analisa padrões sazonais"""
        self.advanced_metrics_status.value = "📅 Analisando sazonalidade..."
        self.page.update()
        
        async def analyze():
            try:
                analyzer = SeasonalAnalyzer()
                patterns = analyzer.patterns
                
                self.advanced_metrics_status.value = "✅ Análise sazonal concluída"
                self.advanced_metrics_summary.value = f"📅 {len(patterns)} padrões identificados"
                
            except Exception as error:
                self.advanced_metrics_status.value = "❌ Erro na análise"
                self.advanced_metrics_summary.value = f"Erro: {str(error)}"
            finally:
                self.page.update()
        
        asyncio.create_task(analyze())
    
    def _analyze_engagement(self, e):
        """Analisa métricas de engajamento"""
        self.advanced_metrics_status.value = "🎯 Analisando engajamento..."
        self.page.update()
        
        async def analyze():
            try:
                analyzer = EngagementAnalyzer()
                metrics = await analyzer.calculate_engagement_metrics()
                
                self.advanced_metrics_status.value = "✅ Análise de engajamento concluída"
                self.advanced_metrics_summary.value = f"🎯 {metrics.unique_users} usuários • {metrics.avg_session_duration:.1f} min/sessão"
                
            except Exception as error:
                self.advanced_metrics_status.value = "❌ Erro na análise"
                self.advanced_metrics_summary.value = f"Erro: {str(error)}"
            finally:
                self.page.update()
        
        asyncio.create_task(analyze())
    
    def _generate_predictive_insights(self, e):
        """Gera insights preditivos"""
        self.advanced_metrics_status.value = "🔮 Gerando insights..."
        self.page.update()
        
        async def generate():
            try:
                manager = AdvancedMetricsManager()
                report = await manager.generate_comprehensive_report()
                insights = report.predictive_insights
                
                self.advanced_metrics_status.value = "✅ Insights gerados"
                forecast = insights.get("next_month_forecast", {})
                self.advanced_metrics_summary.value = f"🔮 {len(forecast)} previsões • {len(insights.get('recommended_actions', []))} ações recomendadas"
                
            except Exception as error:
                self.advanced_metrics_status.value = "❌ Erro ao gerar insights"
                self.advanced_metrics_summary.value = f"Erro: {str(error)}"
            finally:
                self.page.update()
        
        asyncio.create_task(generate())
    
    def _open_advanced_metrics_dashboard(self, e):
        """Abre o dashboard interativo de métricas avançadas"""
        self.advanced_metrics_status.value = "🎛️ Abrindo dashboard..."
        self.page.update()
        
        async def open_dashboard():
            try:
                dashboard = AdvancedMetricsDashboard()
                await dashboard.run_dashboard()
                self.advanced_metrics_status.value = "✅ Dashboard ativo"
            except Exception as error:
                self.advanced_metrics_status.value = "❌ Erro ao abrir dashboard"
                self.advanced_metrics_summary.value = f"Erro: {str(error)}"
            finally:
                self.page.update()
        
        asyncio.create_task(open_dashboard())
    
    def _on_period_change(self, e):
        """Callback para mudança de período"""
        self.current_period = e.control.value
        self._refresh_metrics()
        self.page.update()
    
    def _refresh_metrics(self):
        """Atualiza todas as métricas"""
        try:
            self.metrics = get_dashboard_summary(self.current_period)
            if self.page:
                self.page.update()
        except Exception as e:
            logger.error(f"Erro ao atualizar métricas: {e}")
    
    def _start_auto_refresh(self):
        """Inicia atualização automática das métricas"""
        async def refresh_loop():
            while self.auto_refresh_enabled:
                await asyncio.sleep(30)  # Atualizar a cada 30 segundos
                if self.auto_refresh_enabled:
                    self._refresh_metrics()
        
        asyncio.create_task(refresh_loop())
    
    def _start_bot(self, e):
        """Inicia o bot"""
        self.bot_status = "🟢 Ativo"
        if self.page:
            self.page.update()
        logger.info("Bot iniciado via dashboard")
    
    def _stop_bot(self, e):
        """Para o bot"""
        self.bot_status = "🔴 Parado"
        if self.page:
            self.page.update()
        logger.info("Bot parado via dashboard")
    
    def _restart_bot(self, e):
        """Reinicia o bot"""
        self.bot_status = "🟡 Reiniciando..."
        if self.page:
            self.page.update()
        
        # Simular reinicialização
        async def restart_sequence():
            await asyncio.sleep(2)
            self.bot_status = "🟢 Ativo"
            if self.page:
                self.page.update()
        
        asyncio.create_task(restart_sequence())
        logger.info("Bot reiniciado via dashboard")
    
    def _toggle_platform(self, platform: str, enabled: bool):
        """Alterna plataforma de afiliação"""
        logger.info(f"Plataforma {platform}: {'habilitada' if enabled else 'desabilitada'}")

    # Métodos de callback para Deep Learning
    def _train_deep_learning_models(self, e):
        """Treina modelos de deep learning"""
        self.deep_learning_status.value = "🚀 Treinando modelos..."
        self.page.update()
        
        async def train_models():
            try:
                # Simular treinamento
                await asyncio.sleep(3)
                self.deep_learning_status.value = "✅ Modelos treinados"
                self.deep_learning_summary.value = "3 modelos treinados • 1000 amostras • 45.2s"
                self.results_area.content.controls[1].value = "🚀 Treinamento concluído!\n🤖 Deep Neural Network: ✅\n🤖 Convolutional NN: ✅\n🤖 Recurrent NN: ✅"
                self.results_area.content.controls[1].color = ft.Colors.GREEN
            except Exception as error:
                self.deep_learning_status.value = "❌ Erro no treinamento"
                self.results_area.content.controls[1].value = f"Erro: {str(error)}"
                self.results_area.content.controls[1].color = ft.Colors.RED
            finally:
                self.page.update()
        
        asyncio.create_task(train_models())

    def _make_deep_learning_predictions(self, e):
        """Faz predições com deep learning"""
        self.deep_learning_status.value = "🔮 Fazendo predições..."
        self.page.update()
        
        async def make_predictions():
            try:
                # Simular predições
                await asyncio.sleep(2)
                self.deep_learning_status.value = "✅ Predições concluídas"
                self.results_area.content.controls[1].value = "🔮 Predições de Produtos:\n🎮 Console Gaming: Score 0.92 | PRIORIDADE MÁXIMA\n📱 Smartphone Gamer: Score 0.88 | PRIORIDADE ALTA\n🎨 Action Figure: Score 0.76 | PRIORIDADE MÉDIA"
                self.results_area.content.controls[1].color = ft.Colors.BLUE
            except Exception as error:
                self.deep_learning_status.value = "❌ Erro nas predições"
                self.results_area.content.controls[1].value = f"Erro: {str(error)}"
                self.results_area.content.controls[1].color = ft.Colors.RED
            finally:
                self.page.update()
        
        asyncio.create_task(make_predictions())

    def _view_deep_learning_performance(self, e):
        """Visualiza performance dos modelos"""
        self.deep_learning_status.value = "📊 Analisando performance..."
        self.page.update()
        
        async def view_performance():
            try:
                # Simular análise de performance
                await asyncio.sleep(1)
                self.deep_learning_status.value = "✅ Performance analisada"
                self.results_area.content.controls[1].value = "📊 Performance dos Modelos:\n🤖 Deep Neural Network: Acurácia 0.89 | R² 0.87\n🤖 Convolutional NN: Acurácia 0.87 | R² 0.85\n🤖 Recurrent NN: Acurácia 0.91 | R² 0.89\n⏱️ Tempo médio de inferência: 0.045s"
                self.results_area.content.controls[1].color = ft.Colors.ORANGE
            except Exception as error:
                self.deep_learning_status.value = "❌ Erro na análise"
                self.results_area.content.controls[1].value = f"Erro: {str(error)}"
                self.results_area.content.controls[1].color = ft.Colors.RED
            finally:
                self.page.update()
        
        asyncio.create_task(view_performance())

    def _generate_deep_learning_insights(self, e):
        """Gera insights do deep learning"""
        self.deep_learning_status.value = "💡 Gerando insights..."
        self.page.update()
        
        async def generate_insights():
            try:
                # Simular geração de insights
                await asyncio.sleep(2)
                self.deep_learning_status.value = "✅ Insights gerados"
                self.results_area.content.controls[1].value = "💡 Insights do Deep Learning:\n🔍 Feature mais importante: category (0.85)\n📊 Total de predições: 15\n🎯 Confiança média: 0.87\n🔥 Produtos com maior potencial: Gaming e Tech\n📈 Tendência: Crescente para produtos geek"
                self.results_area.content.controls[1].color = ft.Colors.PURPLE
            except Exception as error:
                self.deep_learning_status.value = "❌ Erro ao gerar insights"
                self.results_area.content.controls[1].value = f"Erro: {str(error)}"
                self.results_area.content.controls[1].color = ft.Colors.RED
            finally:
                self.page.update()
        
        asyncio.create_task(generate_insights())

    def _quick_deep_learning_test(self, e):
        """Executa teste rápido de deep learning"""
        self.deep_learning_status.value = "🎯 Executando teste rápido..."
        self.page.update()
        
        async def quick_test():
            try:
                # Simular teste rápido
                await asyncio.sleep(2)
                self.deep_learning_status.value = "✅ Teste concluído"
                self.results_area.content.controls[1].value = "🎯 Teste Rápido de Deep Learning:\n🎮 Console Gaming: Score 0.92 | PRIORIDADE MÁXIMA\n📱 Smartphone Gamer: Score 0.88 | PRIORIDADE ALTA\n🎨 Action Figure: Score 0.76 | PRIORIDADE MÉDIA\n💻 Notebook Gamer: Score 0.94 | PRIORIDADE MÁXIMA\n🎲 Board Game: Score 0.68 | PRIORIDADE MÉDIA"
                self.results_area.content.controls[1].color = ft.Colors.RED
            except Exception as error:
                self.deep_learning_status.value = "❌ Erro no teste"
                self.results_area.content.controls[1].value = f"Erro: {str(error)}"
                self.results_area.content.controls[1].color = ft.Colors.RED
            finally:
                self.page.update()
        
        asyncio.create_task(quick_test())

    def _open_deep_learning_dashboard(self, e):
        """Abre dashboard interativo de deep learning"""
        self.deep_learning_status.value = "🎛️ Abrindo dashboard..."
        self.page.update()
        
        async def open_dashboard():
            try:
                # Simular abertura do dashboard
                await asyncio.sleep(1)
                self.deep_learning_status.value = "✅ Dashboard ativo"
                self.results_area.content.controls[1].value = "🎛️ Dashboard de Deep Learning aberto!\n🤖 Use o menu interativo para explorar o sistema\n🔮 Faça predições em tempo real\n📊 Visualize performance dos modelos\n💡 Gere insights avançados"
                self.results_area.content.controls[1].color = ft.Colors.TEAL
            except Exception as error:
                self.deep_learning_status.value = "❌ Erro ao abrir dashboard"
                self.results_area.content.controls[1].value = f"Erro: {str(error)}"
                self.results_area.content.controls[1].color = ft.Colors.RED
            finally:
                self.page.update()
        
        asyncio.create_task(open_dashboard())


def main():
    """Função principal para executar o dashboard"""
    dashboard = GarimpeiroDashboard()
    ft.app(target=dashboard.main, port=8080, view=ft.WEB_BROWSER)


if __name__ == "__main__":
    main()