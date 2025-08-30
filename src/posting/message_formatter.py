"""
Sistema de Formatação de Mensagens para Ofertas
Formata ofertas com templates profissionais por plataforma
"""

import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from core.models import Offer


@dataclass
class MessageTemplate:
    """Template de mensagem para uma plataforma"""
    
    platform: str
    emoji_prefix: str
    title_format: str
    price_format: str
    discount_format: str
    store_format: str
    category_format: str
    coupon_format: str
    badge_format: str
    footer_format: str


class MessageFormatter:
    """Formatador de mensagens para ofertas"""
    
    def __init__(self):
        # Templates por plataforma
        self.templates = {
            "amazon": MessageTemplate(
                platform="Amazon",
                emoji_prefix="🛒",
                title_format="**{title}**",
                price_format="💰 **R$ {current_price:.2f}**",
                discount_format="🎯 **{discount_percentage}% OFF**",
                store_format="🏪 {store}",
                category_format="📂 {category}",
                coupon_format="🎫 Cupom: **{coupon}**" if "{coupon}" else "",
                badge_format="🔥 **Menor preço em 90 dias!**" if "{is_lowest_price}" else "",
                footer_format="🔗 [Ver oferta]({affiliate_url})"
            ),
            "mercadolivre": MessageTemplate(
                platform="Mercado Livre",
                emoji_prefix="🛍️",
                title_format="**{title}**",
                price_format="💰 **R$ {current_price:.2f}**",
                discount_format="🎯 **{discount_percentage}% OFF**",
                store_format="🏪 {store}",
                category_format="📂 {category}",
                coupon_format="🎫 Cupom: **{coupon}**" if "{coupon}" else "",
                badge_format="🔥 **Menor preço em 90 dias!**" if "{is_lowest_price}" else "",
                footer_format="🔗 [Ver oferta]({affiliate_url})"
            ),
            "shopee": MessageTemplate(
                platform="Shopee",
                emoji_prefix="🛒",
                title_format="**{title}**",
                price_format="💰 **R$ {current_price:.2f}**",
                discount_format="🎯 **{discount_percentage}% OFF**",
                store_format="🏪 {store}",
                category_format="📂 {category}",
                coupon_format="🎫 Cupom: **{coupon}**" if "{coupon}" else "",
                badge_format="🔥 **Menor preço em 90 dias!**" if "{is_lowest_price}" else "",
                footer_format="🔗 [Ver oferta]({affiliate_url})"
            ),
            "magazineluiza": MessageTemplate(
                platform="Magazine Luiza",
                emoji_prefix="🛍️",
                title_format="**{title}**",
                price_format="💰 **R$ {current_price:.2f}**",
                discount_format="🎯 **{discount_percentage}% OFF**",
                store_format="🏪 {store}",
                category_format="📂 {category}",
                coupon_format="🎫 Cupom: **{coupon}**" if "{coupon}" else "",
                badge_format="🔥 **Menor preço em 90 dias!**" if "{is_lowest_price}" else "",
                footer_format="🔗 [Ver oferta]({affiliate_url})"
            ),
            "aliexpress": MessageTemplate(
                platform="AliExpress",
                emoji_prefix="🌏",
                title_format="**{title}**",
                price_format="💰 **R$ {current_price:.2f}**",
                discount_format="🎯 **{discount_percentage}% OFF**",
                store_format="🏪 {store}",
                category_format="📂 {category}",
                coupon_format="🎫 Cupom: **{coupon}**" if "{coupon}" else "",
                badge_format="🔥 **Menor preço em 90 dias!**" if "{is_lowest_price}" else "",
                footer_format="🔗 [Ver oferta]({affiliate_url})"
            ),
            "awin": MessageTemplate(
                platform="Awin",
                emoji_prefix="🔄",
                title_format="**{title}**",
                price_format="💰 **R$ {current_price:.2f}**",
                discount_format="🎯 **{discount_percentage}% OFF**",
                store_format="🏪 {store}",
                category_format="📂 {category}",
                coupon_format="🎫 Cupom: **{coupon}**" if "{coupon}" else "",
                badge_format="🔥 **Menor preço em 90 dias!**" if "{is_lowest_price}" else "",
                footer_format="🔗 [Ver oferta]({affiliate_url})"
            ),
            "rakuten": MessageTemplate(
                platform="Rakuten",
                emoji_prefix="🎁",
                title_format="**{title}**",
                price_format="💰 **R$ {current_price:.2f}**",
                discount_format="🎯 **{discount_percentage}% OFF**",
                store_format="🏪 {store}",
                category_format="📂 {category}",
                coupon_format="🎫 Cupom: **{coupon}**" if "{coupon}" else "",
                badge_format="🔥 **Menor preço em 90 dias!**" if "{is_lowest_price}" else "",
                footer_format="🔗 [Ver oferta]({affiliate_url})"
            )
        }
        
        # Template padrão para plataformas não reconhecidas
        self.default_template = MessageTemplate(
            platform="Loja",
            emoji_prefix="🛒",
            title_format="**{title}**",
            price_format="💰 **R$ {current_price:.2f}**",
            discount_format="🎯 **{discount_percentage}% OFF**",
            store_format="🏪 {store}",
            category_format="📂 {category}",
            coupon_format="🎫 Cupom: **{coupon}**" if "{coupon}" else "",
            badge_format="🔥 **Menor preço em 90 dias!**" if "{is_lowest_price}" else "",
            footer_format="🔗 [Ver oferta]({affiliate_url})"
        )
    
    def format_offer_message(self, offer: Offer, platform: Optional[str] = None) -> str:
        """
        Formata uma oferta em mensagem completa
        
        Args:
            offer: Oferta a ser formatada
            platform: Plataforma específica (opcional)
            
        Returns:
            Mensagem formatada
        """
        try:
            # Identificar plataforma se não fornecida
            if not platform:
                platform = self._identify_platform(offer)
            
            # Obter template
            template = self.templates.get(platform, self.default_template)
            
            # Preparar dados para formatação
            message_data = self._prepare_message_data(offer, template)
            
            # Construir mensagem
            message = self._build_message(template, message_data)
            
            return message
            
        except Exception as e:
            # Fallback para mensagem simples
            return self._format_simple_message(offer)
    
    def _identify_platform(self, offer: Offer) -> str:
        """Identifica a plataforma baseada na oferta"""
        if hasattr(offer, 'platform') and offer.platform:
            return offer.platform.lower()
        
        # Tentar identificar pelo URL
        if hasattr(offer, 'url') and offer.url:
            url = offer.url.lower()
            if 'amazon' in url or 'amzn.to' in url:
                return 'amazon'
            elif 'mercadolivre' in url:
                return 'mercadolivre'
            elif 'shopee' in url:
                return 'shopee'
            elif 'magazine' in url:
                return 'magazineluiza'
            elif 'aliexpress' in url:
                return 'aliexpress'
            elif 'awin' in url or 'tidd.ly' in url:
                return 'awin'
            elif 'rakuten' in url:
                return 'rakuten'
        
        return 'default'
    
    def _prepare_message_data(self, offer: Offer, template: MessageTemplate) -> Dict[str, Any]:
        """Prepara dados para formatação da mensagem"""
        # Preços
        current_price = getattr(offer, 'price', getattr(offer, 'current_price', 0))
        original_price = getattr(offer, 'original_price', 0)
        
        # Calcular desconto se não fornecido
        discount_percentage = getattr(offer, 'discount_percentage', 0)
        if not discount_percentage and original_price and current_price:
            discount_percentage = int(((original_price - current_price) / original_price) * 100)
        
        # Outros campos
        title = getattr(offer, 'title', 'Produto')
        store = getattr(offer, 'store', 'Loja')
        category = getattr(offer, 'category', 'Categoria')
        coupon = getattr(offer, 'coupon', '')
        affiliate_url = getattr(offer, 'url', getattr(offer, 'affiliate_url', ''))
        
        # Verificar se é menor preço (simulado)
        is_lowest_price = getattr(offer, 'is_lowest_price', False)
        
        return {
            'title': title,
            'current_price': current_price,
            'original_price': original_price,
            'discount_percentage': discount_percentage,
            'store': store,
            'category': category,
            'coupon': coupon,
            'affiliate_url': affiliate_url,
            'is_lowest_price': is_lowest_price
        }
    
    def _build_message(self, template: MessageTemplate, data: Dict[str, Any]) -> str:
        """Constrói a mensagem usando o template"""
        message_parts = []
        
        # Emoji e título da plataforma
        message_parts.append(f"{template.emoji_prefix} **{template.platform}**")
        message_parts.append("")
        
        # Título do produto
        title = template.title_format.format(**data)
        message_parts.append(title)
        message_parts.append("")
        
        # Preço atual
        if data['current_price']:
            price = template.price_format.format(**data)
            message_parts.append(price)
        
        # Preço original (se diferente)
        if data['original_price'] and data['original_price'] > data['current_price']:
            original = f"~~R$ {data['original_price']:.2f}~~"
            message_parts.append(original)
        
        # Desconto
        if data['discount_percentage']:
            discount = template.discount_format.format(**data)
            message_parts.append(discount)
        
        # Cupom
        if data['coupon']:
            coupon = template.coupon_format.format(**data)
            message_parts.append(coupon)
        
        # Badge de menor preço
        if data['is_lowest_price']:
            badge = template.badge_format.format(**data)
            message_parts.append(badge)
        
        message_parts.append("")
        
        # Informações da loja
        store_info = template.store_format.format(**data)
        message_parts.append(store_info)
        
        # Categoria
        if data['category']:
            category_info = template.category_format.format(**data)
            message_parts.append(category_info)
        
        message_parts.append("")
        
        # Link da oferta
        if data['affiliate_url']:
            footer = template.footer_format.format(**data)
            message_parts.append(footer)
        
        return "\n".join(message_parts)
    
    def _format_simple_message(self, offer: Offer) -> str:
        """Formatação simples de fallback"""
        title = getattr(offer, 'title', 'Produto')
        price = getattr(offer, 'price', getattr(offer, 'current_price', 0))
        store = getattr(offer, 'store', 'Loja')
        url = getattr(offer, 'url', getattr(offer, 'affiliate_url', ''))
        
        message = f"🛒 **{title}**\n"
        message += f"💰 **R$ {price:.2f}**\n"
        message += f"🏪 {store}\n"
        
        if url:
            message += f"🔗 [Ver oferta]({url})"
        
        return message
    
    def validate_message(self, message: str) -> Dict[str, Any]:
        """
        Valida uma mensagem formatada
        
        Args:
            message: Mensagem a ser validada
            
        Returns:
            Resultado da validação
        """
        validation_result = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'stats': {}
        }
        
        try:
            # Verificar campos obrigatórios
            required_fields = ['**', '💰', '🔗']
            for field in required_fields:
                if field not in message:
                    validation_result['errors'].append(f"Campo obrigatório ausente: {field}")
                    validation_result['is_valid'] = False
            
            # Verificar comprimento
            if len(message) < 50:
                validation_result['warnings'].append("Mensagem muito curta")
            
            if len(message) > 2000:
                validation_result['errors'].append("Mensagem muito longa")
                validation_result['is_valid'] = False
            
            # Estatísticas
            validation_result['stats'] = {
                'length': len(message),
                'lines': len(message.split('\n')),
                'emojis': len(re.findall(r'[🛒🛍️🌏🔄🎁💰🎯🏪📂🎫🔥🔗]', message))
            }
            
        except Exception as e:
            validation_result['errors'].append(f"Erro na validação: {str(e)}")
            validation_result['is_valid'] = False
        
        return validation_result
    
    def format_batch_offers(self, offers: List[Offer]) -> List[str]:
        """
        Formata um lote de ofertas
        
        Args:
            offers: Lista de ofertas
            
        Returns:
            Lista de mensagens formatadas
        """
        messages = []
        
        for offer in offers:
            try:
                message = self.format_offer_message(offer)
                messages.append(message)
            except Exception as e:
                # Log do erro e mensagem de fallback
                fallback_message = f"❌ Erro ao formatar oferta: {str(e)}"
                messages.append(fallback_message)
        
        return messages


# Instância global para uso em outros módulos
message_formatter = MessageFormatter()

