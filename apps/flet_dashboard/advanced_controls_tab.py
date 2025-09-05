#!/usr/bin/env python3
"""Tab Avançada de Controles para Dashboard"""

import flet as ft
import asyncio
from datetime import datetime
from typing import Dict, List, Optional
import json

class AdvancedControlsTab:
    """Tab avançada com controles, métricas e alertas"""
    
    def __init__(self):
        self.period_selector = None
        self.metrics_engine = None
        self.bot_controller = None
        self.current_period = "7d"
        
        # Estados
        self.overview_data = {}
        self.asin_data = {}
        self.affiliation_data = []
        self.alerts_data = {}
        self.bot_status = {}
        self.system_health = {}
        
        # Controles
        self.period_dropdown = None
        self.export_button = None
        self.bot_controls = {}
        self.platform_toggles = {}
        
    def build(self) -> ft.Tab:
        """Constrói a tab avançada"""
        return ft.Tab(
            text="🎛️ Controles Avançados",
            content=self._build_content()
        )
    
    def _build_content(self) -> ft.Container:
        """Constrói o conteúdo da tab"""
        return ft.Container(
            content=ft.Column([
                # Header com seletor de período
                self._build_header(),
                
                # Métricas principais
                self._build_overview_section(),
                
                # Seção de controles do bot
                self._build_bot_controls_section(),
                
                # Seção de métricas ASIN
                self._build_asin_section(),
                
                # Seção de afiliação
                self._build_affiliation_section(),
                
                # Seção de alertas
                self._build_alerts_section(),
                
                # Seção de performance
                self._build_performance_section(),
                
                # Seção de logs
                self._build_logs_section(),
                
                # Seção de agendamentos
                self._build_schedules_section(),
            ]),
            padding=20,
            scroll=ft.ScrollMode.AUTO
        )
    
    def _build_header(self) -> ft.Container:
        """Constrói header com seletor de período"""
        self.period_dropdown = ft.Dropdown(
            label="Período",
            value="7d",
            options=[
                ft.dropdown.Option("7d", "Últimos 7 dias"),
                ft.dropdown.Option("30d", "Últimos 30 dias"),
                ft.dropdown.Option("90d", "Últimos 90 dias"),
            ],
            on_change=self._on_period_change
        )
        
        self.export_button = ft.ElevatedButton(
            "📊 Exportar CSV",
            icon=ft.Icons.DOWNLOAD,
            on_click=self._export_csv
        )
        
        return ft.Container(
            content=ft.Row([
                ft.Text("🎛️ Controles Avançados", size=24, weight=ft.FontWeight.BOLD),
                ft.Container(expand=True),  # Substitui ft.Spacer()
                self.period_dropdown,
                self.export_button,
            ]),
            padding=ft.padding.only(bottom=20)
        )
    
    def _build_overview_section(self) -> ft.Container:
        """Constrói seção de visão geral"""
        return ft.Container(
            content=ft.Column([
                ft.Text("📊 Visão Geral", size=20, weight=ft.FontWeight.BOLD),
                ft.Row([
                    self._build_metric_card("ASIN Quality", "0%", "Meta: 95%", "critical"),
                    self._build_metric_card("Posts Bloqueados", "0", "7 dias", "warning"),
                    self._build_metric_card("Receita Total", "R$ 0,00", "Período", "neutral"),
                    self._build_metric_card("Receita/Post", "R$ 0,00", "Média", "neutral"),
                ], wrap=True),
            ]),
            padding=ft.padding.only(bottom=20)
        )
    
    def _build_bot_controls_section(self) -> ft.Container:
        """Constrói seção de controles do bot"""
        # Botões de controle
        self.bot_controls = {
            "start": ft.ElevatedButton(
                "🟢 Iniciar Bot",
                style=ft.ButtonStyle(
                    color=ft.colors.WHITE,
                    bgcolor=ft.colors.GREEN_600,
                ),
                on_click=self._start_bot
            ),
            "stop": ft.ElevatedButton(
                "🔴 Parar Bot",
                style=ft.ButtonStyle(
                    color=ft.colors.WHITE,
                    bgcolor=ft.colors.RED_600,
                ),
                on_click=self._stop_bot
            ),
            "restart": ft.ElevatedButton(
                "🟠 Reiniciar Bot",
                style=ft.ButtonStyle(
                    color=ft.colors.WHITE,
                    bgcolor=ft.colors.ORANGE_600,
                ),
                on_click=self._restart_bot
            ),
        }
        
        # Toggles de plataformas
        platforms = ["awin", "mercadolivre", "magalu", "amazon", "shopee", "aliexpress", "rakuten"]
        platform_toggles_row = []
        
        for platform in platforms:
            toggle = ft.Switch(
                label=platform.upper(),
                value=True,
                on_change=lambda e, p=platform: self._toggle_platform(p, e.control.value)
            )
            self.platform_toggles[platform] = toggle
            platform_toggles_row.append(toggle)
        
        return ft.Container(
            content=ft.Column([
                ft.Text("🤖 Controles do Bot", size=20, weight=ft.FontWeight.BOLD),
                
                # Botões de controle
                ft.Container(
                    content=ft.Row([
                        self.bot_controls["start"],
                        self.bot_controls["stop"],
                        self.bot_controls["restart"],
                    ]),
                    padding=ft.padding.only(bottom=20)
                ),
                
                # Status do bot
                ft.Container(
                    content=ft.Column([
                        ft.Text("📊 Status do Sistema", size=16, weight=ft.FontWeight.BOLD),
                        ft.Text("Status: Parado", id="bot_status_text"),
                        ft.Text("Uptime: 0s", id="bot_uptime_text"),
                        ft.Text("Views SQL: 0/0", id="sql_views_text"),
                        ft.Text("Eventos (24h): 0", id="events_24h_text"),
                    ]),
                    padding=20,
                    bgcolor=ft.colors.BLUE_GREY_50,
                    border_radius=10,
                    margin=ft.margin.only(bottom=20)
                ),
                
                # Toggles de plataformas
                ft.Container(
                    content=ft.Column([
                        ft.Text("🌐 Plataformas Ativas", size=16, weight=ft.FontWeight.BOLD),
                        ft.Row(platform_toggles_row, wrap=True),
                    ]),
                    padding=20,
                    bgcolor=ft.colors.GREY_50,
                    border_radius=10,
                ),
            ]),
            padding=ft.padding.only(bottom=20)
        )
    
    def _build_asin_section(self) -> ft.Container:
        """Constrói seção de métricas ASIN"""
        return ft.Container(
            content=ft.Column([
                ft.Text("📦 Métricas ASIN", size=20, weight=ft.FontWeight.BOLD),
                ft.Row([
                    self._build_metric_card("Com ASIN", "0", "Total", "neutral"),
                    self._build_metric_card("Sem ASIN", "0", "Total", "warning"),
                    self._build_metric_card("Total Ofertas", "0", "Período", "neutral"),
                ], wrap=True),
                
                # Gráfico de estratégias (simulado)
                ft.Container(
                    content=ft.Column([
                        ft.Text("🎯 Estratégias de Extração ASIN", size=16),
                        ft.Text("URL: 0 | HTML: 0 | API: 0", size=14, color=ft.colors.GREY_600),
                    ]),
                    padding=20,
                    bgcolor=ft.colors.WHITE,
                    border=ft.border.all(1, ft.colors.GREY_300),
                    border_radius=10,
                    margin=ft.margin.only(top=20)
                ),
            ]),
            padding=ft.padding.only(bottom=20)
        )
    
    def _build_affiliation_section(self) -> ft.Container:
        """Constrói seção de afiliação"""
        return ft.Container(
            content=ft.Column([
                ft.Text("🔗 Afiliação", size=20, weight=ft.FontWeight.BOLD),
                
                # Tabela de bloqueios
                ft.Container(
                    content=ft.Column([
                        ft.Text("🚫 Posts Bloqueados por Plataforma", size=16),
                        ft.DataTable(
                            columns=[
                                ft.DataColumn(ft.Text("Plataforma")),
                                ft.DataColumn(ft.Text("Motivo")),
                                ft.DataColumn(ft.Text("Quantidade")),
                            ],
                            rows=[
                                ft.DataRow(cells=[
                                    ft.DataCell(ft.Text("Mercado Livre")),
                                    ft.DataCell(ft.Text("Formato inválido")),
                                    ft.DataCell(ft.Text("58")),
                                ]),
                                ft.DataRow(cells=[
                                    ft.DataCell(ft.Text("AliExpress")),
                                    ft.DataCell(ft.Text("Link quebrado")),
                                    ft.DataCell(ft.Text("27")),
                                ]),
                            ]
                        ),
                    ]),
                    padding=20,
                    bgcolor=ft.colors.WHITE,
                    border=ft.border.all(1, ft.colors.GREY_300),
                    border_radius=10,
                ),
            ]),
            padding=ft.padding.only(bottom=20)
        )
    
    def _build_alerts_section(self) -> ft.Container:
        """Constrói seção de alertas"""
        return ft.Container(
            content=ft.Column([
                ft.Text("🚨 Alertas", size=20, weight=ft.FontWeight.BOLD),
                
                # Resumo de alertas
                ft.Row([
                    self._build_metric_card("Total", "0", "7 dias", "neutral"),
                    self._build_metric_card("Críticos", "0", "Ação necessária", "critical"),
                    self._build_metric_card("Ação", "0", "Requer atenção", "warning"),
                ], wrap=True),
                
                # Lista de alertas
                ft.Container(
                    content=ft.Column([
                        ft.Text("📋 Alertas Ativos", size=16),
                        ft.Text("Nenhum alerta ativo", size=14, color=ft.colors.GREY_600),
                    ]),
                    padding=20,
                    bgcolor=ft.colors.WHITE,
                    border=ft.border.all(1, ft.colors.GREY_300),
                    border_radius=10,
                    margin=ft.margin.only(top=20)
                ),
            ]),
            padding=ft.padding.only(bottom=20)
        )
    
    def _build_performance_section(self) -> ft.Container:
        """Constrói seção de performance"""
        return ft.Container(
            content=ft.Column([
                ft.Text("⚡ Performance", size=20, weight=ft.FontWeight.BOLD),
                ft.Row([
                    ft.Container(
                        content=ft.Column([
                            ft.Text("⏱️ Latência", size=16),
                            ft.Text("2.5s", size=24, weight=ft.FontWeight.BOLD),
                            ft.Text("Média", size=12, color=ft.colors.GREY_600),
                        ]),
                        padding=20,
                        bgcolor=ft.colors.WHITE,
                        border=ft.border.all(1, ft.colors.GREY_300),
                        border_radius=10,
                        expand=True,
                    ),
                    ft.Container(
                        content=ft.Column([
                            ft.Text("📅 Freshness", size=16),
                            ft.Text("24h", size=24, weight=ft.FontWeight.BOLD),
                            ft.Text("Último evento", size=12, color=ft.colors.GREY_600),
                        ]),
                        padding=20,
                        bgcolor=ft.colors.WHITE,
                        border=ft.border.all(1, ft.colors.GREY_300),
                        border_radius=10,
                        expand=True,
                    ),
                    ft.Container(
                        content=ft.Column([
                            ft.Text("🏷️ Badges", size=16),
                            ft.Text("0", size=24, weight=ft.FontWeight.BOLD),
                            ft.Text("Ativos", size=12, color=ft.colors.GREY_600),
                        ]),
                        padding=20,
                        bgcolor=ft.colors.WHITE,
                        border=ft.border.all(1, ft.colors.GREY_300),
                        border_radius=10,
                        expand=True,
                    ),
                ]),
            ]),
            padding=ft.padding.only(bottom=20)
        )
    
    def _build_logs_section(self) -> ft.Container:
        """Constrói seção de logs"""
        return ft.Container(
            content=ft.Column([
                ft.Text("📝 Logs Recentes", size=20, weight=ft.FontWeight.BOLD),
                ft.Container(
                    content=ft.Column([
                        ft.Text("🔄 Últimas Ações", size=16),
                        ft.Text("Nenhum log disponível", size=14, color=ft.colors.GREY_600),
                    ]),
                    padding=20,
                    bgcolor=ft.colors.WHITE,
                    border=ft.border.all(1, ft.colors.GREY_300),
                    border_radius=10,
                ),
            ]),
            padding=ft.padding.only(bottom=20)
        )
    
    def _build_schedules_section(self) -> ft.Container:
        """Constrói seção de agendamentos"""
        return ft.Container(
            content=ft.Column([
                ft.Text("⏰ Agendamentos", size=20, weight=ft.FontWeight.BOLD),
                ft.Container(
                    content=ft.Column([
                        ft.Text("📅 Tarefas Agendadas", size=16),
                        ft.Text("Nenhum agendamento configurado", size=14, color=ft.colors.GREY_600),
                    ]),
                    padding=20,
                    bgcolor=ft.colors.WHITE,
                    border=ft.border.all(1, ft.colors.GREY_300),
                    border_radius=10,
                ),
            ]),
            padding=ft.padding.only(bottom=20)
        )
    
    def _build_metric_card(self, title: str, value: str, subtitle: str, tone: str) -> ft.Container:
        """Constrói card de métrica"""
        colors = {
            "critical": (ft.colors.RED_50, ft.colors.RED_700),
            "warning": (ft.colors.ORANGE_50, ft.colors.ORANGE_700),
            "neutral": (ft.colors.BLUE_50, ft.colors.BLUE_700),
        }
        
        bg_color, border_color = colors.get(tone, colors["neutral"])
        
        return ft.Container(
            content=ft.Column([
                ft.Text(title, size=14, color=ft.colors.GREY_700),
                ft.Text(value, size=24, weight=ft.FontWeight.BOLD, color=border_color),
                ft.Text(subtitle, size=12, color=ft.colors.GREY_500),
            ]),
            padding=20,
            bgcolor=bg_color,
            border=ft.border.all(2, border_color),
            border_radius=10,
            expand=True,
            margin=ft.margin.only(right=10, bottom=10),
        )
    
    async def _on_period_change(self, e):
        """Callback para mudança de período"""
        self.current_period = e.control.value
        await self._refresh_data()
    
    async def _export_csv(self, e):
        """Exporta dados para CSV"""
        # Implementar exportação CSV
        pass
    
    async def _start_bot(self, e):
        """Inicia o bot"""
        # Implementar início do bot
        pass
    
    async def _stop_bot(self, e):
        """Para o bot"""
        # Implementar parada do bot
        pass
    
    async def _restart_bot(self, e):
        """Reinicia o bot"""
        # Implementar reinicialização do bot
        pass
    
    async def _toggle_platform(self, platform: str, enabled: bool):
        """Ativa/desativa plataforma"""
        # Implementar toggle de plataforma
        pass
    
    async def _refresh_data(self):
        """Atualiza dados da tab"""
        # Implementar atualização de dados
        pass
