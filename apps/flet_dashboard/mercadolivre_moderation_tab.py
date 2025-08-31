#!/usr/bin/env python3
"""
Interface de Moderação Manual do Mercado Livre no Dashboard
Permite ao usuário converter links e gerenciar ofertas
"""

import flet as ft
import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

from src.app.queue.mercadolivre_moderation import (
    MercadoLivreModerationSystem, 
    ModerationStatus,
    get_mercadolivre_moderation_system
)
from src.scrapers.lojas.mercadolivre import get_mercadolivre_scraper
from .ui_components import MetricCard, DataTable, AlertBanner


class MercadoLivreModerationTab:
    """Tab de moderação manual do Mercado Livre"""
    
    def __init__(self):
        self.moderation_system = get_mercadolivre_moderation_system()
        self.logger = logging.getLogger("dashboard.mercadolivre_moderation")
        
        # Estado da interface
        self.pending_tasks: List[Any] = []
        self.ready_tasks: List[Any] = []
        self.selected_task_id: Optional[str] = None
        
        # Callbacks
        self.on_conversion_submitted = None
        self.on_ready_for_posting = None

    def build(self) -> ft.Container:
        """Constrói a interface de moderação"""
        try:
            # Atualizar dados
            self._refresh_data()
            
            # Interface principal
            content = ft.Column([
                self._build_header(),
                ft.Divider(height=20),
                self._build_controls(),
                ft.Divider(height=20),
                self._build_tabs()
            ], spacing=20)
            
            return ft.Container(content=content, padding=20)
            
        except Exception as e:
            self.logger.error(f"Erro ao construir interface: {e}")
            return ft.Container(
                content=ft.Text(f"Erro ao carregar interface: {e}", color=ft.Colors.RED_400),
                padding=20
            )

    def _build_header(self) -> ft.Container:
        """Header com estatísticas e título"""
        stats = self.moderation_system.get_stats()
        
        stats_cards = ft.Row([
            MetricCard(
                "Pendentes",
                str(stats["pending_conversion"]),
                "Aguardando conversão",
                ft.Colors.ORANGE_400,
                stats["pending_conversion"] > 10
            ).build(),
            
            MetricCard(
                "Prontas",
                str(stats["ready_for_posting"]),
                "Para postagem",
                ft.Colors.GREEN_400,
                stats["ready_for_posting"] == 0
            ).build(),
            
            MetricCard(
                "Total",
                str(stats["total_tasks"]),
                "Tarefas ativas",
                ft.Colors.BLUE_400
            ).build(),
            
            MetricCard(
                "Atrasadas",
                str(stats["overdue_tasks"]),
                "Mais de 24h",
                ft.Colors.RED_400,
                stats["overdue_tasks"] > 0
            ).build()
        ], alignment=ft.MainAxisAlignment.SPACE_EVENLY)
        
        return ft.Container(
            content=ft.Column([
                ft.Text("🛒 Moderação Manual - Mercado Livre", size=24, weight=ft.FontWeight.BOLD),
                ft.Text("Converta links para afiliados e gerencie ofertas", size=14, color=ft.Colors.GREY_400),
                ft.Divider(height=20),
                stats_cards
            ]),
            padding=20,
            bgcolor=ft.Colors.BLUE_900,
            border_radius=12
        )

    def _build_controls(self) -> ft.Container:
        """Controles para scraping e ações em lote"""
        return ft.Container(
            content=ft.Column([
                ft.Text("🎮 Controles", size=18, weight=ft.FontWeight.BOLD),
                ft.Row([
                    ft.ElevatedButton(
                        "🔍 Executar Scraping",
                        on_click=self._run_scraping,
                        bgcolor=ft.Colors.BLUE_600,
                        color=ft.Colors.WHITE
                    ),
                    ft.ElevatedButton(
                        "🔄 Atualizar Dados",
                        on_click=self._refresh_data,
                        bgcolor=ft.Colors.GREEN_600,
                        color=ft.Colors.WHITE
                    ),
                    ft.ElevatedButton(
                        "📤 Exportar Prontas",
                        on_click=self._export_ready_offers,
                        bgcolor=ft.Colors.PURPLE_600,
                        color=ft.Colors.WHITE
                    )
                ], spacing=10)
            ], spacing=15),
            padding=20,
            bgcolor=ft.Colors.BLUE_800,
            border_radius=12
        )

    def _build_tabs(self) -> ft.Tabs:
        """Tabs para diferentes visualizações"""
        return ft.Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                ft.Tab(
                    text="⏳ Pendentes de Conversão",
                    content=self._build_pending_tab()
                ),
                ft.Tab(
                    text="✅ Prontas para Postagem",
                    content=self._build_ready_tab()
                ),
                ft.Tab(
                    text="📊 Histórico",
                    content=self._build_history_tab()
                )
            ],
            expand=True
        )

    def _build_pending_tab(self) -> ft.Container:
        """Tab de tarefas pendentes de conversão"""
        if not self.pending_tasks:
            content = ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN_400, size=48),
                    ft.Text("✅ Nenhuma tarefa pendente!", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_400),
                    ft.Text("Execute o scraping para encontrar novas ofertas", size=14, color=ft.Colors.GREY_400)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=40,
                bgcolor=ft.Colors.GREEN_900,
                border_radius=12,
                alignment=ft.alignment.center
            )
        else:
            # Lista de tarefas pendentes
            task_items = []
            for task in self.pending_tasks:
                task_card = self._build_task_card(task, show_conversion=True)
                task_items.append(task_card)
            
            content = ft.Column([
                ft.Text(f"📋 {len(self.pending_tasks)} ofertas aguardando conversão", size=16, weight=ft.FontWeight.BOLD),
                ft.Divider(height=10),
                *task_items
            ], spacing=10)
        
        return ft.Container(content=content, padding=20)

    def _build_ready_tab(self) -> ft.Container:
        """Tab de tarefas prontas para postagem"""
        if not self.ready_tasks:
            content = ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.INFO, color=ft.Colors.BLUE_400, size=48),
                    ft.Text("ℹ️ Nenhuma oferta pronta", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_400),
                    ft.Text("Converta links pendentes para ver ofertas prontas", size=14, color=ft.Colors.GREY_400)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=40,
                bgcolor=ft.Colors.BLUE_900,
                border_radius=12,
                alignment=ft.alignment.center
            )
        else:
            # Lista de tarefas prontas
            task_items = []
            for task in self.ready_tasks:
                task_card = self._build_task_card(task, show_conversion=False)
                task_items.append(task_card)
            
            content = ft.Column([
                ft.Text(f"🚀 {len(self.ready_tasks)} ofertas prontas para postagem", size=16, weight=ft.FontWeight.BOLD),
                ft.Divider(height=10),
                *task_items
            ], spacing=10)
        
        return ft.Container(content=content, padding=20)

    def _build_history_tab(self) -> ft.Container:
        """Tab de histórico de tarefas"""
        all_tasks = list(self.moderation_system.moderation_tasks.values())
        
        if not all_tasks:
            content = ft.Container(
                content=ft.Text("Nenhuma tarefa encontrada", size=16, color=ft.Colors.GREY_400),
                alignment=ft.alignment.center,
                height=100
            )
        else:
            # Tabela de histórico
            history_data = []
            for task in all_tasks[:50]:  # Limitar a 50
                history_data.append({
                    "id": task.id[:8],
                    "title": task.offer.title[:50] + "..." if len(task.offer.title) > 50 else task.offer.title,
                    "status": task.status.value,
                    "created": task.created_at.strftime("%d/%m %H:%M"),
                    "updated": task.updated_at.strftime("%d/%m %H:%M")
                })
            
            content = DataTable(
                "Histórico de Tarefas",
                history_data,
                [
                    {"key": "id", "label": "ID"},
                    {"key": "title", "label": "Título"},
                    {"key": "status", "label": "Status"},
                    {"key": "created", "label": "Criada"},
                    {"key": "updated", "label": "Atualizada"}
                ]
            ).build()
        
        return ft.Container(content=content, padding=20)

    def _build_task_card(self, task, show_conversion: bool = True) -> ft.Container:
        """Constrói card de uma tarefa"""
        # Informações da oferta
        offer_info = ft.Column([
            ft.Text(task.offer.title, weight=ft.FontWeight.BOLD, size=14),
            ft.Text(f"Preço: R$ {task.offer.price:.2f}", size=12, color=ft.Colors.GREY_400),
            ft.Text(f"URL: {task.original_url[:60]}...", size=10, color=ft.Colors.GREY_500),
            ft.Text(f"Criada: {task.created_at.strftime('%d/%m %H:%M')}", size=10, color=ft.Colors.GREY_500)
        ], spacing=4)
        
        # Status da tarefa
        status_color = {
            ModerationStatus.PENDING_CONVERSION: ft.Colors.ORANGE_400,
            ModerationStatus.CONVERSION_SUBMITTED: ft.Colors.BLUE_400,
            ModerationStatus.CONVERSION_APPROVED: ft.Colors.GREEN_400,
            ModerationStatus.READY_FOR_POSTING: ft.Colors.GREEN_600,
            ModerationStatus.POSTED: ft.Colors.GREY_400
        }.get(task.status, ft.Colors.GREY_400)
        
        status_badge = ft.Container(
            content=ft.Text(
                task.status.value.replace("_", " ").title(),
                size=10,
                color=ft.Colors.WHITE,
                weight=ft.FontWeight.BOLD
            ),
            bgcolor=status_color,
            padding=ft.padding.symmetric(horizontal=8, vertical=2),
            border_radius=4
        )
        
        # Interface de conversão (se aplicável)
        conversion_interface = ft.Container()
        if show_conversion and task.status == ModerationStatus.PENDING_CONVERSION:
            conversion_interface = ft.Column([
                ft.Text("🔗 Converter para Link de Afiliado:", size=12, weight=ft.FontWeight.BOLD),
                ft.TextField(
                    label="URL de Afiliado",
                    hint_text="https://mercadolivre.com/sec/... ou https://mercadolivre.com.br/social/...",
                    width=400,
                    on_change=lambda e, t=task: self._on_affiliate_url_change(t, e.control.value)
                ),
                ft.TextField(
                    label="Observações (opcional)",
                    hint_text="Notas sobre a conversão",
                    width=400,
                    on_change=lambda e, t=task: self._on_notes_change(t, e.control.value)
                ),
                ft.Row([
                    ft.ElevatedButton(
                        "✅ Submeter Conversão",
                        on_click=lambda e, t=task: self._submit_conversion(t),
                        bgcolor=ft.Colors.GREEN_600,
                        color=ft.Colors.WHITE
                    ),
                    ft.ElevatedButton(
                        "❌ Rejeitar",
                        on_click=lambda e, t=task: self._reject_task(t),
                        bgcolor=ft.Colors.RED_600,
                        color=ft.Colors.WHITE
                    )
                ], spacing=10)
            ], spacing=10)
        
        # Card completo
        card_content = ft.Row([
            ft.Icon(ft.Icons.SHOPPING_CART, color=ft.Colors.BLUE_400, size=24),
            ft.Column([
                ft.Row([offer_info, status_badge], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                conversion_interface
            ], expand=True, spacing=10)
        ], spacing=15)
        
        return ft.Container(
            content=card_content,
            padding=15,
            bgcolor=ft.Colors.BLUE_800,
            border_radius=8,
            border=ft.border.all(1, status_color),
            margin=ft.margin.only(bottom=10)
        )

    def _on_affiliate_url_change(self, task, value: str):
        """Callback para mudança na URL de afiliado"""
        task.converted_affiliate_url = value

    def _on_notes_change(self, task, value: str):
        """Callback para mudança nas observações"""
        task.conversion_notes = value

    async def _run_scraping(self, e):
        """Executa o scraping do Mercado Livre"""
        try:
            # Mostrar indicador de carregamento
            e.control.text = "🔍 Executando..."
            e.control.disabled = True
            e.control.update()
            
            # Executar scraping
            scraper = await get_mercadolivre_scraper()
            offers = await scraper.run(max_results=20)
            
            # Criar tarefas de moderação
            for offer in offers:
                self.moderation_system.create_moderation_task(offer)
            
            # Atualizar interface
            self._refresh_data()
            
            # Feedback
            e.control.text = f"✅ {len(offers)} ofertas encontradas"
            e.control.bgcolor = ft.Colors.GREEN_600
            e.control.update()
            
            # Reset após 3 segundos
            await asyncio.sleep(3)
            e.control.text = "🔍 Executar Scraping"
            e.control.bgcolor = ft.Colors.BLUE_600
            e.control.disabled = False
            e.control.update()
            
        except Exception as error:
            self.logger.error(f"Erro no scraping: {error}")
            e.control.text = "❌ Erro no scraping"
            e.control.bgcolor = ft.Colors.RED_600
            e.control.disabled = False
            e.control.update()

    def _refresh_data(self, e=None):
        """Atualiza os dados da interface"""
        try:
            self.pending_tasks = self.moderation_system.get_pending_tasks(limit=50)
            self.ready_tasks = self.moderation_system.get_ready_for_posting_tasks(limit=50)
            
            # Atualizar estatísticas
            if hasattr(self, 'page') and self.page:
                self.page.update()
                
        except Exception as error:
            self.logger.error(f"Erro ao atualizar dados: {error}")

    def _submit_conversion(self, task):
        """Submete uma conversão de link"""
        try:
            if not task.converted_affiliate_url:
                # Mostrar erro
                return
            
            success = self.moderation_system.submit_conversion(
                task.id,
                task.converted_affiliate_url,
                "dashboard_user",
                task.conversion_notes
            )
            
            if success:
                # Atualizar interface
                self._refresh_data()
                
        except Exception as error:
            self.logger.error(f"Erro ao submeter conversão: {error}")

    def _reject_task(self, task):
        """Rejeita uma tarefa"""
        try:
            success = self.moderation_system.reject_conversion(
                task.id,
                "Rejeitada pelo usuário via dashboard"
            )
            
            if success:
                # Atualizar interface
                self._refresh_data()
                
        except Exception as error:
            self.logger.error(f"Erro ao rejeitar tarefa: {error}")

    def _export_ready_offers(self, e):
        """Exporta ofertas prontas para postagem"""
        try:
            offers = self.moderation_system.export_ready_offers()
            
            # Aqui você pode implementar a lógica para enviar para o sistema de postagem
            # Por enquanto, apenas log
            self.logger.info(f"Exportadas {len(offers)} ofertas prontas para postagem")
            
            # Feedback visual
            e.control.text = f"📤 {len(offers)} exportadas"
            e.control.bgcolor = ft.Colors.GREEN_600
            e.control.update()
            
        except Exception as error:
            self.logger.error(f"Erro ao exportar ofertas: {error}")
            e.control.text = "❌ Erro na exportação"
            e.control.bgcolor = ft.Colors.RED_600
            e.control.update()


# Função de conveniência para uso externo
def get_mercadolivre_moderation_tab() -> MercadoLivreModerationTab:
    """Retorna instância da tab de moderação do Mercado Livre"""
    return MercadoLivreModerationTab()
