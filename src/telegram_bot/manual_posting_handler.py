"""
Sistema de Postagem Manual para Mercado Livre e Outras Lojas
Recebe links de afiliado via Telegram e posta no canal automaticamente
"""

import asyncio
import logging
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from src.core.models import Offer
from src.core.affiliate_validator import AffiliateValidator
from src.posting.message_formatter import MessageFormatter
from src.posting.posting_manager import PostingManager
from src.core.price_history import PriceHistoryTracker
from src.utils.image_downloader import ProductImageDownloader

logger = logging.getLogger(__name__)


@dataclass
class ManualPostRequest:
    """Solicitação de postagem manual"""
    
    user_id: int
    username: str
    affiliate_url: str
    platform: str
    category: str
    title: str
    price: float
    original_price: Optional[float] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class ManualPostingHandler:
    """Handler para postagens manuais via Telegram"""
    
    def __init__(self):
        self.validator = AffiliateValidator()
        self.message_formatter = MessageFormatter()
        self.posting_manager = PostingManager()
        self.price_tracker = PriceHistoryTracker()
        self.image_downloader = ProductImageDownloader()
        
        # Usuários autorizados para postagem manual
        self.authorized_users = set()
        
        # Cache de solicitações pendentes
        self.pending_requests: Dict[int, ManualPostRequest] = {}
        
        # Configurações de postagem
        self.posting_config = {
            "mercadolivre": {
                "enabled": True,
                "auto_approve": False,  # Sempre aprovar manualmente
                "require_image": True,
                "categories": ["eletronicos", "informatica", "games", "casa", "moda", "esporte"]
            },
            "amazon": {
                "enabled": True,
                "auto_approve": False,
                "require_image": True,
                "categories": ["eletronicos", "livros", "casa", "moda", "esporte"]
            },
            "shopee": {
                "enabled": True,
                "auto_approve": False,
                "require_image": True,
                "categories": ["eletronicos", "moda", "casa", "beleza", "esporte"]
            },
            "aliexpress": {
                "enabled": True,
                "auto_approve": False,
                "require_image": True,
                "categories": ["eletronicos", "moda", "casa", "beleza", "esporte"]
            }
        }
    
    async def handle_manual_link(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Processa link manual enviado pelo usuário"""
        try:
            user_id = update.effective_user.id
            username = update.effective_user.username or "Usuário"
            message_text = update.message.text
            
            # Verificar se usuário está autorizado
            if not self._is_authorized_user(user_id):
                await self._send_unauthorized_message(update, context)
                return
            
            # Extrair informações do link
            link_info = await self._extract_link_info(message_text)
            if not link_info:
                await self._send_invalid_link_message(update, context)
                return
            
            # Criar solicitação de postagem
            post_request = ManualPostRequest(
                user_id=user_id,
                username=username,
                affiliate_url=link_info["url"],
                platform=link_info["platform"],
                category=link_info["category"],
                title=link_info["title"],
                price=link_info["price"],
                original_price=link_info.get("original_price"),
                description=link_info.get("description"),
                image_url=link_info.get("image_url")
            )
            
            # Salvar solicitação pendente
            self.pending_requests[user_id] = post_request
            
            # Enviar confirmação com opções de edição
            await self._send_confirmation_message(update, context, post_request)
            
        except Exception as e:
            logger.error(f"Erro ao processar link manual: {e}")
            await self._send_error_message(update, context)
    
    async def _extract_link_info(self, message_text: str) -> Optional[Dict]:
        """Extrai informações do link enviado"""
        try:
            # Padrões de links suportados
            patterns = {
                "mercadolivre": r"https?://(?:www\.)?mercadolivre\.com(?:\.br)?/sec/[A-Za-z0-9]+",
                "amazon": r"https?://(?:www\.)?amazon\.com\.br/dp/[A-Z0-9]+",
                "shopee": r"https?://s\.shopee\.com\.br/[A-Za-z0-9]+",
                "aliexpress": r"https?://s\.click\.aliexpress\.com/e/[A-Za-z0-9_-]+"
            }
            
            # Identificar plataforma
            platform = None
            url = None
            
            for p_name, pattern in patterns.items():
                match = re.search(pattern, message_text)
                if match:
                    platform = p_name
                    url = match.group(0)
                    break
            
            if not platform or not url:
                return None
            
            # Extrair informações básicas (serão complementadas pelo usuário)
            return {
                "url": url,
                "platform": platform,
                "category": "geral",
                "title": "Produto",
                "price": 0.0,
                "original_price": None,
                "description": None,
                "image_url": None
            }
            
        except Exception as e:
            logger.error(f"Erro ao extrair informações do link: {e}")
            return None
    
    async def _send_confirmation_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE, post_request: ManualPostRequest) -> None:
        """Envia mensagem de confirmação com opções de edição"""
        try:
            # Criar teclado inline com opções
            keyboard = [
                [
                    InlineKeyboardButton("✏️ Editar Título", callback_data=f"edit_title_{post_request.user_id}"),
                    InlineKeyboardButton("💰 Editar Preço", callback_data=f"edit_price_{post_request.user_id}")
                ],
                [
                    InlineKeyboardButton("📂 Editar Categoria", callback_data=f"edit_category_{post_request.user_id}"),
                    InlineKeyboardButton("🖼️ Adicionar Imagem", callback_data=f"add_image_{post_request.user_id}")
                ],
                [
                    InlineKeyboardButton("✅ Confirmar e Postar", callback_data=f"confirm_post_{post_request.user_id}"),
                    InlineKeyboardButton("❌ Cancelar", callback_data=f"cancel_post_{post_request.user_id}")
                ]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Mensagem de confirmação
            message = (
                f"🔄 **SOLICITAÇÃO DE POSTAGEM MANUAL**\n\n"
                f"📱 **Plataforma:** {post_request.platform.upper()}\n"
                f"🔗 **Link:** {post_request.affiliate_url}\n"
                f"📝 **Título:** {post_request.title}\n"
                f"💰 **Preço:** R$ {post_request.price:.2f}\n"
                f"📂 **Categoria:** {post_request.category}\n\n"
                f"⚠️ **IMPORTANTE:** Complete as informações antes de postar!\n\n"
                f"Escolha uma opção:"
            )
            
            await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem de confirmação: {e}")
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Processa callbacks dos botões inline"""
        try:
            query = update.callback_query
            await query.answer()
            
            data = query.data
            user_id = int(data.split('_')[-1])
            
            if data.startswith("edit_title"):
                await self._start_title_edit(query, context, user_id)
            elif data.startswith("edit_price"):
                await self._start_price_edit(query, context, user_id)
            elif data.startswith("edit_category"):
                await self._start_category_edit(query, context, user_id)
            elif data.startswith("add_image"):
                await self._start_image_add(query, context, user_id)
            elif data.startswith("confirm_post"):
                await self._confirm_and_post(query, context, user_id)
            elif data.startswith("cancel_post"):
                await self._cancel_post(query, context, user_id)
                
        except Exception as e:
            logger.error(f"Erro ao processar callback: {e}")
    
    async def _start_title_edit(self, query, context, user_id):
        """Inicia edição do título"""
        await query.edit_message_text(
            "✏️ **EDITAR TÍTULO**\n\n"
            "Envie o novo título do produto:",
            parse_mode='Markdown'
        )
        # Marcar usuário como editando título
        context.user_data['editing_title'] = True
    
    async def _start_price_edit(self, query, context, user_id):
        """Inicia edição do preço"""
        await query.edit_message_text(
            "💰 **EDITAR PREÇO**\n\n"
            "Envie o preço atual do produto (apenas números):\n"
            "Exemplo: 1299.99",
            parse_mode='Markdown'
        )
        context.user_data['editing_price'] = True
    
    async def _start_category_edit(self, query, context, user_id):
        """Inicia edição da categoria"""
        if user_id not in self.pending_requests:
            await query.edit_message_text("❌ Solicitação não encontrada")
            return
        
        platform = self.pending_requests[user_id].platform
        categories = self.posting_config[platform]["categories"]
        
        # Criar teclado com categorias disponíveis
        keyboard = []
        for i in range(0, len(categories), 2):
            row = []
            for j in range(2):
                if i + j < len(categories):
                    cat = categories[i + j]
                    row.append(InlineKeyboardButton(
                        cat.title(), 
                        callback_data=f"set_category_{user_id}_{cat}"
                    ))
            keyboard.append(row)
        
        keyboard.append([InlineKeyboardButton("❌ Cancelar", callback_data=f"cancel_edit_{user_id}")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "📂 **SELECIONAR CATEGORIA**\n\n"
            "Escolha a categoria do produto:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def _start_image_add(self, query, context, user_id):
        """Inicia adição de imagem"""
        await query.edit_message_text(
            "🖼️ **ADICIONAR IMAGEM**\n\n"
            "Envie a imagem do produto:",
            parse_mode='Markdown'
        )
        context.user_data['adding_image'] = True
    
    async def _confirm_and_post(self, query, context, user_id):
        """Confirma e executa a postagem"""
        try:
            if user_id not in self.pending_requests:
                await query.edit_message_text("❌ Solicitação não encontrada")
                return
            
            post_request = self.pending_requests[user_id]
            
            # Validar se todas as informações estão completas
            if not self._validate_post_request(post_request):
                await query.edit_message_text(
                    "❌ **INFORMAÇÕES INCOMPLETAS**\n\n"
                    "Complete todas as informações antes de postar:\n"
                    f"• Título: {post_request.title}\n"
                    f"• Preço: R$ {post_request.price:.2f}\n"
                    f"• Categoria: {post_request.category}\n"
                    f"• Imagem: {'✅' if post_request.image_url else '❌'}",
                    parse_mode='Markdown'
                )
                return
            
            # Executar postagem
            await self._execute_manual_post(post_request)
            
            # Limpar solicitação pendente
            del self.pending_requests[user_id]
            
            await query.edit_message_text(
                "✅ **POSTAGEM REALIZADA COM SUCESSO!**\n\n"
                f"📱 Produto postado no canal\n"
                f"🔗 Link: {post_request.affiliate_url}\n"
                f"💰 Preço: R$ {post_request.price:.2f}",
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"Erro ao confirmar postagem: {e}")
            await query.edit_message_text("❌ Erro ao realizar postagem")
    
    def _validate_post_request(self, post_request: ManualPostRequest) -> bool:
        """Valida se a solicitação está completa"""
        return (
            post_request.title != "Produto" and
            post_request.price > 0 and
            post_request.category != "geral" and
            post_request.image_url is not None
        )
    
    async def _execute_manual_post(self, post_request: ManualPostRequest) -> None:
        """Executa a postagem manual"""
        try:
            # Criar objeto Offer
            offer = Offer(
                title=post_request.title,
                price=post_request.price,
                url=post_request.affiliate_url,
                store=post_request.platform,
                original_price=post_request.original_price,
                category=post_request.category,
                description=post_request.description,
                affiliate_url=post_request.affiliate_url,
                image_url=post_request.image_url
            )
            
            # Verificar preços históricos
            price_analysis = await self.price_tracker.analyze_price(
                post_request.title, 
                post_request.price,
                post_request.platform
            )
            
            # Formatar mensagem personalizada
            message = self.message_formatter.format_offer_message(
                offer, 
                platform=post_request.platform
            )
            
            # Adicionar informações de preço histórico se disponível
            if price_analysis:
                message += self._format_price_analysis(price_analysis)
            
            # Postar no canal
            await self.posting_manager.post_offer_manual(
                offer, 
                message, 
                post_request.image_url
            )
            
            logger.info(f"Postagem manual realizada: {post_request.title}")
            
        except Exception as e:
            logger.error(f"Erro ao executar postagem manual: {e}")
            raise
    
    def _format_price_analysis(self, price_analysis: Dict) -> str:
        """Formata análise de preços para a mensagem"""
        message_parts = []
        
        if price_analysis.get("is_lowest_3m"):
            message_parts.append("🔥 **MENOR PREÇO EM 3 MESES!**")
        
        if price_analysis.get("is_lowest_6m"):
            message_parts.append("🔥 **MENOR PREÇO EM 6 MESES!**")
        
        if price_analysis.get("is_lowest_ever"):
            message_parts.append("🔥 **MENOR PREÇO HISTÓRICO!**")
        
        if price_analysis.get("discount_percentage", 0) > 20:
            message_parts.append(f"🎯 **DESCONTO IMPERDÍVEL: {price_analysis['discount_percentage']:.0f}% OFF**")
        
        if message_parts:
            return "\n" + "\n".join(message_parts)
        
        return ""
    
    def _is_authorized_user(self, user_id: int) -> bool:
        """Verifica se usuário está autorizado"""
        return user_id in self.authorized_users
    
    async def _send_unauthorized_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Envia mensagem de usuário não autorizado"""
        await update.message.reply_text(
            "❌ **ACESSO NEGADO**\n\n"
            "Você não está autorizado a fazer postagens manuais.\n"
            "Entre em contato com o administrador.",
            parse_mode='Markdown'
        )
    
    async def _send_invalid_link_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Envia mensagem de link inválido"""
        await update.message.reply_text(
            "❌ **LINK INVÁLIDO**\n\n"
            "O link enviado não é válido ou não é suportado.\n\n"
            "**Plataformas suportadas:**\n"
            "• Mercado Livre (shortlink)\n"
            "• Amazon (produto)\n"
            "• Shopee (shortlink)\n"
            "• AliExpress (shortlink)",
            parse_mode='Markdown'
        )
    
    async def _send_error_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Envia mensagem de erro genérico"""
        await update.message.reply_text(
            "❌ **ERRO INTERNO**\n\n"
            "Ocorreu um erro ao processar sua solicitação.\n"
            "Tente novamente mais tarde.",
            parse_mode='Markdown'
        )
    
    def add_authorized_user(self, user_id: int) -> None:
        """Adiciona usuário autorizado"""
        self.authorized_users.add(user_id)
        logger.info(f"Usuário {user_id} autorizado para postagem manual")
    
    def remove_authorized_user(self, user_id: int) -> None:
        """Remove usuário autorizado"""
        self.authorized_users.discard(user_id)
        logger.info(f"Usuário {user_id} removido da lista de autorizados")


# Instância global
manual_posting_handler = ManualPostingHandler()
