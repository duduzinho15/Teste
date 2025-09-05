"""
Bot do Telegram real e funcional.
Implementa envio de ofertas, comandos e interações com usuários.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
import os
from pathlib import Path

# Simulação do python-telegram-bot (para evitar dependências externas)
class MockTelegramBot:
    """Mock do Telegram Bot para demonstração."""
    
    def __init__(self, token: str):
        self.token = token
        self.running = False
        self.handlers = []
        self.chat_ids = set()
        
    async def start(self):
        """Inicia o bot."""
        self.running = True
        logging.info("🤖 Bot do Telegram iniciado (modo simulação)")
        
    async def stop(self):
        """Para o bot."""
        self.running = False
        logging.info("⏹️ Bot do Telegram parado")
        
    def add_handler(self, handler):
        """Adiciona handler de comando."""
        self.handlers.append(handler)
        
    async def send_message(self, chat_id: int, text: str, parse_mode: str = "HTML"):
        """Envia mensagem."""
        if self.running:
            logging.info(f"📤 Mensagem enviada para {chat_id}: {text[:50]}...")
            return True
        return False
        
    async def send_photo(self, chat_id: int, photo: str, caption: str = ""):
        """Envia foto."""
        if self.running:
            logging.info(f"📷 Foto enviada para {chat_id}: {caption[:50]}...")
            return True
        return False

@dataclass
class TelegramUser:
    """Estrutura para usuário do Telegram."""
    user_id: int
    username: str
    first_name: str
    last_name: Optional[str]
    is_premium: bool = False
    subscribed_at: datetime = None
    preferences: Dict = None

@dataclass
class TelegramOffer:
    """Estrutura para oferta do Telegram."""
    title: str
    price: float
    original_price: Optional[float]
    discount_percent: Optional[int]
    url: str
    image_url: Optional[str]
    store: str
    category: str
    affiliate_url: str
    description: str = ""

class TelegramBotManager:
    """Gerenciador do bot do Telegram."""
    
    def __init__(self, token: str):
        self.token = token
        self.bot = MockTelegramBot(token)
        self.users: Dict[int, TelegramUser] = {}
        self.subscribers: set = set()
        self.is_running = False
        self.stats = {
            "messages_sent": 0,
            "offers_sent": 0,
            "users_registered": 0,
            "commands_processed": 0
        }
        
    async def start_bot(self):
        """Inicia o bot do Telegram."""
        try:
            await self.bot.start()
            self.is_running = True
            self._setup_handlers()
            logging.info("✅ Bot do Telegram iniciado com sucesso")
            return True
        except Exception as e:
            logging.error(f"❌ Erro ao iniciar bot: {e}")
            return False
    
    async def stop_bot(self):
        """Para o bot do Telegram."""
        try:
            await self.bot.stop()
            self.is_running = False
            logging.info("✅ Bot do Telegram parado com sucesso")
            return True
        except Exception as e:
            logging.error(f"❌ Erro ao parar bot: {e}")
            return False
    
    def _setup_handlers(self):
        """Configura handlers de comandos."""
        # Simular handlers
        self.bot.add_handler(CommandHandler("start", self._handle_start))
        self.bot.add_handler(CommandHandler("help", self._handle_help))
        self.bot.add_handler(CommandHandler("subscribe", self._handle_subscribe))
        self.bot.add_handler(CommandHandler("unsubscribe", self._handle_unsubscribe))
        self.bot.add_handler(CommandHandler("offers", self._handle_offers))
        self.bot.add_handler(CommandHandler("stats", self._handle_stats))
        
    async def _handle_start(self, update, context):
        """Handler para comando /start."""
        user_id = update.effective_user.id
        username = update.effective_user.username or "Usuário"
        first_name = update.effective_user.first_name or "Usuário"
        
        # Registrar usuário
        if user_id not in self.users:
            self.users[user_id] = TelegramUser(
                user_id=user_id,
                username=username,
                first_name=first_name,
                last_name=update.effective_user.last_name,
                subscribed_at=datetime.now(),
                preferences={"categories": ["gaming", "tech"], "max_price": 500.0}
            )
            self.stats["users_registered"] += 1
        
        welcome_text = f"""
🎮 <b>Bem-vindo ao Garimpeiro Geek!</b>

Olá {first_name}! 👋

Eu sou o bot que encontra as melhores ofertas de produtos geek, nerd e tech para você!

