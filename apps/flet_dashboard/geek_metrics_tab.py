"""
Aba de Métricas Geek para o Dashboard Flet
Mostra estatísticas específicas de produtos geek/gamer
"""

import flet as ft
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from src.core.geek_prioritizer import GeekPrioritizer
    from src.core.geek_alerts import GeekAlertManager
    from src.core.models import Offer
except ImportError:
    # Fallback para quando não conseguir importar
    GeekPrioritizer = None
    GeekAlertManager = None
    Offer = None

class GeekMetricsTab(ft.UserControl):
    """Aba de métricas geek para o dashboard"""
    
    def __init__(self):
        super().__init__()
        self.prioritizer = None
        self.alert_manager = None
        self.refresh_timer = None
        
        # Dados de exemplo para demonstração
        self.sample_data = {
            "total_offers": 1250,
            "geek_offers": 342,
            "gaming_offers": 156,
            "tech_offers": 89,
            "anime_offers": 67,
            "collectibles_offers": 30,
            "avg_geek_score": 0.73,
            "high_priority_count": 45,
            "critical_alerts": 12,
            "conversion_rate": 0.18
        }
    
    def build(self):
        """Constrói a interface da aba"""
        return ft.Container(
            content=ft.Column([
                # Cabeçalho
                ft.Container(
                    content=ft.Text(
                        "🎮 MÉTRICAS GEEK & GAMER",
                        size=28,
                        weight=ft.FontWeight.BOLD,
                        color=ft.colors.BLUE_400
                    ),
                    alignment=ft.alignment.center,
                    margin=ft.margin.only(bottom=20)
                ),
                
                # Cards de métricas principais
                ft.Row([
                    self._build_metric_card("🎯 Total Ofertas Geek", "342", "de 1.250 total", ft.colors.BLUE_500),
                    self._build_metric_card("⭐ Score Médio Geek", "0.73", "de 1.0 máximo", ft.colors.GREEN_500),
                    self._build_metric_card("🚨 Alertas Críticos", "12", "hoje", ft.colors.RED_500),
                    self._build_metric_card("💰 Taxa Conversão", "18%", "geek vs 12% geral", ft.colors.ORANGE_500),
                ], alignment=ft.MainAxisAlignment.SPACE_EVENLY),
                
                # Gráficos e estatísticas
                ft.Container(height=20),  # Espaçamento
                
                ft.Row([
                    # Distribuição por categoria
                    ft.Container(
                        content=ft.Column([
                            ft.Text("📊 DISTRIBUIÇÃO POR CATEGORIA", size=18, weight=ft.FontWeight.BOLD),
                            self._build_category_chart(),
                        ]),
                        width=400,
                        padding=20,
                        border=ft.border.all(1, ft.colors.GREY_400),
                        border_radius=10,
                    ),
                    
                    # Top produtos geek
                    ft.Container(
                        content=ft.Column([
                            ft.Text("🏆 TOP PRODUTOS GEEK", size=18, weight=ft.FontWeight.BOLD),
                            self._build_top_products_list(),
                        ]),
                        width=400,
                        padding=20,
                        border=ft.border.all(1, ft.colors.GREY_400),
                        border_radius=10,
                    ),
                ], alignment=ft.MainAxisAlignment.SPACE_EVENLY),
                
                ft.Container(height=20),  # Espaçamento
                
                # Estatísticas detalhadas
                ft.Row([
                    # Performance por categoria
                    ft.Container(
                        content=ft.Column([
                            ft.Text("📈 PERFORMANCE POR CATEGORIA", size=18, weight=ft.FontWeight.BOLD),
                            self._build_performance_table(),
                        ]),
                        width=400,
                        padding=20,
                        border=ft.border.all(1, ft.colors.GREY_400),
                        border_radius=10,
                    ),
                    
                    # Alertas e notificações
                    ft.Container(
                        content=ft.Column([
                            ft.Text("🚨 ALERTAS E NOTIFICAÇÕES", size=18, weight=ft.FontWeight.BOLD),
                            self._build_alerts_panel(),
                        ]),
                        width=400,
                        padding=20,
                        border=ft.border.all(1, ft.colors.GREY_400),
                        border_radius=10,
                    ),
                ], alignment=ft.MainAxisAlignment.SPACE_EVENLY),
                
                # Controles
                ft.Container(height=20),  # Espaçamento
                
                ft.Row([
                    ft.ElevatedButton(
                        "🔄 Atualizar Métricas",
                        on_click=self._refresh_metrics,
                        style=ft.ButtonStyle(
                            color=ft.colors.WHITE,
                            bgcolor=ft.colors.BLUE_500,
                        )
                    ),
                    ft.ElevatedButton(
                        "📊 Exportar Relatório",
                        on_click=self._export_report,
                        style=ft.ButtonStyle(
                            color=ft.colors.WHITE,
                            bgcolor=ft.colors.GREEN_500,
                        )
                    ),
                    ft.ElevatedButton(
                        "⚙️ Configurações",
                        on_click=self._open_settings,
                        style=ft.ButtonStyle(
                            color=ft.colors.WHITE,
                            bgcolor=ft.colors.GREY_500,
                        )
                    ),
                ], alignment=ft.MainAxisAlignment.CENTER),
                
            ]),
            padding=20,
        )
    
    def _build_metric_card(self, title: str, value: str, subtitle: str, color: str) -> ft.Container:
        """Constrói um card de métrica"""
        return ft.Container(
            content=ft.Column([
                ft.Text(title, size=14, weight=ft.FontWeight.BOLD, color=ft.colors.GREY_700),
                ft.Text(value, size=32, weight=ft.FontWeight.BOLD, color=color),
                ft.Text(subtitle, size=12, color=ft.colors.GREY_600),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            width=200,
            height=120,
            padding=20,
            border=ft.border.all(1, ft.colors.GREY_300),
            border_radius=10,
            alignment=ft.alignment.center,
        )
    
    def _build_category_chart(self) -> ft.Container:
        """Constrói gráfico de distribuição por categoria"""
        categories = [
            {"name": "🎮 Gaming", "count": 156, "color": ft.colors.BLUE_500},
            {"name": "⚡ Tech Geek", "count": 89, "color": ft.colors.GREEN_500},
            {"name": "🌸 Anime/Otaku", "count": 67, "color": ft.colors.PINK_500},
            {"name": "🏆 Collectibles", "count": 30, "color": ft.colors.ORANGE_500},
        ]
        
        total = sum(cat["count"] for cat in categories)
        
        chart_items = []
        for cat in categories:
            percentage = (cat["count"] / total) * 100
            chart_items.append(
                ft.Row([
                    ft.Container(
                        width=20,
                        height=20,
                        bgcolor=cat["color"],
                        border_radius=5,
                    ),
                    ft.Text(f"{cat['name']}: {cat['count']} ({percentage:.1f}%)", size=14),
                ])
            )
        
        return ft.Container(
            content=ft.Column(chart_items, spacing=10),
            padding=10,
        )
    
    def _build_top_products_list(self) -> ft.Container:
        """Constrói lista dos top produtos geek"""
        top_products = [
            {"title": "PlayStation 5", "score": 0.95, "category": "🎮 Gaming"},
            {"title": "RTX 4070 Ti", "score": 0.92, "category": "⚡ Tech Geek"},
            {"title": "Goku Ultra Instinct", "score": 0.89, "category": "🌸 Anime"},
            {"title": "Gaming Chair RGB", "score": 0.87, "category": "🎮 Gaming"},
            {"title": "Smart TV OLED", "score": 0.85, "category": "🏠 Smart Home"},
        ]
        
        product_items = []
        for i, product in enumerate(top_products, 1):
            product_items.append(
                ft.Container(
                    content=ft.Row([
                        ft.Text(f"{i}.", size=16, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE_500),
                        ft.Column([
                            ft.Text(product["title"], size=14, weight=ft.FontWeight.BOLD),
                            ft.Text(f"{product['category']} • Score: {product['score']:.2f}", size=12, color=ft.colors.GREY_600),
                        ], spacing=2),
                    ]),
                    padding=ft.padding.only(left=10, right=10, top=5, bottom=5),
                    border=ft.border.only(bottom=1, color=ft.colors.GREY_200),
                )
            )
        
        return ft.Container(
            content=ft.Column(product_items),
            height=200,
        )
    
    def _build_performance_table(self) -> ft.Container:
        """Constrói tabela de performance por categoria"""
        performance_data = [
            {"category": "🎮 Gaming", "offers": 156, "conversion": "22%", "avg_score": "0.89"},
            {"category": "⚡ Tech Geek", "offers": 89, "conversion": "19%", "avg_score": "0.76"},
            {"category": "🌸 Anime/Otaku", "offers": 67, "conversion": "15%", "avg_score": "0.71"},
            {"category": "🏠 Smart Home", "offers": 45, "conversion": "18%", "avg_score": "0.83"},
            {"category": "🎧 Audio Premium", "offers": 38, "conversion": "21%", "avg_score": "0.81"},
        ]
        
        table_rows = []
        for data in performance_data:
            table_rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(data["category"], size=12)),
                        ft.DataCell(ft.Text(str(data["offers"]), size=12)),
                        ft.DataCell(ft.Text(data["conversion"], size=12, color=ft.colors.GREEN_600)),
                        ft.DataCell(ft.Text(data["avg_score"], size=12, color=ft.colors.BLUE_600)),
                    ]
                )
            )
        
        table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Categoria", size=12, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Ofertas", size=12, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Conversão", size=12, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Score Médio", size=12, weight=ft.FontWeight.BOLD)),
            ],
            rows=table_rows,
            border=ft.border.all(1, ft.colors.GREY_300),
            border_radius=5,
        )
        
        return ft.Container(
            content=table,
            height=200,
        )
    
    def _build_alerts_panel(self) -> ft.Container:
        """Constrói painel de alertas"""
        alerts_data = [
            {"type": "🚨 Crítico", "count": 12, "color": ft.colors.RED_500},
            {"type": "⚠️ Alta", "count": 23, "color": ft.colors.ORANGE_500},
            {"type": "📢 Média", "count": 45, "color": ft.colors.YELLOW_500},
            {"type": "ℹ️ Baixa", "count": 67, "color": ft.colors.BLUE_500},
        ]
        
        alert_items = []
        for alert in alerts_data:
            alert_items.append(
                ft.Row([
                    ft.Container(
                        width=15,
                        height=15,
                        bgcolor=alert["color"],
                        border_radius=3,
                    ),
                    ft.Text(alert["type"], size=14, weight=ft.FontWeight.BOLD),
                    ft.Text(f": {alert['count']}", size=14),
                ], spacing=10)
            )
        
        # Estatísticas de alertas
        stats = ft.Container(
            content=ft.Column([
                ft.Text("📊 ESTATÍSTICAS", size=14, weight=ft.FontWeight.BOLD),
                ft.Text(f"Total de Alertas: {sum(a['count'] for a in alerts_data)}", size=12),
                ft.Text(f"Pendentes: 23", size=12, color=ft.colors.ORANGE_600),
                ft.Text(f"Enviados: 124", size=12, color=ft.colors.GREEN_600),
            ], spacing=5),
            padding=10,
            border=ft.border.all(1, ft.colors.GREY_300),
            border_radius=5,
        )
        
        return ft.Container(
            content=ft.Column([
                ft.Column(alert_items, spacing=8),
                ft.Container(height=10),
                stats,
            ]),
            height=200,
        )
    
    async def _refresh_metrics(self, e):
        """Atualiza as métricas"""
        try:
            # Aqui você implementaria a lógica real de atualização
            # Por enquanto, apenas simula uma atualização
            await self._simulate_refresh()
            
        except Exception as error:
            print(f"Erro ao atualizar métricas: {error}")
    
    async def _simulate_refresh(self):
        """Simula uma atualização das métricas"""
        # Simular carregamento
        await asyncio.sleep(1)
        
        # Atualizar dados de exemplo
        self.sample_data["total_offers"] += 5
        self.sample_data["geek_offers"] += 2
        self.sample_data["avg_geek_score"] = round(self.sample_data["avg_geek_score"] + 0.01, 2)
        
        # Aqui você atualizaria a interface
        print("✅ Métricas atualizadas!")
    
    async def _export_report(self, e):
        """Exporta relatório das métricas geek"""
        try:
            # Aqui você implementaria a exportação real
            print("📊 Exportando relatório geek...")
            
            # Simular exportação
            await asyncio.sleep(1)
            print("✅ Relatório exportado com sucesso!")
            
        except Exception as error:
            print(f"Erro ao exportar relatório: {error}")
    
    async def _open_settings(self, e):
        """Abre configurações das métricas geek"""
        try:
            # Aqui você implementaria a abertura das configurações
            print("⚙️ Abrindo configurações geek...")
            
        except Exception as error:
            print(f"Erro ao abrir configurações: {error}")
    
    async def initialize(self):
        """Inicializa a aba com dados reais"""
        try:
            # Tentar inicializar componentes reais
            if GeekPrioritizer:
                self.prioritizer = GeekPrioritizer()
                print("✅ GeekPrioritizer inicializado")
            
            if GeekAlertManager:
                self.alert_manager = GeekAlertManager()
                print("✅ GeekAlertManager inicializado")
            
            # Configurar timer de atualização automática
            self._setup_auto_refresh()
            
        except Exception as error:
            print(f"Erro ao inicializar aba geek: {error}")
    
    def _setup_auto_refresh(self):
        """Configura atualização automática das métricas"""
        try:
            # Atualizar a cada 5 minutos
            self.refresh_timer = asyncio.create_task(self._auto_refresh_loop())
        except Exception as error:
            print(f"Erro ao configurar auto-refresh: {error}")
    
    async def _auto_refresh_loop(self):
        """Loop de atualização automática"""
        try:
            while True:
                await asyncio.sleep(300)  # 5 minutos
                await self._refresh_metrics(None)
        except asyncio.CancelledError:
            print("Auto-refresh cancelado")
        except Exception as error:
            print(f"Erro no auto-refresh: {error}")
    
    def dispose(self):
        """Limpa recursos da aba"""
        if self.refresh_timer:
            self.refresh_timer.cancel()
