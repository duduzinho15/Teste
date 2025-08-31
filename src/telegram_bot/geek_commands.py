"""
Comandos específicos para produtos geek/gamer no Bot do Telegram
Implementa filtros e comandos especializados para o público geek
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from src.core.geek_prioritizer import GeekPrioritizer, GeekScore
    from src.core.geek_alerts import GeekAlertManager
    from src.core.models import Offer
    from src.telegram_bot.message_formatter import MessageFormatter
except ImportError:
    # Fallback para quando não conseguir importar
    GeekPrioritizer = None
    GeekAlertManager = None
    Offer = None
    MessageFormatter = None

logger = logging.getLogger(__name__)

class GeekCommands:
    """Comandos específicos para produtos geek/gamer"""
    
    def __init__(self):
        """Inicializa os comandos geek"""
        self.logger = logging.getLogger(__name__)
        
        # Inicializar componentes
        self.prioritizer = None
        self.alert_manager = None
        self.message_formatter = None
        
        if GeekPrioritizer:
            try:
                self.prioritizer = GeekPrioritizer()
                self.logger.info("GeekPrioritizer inicializado para comandos")
            except Exception as e:
                self.logger.error(f"Erro ao inicializar GeekPrioritizer: {e}")
        
        if GeekAlertManager:
            try:
                self.alert_manager = GeekAlertManager()
                self.logger.info("GeekAlertManager inicializado para comandos")
            except Exception as e:
                self.logger.error(f"Erro ao inicializar GeekAlertManager: {e}")
        
        if MessageFormatter:
            try:
                self.message_formatter = MessageFormatter()
                self.logger.info("MessageFormatter inicializado para comandos")
            except Exception as e:
                self.logger.error(f"Erro ao inicializar MessageFormatter: {e}")
        
        # Comandos disponíveis
        self.available_commands = {
            "/geek": "Mostra ofertas geek prioritárias",
            "/gaming": "Filtro específico para gaming",
            "/tech": "Produtos tech premium",
            "/anime": "Produtos anime/otaku",
            "/smart": "Smart home e IoT",
            "/audio": "Audio premium e gaming",
            "/collectibles": "Collectibles e edições limitadas",
            "/geekstats": "Estatísticas geek do sistema",
            "/geekhelp": "Ajuda sobre comandos geek"
        }
    
    async def handle_geek_command(self, command: str, args: List[str] = None, user_id: int = None) -> str:
        """
        Processa comandos geek específicos
        
        Args:
            command: Comando recebido
            args: Argumentos do comando
            user_id: ID do usuário
            
        Returns:
            Resposta formatada para o usuário
        """
        try:
            if not args:
                args = []
            
            command_lower = command.lower()
            
            if command_lower == "/geek":
                return await self._show_geek_offers(args, user_id)
            elif command_lower == "/gaming":
                return await self._show_gaming_offers(args, user_id)
            elif command_lower == "/tech":
                return await self._show_tech_offers(args, user_id)
            elif command_lower == "/anime":
                return await self._show_anime_offers(args, user_id)
            elif command_lower == "/smart":
                return await self._show_smart_home_offers(args, user_id)
            elif command_lower == "/audio":
                return await self._show_audio_offers(args, user_id)
            elif command_lower == "/collectibles":
                return await self._show_collectibles_offers(args, user_id)
            elif command_lower == "/geekstats":
                return await self._show_geek_stats(user_id)
            elif command_lower == "/geekhelp":
                return self._show_geek_help()
            else:
                return "❌ Comando geek não reconhecido. Use /geekhelp para ver comandos disponíveis."
                
        except Exception as e:
            self.logger.error(f"Erro ao processar comando geek {command}: {e}")
            return "❌ Erro interno ao processar comando geek. Tente novamente."
    
    async def _show_geek_offers(self, args: List[str], user_id: int) -> str:
        """Mostra ofertas geek prioritárias"""
        try:
            # Simular ofertas geek (em produção, viria do banco de dados)
            sample_offers = [
                {
                    "title": "PlayStation 5 Console Digital Edition",
                    "price": "R$ 3.499,00",
                    "discount": "15%",
                    "category": "🎮 Gaming",
                    "score": 0.95,
                    "store": "Amazon",
                    "url": "https://amzn.to/example1"
                },
                {
                    "title": "RTX 4070 Ti Gaming X Trio",
                    "price": "R$ 4.299,00",
                    "discount": "20%",
                    "category": "⚡ Tech Geek",
                    "score": 0.92,
                    "store": "Kabum",
                    "url": "https://kabum.com/example1"
                },
                {
                    "title": "Smart TV LG OLED 55\" 4K",
                    "price": "R$ 2.999,00",
                    "discount": "25%",
                    "category": "🏠 Smart Home",
                    "score": 0.88,
                    "store": "Magazine Luiza",
                    "url": "https://magalu.com/example1"
                },
                {
                    "title": "Headphone Sony WH-1000XM5",
                    "price": "R$ 1.899,00",
                    "discount": "18%",
                    "category": "🎧 Audio Premium",
                    "score": 0.85,
                    "store": "Mercado Livre",
                    "url": "https://mercadolivre.com/example1"
                }
            ]
            
            # Filtrar por argumentos se fornecidos
            if args:
                filter_term = " ".join(args).lower()
                sample_offers = [
                    offer for offer in sample_offers 
                    if filter_term in offer["title"].lower() or filter_term in offer["category"].lower()
                ]
            
            if not sample_offers:
                return "🔍 Nenhuma oferta geek encontrada com os filtros especificados."
            
            # Formatar resposta
            response = "🎮 **OFERTAS GEEK PRIORITÁRIAS** 🎮\n\n"
            
            for i, offer in enumerate(sample_offers[:5], 1):  # Máximo 5 ofertas
                response += f"**{i}. {offer['title']}**\n"
                response += f"💰 **Preço:** {offer['price']}\n"
                response += f"🔥 **Desconto:** {offer['discount']}\n"
                response += f"🎯 **Categoria:** {offer['category']}\n"
                response += f"⭐ **Score Geek:** {offer['score']:.2f}\n"
                response += f"🏪 **Loja:** {offer['store']}\n"
                response += f"🔗 **Link:** {offer['url']}\n\n"
            
            response += f"📊 **Total encontrado:** {len(sample_offers)} ofertas\n"
            response += "💡 Use filtros específicos: /gaming, /tech, /anime, etc."
            
            return response
            
        except Exception as e:
            self.logger.error(f"Erro ao mostrar ofertas geek: {e}")
            return "❌ Erro ao buscar ofertas geek. Tente novamente."
    
    async def _show_gaming_offers(self, args: List[str], user_id: int) -> str:
        """Mostra ofertas específicas de gaming"""
        try:
            # Simular ofertas de gaming
            gaming_offers = [
                {
                    "title": "PlayStation 5 Console Disc Edition",
                    "price": "R$ 3.899,00",
                    "discount": "12%",
                    "category": "🎮 Console Gaming",
                    "score": 0.96,
                    "store": "Amazon",
                    "url": "https://amzn.to/gaming1"
                },
                {
                    "title": "Nintendo Switch OLED 64GB",
                    "price": "R$ 2.199,00",
                    "discount": "8%",
                    "category": "🎮 Console Gaming",
                    "score": 0.89,
                    "store": "Kabum",
                    "url": "https://kabum.com/gaming1"
                },
                {
                    "title": "Mouse Gamer Logitech G Pro X Superlight",
                    "price": "R$ 399,00",
                    "discount": "22%",
                    "category": "🎮 Periféricos Gaming",
                    "score": 0.87,
                    "store": "Magazine Luiza",
                    "url": "https://magalu.com/gaming1"
                },
                {
                    "title": "Teclado Mecânico Corsair K100 RGB",
                    "price": "R$ 899,00",
                    "discount": "15%",
                    "category": "🎮 Periféricos Gaming",
                    "score": 0.84,
                    "store": "Mercado Livre",
                    "url": "https://mercadolivre.com/gaming1"
                }
            ]
            
            # Filtrar por argumentos
            if args:
                filter_term = " ".join(args).lower()
                gaming_offers = [
                    offer for offer in gaming_offers 
                    if filter_term in offer["title"].lower() or filter_term in offer["category"].lower()
                ]
            
            if not gaming_offers:
                return "🎮 Nenhuma oferta de gaming encontrada com os filtros especificados."
            
            # Formatar resposta
            response = "🎮 **OFERTAS GAMING EXCLUSIVAS** 🎮\n\n"
            
            for i, offer in enumerate(gaming_offers[:5], 1):
                response += f"**{i}. {offer['title']}**\n"
                response += f"💰 **Preço:** {offer['price']}\n"
                response += f"🔥 **Desconto:** {offer['discount']}\n"
                response += f"🎯 **Categoria:** {offer['category']}\n"
                response += f"⭐ **Score Gaming:** {offer['score']:.2f}\n"
                response += f"🏪 **Loja:** {offer['store']}\n"
                response += f"🔗 **Link:** {offer['url']}\n\n"
            
            response += f"🎮 **Total Gaming:** {len(gaming_offers)} ofertas\n"
            response += "💡 Filtros: console, periférico, jogo, etc."
            
            return response
            
        except Exception as e:
            self.logger.error(f"Erro ao mostrar ofertas gaming: {e}")
            return "❌ Erro ao buscar ofertas gaming. Tente novamente."
    
    async def _show_tech_offers(self, args: List[str], user_id: int) -> str:
        """Mostra ofertas tech premium"""
        try:
            # Simular ofertas tech
            tech_offers = [
                {
                    "title": "MacBook Air M2 13\" 256GB",
                    "price": "R$ 6.999,00",
                    "discount": "10%",
                    "category": "⚡ Tech Premium",
                    "score": 0.93,
                    "store": "Apple Store",
                    "url": "https://apple.com/tech1"
                },
                {
                    "title": "Samsung Galaxy S23 Ultra 256GB",
                    "price": "R$ 4.999,00",
                    "discount": "18%",
                    "category": "📱 Smartphone Premium",
                    "score": 0.91,
                    "store": "Samsung",
                    "url": "https://samsung.com/tech1"
                },
                {
                    "title": "iPad Pro 12.9\" M2 128GB",
                    "price": "R$ 7.499,00",
                    "discount": "12%",
                    "category": "📱 Tablet Premium",
                    "score": 0.89,
                    "store": "Apple Store",
                    "url": "https://apple.com/tech2"
                }
            ]
            
            # Filtrar por argumentos
            if args:
                filter_term = " ".join(args).lower()
                tech_offers = [
                    offer for offer in tech_offers 
                    if filter_term in offer["title"].lower() or filter_term in offer["category"].lower()
                ]
            
            if not tech_offers:
                return "⚡ Nenhuma oferta tech premium encontrada com os filtros especificados."
            
            # Formatar resposta
            response = "⚡ **OFERTAS TECH PREMIUM** ⚡\n\n"
            
            for i, offer in enumerate(tech_offers[:5], 1):
                response += f"**{i}. {offer['title']}**\n"
                response += f"💰 **Preço:** {offer['price']}\n"
                response += f"🔥 **Desconto:** {offer['discount']}\n"
                response += f"🎯 **Categoria:** {offer['category']}\n"
                response += f"⭐ **Score Tech:** {offer['score']:.2f}\n"
                response += f"🏪 **Loja:** {offer['store']}\n"
                response += f"🔗 **Link:** {offer['url']}\n\n"
            
            response += f"⚡ **Total Tech:** {len(tech_offers)} ofertas\n"
            response += "💡 Filtros: smartphone, tablet, notebook, etc."
            
            return response
            
        except Exception as e:
            self.logger.error(f"Erro ao mostrar ofertas tech: {e}")
            return "❌ Erro ao buscar ofertas tech. Tente novamente."
    
    async def _show_anime_offers(self, args: List[str], user_id: int) -> str:
        """Mostra ofertas anime/otaku"""
        try:
            # Simular ofertas anime
            anime_offers = [
                {
                    "title": "Figura Goku Ultra Instinct Mastered",
                    "price": "R$ 299,00",
                    "discount": "25%",
                    "category": "🌸 Anime Figuras",
                    "score": 0.88,
                    "store": "AliExpress",
                    "url": "https://aliexpress.com/anime1"
                },
                {
                    "title": "Manga One Piece Vol. 1-10 Box Set",
                    "price": "R$ 199,00",
                    "discount": "30%",
                    "category": "🌸 Anime Mangás",
                    "score": 0.82,
                    "store": "Amazon",
                    "url": "https://amzn.to/anime1"
                },
                {
                    "title": "Cosplay Naruto Uzumaki Completo",
                    "price": "R$ 159,00",
                    "discount": "20%",
                    "category": "🌸 Anime Cosplay",
                    "score": 0.79,
                    "store": "Shopee",
                    "url": "https://shopee.com/anime1"
                }
            ]
            
            # Filtrar por argumentos
            if args:
                filter_term = " ".join(args).lower()
                anime_offers = [
                    offer for offer in anime_offers 
                    if filter_term in offer["title"].lower() or filter_term in offer["category"].lower()
                ]
            
            if not anime_offers:
                return "🌸 Nenhuma oferta anime/otaku encontrada com os filtros especificados."
            
            # Formatar resposta
            response = "🌸 **OFERTAS ANIME & OTAKU** 🌸\n\n"
            
            for i, offer in enumerate(anime_offers[:5], 1):
                response += f"**{i}. {offer['title']}**\n"
                response += f"💰 **Preço:** {offer['price']}\n"
                response += f"🔥 **Desconto:** {offer['discount']}\n"
                response += f"🎯 **Categoria:** {offer['category']}\n"
                response += f"⭐ **Score Anime:** {offer['score']:.2f}\n"
                response += f"🏪 **Loja:** {offer['store']}\n"
                response += f"🔗 **Link:** {offer['url']}\n\n"
            
            response += f"🌸 **Total Anime:** {len(anime_offers)} ofertas\n"
            response += "💡 Filtros: figura, manga, cosplay, etc."
            
            return response
            
        except Exception as e:
            self.logger.error(f"Erro ao mostrar ofertas anime: {e}")
            return "❌ Erro ao buscar ofertas anime. Tente novamente."
    
    async def _show_smart_home_offers(self, args: List[str], user_id: int) -> str:
        """Mostra ofertas smart home e IoT"""
        try:
            # Simular ofertas smart home
            smart_offers = [
                {
                    "title": "Smart TV Samsung 65\" QLED 4K",
                    "price": "R$ 3.999,00",
                    "discount": "22%",
                    "category": "🏠 Smart Home",
                    "score": 0.91,
                    "store": "Samsung",
                    "url": "https://samsung.com/smart1"
                },
                {
                    "title": "Echo Dot 5ª Geração Alexa",
                    "price": "R$ 199,00",
                    "discount": "35%",
                    "category": "🏠 Smart Home",
                    "score": 0.85,
                    "store": "Amazon",
                    "url": "https://amzn.to/smart1"
                },
                {
                    "title": "Lâmpada Smart Philips Hue RGB",
                    "price": "R$ 89,00",
                    "discount": "28%",
                    "category": "🏠 Smart Home",
                    "score": 0.83,
                    "store": "Magazine Luiza",
                    "url": "https://magalu.com/smart1"
                }
            ]
            
            # Filtrar por argumentos
            if args:
                filter_term = " ".join(args).lower()
                smart_offers = [
                    offer for offer in smart_offers 
                    if filter_term in offer["title"].lower() or filter_term in offer["category"].lower()
                ]
            
            if not smart_offers:
                return "🏠 Nenhuma oferta smart home encontrada com os filtros especificados."
            
            # Formatar resposta
            response = "🏠 **OFERTAS SMART HOME & IOT** 🏠\n\n"
            
            for i, offer in enumerate(smart_offers[:5], 1):
                response += f"**{i}. {offer['title']}**\n"
                response += f"💰 **Preço:** {offer['price']}\n"
                response += f"🔥 **Desconto:** {offer['discount']}\n"
                response += f"🎯 **Categoria:** {offer['category']}\n"
                response += f"⭐ **Score Smart:** {offer['score']:.2f}\n"
                response += f"🏪 **Loja:** {offer['store']}\n"
                response += f"🔗 **Link:** {offer['url']}\n\n"
            
            response += f"🏠 **Total Smart Home:** {len(smart_offers)} ofertas\n"
            response += "💡 Filtros: smart tv, speaker, lâmpada, etc."
            
            return response
            
        except Exception as e:
            self.logger.error(f"Erro ao mostrar ofertas smart home: {e}")
            return "❌ Erro ao buscar ofertas smart home. Tente novamente."
    
    async def _show_audio_offers(self, args: List[str], user_id: int) -> str:
        """Mostra ofertas de audio premium"""
        try:
            # Simular ofertas de audio
            audio_offers = [
                {
                    "title": "Headphone Sony WH-1000XM5",
                    "price": "R$ 1.899,00",
                    "discount": "18%",
                    "category": "🎧 Audio Premium",
                    "score": 0.92,
                    "store": "Sony",
                    "url": "https://sony.com/audio1"
                },
                {
                    "title": "Headset Gaming HyperX Cloud Alpha",
                    "price": "R$ 399,00",
                    "discount": "25%",
                    "category": "🎧 Audio Gaming",
                    "score": 0.87,
                    "store": "Kabum",
                    "url": "https://kabum.com/audio1"
                },
                {
                    "title": "Soundbar Samsung HW-Q800B",
                    "price": "R$ 1.299,00",
                    "discount": "20%",
                    "category": "🎧 Audio Premium",
                    "score": 0.89,
                    "store": "Samsung",
                    "url": "https://samsung.com/audio1"
                }
            ]
            
            # Filtrar por argumentos
            if args:
                filter_term = " ".join(args).lower()
                audio_offers = [
                    offer for offer in audio_offers 
                    if filter_term in offer["title"].lower() or filter_term in offer["category"].lower()
                ]
            
            if not audio_offers:
                return "🎧 Nenhuma oferta de audio encontrada com os filtros especificados."
            
            # Formatar resposta
            response = "🎧 **OFERTAS AUDIO PREMIUM** 🎧\n\n"
            
            for i, offer in enumerate(audio_offers[:5], 1):
                response += f"**{i}. {offer['title']}**\n"
                response += f"💰 **Preço:** {offer['price']}\n"
                response += f"🔥 **Desconto:** {offer['discount']}\n"
                response += f"🎯 **Categoria:** {offer['category']}\n"
                response += f"⭐ **Score Audio:** {offer['score']:.2f}\n"
                response += f"🏪 **Loja:** {offer['store']}\n"
                response += f"🔗 **Link:** {offer['url']}\n\n"
            
            response += f"🎧 **Total Audio:** {len(audio_offers)} ofertas\n"
            response += "💡 Filtros: headphone, headset, soundbar, etc."
            
            return response
            
        except Exception as e:
            self.logger.error(f"Erro ao mostrar ofertas audio: {e}")
            return "❌ Erro ao buscar ofertas audio. Tente novamente."
    
    async def _show_collectibles_offers(self, args: List[str], user_id: int) -> str:
        """Mostra ofertas de collectibles"""
        try:
            # Simular ofertas de collectibles
            collectible_offers = [
                {
                    "title": "Funko Pop! Batman 80th Anniversary",
                    "price": "R$ 89,00",
                    "discount": "15%",
                    "category": "🏆 Collectibles",
                    "score": 0.86,
                    "store": "Amazon",
                    "url": "https://amzn.to/collect1"
                },
                {
                    "title": "Action Figure Marvel Legends Iron Man",
                    "price": "R$ 159,00",
                    "discount": "20%",
                    "category": "🏆 Collectibles",
                    "score": 0.84,
                    "store": "Mercado Livre",
                    "url": "https://mercadolivre.com/collect1"
                },
                {
                    "title": "Vinyl Toy Kidrobot Dunny Series",
                    "price": "R$ 299,00",
                    "discount": "10%",
                    "category": "🏆 Collectibles",
                    "score": 0.81,
                    "store": "Shopee",
                    "url": "https://shopee.com/collect1"
                }
            ]
            
            # Filtrar por argumentos
            if args:
                filter_term = " ".join(args).lower()
                collectible_offers = [
                    offer for offer in collectible_offers 
                    if filter_term in offer["title"].lower() or filter_term in offer["category"].lower()
                ]
            
            if not collectible_offers:
                return "🏆 Nenhuma oferta de collectibles encontrada com os filtros especificados."
            
            # Formatar resposta
            response = "🏆 **OFERTAS COLLECTIBLES** 🏆\n\n"
            
            for i, offer in enumerate(collectible_offers[:5], 1):
                response += f"**{i}. {offer['title']}**\n"
                response += f"💰 **Preço:** {offer['price']}\n"
                response += f"🔥 **Desconto:** {offer['discount']}\n"
                response += f"🎯 **Categoria:** {offer['category']}\n"
                response += f"⭐ **Score Collectible:** {offer['score']:.2f}\n"
                response += f"🏪 **Loja:** {offer['store']}\n"
                response += f"🔗 **Link:** {offer['url']}\n\n"
            
            response += f"🏆 **Total Collectibles:** {len(collectible_offers)} ofertas\n"
            response += "💡 Filtros: funko, action figure, vinyl toy, etc."
            
            return response
            
        except Exception as e:
            self.logger.error(f"Erro ao mostrar ofertas collectibles: {e}")
            return "❌ Erro ao buscar ofertas collectibles. Tente novamente."
    
    async def _show_geek_stats(self, user_id: int) -> str:
        """Mostra estatísticas geek do sistema"""
        try:
            # Simular estatísticas (em produção, viria do banco de dados)
            stats = {
                "total_offers": 1250,
                "geek_offers": 342,
                "gaming_offers": 156,
                "tech_offers": 89,
                "anime_offers": 67,
                "smart_home_offers": 45,
                "audio_offers": 38,
                "collectible_offers": 30,
                "avg_geek_score": 0.73,
                "high_priority_count": 45,
                "critical_alerts": 12,
                "conversion_rate": 0.18
            }
            
            response = "📊 **ESTATÍSTICAS GEEK DO SISTEMA** 📊\n\n"
            
            response += "🎯 **RESUMO GERAL:**\n"
            response += f"• Total de ofertas: **{stats['total_offers']}**\n"
            response += f"• Ofertas geek: **{stats['geek_offers']}** ({stats['geek_offers']/stats['total_offers']*100:.1f}%)\n"
            response += f"• Score médio geek: **{stats['avg_geek_score']:.2f}**\n"
            response += f"• Taxa de conversão: **{stats['conversion_rate']*100:.1f}%**\n\n"
            
            response += "🎮 **DISTRIBUIÇÃO POR CATEGORIA:**\n"
            response += f"• Gaming: **{stats['gaming_offers']}** ofertas\n"
            response += f"• Tech Geek: **{stats['tech_offers']}** ofertas\n"
            response += f"• Anime/Otaku: **{stats['anime_offers']}** ofertas\n"
            response += f"• Smart Home: **{stats['smart_home_offers']}** ofertas\n"
            response += f"• Audio Premium: **{stats['audio_offers']}** ofertas\n"
            response += f"• Collectibles: **{stats['collectible_offers']}** ofertas\n\n"
            
            response += "🚨 **ALERTAS E PRIORIDADES:**\n"
            response += f"• Ofertas alta prioridade: **{stats['high_priority_count']}**\n"
            response += f"• Alertas críticos: **{stats['critical_alerts']}**\n\n"
            
            response += "💡 **COMANDOS DISPONÍVEIS:**\n"
            response += "• /geek - Ofertas geek gerais\n"
            response += "• /gaming - Filtro gaming\n"
            response += "• /tech - Produtos tech premium\n"
            response += "• /anime - Produtos anime/otaku\n"
            response += "• /smart - Smart home e IoT\n"
            response += "• /audio - Audio premium\n"
            response += "• /collectibles - Collectibles\n"
            
            return response
            
        except Exception as e:
            self.logger.error(f"Erro ao mostrar estatísticas geek: {e}")
            return "❌ Erro ao buscar estatísticas geek. Tente novamente."
    
    def _show_geek_help(self) -> str:
        """Mostra ajuda sobre comandos geek"""
        help_text = """
