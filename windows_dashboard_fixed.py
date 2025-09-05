#!/usr/bin/env python3
# Dashboard Flet para Windows - Garimpeiro Geek (revisado)

import flet as ft
from pathlib import Path
import sys

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

class WindowsDashboard:
    def __init__(self):
        self.page: ft.Page | None = None

        # estado
        self.bot_status = "⏸️ Parado"
        self.systems_status = {
            "deep_learning": "✅ Ativo",
            "advanced_metrics": "✅ Ativo",
            "affiliate_integration": "✅ Ativo",
            "telegram_bot": "⏸️ Parado",
        }

        # refs reativas
        self.bot_status_text: ft.Text | None = None
        self.bot_status_chip: ft.Container | None = None
        self.telegram_chip: ft.Text | None = None
        self.header_status_chip: ft.Container | None = None

        self.snack: ft.SnackBar | None = None
        self.t = {}  # tokens de cor

    # -------------------- helpers de tema --------------------
    def _build_theme(self):
        self.page.theme = ft.Theme(use_material3=True, color_scheme_seed=ft.colors.BLUE)
        # tokens dependentes do tema
        dark = self.page.theme_mode == ft.ThemeMode.DARK
        self.t = dict(
            appbar = ft.colors.BLUE_900 if dark else ft.colors.BLUE_800,
            surface= ft.colors.BLUE_GREY_900 if dark else ft.colors.WHITE,
            block  = ft.colors.with_opacity(.06, ft.colors.WHITE) if dark else ft.colors.BLUE_GREY_50,
            card   = ft.colors.BLUE_GREY_800 if dark else ft.colors.BLUE_GREY_50,
            text   = ft.colors.WHITE if dark else ft.colors.BLACK,
            text2  = ft.colors.WHITE70 if dark else ft.colors.BLACK87,
            ok     = ft.colors.GREEN_400,
            warn   = ft.colors.AMBER_400,
            err    = ft.colors.RED_400,
            chip_ok_bg   = ft.colors.GREEN_900 if dark else ft.colors.GREEN_50,
            chip_text_ok = ft.colors.GREEN_300 if dark else ft.colors.GREEN_700,
        )

    def toast(self, msg: str):
        self.snack.content.value = msg
        self.snack.open = True
        self.page.update()

    # -------------------- entrypoint --------------------
    def main(self, page: ft.Page):
        self.page = page
        page.title = "Garimpeiro Geek - Dashboard"
        page.window_width, page.window_height = 1200, 800
        page.window_min_width, page.window_min_height = 900, 600
        page.padding = 16
        page.theme_mode = ft.ThemeMode.DARK  # padrão
        self._build_theme()

        # snackbar único
        self.snack = ft.SnackBar(content=ft.Text(""), show_close_icon=True)
        page.snack_bar = self.snack

        header = self._header()
        tabs = ft.Tabs(
            expand=1,
            animation_duration=200,
            tabs=[
                ft.Tab(text="🏠 Início", content=self._tab_home()),
                ft.Tab(text="🤖 Bot Telegram", content=self._tab_telegram()),
                ft.Tab(text="📊 Métricas", content=self._tab_metrics()),
                ft.Tab(text="🔗 Afiliados", content=self._tab_affiliates()),
                ft.Tab(text="⚙️ Configurações", content=self._tab_settings()),
            ],
        )

        page.add(ft.Column(expand=1, controls=[header, tabs]))

    # -------------------- UI --------------------
    def _header(self) -> ft.Container:
        # chip de status (reativo)
        status_text = ft.Text("Sistema Online", size=12, color=self.t["chip_text_ok"])
        self.header_status_chip = ft.Container(
            padding=8,
            bgcolor=self.t["chip_ok_bg"],
            border_radius=20,
            content=ft.Row(
                spacing=6,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[ft.Icon(ft.icons.CIRCLE, size=10, color=self.t["ok"]), status_text],
            ),
        )

        dark_switch = ft.Switch(
            label="Modo escuro",
            value=True,
            on_change=self._toggle_dark_mode,
        )

        return ft.Container(
            bgcolor=self.t["appbar"],
            border_radius=12,
            padding=16,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Column(controls=[
                        ft.Text("Garimpeiro Geek", size=26, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                        ft.Text("Sistema de Recomendações de Ofertas", size=13, color=ft.colors.WHITE70),
                    ]),
                    ft.Row(controls=[dark_switch, self.header_status_chip]),
                ],
            ),
        )

    # -------------- abas --------------
    def _tab_home(self) -> ft.Control:
        # cards de status (simples)
        def status_card(title: str, value: str) -> ft.Container:
            return ft.Container(
                bgcolor=self.t["card"],
                border_radius=12,
                padding=12,
                expand=True,
                content=ft.Column(spacing=4, controls=[
                    ft.Text(title, size=13, weight=ft.FontWeight.BOLD, color=self.t["text"]),
                    ft.Text(value, size=12, color=self.t["text2"]),
                ]),
            )

        status_grid = ft.Row(
            wrap=True,
            spacing=12,
            controls=[
                status_card("🤖 Deep Learning", self.systems_status["deep_learning"]),
                status_card("📊 Métricas Avançadas", self.systems_status["advanced_metrics"]),
                status_card("🔗 Integração Afiliados", self.systems_status["affiliate_integration"]),
                status_card("📱 Bot Telegram", self.systems_status["telegram_bot"]),
            ],
        )

        # controles rápidos
        controls = ft.Row(wrap=True, spacing=12, controls=[
            ft.ElevatedButton("Iniciar Bot", icon=ft.icons.PLAY_ARROW, on_click=self._start_bot),
            ft.ElevatedButton("Parar Bot", icon=ft.icons.STOP, on_click=self._stop_bot),
            ft.ElevatedButton("Reiniciar Sistema", icon=ft.icons.REFRESH, on_click=self._restart_system),
        ])

        # logs (skeleton placeholder)
        logs = ft.Container(
            bgcolor=self.t["block"],
            border_radius=12,
            padding=16,
            content=ft.Column(controls=[
                ft.Text("📝 Logs Recentes", size=16, weight=ft.FontWeight.BOLD, color=self.t["text"]),
                ft.Text("✅ Dashboard iniciado", color=self.t["text2"]),
                ft.Text("✅ Serviços carregados", color=self.t["text2"]),
                ft.Text("⏸️ Bot Telegram parado", color=self.t["warn"]),
            ]),
        )

        return ft.Container(
            expand=1,
            content=ft.Column(
                expand=1,
                scroll=ft.ScrollMode.AUTO,
                spacing=12,
                controls=[
                    ft.Text("📊 Status dos Sistemas", size=18, weight=ft.FontWeight.BOLD, color=self.t["text"]),
                    status_grid,
                    ft.Text("🎛️ Controles Rápidos", size=18, weight=ft.FontWeight.BOLD, color=self.t["text"]),
                    controls,
                    logs,
                ],
            ),
        )

    def _tab_telegram(self) -> ft.Control:
        # status box
        self.bot_status_text = ft.Text(self.bot_status, size=16, color=self.t["warn"])
        self.bot_status_chip = ft.Container(
            bgcolor=ft.colors.AMBER_50 if self.page.theme_mode == ft.ThemeMode.LIGHT else ft.colors.with_opacity(.15, ft.colors.AMBER),
            border_radius=10,
            padding=12,
            expand=True,
            content=ft.Column(spacing=4, controls=[ft.Text("Status", weight=ft.FontWeight.BOLD), self.bot_status_text]),
        )

        msgs = ft.Container(
            bgcolor=ft.colors.BLUE_50 if self.page.theme_mode == ft.ThemeMode.LIGHT else ft.colors.with_opacity(.12, ft.colors.BLUE),
            border_radius=10,
            padding=12,
            expand=True,
            content=ft.Column(spacing=4, controls=[ft.Text("Mensagens", weight=ft.FontWeight.BOLD), ft.Text("0", color=ft.colors.BLUE)]),
        )

        users = ft.Container(
            bgcolor=ft.colors.GREEN_50 if self.page.theme_mode == ft.ThemeMode.LIGHT else ft.colors.with_opacity(.12, ft.colors.GREEN),
            border_radius=10,
            padding=12,
            expand=True,
            content=ft.Column(spacing=4, controls=[ft.Text("Usuários", weight=ft.FontWeight.BOLD), ft.Text("0", color=ft.colors.GREEN)]),
        )

        buttons = ft.Row(wrap=True, spacing=12, controls=[
            ft.ElevatedButton("Iniciar Bot", icon=ft.icons.PLAY_ARROW, on_click=self._start_bot, tooltip="Iniciar serviço do bot"),
            ft.ElevatedButton("Parar Bot", icon=ft.icons.STOP, on_click=self._stop_bot),
            ft.ElevatedButton("Ver Logs", icon=ft.icons.LIST, on_click=self._view_logs),
        ])

        return ft.Container(
            expand=1,
            content=ft.Column(expand=1, scroll=ft.ScrollMode.AUTO, spacing=12, controls=[
                ft.Text("🤖 Bot Telegram", size=18, weight=ft.FontWeight.BOLD, color=self.t["text"]),
                ft.Row(wrap=True, spacing=12, controls=[self.bot_status_chip, msgs, users]),
                buttons,
            ]),
        )

    def _tab_metrics(self) -> ft.Control:
        # cards de métrica simples (placeholders)
        def metric_card(title: str, value: str, subtitle: str) -> ft.Container:
            return ft.Container(
                bgcolor=self.t["card"], border_radius=12, padding=12, expand=True,
                content=ft.Column(spacing=2, controls=[
                    ft.Text(title, size=12, color=self.t["text2"]),
                    ft.Text(value, size=22, weight=ft.FontWeight.BOLD, color=self.t["text"]),
                    ft.Text(subtitle, size=11, color=self.t["text2"]),
                ]),
            )

        grid = ft.Row(wrap=True, spacing=12, controls=[
            metric_card("Ofertas Processadas", "0", "Hoje"),
            metric_card("Conversões", "0", "Taxa 0%"),
            metric_card("Receita", "R$ 0,00", "Total"),
            metric_card("Usuários Ativos", "0", "7 dias"),
        ])

        chart_placeholder = ft.Container(
            bgcolor=self.t["block"], border_radius=12, height=260,
            content=ft.Column(controls=[
                ft.Text("📈 Gráfico de Conversões", size=16, weight=ft.FontWeight.BOLD, color=self.t["text"]),
                ft.Text("Sem dados — conectar fonte", color=self.t["text2"]),
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        )

        return ft.Container(
            expand=1,
            content=ft.Column(expand=1, scroll=ft.ScrollMode.AUTO, spacing=12, controls=[
                ft.Text("📊 Métricas e Analytics", size=18, weight=ft.FontWeight.BOLD, color=self.t["text"]),
                grid,
                chart_placeholder,
            ]),
        )

    def _tab_affiliates(self) -> ft.Control:
        def platform_card(name: str, status: str, color: str) -> ft.Container:
            return ft.Container(
                bgcolor=self.t["card"], border_radius=12, padding=12, expand=True,
                content=ft.Column(spacing=4, controls=[
                    ft.Text(name, weight=ft.FontWeight.BOLD, color=self.t["text"]),
                    ft.Text(status, color=color),
                ]),
            )

        grid = ft.Row(wrap=True, spacing=12, controls=[
            platform_card("Amazon", "✅ Ativo", ft.colors.ORANGE),
            platform_card("Mercado Livre", "✅ Ativo", ft.colors.YELLOW),
            platform_card("Magazine Luiza", "✅ Ativo", ft.colors.PINK),
            platform_card("Shopee", "✅ Ativo", ft.colors.RED),
        ])

        actions = ft.Row(wrap=True, spacing=12, controls=[
            ft.ElevatedButton("Validar Links", icon=ft.icons.SEARCH, on_click=self._validate_links),
            ft.ElevatedButton("Relatório", icon=ft.icons.ANALYTICS, on_click=self._generate_report),
        ])

        return ft.Container(
            expand=1,
            content=ft.Column(expand=1, scroll=ft.ScrollMode.AUTO, spacing=12, controls=[
                ft.Text("🔗 Integração com Afiliados", size=18, weight=ft.FontWeight.BOLD, color=self.t["text"]),
                grid, actions,
            ]),
        )

    def _tab_settings(self) -> ft.Control:
        auto = ft.Switch(label="Auto-iniciar Bot", value=False, on_change=self._toggle_auto_start)

        actions = ft.Row(wrap=True, spacing=12, controls=[
            ft.ElevatedButton("Backup", icon=ft.icons.BACKUP, on_click=self._backup_system),
            ft.ElevatedButton("Atualizar", icon=ft.icons.UPDATE, on_click=self._update_system),
            ft.ElevatedButton("Logs", icon=ft.icons.LIST, on_click=self._view_system_logs),
        ])

        return ft.Container(
            expand=1,
            content=ft.Column(expand=1, scroll=ft.ScrollMode.AUTO, spacing=12, controls=[
                ft.Text("⚙️ Configurações do Sistema", size=18, weight=ft.FontWeight.BOLD, color=self.t["text"]),
                ft.Container(padding=12, bgcolor=self.t["card"], border_radius=12, content=ft.Row(wrap=True, controls=[auto])),
                ft.Text("Ações do Sistema", size=16, weight=ft.FontWeight.BOLD, color=self.t["text"]),
                actions,
            ]),
        )

    # -------------------- callbacks --------------------
    def _start_bot(self, e):
        self.bot_status = "🟢 Rodando"
        self.systems_status["telegram_bot"] = "🟢 Rodando"
        if self.bot_status_text: self.bot_status_text.value = self.bot_status; self.bot_status_text.color = self.t["ok"]
        if self.bot_status_chip: self.bot_status_chip.bgcolor = ft.colors.with_opacity(.12, ft.colors.GREEN)
        self.toast("🤖 Bot iniciado com sucesso!")

    def _stop_bot(self, e):
        self.bot_status = "⏸️ Parado"
        self.systems_status["telegram_bot"] = "⏸️ Parado"
        if self.bot_status_text: self.bot_status_text.value = self.bot_status; self.bot_status_text.color = self.t["warn"]
        if self.bot_status_chip: self.bot_status_chip.bgcolor = ft.colors.with_opacity(.12, ft.colors.AMBER)
        self.toast("⏹️ Bot parado com sucesso!")

    def _restart_system(self, e):
        self.toast("🔄 Reiniciando serviços...")

    def _view_logs(self, e):
        self.toast("📋 Abrindo logs...")

    def _validate_links(self, e):
        self.toast("🔍 Validando links de afiliados...")

    def _generate_report(self, e):
        self.toast("📊 Gerando relatório...")

    def _toggle_dark_mode(self, e: ft.ControlEvent):
        self.page.theme_mode = ft.ThemeMode.DARK if e.control.value else ft.ThemeMode.LIGHT
        self._build_theme()  # reconstroi tokens
        # força recolorir header chip
        self.header_status_chip.bgcolor = self.t["chip_ok_bg"]
        self.header_status_chip.content.controls[1].color = self.t["chip_text_ok"]
        self.page.update()

    def _toggle_auto_start(self, e):
        self.toast(f"Auto-início: {'Ativado' if e.control.value else 'Desativado'}")

    def _backup_system(self, e): self.toast("💾 Iniciando backup...")
    def _update_system(self, e): self.toast("🔄 Verificando atualizações...")
    def _view_system_logs(self, e): self.toast("📋 Abrindo logs do sistema...")

def main():
    app = WindowsDashboard()
    ft.app(target=app.main, view=ft.FLET_APP)

if __name__ == "__main__":
    main()