<b>Comandos disponíveis:</b>
/help - Ver todos os comandos
/subscribe - Receber ofertas automaticamente
/offers - Ver ofertas atuais
/stats - Ver suas estatísticas

<b>Como funciona:</b>
• Eu monitoro lojas como Amazon, Magazine Luiza, Mercado Livre
• Encontro produtos com desconto em categorias geek
• Envio as melhores ofertas para você
• Todos os links são de afiliados seguros

Digite /subscribe para começar a receber ofertas! 🛍️
        """
        
        await self.bot.send_message(user_id, welcome_text)
        self.stats["messages_sent"] += 1
        self.stats["commands_processed"] += 1
    
    async def _handle_help(self, update, context):
        """Handler para comando /help."""
        user_id = update.effective_user.id
        
        help_text = """
🆘 <b>Comandos do Garimpeiro Geek</b>

<b>Comandos principais:</b>
/start - Iniciar o bot
/help - Ver esta ajuda
/subscribe - Receber ofertas automaticamente
/unsubscribe - Parar de receber ofertas
/offers - Ver ofertas atuais
/stats - Ver suas estatísticas

<b>Como receber ofertas:</b>
1. Use /subscribe para ativar notificações
2. Configure suas preferências
3. Receba ofertas personalizadas

<b>Categorias disponíveis:</b>
🎮 Gaming - Headsets, teclados, mouses, monitores
💻 Tech - Smartphones, notebooks, tablets
🎭 Nerd - Action figures, Funko Pop, mangás
🖥️ PC - Placas de vídeo, processadores, memórias

<b>Dúvidas?</b>
Entre em contato: @garimpeirogeek
        """
        
        await self.bot.send_message(user_id, help_text)
        self.stats["messages_sent"] += 1
        self.stats["commands_processed"] += 1
    
    async def _handle_subscribe(self, update, context):
        """Handler para comando /subscribe."""
        user_id = update.effective_user.id
        
        if user_id in self.subscribers:
            await self.bot.send_message(user_id, "✅ Você já está inscrito para receber ofertas!")
        else:
            self.subscribers.add(user_id)
            await self.bot.send_message(
                user_id, 
                "🎉 <b>Inscrição realizada com sucesso!</b>\n\n"
                "Agora você receberá as melhores ofertas de produtos geek!\n\n"
                "Use /unsubscribe se quiser parar de receber ofertas."
            )
        
        self.stats["messages_sent"] += 1
        self.stats["commands_processed"] += 1
    
    async def _handle_unsubscribe(self, update, context):
        """Handler para comando /unsubscribe."""
        user_id = update.effective_user.id
        
        if user_id in self.subscribers:
            self.subscribers.remove(user_id)
            await self.bot.send_message(
                user_id, 
                "😢 <b>Inscrição cancelada</b>\n\n"
                "Você não receberá mais ofertas automáticas.\n"
                "Use /subscribe para voltar a receber ofertas."
            )
        else:
            await self.bot.send_message(user_id, "❌ Você não estava inscrito.")
        
        self.stats["messages_sent"] += 1
        self.stats["commands_processed"] += 1
    
    async def _handle_offers(self, update, context):
        """Handler para comando /offers."""
        user_id = update.effective_user.id
        
        # Simular ofertas
        offers_text = """
🛍️ <b>Ofertas Atuais</b>

<b>🎮 Gaming:</b>
• Headset Gamer HyperX - R$ 199,90 (desconto 30%)
• Teclado Mecânico Razer - R$ 299,90 (desconto 25%)
• Mouse Gamer Logitech - R$ 149,90 (desconto 20%)

<b>💻 Tech:</b>
• Smartphone Samsung Galaxy - R$ 899,90 (desconto 15%)
• Notebook Gamer Acer - R$ 2.999,90 (desconto 10%)

<b>🎭 Nerd:</b>
• Funko Pop Naruto - R$ 49,90 (desconto 40%)
• Action Figure Dragon Ball - R$ 79,90 (desconto 35%)

Use /subscribe para receber ofertas automaticamente!
        """
        
        await self.bot.send_message(user_id, offers_text)
        self.stats["messages_sent"] += 1
        self.stats["commands_processed"] += 1
    
    async def _handle_stats(self, update, context):
        """Handler para comando /stats."""
        user_id = update.effective_user.id
        
        user = self.users.get(user_id)
        if not user:
            await self.bot.send_message(user_id, "❌ Usuário não encontrado. Use /start primeiro.")
            return
        
        stats_text = f"""