🎮 **AJUDA - COMANDOS GEEK** 🎮

O Garimpeiro Geek possui comandos específicos para filtrar produtos por categoria geek/gamer:

**🎯 COMANDOS PRINCIPAIS:**
• `/geek` - Mostra ofertas geek prioritárias
• `/gaming` - Filtro específico para gaming
• `/tech` - Produtos tech premium
• `/anime` - Produtos anime/otaku
• `/smart` - Smart home e IoT
• `/audio` - Audio premium e gaming
• `/collectibles` - Collectibles e edições limitadas

**📊 ESTATÍSTICAS:**
• `/geekstats` - Estatísticas geek do sistema
• `/geekhelp` - Esta ajuda

**💡 USO AVANÇADO:**
• `/gaming console` - Filtra gaming por "console"
• `/tech smartphone` - Filtra tech por "smartphone"
• `/anime figura` - Filtra anime por "figura"

**🎯 CATEGORIAS PRIORITÁRIAS:**
• 🎮 Gaming (consoles, periféricos, jogos)
• ⚡ Tech Geek (smartphones, tablets, notebooks)
• 🌸 Anime/Otaku (figuras, mangás, cosplay)
• 🏠 Smart Home (smart TVs, IoT, automação)
• 🎧 Audio Premium (headphones, headsets, soundbars)
• 🏆 Collectibles (action figures, vinyl toys)

