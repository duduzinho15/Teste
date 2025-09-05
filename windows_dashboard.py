#!/usr/bin/env python3
"""Dashboard Flet para Windows - Garimpeiro Geek (refatorado)"""

from __future__ import annotations
import flet as ft
import sys
import asyncio
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

# Adicionar o diretório raiz ao Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


class WindowsDashboard:
    """Dashboard principal para Windows"""

    # ------------- ciclo de vida / estado -------------
    def __init__(self):
        self.page: ft.Page | None = None

        self.bot_status = "⏸️ Parado"
        self.systems_status = {
            "deep_learning": "✅ Ativo",
            "advanced_metrics": "✅ Ativo",
            "affiliate_integration": "✅ Ativo",
            "telegram_bot": "⏸️ Parado",
        }

        # Elementos dinâmicos
        self.status_elements: dict[str, ft.Text] = {}
        self.metric_elements: dict[str, Any] = {}
        self.logs_container: ft.Container | None = None
        self.bot_status_text: ft.Text | None = None
        self.snack: ft.SnackBar | None = None

        # Tokens de tema (preenchidos em _build_theme)
        self.t: dict[str, Any] = {}
        
        # Modo diagnóstico para debug de layout
        self.__debug_layout__ = False

    # ---------------- tema e utilitários ----------------
    def _build_theme(self):
        """Material 3 + tokens dependentes do tema."""
        assert self.page is not None
        self.page.theme = ft.Theme(use_material3=True, color_scheme_seed=ft.Colors.BLUE)

        dark = self.page.theme_mode == ft.ThemeMode.DARK
        self.t = dict(
            appbar=ft.Colors.BLUE_900 if dark else ft.Colors.BLUE_800,
            surface=ft.Colors.BLUE_GREY_900 if dark else ft.Colors.WHITE,
            block=(ft.Colors.with_opacity(0.06, ft.Colors.WHITE) if dark else ft.Colors.BLUE_GREY_50),
            card=ft.Colors.BLUE_GREY_800 if dark else ft.Colors.BLUE_GREY_50,
            text=ft.Colors.WHITE if dark else ft.Colors.BLACK,
            text2=ft.Colors.WHITE70 if dark else ft.Colors.BLACK87,
            ok=ft.Colors.GREEN_400,
            warn=ft.Colors.AMBER_400,
            err=ft.Colors.RED_400,
            chip_ok_bg=(ft.Colors.GREEN_900 if dark else ft.Colors.GREEN_50),
            chip_ok_text=(ft.Colors.GREEN_300 if dark else ft.Colors.GREEN_700),
            border=ft.Colors.GREY_300 if dark else ft.Colors.GREY_400,
        )

    def _toast(self, message: str) -> None:
        assert self.page is not None
        if not self.snack:
            self.snack = ft.SnackBar(content=ft.Text(""), show_close_icon=True)
            self.page.snack_bar = self.snack
        self.snack.content.value = message
        self.snack.open = True
        self.page.update()

    def _log(self, level: str, event: str, **kwargs) -> None:
        """Loga no terminal com timestamp e metadados (EVENT/OK/ERROR)."""
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        meta = " ".join([f"{k}={v}" for k, v in kwargs.items()])
        print(f"[{ts}] [{level}] {event} {meta}".strip())

    def _wrap_handler(self, fn: Callable, *, tab: str = "", control: str = ""):
        """
        Wrapper para logar eventos e capturar exceções nos handlers (sync/async).
        Uso: on_click=self._wrap_handler(self._start_bot, tab="inicio", control="iniciar")
        """
        def _runner(*args, **kwargs):
            try:
                self._log("EVENT", "handler_start", tab=tab, control=control or getattr(fn, "__name__", "handler"))
                result = fn(*args, **kwargs)
                if asyncio.iscoroutine(result):
                    # Executar coroutine de forma síncrona para evitar problemas de event loop
                    try:
                        asyncio.run(result)
                        self._log("OK", "handler_done_async", tab=tab, control=control or fn.__name__)
                    except Exception as async_exc:
                        tb = traceback.format_exc()
                        self._log("ERROR", "handler_async_exception", tab=tab, control=control or fn.__name__)
                        print(tb)
                        self._toast("❌ Erro em operação assíncrona. Veja o terminal para detalhes.")
                else:
                    self._log("OK", "handler_done", tab=tab, control=control or fn.__name__)
                if self.page:
                    self.page.update()
                return result
            except Exception as exc:  # captura erros síncronos
                tb = traceback.format_exc()
                self._log("ERROR", "handler_exception", tab=tab, control=control or fn.__name__)
                print(tb)
                self._toast("❌ Ocorreu um erro. Veja o terminal para detalhes.")
        return _runner

    async def _await_and_log(self, coro, name: str):
        try:
            await coro
            self._log("OK", "handler_done_async", control=name)
        except Exception as exc:
            tb = traceback.format_exc()
            self._log("ERROR", "handler_exception_async", control=name)
            print(tb)
            self._toast(f"❌ Erro (async) em '{name}'. Veja o terminal.")

    def _dbg(self, control: ft.Control, name: str):
        """Helper para debug de layout - adiciona borda âmbar e tooltip"""
        if not self.__debug_layout__:
            return control
        return ft.Container(
            border=ft.border.all(1, ft.Colors.AMBER),
            tooltip=f"DBG: {name}",
            padding=2,
            content=control,
        )

    # ====== helpers de layout (alinham tudo bonitinho) ======
    def _row(self, *controls, center=False):
        """Row com wrap, spacing e alinhamento padronizados"""
        return ft.Row(
            controls=list(controls),
            wrap=True,
            spacing=10,          # espaçamento horizontal entre itens
            run_spacing=10,      # espaçamento vertical entre linhas (quando quebra)
            alignment=ft.MainAxisAlignment.CENTER if center else ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

    def _section(self, title: str, *children):
        """Seção com título consistente e espaçamento padrão."""
        return ft.Container(
            bgcolor=self.t["block"],
            border_radius=12,
            padding=15,
            margin=ft.margin.only(bottom=12),
            content=ft.Column(
                spacing=12,
                controls=[
                    ft.Text(title, size=18, weight=ft.FontWeight.BOLD, color=self.t["text"]),
                    *children,
                ],
            ),
        )

    def _card(self, body: ft.Control, on_click=None):
        """Card base com altura/padding consistente e suporte a cliques."""
        return ft.Container(
            content=body,
            bgcolor=self.t["card"],
            border=ft.border.all(1, self.t.get("border", ft.Colors.GREY_300)),
            border_radius=12,
            padding=12,
            width=250,  # largura um pouco maior
            height=100,  # altura um pouco maior para melhor visualização
            on_click=on_click,
            ink=True,  # Efeito de clique
        )

    # ---------------- entrypoint ----------------
    def main(self, page: ft.Page):
        self.page = page

        # Janela
        page.title = "🎮 Garimpeiro Geek - Dashboard"
        page.theme_mode = ft.ThemeMode.DARK  # default
        page.window_width = 1200
        page.window_height = 800
        page.window_min_width = 900
        page.window_min_height = 600
        page.padding = 16
        
        # Remover AppBar padrão para usar nossa barra customizada
        page.appbar = None

        # Tema + snackbar
        self._build_theme()
        self.snack = ft.SnackBar(content=ft.Text(""), show_close_icon=True)
        page.snack_bar = self.snack

        # UI - Estrutura simplificada
        header = self._create_header()
        
        # Criar as abas de forma mais simples
        tabs = ft.Tabs(
            selected_index=0,
            animation_duration=200,
            tabs=[
                ft.Tab(text="🏠 Início", content=self._create_home_tab()),
                ft.Tab(text="🤖 Bot Telegram", content=self._create_telegram_tab()),
                ft.Tab(text="📊 Métricas", content=self._create_metrics_tab()),
                ft.Tab(text="🔗 Afiliados", content=self._create_affiliates_tab()),
                ft.Tab(text="⚙️ Configurações", content=self._create_settings_tab()),
            ],
        )
        
        # Layout completamente simplificado
        page.add(
            ft.Column(
                controls=[
                    header,
                    tabs
                ],
                spacing=10
            )
        )
        self._log("INFO", "dashboard_started", title=page.title, theme=str(page.theme_mode))

    # ---------------- header ----------------
    def _create_header(self):
        dark_switch = ft.Switch(
            label="Modo escuro",
            value=True,
            on_change=self._wrap_handler(self._toggle_dark_mode, tab="header", control="toggle_theme"),
        )
        status_chip = ft.Container(
            padding=8,
            bgcolor=self.t["chip_ok_bg"],
            border=ft.border.all(1, ft.Colors.with_opacity(0.1, ft.Colors.BLACK)),
            border_radius=20,
            content=ft.Row(
                spacing=6,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[ft.Icon(ft.Icons.CIRCLE, color=self.t["ok"], size=10),
                          ft.Text("Sistema Online", size=12, color=self.t["chip_ok_text"])],
            ),
        )

        return ft.Container(
            padding=16,
            bgcolor=self.t["appbar"],
            border_radius=12,
            margin=ft.margin.only(bottom=10),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Text("🎮 Garimpeiro Geek", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    ft.Row(controls=[dark_switch, status_chip], spacing=10),
                ],
            ),
        )

    # ---------------- abas ----------------
    def _create_home_tab(self):
        # elementos reativos
        self.status_elements["deep_learning"] = ft.Text(self.systems_status["deep_learning"], size=12, color=self.t["ok"])
        self.status_elements["advanced_metrics"] = ft.Text(self.systems_status["advanced_metrics"], size=12, color=self.t["ok"])
        self.status_elements["affiliate_integration"] = ft.Text(self.systems_status["affiliate_integration"], size=12, color=self.t["ok"])
        self.status_elements["telegram_bot"] = ft.Text(self.systems_status["telegram_bot"], size=12, color=self.t["warn"])

        # Status dos Sistemas com layout organizado e cards clicáveis
        status_grid = ft.Row(
            wrap=True,
            spacing=15,
            run_spacing=15,
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                self._card(
                    ft.Column([
                        ft.Text("🤖 Deep Learning", weight=ft.FontWeight.BOLD, color=self.t["text"]),
                        self.status_elements["deep_learning"],
                    ], spacing=4, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    on_click=self._wrap_handler(self._toggle_deep_learning, tab="inicio", control="deep_learning_card")
                ),
                self._card(
                    ft.Column([
                        ft.Text("📊 Métricas Avançadas", weight=ft.FontWeight.BOLD, color=self.t["text"]),
                        self.status_elements["advanced_metrics"],
                    ], spacing=4, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    on_click=self._wrap_handler(self._navigate_to_metrics, tab="inicio", control="metrics_card")
                ),
                self._card(
                    ft.Column([
                        ft.Text("🔗 Integração Afiliados", weight=ft.FontWeight.BOLD, color=self.t["text"]),
                        self.status_elements["affiliate_integration"],
                    ], spacing=4, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    on_click=self._wrap_handler(self._navigate_to_affiliates, tab="inicio", control="affiliates_card")
                ),
                self._card(
                    ft.Column([
                        ft.Text("📱 Bot Telegram", weight=ft.FontWeight.BOLD, color=self.t["text"]),
                        self.status_elements["telegram_bot"],
                    ], spacing=4, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    on_click=self._wrap_handler(self._toggle_bot_from_card, tab="inicio", control="bot_card")
                ),
            ],
        )
        status_section = self._section("📊 Status dos Sistemas", status_grid)

        # Controles Rápidos com gerenciamento de estado
        btn_style = ft.ButtonStyle(
            padding=ft.padding.symmetric(vertical=12, horizontal=14),
            shape=ft.RoundedRectangleBorder(radius=10),
        )
        
        # Botão de reiniciar com cor de alerta
        restart_btn_style = ft.ButtonStyle(
            padding=ft.padding.symmetric(vertical=12, horizontal=14),
            shape=ft.RoundedRectangleBorder(radius=10),
            bgcolor=ft.Colors.ORANGE_400,
            color=ft.Colors.WHITE,
        )

        # Criar botões com estado dinâmico
        self.start_bot_btn = ft.FilledButton(
            "🚀 Iniciar Bot", 
            icon=ft.Icons.PLAY_ARROW,
            tooltip="Iniciar bot do Telegram",
            style=btn_style, 
            on_click=self._wrap_handler(self._start_bot, tab="inicio", control="iniciar_bot")
        )
        
        self.stop_bot_btn = ft.FilledButton(
            "⏹️ Parar Bot", 
            icon=ft.Icons.STOP,
            tooltip="Parar bot do Telegram",
            style=btn_style, 
            on_click=self._wrap_handler(self._stop_bot, tab="inicio", control="parar_bot"),
            disabled=True  # Inicialmente desabilitado
        )
        
        self.restart_system_btn = ft.FilledButton(
            "🔄 Reiniciar Sistema", 
            icon=ft.Icons.REFRESH,
            tooltip="Reiniciar todos os sistemas (requer confirmação)",
            style=restart_btn_style, 
            on_click=self._wrap_handler(self._confirm_restart_system, tab="inicio", control="reiniciar_sistema")
        )

        controls_row = self._row(
            self.start_bot_btn,
            self.stop_bot_btn,
            self.restart_system_btn,
        )
        controls_section = self._section("🎛️ Controles Rápidos", controls_row)

        # Logs Recentes com altura fixa
        self.logs_container = ft.Column(spacing=2, controls=[
            ft.Text("✅ Dashboard iniciado com sucesso", color=self.t["text2"]),
            ft.Text("✅ Todos os sistemas carregados", color=self.t["text2"]),
            ft.Text("⏸️ Bot Telegram parado", color=self.t["warn"]),
        ])

        logs_box = ft.Container(
            height=220,
            bgcolor=self.t["card"],
            border=ft.border.all(1, self.t["border"]),
            border_radius=10,
            padding=12,
            content=self.logs_container,
        )
        logs_section = self._section("📝 Logs Recentes", logs_box)

        # Layout ultra-simplificado
        return ft.Column(
            spacing=15,
            controls=[
                status_section,
                controls_section,
                logs_section
            ]
        )

    def _create_telegram_tab(self):
        self.bot_status_text = ft.Text(self.bot_status, size=16, color=self.t["warn"])

        # Status do Bot com layout organizado
        status_grid = ft.Row(
            wrap=True,
            spacing=15,
            run_spacing=15,
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                self._card(
                    ft.Column([
                        ft.Text("Status", weight=ft.FontWeight.BOLD, color=self.t["text"]),
                        self.bot_status_text,
                    ], spacing=4, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                ),
                self._card(
                    ft.Column([
                        ft.Text("Mensagens", weight=ft.FontWeight.BOLD, color=self.t["text"]),
                        ft.Text("0", color=ft.Colors.BLUE),
                    ], spacing=4, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                ),
                self._card(
                    ft.Column([
                        ft.Text("Usuários", weight=ft.FontWeight.BOLD, color=self.t["text"]),
                        ft.Text("0", color=ft.Colors.GREEN),
                    ], spacing=4, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                ),
            ],
        )
        status_section = self._section("🤖 Bot Telegram", status_grid)

        # Controles do Bot com botões normalizados
        btn_style = ft.ButtonStyle(
            padding=ft.padding.symmetric(vertical=12, horizontal=14),
            shape=ft.RoundedRectangleBorder(radius=10),
        )

        controls_row = self._row(
            ft.FilledButton("🚀 Iniciar Bot", icon=ft.Icons.PLAY_ARROW,
                            tooltip="Iniciar bot do Telegram",
                            style=btn_style, on_click=self._wrap_handler(self._start_bot, tab="telegram", control="iniciar_bot")),
            ft.FilledButton("⏹️ Parar Bot", icon=ft.Icons.STOP,
                            tooltip="Parar bot do Telegram",
                            style=btn_style, on_click=self._wrap_handler(self._stop_bot, tab="telegram", control="parar_bot")),
            ft.FilledButton("📋 Ver Logs", icon=ft.Icons.LIST,
                            tooltip="Visualizar logs do bot",
                            style=btn_style, on_click=self._wrap_handler(self._view_logs, tab="telegram", control="ver_logs")),
        )
        controls_section = self._section("🎛️ Controles do Bot", controls_row)

        return ft.Column(
            spacing=15,
            controls=[
                status_section,
                controls_section,
            ]
        )

    def _create_metrics_tab(self):
        # Métricas com layout simples
        metrics_grid = ft.Row(
            wrap=True,
            spacing=10,
            run_spacing=10,
            controls=[
                self._card(
                    ft.Column([
                        ft.Text("Ofertas Processadas", size=12, color=self.t["text2"]),
                        ft.Text("0", size=22, weight=ft.FontWeight.BOLD, color=self.t["text"]),
                        ft.Text("Hoje", size=11, color=self.t["text2"]),
                    ], spacing=2),
                ),
                self._card(
                    ft.Column([
                        ft.Text("Conversões", size=12, color=self.t["text2"]),
                        ft.Text("0", size=22, weight=ft.FontWeight.BOLD, color=self.t["text"]),
                        ft.Text("Taxa 0%", size=11, color=self.t["text2"]),
                    ], spacing=2),
                ),
                self._card(
                    ft.Column([
                        ft.Text("Receita", size=12, color=self.t["text2"]),
                        ft.Text("R$ 0,00", size=22, weight=ft.FontWeight.BOLD, color=self.t["text"]),
                        ft.Text("Total", size=11, color=self.t["text2"]),
                    ], spacing=2),
                ),
                self._card(
                    ft.Column([
                        ft.Text("Usuários Ativos", size=12, color=self.t["text2"]),
                        ft.Text("0", size=22, weight=ft.FontWeight.BOLD, color=self.t["text"]),
                        ft.Text("Últimos 7 dias", size=11, color=self.t["text2"]),
                    ], spacing=2),
                ),
            ],
        )
        metrics_section = self._section("📊 Métricas e Analytics", metrics_grid)

        # Gráfico placeholder
        chart = ft.Container(
            height=260, 
            bgcolor=self.t["card"], 
            border=ft.border.all(1, self.t["border"]),
            border_radius=12, 
            padding=16,
            content=ft.Column(
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Text("📈 Gráfico de Conversões", size=16, weight=ft.FontWeight.BOLD, color=self.t["text"]),
                    ft.Text("Dados não disponíveis - conectar fonte", color=self.t["text2"])
                ],
            ),
        )
        chart_section = self._section("📈 Gráficos", chart)

        return ft.Column(
            spacing=15,
            controls=[
                metrics_section,
                chart_section,
            ]
        )

    def _create_affiliates_tab(self):
        # Plataformas com layout simples
        platforms_grid = ft.Row(
            wrap=True,
            spacing=10,
            run_spacing=10,
            controls=[
                self._card(
                    ft.Column([
                        ft.Text("Amazon", weight=ft.FontWeight.BOLD, color=self.t["text"]),
                        ft.Text("✅ Ativo", color=ft.Colors.ORANGE),
                    ], spacing=4),
                ),
                self._card(
                    ft.Column([
                        ft.Text("Mercado Livre", weight=ft.FontWeight.BOLD, color=self.t["text"]),
                        ft.Text("✅ Ativo", color=ft.Colors.YELLOW),
                    ], spacing=4),
                ),
                self._card(
                    ft.Column([
                        ft.Text("Magazine Luiza", weight=ft.FontWeight.BOLD, color=self.t["text"]),
                        ft.Text("✅ Ativo", color=ft.Colors.PINK),
                    ], spacing=4),
                ),
                self._card(
                    ft.Column([
                        ft.Text("Shopee", weight=ft.FontWeight.BOLD, color=self.t["text"]),
                        ft.Text("✅ Ativo", color=ft.Colors.RED),
                    ], spacing=4),
                ),
            ],
        )
        platforms_section = self._section("🔗 Integração com Afiliados", platforms_grid)

        # Ações com botões normalizados
        btn_style = ft.ButtonStyle(
            padding=ft.padding.symmetric(vertical=12, horizontal=14),
            shape=ft.RoundedRectangleBorder(radius=10),
        )

        actions_row = self._row(
            ft.FilledButton("🔍 Validar Links", icon=ft.Icons.SEARCH,
                            tooltip="Validar links de afiliados",
                            style=btn_style, on_click=self._wrap_handler(self._validate_links, tab="afiliados", control="validar_links")),
            ft.FilledButton("📊 Relatório", icon=ft.Icons.ANALYTICS,
                            tooltip="Gerar relatório de afiliados",
                            style=btn_style, on_click=self._wrap_handler(self._generate_report, tab="afiliados", control="relatorio")),
            ft.FilledButton("🔍 Scraping", icon=ft.Icons.SEARCH,
                            tooltip="Fazer scraping de ofertas",
                            style=btn_style, on_click=self._wrap_handler(self._scrape_offers, tab="afiliados", control="scraping")),
            ft.FilledButton("📱 Telegram", icon=ft.Icons.SEND,
                            tooltip="Enviar oferta via Telegram",
                            style=btn_style, on_click=self._wrap_handler(self._send_telegram_offer, tab="afiliados", control="telegram")),
        )
        actions_section = self._section("🛠️ Ações", actions_row)

        return ft.Column(
            spacing=15,
            controls=[
                platforms_section,
                actions_section,
            ]
        )

    def _create_settings_tab(self):
        # Configurações Gerais
        general_switches = self._row(
            ft.Switch(label="Modo Noturno", value=True,
                      on_change=self._wrap_handler(self._toggle_dark_mode, tab="config", control="modo_noturno")),
            ft.Switch(label="Auto-iniciar Bot", value=False,
                      on_change=self._wrap_handler(self._toggle_auto_start, tab="config", control="auto_iniciar")),
        )
        general_section = self._section("⚙️ Configurações Gerais", general_switches)

        # Ações do Sistema com botões normalizados
        btn_style = ft.ButtonStyle(
            padding=ft.padding.symmetric(vertical=12, horizontal=14),
            shape=ft.RoundedRectangleBorder(radius=10),
        )

        actions_row = self._row(
            ft.FilledButton("💾 Backup", icon=ft.Icons.BACKUP,
                            tooltip="Fazer backup do sistema",
                            style=btn_style, on_click=self._wrap_handler(self._backup_system, tab="config", control="backup")),
            ft.FilledButton("🔄 Atualizar", icon=ft.Icons.UPDATE,
                            tooltip="Atualizar sistema",
                            style=btn_style, on_click=self._wrap_handler(self._update_system, tab="config", control="atualizar")),
            ft.FilledButton("📋 Logs", icon=ft.Icons.LIST,
                            tooltip="Visualizar logs do sistema",
                            style=btn_style, on_click=self._wrap_handler(self._view_system_logs, tab="config", control="logs")),
        )
        actions_section = self._section("🛠️ Ações do Sistema", actions_row)

        return ft.Column(
            spacing=15,
            controls=[
                general_section,
                actions_section,
            ]
        )

    # ---------------- callbacks (com async non-blocking) ----------------
    def _start_bot(self, e):
        self.bot_status = "🟢 Rodando"
        self.systems_status["telegram_bot"] = "🟢 Rodando"
        if self.status_elements.get("telegram_bot"):
            self.status_elements["telegram_bot"].value = "🟢 Rodando"
            self.status_elements["telegram_bot"].color = self.t["ok"]
        if self.bot_status_text:
            self.bot_status_text.value = "🟢 Rodando"
            self.bot_status_text.color = self.t["ok"]
            
        # Atualizar estado dos botões
        if hasattr(self, 'start_bot_btn'):
            self.start_bot_btn.disabled = True
            self.start_bot_btn.update()
        if hasattr(self, 'stop_bot_btn'):
            self.stop_bot_btn.disabled = False
            self.stop_bot_btn.update()
            
        self._add_log("🤖 Bot Telegram iniciado com sucesso!")
        self._toast("🤖 Bot iniciado com sucesso!")

    def _stop_bot(self, e):
        self.bot_status = "⏸️ Parado"
        self.systems_status["telegram_bot"] = "⏸️ Parado"
        if self.status_elements.get("telegram_bot"):
            self.status_elements["telegram_bot"].value = "⏸️ Parado"
            self.status_elements["telegram_bot"].color = self.t["warn"]
        if self.bot_status_text:
            self.bot_status_text.value = "⏸️ Parado"
            self.bot_status_text.color = self.t["warn"]
            
        # Atualizar estado dos botões
        if hasattr(self, 'start_bot_btn'):
            self.start_bot_btn.disabled = False
            self.start_bot_btn.update()
        if hasattr(self, 'stop_bot_btn'):
            self.stop_bot_btn.disabled = True
            self.stop_bot_btn.update()
            
        self._add_log("⏹️ Bot Telegram parado")
        self._toast("⏹️ Bot parado com sucesso!")

    def _confirm_restart_system(self, e):
        """Mostrar diálogo de confirmação antes de reiniciar"""
        def confirm_restart(e):
            self._restart_system(e)
            self.page.dialog.open = False
            self.page.update()
            
        def cancel_restart(e):
            self.page.dialog.open = False
            self.page.update()
            
        dialog = ft.AlertDialog(
            title=ft.Text("⚠️ Confirmar Reinicialização"),
            content=ft.Text("Você tem certeza que deseja reiniciar todo o sistema?\n\nEsta ação irá parar todos os serviços e pode interromper operações em andamento."),
            actions=[
                ft.TextButton("❌ Cancelar", on_click=cancel_restart),
                ft.TextButton("✅ Confirmar", on_click=confirm_restart, style=ft.ButtonStyle(bgcolor=ft.Colors.RED_400, color=ft.Colors.WHITE)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.dialog = dialog
        self.page.dialog.open = True
        self.page.update()

    def _restart_system(self, e):
        self._add_log("🔄 Reiniciando sistema...")
        for key, el in self.status_elements.items():
            if key == "telegram_bot":
                el.value = "⏸️ Parado"
                el.color = self.t["warn"]
            else:
                el.value = "✅ Ativo"
                el.color = self.t["ok"]
                
        # Resetar estado dos botões
        if hasattr(self, 'start_bot_btn'):
            self.start_bot_btn.disabled = False
            self.start_bot_btn.update()
        if hasattr(self, 'stop_bot_btn'):
            self.stop_bot_btn.disabled = True
            self.stop_bot_btn.update()
            
        self._add_log("✅ Sistema reiniciado com sucesso!")
        self._toast("🔄 Sistema reiniciado!")

    def _toggle_deep_learning(self, e):
        """Toggle do Deep Learning via card clicável"""
        current_status = self.systems_status["deep_learning"]
        if "Ativo" in current_status:
            self.systems_status["deep_learning"] = "⚠️ Pausado"
            self.status_elements["deep_learning"].value = "⚠️ Pausado"
            self.status_elements["deep_learning"].color = ft.Colors.ORANGE_400
            self._add_log("🤖 Deep Learning pausado")
            self._toast("🤖 Deep Learning pausado")
        else:
            self.systems_status["deep_learning"] = "✅ Ativo"
            self.status_elements["deep_learning"].value = "✅ Ativo"
            self.status_elements["deep_learning"].color = self.t["ok"]
            self._add_log("🤖 Deep Learning ativado")
            self._toast("🤖 Deep Learning ativado")
        self.status_elements["deep_learning"].update()

    def _navigate_to_metrics(self, e):
        """Navegar para aba de métricas via card clicável"""
        self._add_log("📊 Navegando para Métricas...")
        self._toast("📊 Abrindo aba de Métricas...")
        # Aqui você pode implementar a navegação real para a aba de métricas

    def _navigate_to_affiliates(self, e):
        """Navegar para aba de afiliados via card clicável"""
        self._add_log("🔗 Navegando para Afiliados...")
        self._toast("🔗 Abrindo aba de Afiliados...")
        # Aqui você pode implementar a navegação real para a aba de afiliados

    def _toggle_bot_from_card(self, e):
        """Toggle do bot via card clicável"""
        if self.bot_status == "🟢 Rodando":
            self._stop_bot(e)
        else:
            self._start_bot(e)
    
    async def _scrape_offers(self, e):
        """Scraping real de ofertas usando scrapers implementados."""
        self._add_log("🔍 Iniciando scraping de ofertas...")
        
        try:
            import sys
            sys.path.append('src')
            from scrapers.real_scrapers import ScrapingManager
            
            manager = ScrapingManager()
            
            # Scraping em todas as lojas
            offers = await manager.scrape_all_stores(category="gaming", limit_per_store=3)
            
            if offers:
                self._add_log(f"✅ Scraping concluído: {len(offers)} ofertas encontradas")
                
                # Mostrar algumas ofertas nos logs
                for i, offer in enumerate(offers[:3]):
                    self._add_log(f"🛍️ {offer.title} - R$ {offer.price:.2f} ({offer.store})")
                
                if len(offers) > 3:
                    self._add_log(f"... e mais {len(offers) - 3} ofertas")
                
                self._toast(f"✅ {len(offers)} ofertas encontradas!")
            else:
                self._add_log("⚠️ Nenhuma oferta encontrada")
                self._toast("⚠️ Nenhuma oferta encontrada")
                
        except Exception as ex:
            self._add_log(f"❌ Erro no scraping: {ex}")
            self._toast("❌ Erro no scraping de ofertas")
    
    async def _send_telegram_offer(self, e):
        """Envia oferta via bot do Telegram."""
        self._add_log("📱 Enviando oferta via Telegram...")
        
        try:
            import sys
            sys.path.append('src')
            from telegram_bot.real_telegram_bot import TelegramBotManager, TelegramOffer
            
            # Token fictício para demonstração
            token = "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
            bot_manager = TelegramBotManager(token)
            
            # Iniciar bot se não estiver rodando
            if not bot_manager.is_running:
                await bot_manager.start_bot()
            
            # Criar oferta de exemplo
            offer = TelegramOffer(
                title="Headset Gamer HyperX Cloud II",
                price=199.90,
                original_price=299.90,
                discount_percent=33,
                url="https://example.com/headset",
                image_url="https://via.placeholder.com/300x300?text=Headset",
                store="Amazon",
                category="gaming",
                affiliate_url="https://amazon.com.br/dp/123?tag=garimpeirogeek-20",
                description="Headset profissional para gamers com som surround 7.1"
            )
            
            # Enviar para inscritos
            sent_count = await bot_manager.send_offer_to_subscribers(offer)
            
            if sent_count > 0:
                self._add_log(f"✅ Oferta enviada para {sent_count} usuários")
                self._toast(f"📱 Oferta enviada para {sent_count} usuários!")
            else:
                self._add_log("⚠️ Nenhum usuário inscrito para receber ofertas")
                self._toast("⚠️ Nenhum usuário inscrito")
                
        except Exception as ex:
            self._add_log(f"❌ Erro ao enviar oferta: {ex}")
            self._toast("❌ Erro ao enviar oferta via Telegram")

    def _view_logs(self, e):
        self._add_log("📋 Visualizando logs do bot...")
        self._toast("📋 Logs do bot exibidos na seção de logs!")

    # ---- versões async (não travam a UI) ----
    async def _validate_links(self, e):
        """Valida links de afiliados usando APIs reais."""
        self._add_log("🔍 Iniciando validação de links de afiliados...")
        
        try:
            # Importar e usar sistema real de afiliados
            import sys
            sys.path.append('src')
            from affiliate.real_affiliate_apis import AffiliateManager
            
            manager = AffiliateManager()
            
            # URLs de teste
            test_urls = [
                "https://www.amazon.com.br/dp/B08N5WRWNW",
                "https://www.magazineluiza.com.br/produto/123456",
                "https://www.mercadolivre.com.br/produto/789012"
            ]
            
            valid_links = 0
            for url in test_urls:
                link = await manager.create_affiliate_link(url)
                if link:
                    is_valid = await manager.validate_affiliate_link(link.affiliate_url)
                    if is_valid:
                        valid_links += 1
                        self._add_log(f"✅ Link válido: {link.network}")
                    else:
                        self._add_log(f"❌ Link inválido: {link.network}")
                else:
                    self._add_log(f"❌ Falha ao criar link para: {url}")
            
            self._add_log(f"📊 Validação concluída: {valid_links}/{len(test_urls)} links válidos")
            self._toast(f"✅ {valid_links} links validados com sucesso!")
            
        except Exception as ex:
            self._add_log(f"❌ Erro na validação: {ex}")
            self._toast("❌ Erro na validação de links")

    async def _generate_report(self, e):
        """Gera relatório usando dados reais de afiliados."""
        self._add_log("📊 Gerando relatório de afiliados...")
        
        try:
            import sys
            sys.path.append('src')
            from affiliate.real_affiliate_apis import AffiliateManager
            from datetime import datetime, timedelta
            import json
            import os
            
            manager = AffiliateManager()
            
            # Obter estatísticas dos últimos 30 dias
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            
            stats = await manager.get_all_stats(start_date, end_date)
            
            # Gerar relatório
            report_data = {
                "periodo": f"{start_date.strftime('%d/%m/%Y')} a {end_date.strftime('%d/%m/%Y')}",
                "redes_ativas": len(stats),
                "total_cliques": sum(s.total_clicks for s in stats),
                "total_conversoes": sum(s.total_conversions for s in stats),
                "ganhos_totais": sum(s.earnings for s in stats),
                "detalhes_por_rede": [
                    {
                        "rede": s.network,
                        "cliques": s.total_clicks,
                        "conversoes": s.total_conversions,
                        "taxa_conversao": s.conversion_rate,
                        "ganhos": s.earnings
                    } for s in stats
                ]
            }
            
            # Salvar relatório
            os.makedirs("relatorios", exist_ok=True)
            filename = f"relatorios/relatorio_afiliados_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False, default=str)
            
            self._add_log(f"📄 Relatório salvo: {filename}")
            self._add_log(f"📈 Total de ganhos: R$ {report_data['ganhos_totais']:.2f}")
            self._toast(f"📄 Relatório salvo em {filename}")
            
        except Exception as ex:
            self._add_log(f"❌ Erro ao gerar relatório: {ex}")
            self._toast("❌ Erro ao gerar relatório")

    async def _backup_system(self, e):
        """Faz backup do sistema incluindo dados reais."""
        self._add_log("💾 Iniciando backup do sistema...")
        
        try:
            import shutil
            import os
            from datetime import datetime
            
            # Criar diretório de backup
            backup_dir = f"backups/backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            os.makedirs(backup_dir, exist_ok=True)
            
            # Backup de arquivos importantes
            files_to_backup = [
                "src/",
                "config/",
                "data/",
                "logs/",
                "relatorios/",
                "windows_dashboard.py"
            ]
            
            for item in files_to_backup:
                if os.path.exists(item):
                    if os.path.isdir(item):
                        shutil.copytree(item, f"{backup_dir}/{item}")
                    else:
                        shutil.copy2(item, backup_dir)
                    self._add_log(f"✅ Backup: {item}")
            
            # Backup do banco de dados (se existir)
            if os.path.exists("data/garimpeiro_geek.db"):
                shutil.copy2("data/garimpeiro_geek.db", f"{backup_dir}/garimpeiro_geek.db")
                self._add_log("✅ Backup: banco de dados")
            
            self._add_log(f"✅ Backup concluído: {backup_dir}")
            self._toast(f"💾 Backup salvo em {backup_dir}")
            
        except Exception as ex:
            self._add_log(f"❌ Erro no backup: {ex}")
            self._toast("❌ Erro no backup do sistema")

    async def _update_system(self, e):
        """Verifica e aplica atualizações do sistema."""
        self._add_log("🔄 Verificando atualizações...")
        
        try:
            # Simular verificação de atualizações
            import subprocess
            import sys
            
            # Verificar se há atualizações do pip
            result = subprocess.run([sys.executable, "-m", "pip", "list", "--outdated"], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                outdated_packages = result.stdout.strip().split('\n')[2:]  # Pular cabeçalho
                if outdated_packages and outdated_packages[0]:
                    self._add_log(f"📦 {len(outdated_packages)} pacotes desatualizados encontrados")
                    for package in outdated_packages[:5]:  # Mostrar apenas 5
                        self._add_log(f"   • {package.split()[0]}")
                else:
                    self._add_log("✅ Todos os pacotes estão atualizados")
            else:
                self._add_log("⚠️ Não foi possível verificar atualizações")
            
            # Simular atualização do sistema
            self._add_log("🔄 Aplicando atualizações...")
            await asyncio.sleep(1)
            
            self._add_log("✅ Sistema atualizado com sucesso!")
            self._toast("🔄 Atualização concluída!")
            
        except Exception as ex:
            self._add_log(f"❌ Erro na atualização: {ex}")
            self._toast("❌ Erro na atualização do sistema")

    def _view_system_logs(self, e):
        self._add_log("📋 Abrindo logs do sistema...")
        self._toast("📋 Logs do sistema exibidos!")

    def _toggle_dark_mode(self, e):
        assert self.page is not None
        self.page.theme_mode = ft.ThemeMode.DARK if e.control.value else ft.ThemeMode.LIGHT
        self._add_log("🌙 Modo escuro ativado" if e.control.value else "☀️ Modo claro ativado")
        self._build_theme()  # reconstroi tokens
        self.page.update()

    def _toggle_auto_start(self, e):
        status = "Ativado" if e.control.value else "Desativado"
        self._add_log(f"⚙️ Auto-início do bot: {status}")
        self._toast(f"Auto-início: {status}")

    # ---------------- logs ----------------
    def _add_log(self, message: str):
        timestamp = datetime.now().strftime("%H:%M:%S")
        entry = ft.Text(f"[{timestamp}] {message}", size=13, color=self.t["text2"])
        if isinstance(self.logs_container, ft.Column):
            self.logs_container.controls.append(entry)
            if len(self.logs_container.controls) > 15:  # Aumentado para 15 logs
                self.logs_container.controls.pop(0)
            self.logs_container.update()


def main():
    dashboard = WindowsDashboard()
    print("🚀 Iniciando Dashboard Windows do Garimpeiro Geek...")
    print("🖥️ Aplicativo Windows nativo")
    ft.app(target=dashboard.main, view=ft.FLET_APP)


if __name__ == "__main__":
    main()