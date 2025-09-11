#!/usr/bin/env python3
"""
Sistema Automático de Postagem no Telegram - Garimpeiro Geek
Integra scheduler, coleta de ofertas e postagem automática
"""

import asyncio
import sys
import os
import random
from pathlib import Path
from datetime import datetime, timedelta
from decimal import Decimal
import logging

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.core.models import Offer
from src.core.settings import settings
from src.posting.message_formatter import MessageFormatter
from src.posting.scheduler import JobScheduler, job_scheduler
from src.pipelines.ingest_offers_api import APIOfferIngestionPipeline, APIOffer

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/auto_system.log'),
        logging.StreamHandler()
    ]
)

class AutoTelegramSystem:
    """Sistema automático de postagem no Telegram"""
    
    def __init__(self):
        self.logger = logging.getLogger("auto_telegram_system")
        self.message_formatter = MessageFormatter()
        self.scheduler = job_scheduler
        self.posted_count = 0
        self.offer_queue = []
        self.running = False
        
        # Configurações do sistema
        self.max_offers_per_hour = 20
        self.min_delay_between_posts = settings.POSTING_MIN_DELAY_SECONDS
        self.last_post_time = None
        
        # Credenciais do Telegram
        self.telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.telegram_channel_id = os.getenv("TELEGRAM_CHANNEL_ID")
        self.bot = None
        self.pipeline = APIOfferIngestionPipeline()
        
    async def setup_telegram_bot(self):
        """Configura o bot do Telegram"""
        try:
            from telegram import Bot
            self.bot = Bot(token=self.telegram_bot_token)
            self.logger.info("✅ Bot do Telegram configurado com sucesso")
            return True
        except ImportError:
            self.logger.error("❌ Biblioteca python-telegram-bot não encontrada")
            return False
        except Exception as e:
            self.logger.error(f"❌ Erro ao configurar bot: {e}")
            return False
    
    def create_sample_offers(self) -> list[Offer]:
        """Cria ofertas de exemplo para demonstração"""
        sample_offers = [
            # Smartphones
            Offer(
                title="iPhone 15 Pro - 128GB - Preto",
                price=Decimal("5999.99"),
                original_price=Decimal("6999.99"),
                discount_percentage=14,
                store="Amazon",
                category="Smartphones Premium",
                url="https://amzn.to/iphone15pro",
                affiliate_url="https://amzn.to/iphone15pro"
            ),
            Offer(
                title="Samsung Galaxy S23 - 256GB",
                price=Decimal("3999.99"),
                original_price=Decimal("4999.99"),
                discount_percentage=20,
                store="Magazine Luiza",
                category="Smartphones",
                url="https://magazinevoce.com.br/samsung-s23",
                affiliate_url="https://magazinevoce.com.br/samsung-s23"
            ),
            
            # Notebooks
            Offer(
                title="Notebook Gamer Acer Nitro 5",
                price=Decimal("3999.99"),
                original_price=Decimal("4999.99"),
                discount_percentage=20,
                store="Casas Bahia",
                category="Notebooks Gamer",
                url="https://casasbahia.com.br/acer-nitro5",
                affiliate_url="https://casasbahia.com.br/acer-nitro5"
            ),
            Offer(
                title="MacBook Air M2 - 13\" - 256GB",
                price=Decimal("7999.99"),
                original_price=Decimal("8999.99"),
                discount_percentage=11,
                store="Americanas",
                category="Notebooks Premium",
                url="https://americanas.com.br/macbook-air-m2",
                affiliate_url="https://americanas.com.br/macbook-air-m2"
            ),
            
            # Smart TVs
            Offer(
                title="Smart TV Samsung 65\" 4K UHD QLED",
                price=Decimal("3999.99"),
                original_price=Decimal("5999.99"),
                discount_percentage=33,
                store="Shopee",
                category="Smart TVs 4K",
                url="https://shopee.com.br/samsung-65-4k",
                affiliate_url="https://shopee.com.br/samsung-65-4k"
            ),
            Offer(
                title="Smart TV LG 55\" 4K UHD OLED",
                price=Decimal("3499.99"),
                original_price=Decimal("4499.99"),
                discount_percentage=22,
                store="Amazon",
                category="Smart TVs OLED",
                url="https://amzn.to/lg-55-oled",
                affiliate_url="https://amzn.to/lg-55-oled"
            ),
            
            # Consoles
            Offer(
                title="PlayStation 5 - Edição Digital",
                price=Decimal("3499.99"),
                original_price=Decimal("3999.99"),
                discount_percentage=13,
                store="Magazine Luiza",
                category="Consoles",
                url="https://magazinevoce.com.br/ps5-digital",
                affiliate_url="https://magazinevoce.com.br/ps5-digital"
            ),
            Offer(
                title="Xbox Series X - 1TB - Preto",
                price=Decimal("3499.99"),
                original_price=Decimal("4499.99"),
                discount_percentage=22,
                store="Casas Bahia",
                category="Consoles",
                url="https://casasbahia.com.br/xbox-series-x",
                affiliate_url="https://casasbahia.com.br/xbox-series-x"
            ),
            
            # Fones
            Offer(
                title="Fone Sony WH-1000XM5 - Noise Cancelling",
                price=Decimal("1899.99"),
                original_price=Decimal("2499.99"),
                discount_percentage=24,
                store="Shopee",
                category="Fones Premium",
                url="https://shopee.com.br/sony-wh1000xm5",
                affiliate_url="https://shopee.com.br/sony-wh1000xm5"
            ),
            Offer(
                title="AirPods Pro 2ª Geração",
                price=Decimal("1999.99"),
                original_price=Decimal("2499.99"),
                discount_percentage=20,
                store="Americanas",
                category="Fones Wireless",
                url="https://americanas.com.br/airpods-pro-2",
                affiliate_url="https://americanas.com.br/airpods-pro-2"
            )
        ]
        
        # Adicionar URLs de imagens
        image_urls = [
            "https://images.unsplash.com/photo-1592750475338-74b7b21085ab?w=800&h=600&fit=crop",
            "https://images.unsplash.com/photo-1592750475338-74b7b21085ab?w=800&h=600&fit=crop",
            "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=800&h=600&fit=crop",
            "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=800&h=600&fit=crop",
            "https://images.unsplash.com/photo-1593359677879-a4bb92f829d1?w=800&h=600&fit=crop",
            "https://images.unsplash.com/photo-1593359677879-a4bb92f829d1?w=800&h=600&fit=crop",
            "https://images.unsplash.com/photo-1607853202273-797f1c22a38e?w=800&h=600&fit=crop",
            "https://images.unsplash.com/photo-1607853202273-797f1c22a38e?w=800&h=600&fit=crop",
            "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800&h=600&fit=crop",
            "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800&h=600&fit=crop"
        ]
        
        for i, offer in enumerate(sample_offers):
            offer.image_url = image_urls[i]

        return sample_offers

    async def fetch_new_offers(self) -> list[Offer]:
        """Coleta novas ofertas via APIs e converte para o modelo Offer"""
        offers: list[Offer] = []
        try:
            api_offers: list[APIOffer] = await self.pipeline.collect_good_deals()
            for api_offer in api_offers:
                try:
                    offer = Offer(
                        title=api_offer.title,
                        price=Decimal(str(api_offer.price)),
                        original_price=(
                            Decimal(str(api_offer.original_price))
                            if api_offer.original_price
                            else None
                        ),
                        discount_percentage=api_offer.discount,
                        store=api_offer.store or "",
                        category=api_offer.category,
                        url=api_offer.product_url,
                        affiliate_url=api_offer.affiliate_url,
                    )
                    offer.source = api_offer.source
                    offers.append(offer)
                except Exception as e:
                    self.logger.error(
                        f"Erro ao converter oferta da fonte {api_offer.source}: {e}"
                    )
        except Exception as e:
            self.logger.error(f"Erro ao coletar ofertas via API: {e}")
        return offers
    
    def detect_platform(self, offer: Offer) -> str:
        """Detecta a plataforma baseada na loja"""
        store = offer.store.lower()
        
        if 'amazon' in store:
            return 'amazon'
        elif 'magazine' in store:
            return 'magazineluiza'
        elif 'casas bahia' in store:
            return 'casasbahia'
        elif 'americanas' in store:
            return 'americanas'
        elif 'shopee' in store:
            return 'shopee'
        else:
            return 'default'
    
    async def collect_offers_job(self):
        """Job de coleta de ofertas"""
        self.logger.info("🎯 Executando coleta de ofertas...")

        try:
            offers = await self.fetch_new_offers()
            
            # Filtrar ofertas com desconto mínimo
            filtered_offers = [
                offer for offer in offers 
                if offer.discount_percentage >= 10
            ]
            
            # Adicionar à fila
            self.offer_queue.extend(filtered_offers)
            
            self.logger.info(f"✅ {len(filtered_offers)} ofertas coletadas e adicionadas à fila")
            self.logger.info(f"📊 Total na fila: {len(self.offer_queue)} ofertas")
            
        except Exception as e:
            self.logger.error(f"❌ Erro na coleta de ofertas: {e}")
    
    async def post_offers_job(self):
        """Job de postagem de ofertas"""
        if not self.bot:
            self.logger.warning("⚠️ Bot do Telegram não configurado")
            return
        
        if not self.offer_queue:
            self.logger.info("📭 Fila de ofertas vazia")
            return
        
        # Verificar rate limiting
        if self.last_post_time:
            elapsed = (datetime.now() - self.last_post_time).total_seconds()
            wait_time = max(0, self.min_delay_between_posts - elapsed)
            if wait_time > 0:
                self.logger.info(
                    f"⏳ Aguardando para respeitar rate limit ({wait_time:.0f}s restantes)"
                )
                await asyncio.sleep(wait_time)
        
        try:
            # Pegar próxima oferta da fila
            offer = self.offer_queue.pop(0)
            
            # Detectar plataforma
            platform = self.detect_platform(offer)
            
            # Formatar mensagem
            message = self.message_formatter.format_offer_message(offer, platform)
            
            # Postar no Telegram
            if hasattr(offer, 'image_url') and offer.image_url:
                # Postar com imagem
                await self.post_with_image(offer, message)
            else:
                # Postar apenas texto
                await self.bot.send_message(
                    chat_id=self.telegram_channel_id,
                    text=message,
                    parse_mode='Markdown'
                )
            
            # Atualizar estatísticas
            self.posted_count += 1
            self.last_post_time = datetime.now()
            
            self.logger.info(f"✅ Oferta postada: {offer.title}")
            self.logger.info(f"📊 Total postado: {self.posted_count}")
            self.logger.info(f"📭 Restantes na fila: {len(self.offer_queue)}")
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao postar oferta: {e}")
            # Recolocar oferta na fila em caso de erro
            if 'offer' in locals():
                self.offer_queue.insert(0, offer)
    
    async def post_with_image(self, offer: Offer, message: str):
        """Posta oferta com imagem"""
        try:
            # Simular postagem com imagem (por enquanto)
            await self.bot.send_message(
                chat_id=self.telegram_channel_id,
                text=f"🖼️ {message}",
                parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao postar com imagem: {e}")
            # Fallback para texto apenas
            await self.bot.send_message(
                chat_id=self.telegram_channel_id,
                text=message,
                parse_mode='Markdown'
            )
    
    async def start_auto_system(self):
        """Inicia o sistema automático"""
        self.logger.info("🚀 Iniciando Sistema Automático de Postagem...")
        
        # Configurar bot do Telegram
        if not await self.setup_telegram_bot():
            self.logger.error("❌ Falha na configuração do bot")
            return False
        
        try:
            # Configurar jobs personalizados
            await self.scheduler.add_job(
                "collect_offers_auto",
                self.collect_offers_job,
                timedelta(minutes=5),  # Coletar a cada 5 minutos
                metadata={"description": "Coleta automática de ofertas"}
            )
            
            await self.scheduler.add_job(
                "post_offers_auto",
                self.post_offers_job,
                timedelta(minutes=3),  # Postar a cada 3 minutos
                metadata={"description": "Postagem automática de ofertas"}
            )
            
            # Iniciar scheduler
            await self.scheduler.start()
            
            self.running = True
            self.logger.info("✅ Sistema automático iniciado com sucesso!")
            
            # Manter sistema rodando
            while self.running:
                await asyncio.sleep(60)  # Verificar a cada minuto
                
                # Mostrar status
                if self.posted_count % 5 == 0 and self.posted_count > 0:
                    self.logger.info(f"📊 Status: {self.posted_count} ofertas postadas, {len(self.offer_queue)} na fila")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao iniciar sistema automático: {e}")
            return False
    
    async def stop_auto_system(self):
        """Para o sistema automático"""
        self.logger.info("🛑 Parando Sistema Automático...")
        
        self.running = False
        
        if self.scheduler:
            await self.scheduler.stop()
        
        self.logger.info("✅ Sistema automático parado")
    
    def get_system_status(self) -> dict:
        """Retorna status do sistema"""
        return {
            "running": self.running,
            "posted_count": self.posted_count,
            "queue_size": len(self.offer_queue),
            "last_post_time": self.last_post_time.isoformat() if self.last_post_time else None,
            "scheduler_running": self.scheduler.running if self.scheduler else False
        }


async def main():
    """Função principal"""
    print("🚀 SISTEMA AUTOMÁTICO DE POSTAGEM - GARIMPEIRO GEEK")
    print("=" * 60)
    
    # Criar sistema
    auto_system = AutoTelegramSystem()
    
    try:
        # Iniciar sistema
        await auto_system.start_auto_system()
        
    except KeyboardInterrupt:
        print("\n🛑 Interrupção detectada, parando sistema...")
        await auto_system.stop_auto_system()
        
    except Exception as e:
        print(f"\n❌ Erro no sistema: {e}")
        await auto_system.stop_auto_system()


if __name__ == "__main__":
    asyncio.run(main())