**⭐ SISTEMA DE SCORES:**
• 0.9-1.0: Crítico (máxima prioridade)
• 0.8-0.9: Alta prioridade
• 0.7-0.8: Média prioridade
• 0.6-0.7: Baixa prioridade

**🚨 ALERTAS AUTOMÁTICOS:**
O sistema monitora automaticamente produtos geek de alta prioridade e envia alertas para:
• Descontos significativos
• Produtos com estoque limitado
• Novos lançamentos geek
• Ofertas com score crítico

**💬 SUPORTE:**
Para dúvidas ou sugestões sobre comandos geek, entre em contato com a equipe do Garimpeiro Geek!
        """
        
        return help_text.strip()
    
    def get_available_commands(self) -> Dict[str, str]:
        """Retorna comandos disponíveis"""
        return self.available_commands.copy()
    
    async def get_user_preferences(self, user_id: int) -> Dict[str, Any]:
        """Retorna preferências do usuário (implementar com banco de dados)"""
        # Simular preferências do usuário
        return {
            "favorite_categories": ["gaming", "tech_geek"],
            "min_score_threshold": 0.7,
            "notification_enabled": True,
            "preferred_stores": ["Amazon", "Kabum", "Magazine Luiza"],
            "price_range": {"min": 50, "max": 5000}
        }
    
    async def update_user_preferences(self, user_id: int, preferences: Dict[str, Any]) -> bool:
        """Atualiza preferências do usuário (implementar com banco de dados)"""
        try:
            # Aqui você implementaria a atualização no banco de dados
            self.logger.info(f"Preferências atualizadas para usuário {user_id}")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao atualizar preferências: {e}")
            return False
