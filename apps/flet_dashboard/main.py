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


def main():
    """Função principal para executar o dashboard"""
    dashboard = GarimpeiroDashboard()
    ft.app(target=dashboard.main, port=8080, view=ft.WEB_BROWSER)


if __name__ == "__main__":
    main()