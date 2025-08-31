"""
Sistema de Formatação de Mensagens para Ofertas
Formata ofertas com templates profissionais por plataforma
"""

import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from src.core.models import Offer


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
        # Tentar identificar pelo store
        if hasattr(offer, 'store') and offer.store:
            store = offer.store.lower()
            if 'amazon' in store:
                return 'amazon'
            elif 'mercadolivre' in store:
                return 'mercadolivre'
            elif 'shopee' in store:
                return 'shopee'
            elif 'magazine' in store:
                return 'magazineluiza'
            elif 'aliexpress' in store:
                return 'aliexpress'
            elif 'awin' in store:
                return 'awin'
            elif 'rakuten' in store:
                return 'rakuten'
        
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
            discount_percentage = ((original_price - current_price) / original_price) * 100
        
        # Cupom
        coupon = getattr(offer, 'coupon', '')
        
        # Badge de menor preço
        is_lowest_price = getattr(offer, 'is_lowest_price', False)
        
        # URL de afiliado
        affiliate_url = getattr(offer, 'affiliate_url', getattr(offer, 'url', ''))
        
        return {
            'title': getattr(offer, 'title', 'Produto'),
            'current_price': current_price,
            'original_price': original_price,
            'discount_percentage': round(discount_percentage, 0) if discount_percentage else 0,
            'store': getattr(offer, 'store', 'Loja'),
            'category': getattr(offer, 'category', 'Geral'),
            'coupon': coupon,
            'is_lowest_price': is_lowest_price,
            'affiliate_url': affiliate_url
        }
    
    def _build_message(self, template: MessageTemplate, data: Dict[str, Any]) -> str:
        """Constrói mensagem usando template e dados"""
        try:
            # Aplicar formatação
            title = template.title_format.format(**data)
            price = template.price_format.format(**data)
            store = template.store_format.format(**data)
            category = template.category_format.format(**data)
            
            # Desconto (só mostrar se houver)
            discount = ""
            if data.get('discount_percentage', 0) > 0:
                discount = template.discount_format.format(**data)
            
            # Cupom (só mostrar se houver)
            coupon = ""
            if data.get('coupon'):
                coupon = template.coupon_format.format(**data)
            
            # Badge (só mostrar se for menor preço)
            badge = ""
            if data.get('is_lowest_price'):
                badge = template.badge_format.format(**data)
            
            # Footer
            footer = template.footer_format.format(**data)
            
            # Montar mensagem
            message_parts = [
                f"{template.emoji_prefix} {title}",
                price
            ]
            
            if discount:
                message_parts.append(discount)
            
            if store:
                message_parts.append(store)
            
            if category:
                message_parts.append(category)
            
            if coupon:
                message_parts.append(coupon)
            
            if badge:
                message_parts.append(badge)
            
            message_parts.append(footer)
            
            return "\n".join(message_parts)
            
        except Exception as e:
            # Fallback para mensagem simples
            return f"🛒 {data.get('title', 'Produto')}\n💰 R$ {data.get('current_price', 0):.2f}\n🔗 [Ver oferta]({data.get('affiliate_url', '')})"
    
    def _format_simple_message(self, offer: Offer) -> str:
        """Formatação simples de fallback"""
        try:
            title = getattr(offer, 'title', 'Produto')
            price = getattr(offer, 'price', 0)
            url = getattr(offer, 'affiliate_url', getattr(offer, 'url', ''))
            
            return f"🛒 **{title}**\n💰 **R$ {price:.2f}**\n🔗 [Ver oferta]({url})"
            
        except Exception:
            return "🛒 Oferta disponível\n🔗 Ver detalhes no link"
    
    def format_batch_offers(self, offers: List[Offer], platform: Optional[str] = None) -> List[str]:
        """
        Formata múltiplas ofertas
        
        Args:
            offers: Lista de ofertas
            platform: Plataforma específica (opcional)
            
        Returns:
            Lista de mensagens formatadas
        """
        messages = []
        for offer in offers:
            try:
                message = self.format_offer_message(offer, platform)
                messages.append(message)
            except Exception as e:
                # Log do erro e continuar com próxima oferta
                print(f"Erro ao formatar oferta {offer.title}: {e}")
                continue
        
        return messages
    
    def get_platform_templates(self) -> List[str]:
        """Retorna lista de plataformas com templates disponíveis"""
        return list(self.templates.keys())
    
    def add_custom_template(self, platform: str, template: MessageTemplate) -> None:
        """Adiciona template personalizado para uma plataforma"""
        self.templates[platform.lower()] = template
    
    def remove_template(self, platform: str) -> None:
        """Remove template de uma plataforma"""
        if platform.lower() in self.templates:
            del self.templates[platform.lower()]


# Instância global
message_formatter = MessageFormatter()