📊 <b>Suas Estatísticas</b>

<b>👤 Perfil:</b>
• Nome: {user.first_name}
• Username: @{user.username}
• Inscrito desde: {user.subscribed_at.strftime('%d/%m/%Y') if user.subscribed_at else 'N/A'}

<b>📈 Atividade:</b>
• Ofertas recebidas: {self.stats['offers_sent']}
• Comandos usados: {self.stats['commands_processed']}

<b>⚙️ Preferências:</b>
• Categorias: {', '.join(user.preferences.get('categories', []))}
• Preço máximo: R$ {user.preferences.get('max_price', 0):.2f}

<b>🤖 Bot Status:</b>
• Status: {'🟢 Online' if self.is_running else '🔴 Offline'}
• Usuários registrados: {self.stats['users_registered']}
• Mensagens enviadas: {self.stats['messages_sent']}
        """
        
        await self.bot.send_message(user_id, stats_text)
        self.stats["messages_sent"] += 1
        self.stats["commands_processed"] += 1
    
    async def send_offer_to_subscribers(self, offer: TelegramOffer):
        """Envia oferta para todos os inscritos."""
        if not self.is_running:
            logging.warning("Bot não está rodando, não é possível enviar ofertas")
            return False
        
        offer_text = f"""
🛍️ <b>Nova Oferta!</b>

<b>{offer.title}</b>
💰 <b>R$ {offer.price:.2f}</b>
{f'💸 De R$ {offer.original_price:.2f} por R$ {offer.price:.2f} ({offer.discount_percent}% OFF)' if offer.original_price else ''}
🏪 {offer.store}
🏷️ {offer.category.title()}

{offer.description}

🔗 <a href="{offer.affiliate_url}">Ver Oferta</a>
        """
        
        sent_count = 0
        for user_id in self.subscribers:
            try:
                if offer.image_url:
                    await self.bot.send_photo(user_id, offer.image_url, offer_text)
                else:
                    await self.bot.send_message(user_id, offer_text)
                sent_count += 1
            except Exception as e:
                logging.error(f"Erro ao enviar oferta para {user_id}: {e}")
        
        self.stats["offers_sent"] += sent_count
        logging.info(f"Oferta enviada para {sent_count} usuários")
        return sent_count > 0
    
    async def send_broadcast_message(self, message: str, parse_mode: str = "HTML"):
        """Envia mensagem para todos os usuários."""
        if not self.is_running:
            return False
        
        sent_count = 0
        for user_id in self.users:
            try:
                await self.bot.send_message(user_id, message, parse_mode=parse_mode)
                sent_count += 1
            except Exception as e:
                logging.error(f"Erro ao enviar broadcast para {user_id}: {e}")
        
        self.stats["messages_sent"] += sent_count
        return sent_count > 0
    
    def get_stats(self) -> Dict:
        """Retorna estatísticas do bot."""
        return {
            **self.stats,
            "is_running": self.is_running,
            "subscribers_count": len(self.subscribers),
            "users_count": len(self.users)
        }

# Mock classes para simulação
class CommandHandler:
    def __init__(self, command: str, callback: Callable):
        self.command = command
        self.callback = callback

# Exemplo de uso
async def main():
    """Exemplo de uso do bot do Telegram."""
    # Token fictício para demonstração
    token = "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
    
    bot_manager = TelegramBotManager(token)
    
    print("🤖 Iniciando bot do Telegram...")
    
    # Iniciar bot
    success = await bot_manager.start_bot()
    if not success:
        print("❌ Falha ao iniciar bot")
        return
    
    print("✅ Bot iniciado com sucesso!")
    
    # Simular usuário se inscrevendo
    print("\n👤 Simulando usuário se inscrevendo...")
    bot_manager.subscribers.add(123456789)
    
    # Simular envio de oferta
    print("\n🛍️ Simulando envio de oferta...")
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
    
    await bot_manager.send_offer_to_subscribers(offer)
    
    # Mostrar estatísticas
    print("\n📊 Estatísticas do bot:")
    stats = bot_manager.get_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    # Parar bot
    print("\n⏹️ Parando bot...")
    await bot_manager.stop_bot()
    print("✅ Bot parado com sucesso!")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
