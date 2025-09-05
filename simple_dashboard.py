#!/usr/bin/env python3
"""Dashboard Flet Simplificado para Garimpeiro Geek"""

import flet as ft
import sys
from pathlib import Path

# Adicionar o diretório raiz ao Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main(page: ft.Page):
    """Função principal do dashboard simplificado"""
    page.title = "Garimpeiro Geek - Dashboard"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20
    
    # Header
    header = ft.Container(
        content=ft.Column([
            ft.Text("🎮 Garimpeiro Geek", size=32, weight=ft.FontWeight.BOLD),
            ft.Text("Sistema de Recomendações de Ofertas", size=16),
            ft.Divider(),
        ]),
        padding=20,
        bgcolor=ft.Colors.BLUE_900,
        border_radius=12,
        margin=ft.margin.only(bottom=20)
    )
    
    # Status do sistema
    status_section = ft.Container(
        content=ft.Column([
            ft.Text("📊 Status do Sistema", size=20, weight=ft.FontWeight.BOLD),
            ft.Row([
                ft.Container(
                    content=ft.Column([
                        ft.Text("🟢 Sistema", size=16, weight=ft.FontWeight.BOLD),
                        ft.Text("Online", size=14, color=ft.Colors.GREEN),
                    ]),
                    padding=20,
                    bgcolor=ft.Colors.GREEN_50,
                    border_radius=10,
                    expand=True,
                    margin=ft.margin.only(right=10)
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Text("🤖 Bot Telegram", size=16, weight=ft.FontWeight.BOLD),
                        ft.Text("Parado", size=14, color=ft.Colors.ORANGE),
                    ]),
                    padding=20,
                    bgcolor=ft.Colors.ORANGE_50,
                    border_radius=10,
                    expand=True,
                    margin=ft.margin.only(right=10)
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Text("📊 Ofertas", size=16, weight=ft.FontWeight.BOLD),
                        ft.Text("0", size=14, color=ft.Colors.BLUE),
                    ]),
                    padding=20,
                    bgcolor=ft.Colors.BLUE_50,
                    border_radius=10,
                    expand=True,
                ),
            ]),
        ]),
        padding=20,
        bgcolor=ft.Colors.GREY_900,
        border_radius=12,
        margin=ft.margin.only(bottom=20)
    )
    
    # Controles
    controls_section = ft.Container(
        content=ft.Column([
            ft.Text("🎛️ Controles", size=20, weight=ft.FontWeight.BOLD),
            ft.Row([
                ft.ElevatedButton(
                    "🚀 Iniciar Bot",
                    icon=ft.Icons.PLAY_ARROW,
                    style=ft.ButtonStyle(
                        color=ft.Colors.WHITE,
                        bgcolor=ft.Colors.GREEN_600,
                    ),
                    on_click=lambda e: print("Iniciando bot...")
                ),
                ft.ElevatedButton(
                    "⏹️ Parar Bot",
                    icon=ft.Icons.STOP,
                    style=ft.ButtonStyle(
                        color=ft.Colors.WHITE,
                        bgcolor=ft.Colors.RED_600,
                    ),
                    on_click=lambda e: print("Parando bot...")
                ),
                ft.ElevatedButton(
                    "🔄 Reiniciar",
                    icon=ft.Icons.REFRESH,
                    style=ft.ButtonStyle(
                        color=ft.Colors.WHITE,
                        bgcolor=ft.Colors.BLUE_600,
                    ),
                    on_click=lambda e: print("Reiniciando sistema...")
                ),
            ], wrap=True),
        ]),
        padding=20,
        bgcolor=ft.Colors.GREY_900,
        border_radius=12,
        margin=ft.margin.only(bottom=20)
    )
    
    # Sistemas implementados
    systems_section = ft.Container(
        content=ft.Column([
            ft.Text("🔧 Sistemas Implementados", size=20, weight=ft.FontWeight.BOLD),
            ft.Row([
                ft.Container(
                    content=ft.Column([
                        ft.Text("🤖 Deep Learning", size=16, weight=ft.FontWeight.BOLD),
                        ft.Text("Redes neurais avançadas", size=12),
                        ft.Text("✅ Ativo", size=12, color=ft.Colors.GREEN),
                    ]),
                    padding=20,
                    bgcolor=ft.Colors.PURPLE_50,
                    border_radius=10,
                    expand=True,
                    margin=ft.margin.only(right=10, bottom=10)
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Text("📊 Métricas Avançadas", size=16, weight=ft.FontWeight.BOLD),
                        ft.Text("Análise temporal e demográfica", size=12),
                        ft.Text("✅ Ativo", size=12, color=ft.Colors.GREEN),
                    ]),
                    padding=20,
                    bgcolor=ft.Colors.CYAN_50,
                    border_radius=10,
                    expand=True,
                    margin=ft.margin.only(right=10, bottom=10)
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Text("🔗 Integração Afiliados", size=16, weight=ft.FontWeight.BOLD),
                        ft.Text("APIs oficiais e validação", size=12),
                        ft.Text("✅ Ativo", size=12, color=ft.Colors.GREEN),
                    ]),
                    padding=20,
                    bgcolor=ft.Colors.TEAL_50,
                    border_radius=10,
                    expand=True,
                    margin=ft.margin.only(bottom=10)
                ),
            ], wrap=True),
        ]),
        padding=20,
        bgcolor=ft.Colors.GREY_900,
        border_radius=12,
        margin=ft.margin.only(bottom=20)
    )
    
    # Logs
    logs_section = ft.Container(
        content=ft.Column([
            ft.Text("📝 Logs Recentes", size=20, weight=ft.FontWeight.BOLD),
            ft.Container(
                content=ft.Column([
                    ft.Text("✅ Sistema inicializado com sucesso", size=14),
                    ft.Text("✅ Dashboard carregado", size=14),
                    ft.Text("✅ Todos os sistemas ativos", size=14),
                ]),
                padding=20,
                bgcolor=ft.Colors.WHITE,
                border=ft.border.all(1, ft.Colors.GREY_300),
                border_radius=10,
            ),
        ]),
        padding=20,
        bgcolor=ft.Colors.GREY_900,
        border_radius=12
    )
    
    # Layout principal
    page.add(
        ft.Column([
            header,
            status_section,
            controls_section,
            systems_section,
            logs_section,
        ], scroll=ft.ScrollMode.AUTO)
    )

if __name__ == "__main__":
    print("🚀 Iniciando Dashboard Simplificado do Garimpeiro Geek...")
    print("📱 Acesse: http://127.0.0.1:8080")
    ft.app(target=main, view=ft.WEB_BROWSER, port=8080)
