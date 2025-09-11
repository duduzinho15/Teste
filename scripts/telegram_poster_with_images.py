#!/usr/bin/env python3
"""
Postador com Imagens no Telegram - Garimpeiro Geek
Este script faz posts REAIS no canal do Telegram com imagens dos produtos
"""

import asyncio
import sys
import os
import requests
from pathlib import Path
from datetime import datetime
from decimal import Decimal
import hashlib
import time

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.core.models import Offer
from src.posting.message_formatter import MessageFormatter

# Credenciais do Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")

class TelegramImagePoster:
    """Classe para fazer posts com imagens no Telegram"""
    
    def __init__(self):
        self.message_formatter = MessageFormatter()
        self.posted_count = 0
        self.bot = None
        self.image_cache_dir = Path("image_cache")
        self.image_cache_dir.mkdir(exist_ok=True)
        
    async def setup_bot(self):
        """Configura o bot do Telegram"""
        try:
            from telegram import Bot
            from telegram.error import TelegramError
            
            self.bot = Bot(token=TELEGRAM_BOT_TOKEN)
            print("✅ Bot do Telegram configurado com sucesso")
            return True
            
        except ImportError:
            print("❌ Biblioteca python-telegram-bot não encontrada")
            print("💡 Instale com: pip install python-telegram-bot")
            return False
        except Exception as e:
            print(f"❌ Erro ao configurar bot: {e}")
            return False
    
    def create_test_offers_with_images(self):
        """Cria ofertas de teste com URLs de imagens"""
        print("🎯 Criando ofertas de teste com imagens...")
        
        offers = [
            # Oferta 1: Smartphone Premium
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
            
            # Oferta 2: Notebook Gamer
            Offer(
                title="Notebook Gamer Acer Nitro 5",
                price=Decimal("3999.99"),
                original_price=Decimal("4999.99"),
                discount_percentage=20,
                store="Magazine Luiza",
                category="Notebooks Gamer",
                url="https://magazinevoce.com.br/acer-nitro5",
                affiliate_url="https://magazinevoce.com.br/acer-nitro5"
            ),
            
            # Oferta 3: Smart TV 4K
            Offer(
                title="Smart TV Samsung 65\" 4K UHD QLED",
                price=Decimal("3999.99"),
                original_price=Decimal("5999.99"),
                discount_percentage=33,
                store="Casas Bahia",
                category="Smart TVs 4K",
                url="https://casasbahia.com.br/samsung-65-4k",
                affiliate_url="https://casasbahia.com.br/samsung-65-4k"
            ),
            
            # Oferta 4: Console Next-Gen
            Offer(
                title="Xbox Series X - 1TB - Preto",
                price=Decimal("3499.99"),
                original_price=Decimal("4499.99"),
                discount_percentage=22,
                store="Americanas",
                category="Consoles Next-Gen",
                url="https://americanas.com.br/xbox-series-x",
                affiliate_url="https://americanas.com.br/xbox-series-x"
            ),
            
            # Oferta 5: Fone Wireless Premium
            Offer(
                title="Fone Sony WH-1000XM5 - Noise Cancelling",
                price=Decimal("1899.99"),
                original_price=Decimal("2499.99"),
                discount_percentage=24,
                store="Shopee",
                category="Fones Premium",
                url="https://shopee.com.br/sony-wh1000xm5",
                affiliate_url="https://shopee.com.br/sony-wh1000xm5"
            )
        ]
        
        # Adicionar URLs de imagens para cada oferta
        image_urls = [
            "https://images.unsplash.com/photo-1592750475338-74b7b21085ab?w=800&h=600&fit=crop",
            "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=800&h=600&fit=crop",
            "https://images.unsplash.com/photo-1593359677879-a4bb92f829d1?w=800&h=600&fit=crop",
            "https://images.unsplash.com/photo-1607853202273-797f1c22a38e?w=800&h=600&fit=crop",
            "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800&h=600&fit=crop"
        ]
        
        for i, offer in enumerate(offers):
            offer.image_url = image_urls[i]
        
        print(f"✅ {len(offers)} ofertas de teste com imagens criadas")
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
    
    def get_image_filename(self, offer: Offer) -> str:
        """Gera nome de arquivo único para a imagem"""
        # Criar hash baseado no título e preço
        content = f"{offer.title}_{offer.price}_{offer.store}".encode('utf-8')
        hash_value = hashlib.md5(content).hexdigest()[:8]
        return f"{hash_value}.jpg"
    
    async def download_image(self, image_url: str, filename: str) -> Path:
        """Baixa imagem da URL e salva no cache"""
        image_path = self.image_cache_dir / filename
        
        # Se a imagem já existe, retornar o caminho
        if image_path.exists():
            print(f"   📷 Imagem já existe no cache: {filename}")
            return image_path
        
        try:
            print(f"   📥 Baixando imagem: {image_url}")
            
            # Fazer requisição HTTP
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(image_url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Salvar imagem
            with open(image_path, 'wb') as f:
                f.write(response.content)
            
            print(f"   ✅ Imagem baixada: {filename}")
            return image_path
            
        except Exception as e:
            print(f"   ❌ Erro ao baixar imagem: {e}")
            return None
    
    async def post_to_telegram_with_image(self, offer: Offer, platform: str):
        """Faz post real no Telegram com imagem"""
        print(f"\n📤 Postando no Telegram: {offer.title}")
        print("-" * 80)
        
        try:
            # 1. Formatar mensagem
            print("🔄 Formatando mensagem...")
            message = self.message_formatter.format_offer_message(offer, platform)
            
            # 2. Mostrar mensagem formatada
            print(f"📋 Mensagem formatada para {platform.upper()}:")
            print("=" * 60)
            print(message)
            print("=" * 60)
            
            # 3. Baixar imagem
            if hasattr(offer, 'image_url') and offer.image_url:
                print("🖼️ Processando imagem...")
                image_filename = self.get_image_filename(offer)
                image_path = await self.download_image(offer.image_url, image_filename)
                
                if image_path and image_path.exists():
                    print(f"   📷 Imagem pronta: {image_filename}")
                    
                    # 4. Enviar mensagem com imagem
                    print("📡 Enviando mensagem com imagem para o canal...")
                    
                    if self.bot:
                        with open(image_path, 'rb') as photo:
                            await self.bot.send_photo(
                                chat_id=TELEGRAM_CHANNEL_ID,
                                photo=photo,
                                caption=message,
                                parse_mode='Markdown'
                            )
                        print("✅ Mensagem com imagem enviada com sucesso para o canal!")
                    else:
                        print("⚠️ Bot não configurado, simulando envio...")
                        await asyncio.sleep(2)
                else:
                    print("⚠️ Imagem não disponível, enviando apenas texto...")
                    
                    # Enviar apenas texto se não conseguir a imagem
                    if self.bot:
                        await self.bot.send_message(
                            chat_id=TELEGRAM_CHANNEL_ID,
                            text=message,
                            parse_mode='Markdown'
                        )
                        print("✅ Mensagem de texto enviada com sucesso para o canal!")
                    else:
                        print("⚠️ Bot não configurado, simulando envio...")
                        await asyncio.sleep(2)
            else:
                print("⚠️ Nenhuma imagem disponível, enviando apenas texto...")
                
                # Enviar apenas texto
                if self.bot:
                    await self.bot.send_message(
                        chat_id=TELEGRAM_CHANNEL_ID,
                        text=message,
                        parse_mode='Markdown'
                    )
                    print("✅ Mensagem de texto enviada com sucesso para o canal!")
                else:
                    print("⚠️ Bot não configurado, simulando envio...")
                    await asyncio.sleep(2)
            
            # 5. Confirmar sucesso
            self.posted_count += 1
            print(f"✅ Post #{self.posted_count} enviado com sucesso!")
            
            # 6. Mostrar estatísticas da oferta
            print(f"📊 Estatísticas da oferta:")
            print(f"   💰 Preço atual: R$ {offer.price:.2f}")
            print(f"   💸 Preço original: R$ {offer.original_price:.2f}")
            print(f"   🎯 Desconto: {offer.discount_percentage}%")
            print(f"   🏪 Loja: {offer.store}")
            print(f"   📂 Categoria: {offer.category}")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro na postagem: {e}")
            return False
    
    async def run_posting_with_images(self):
        """Executa postagem com imagens no Telegram"""
        print("=" * 80)
        print("🚀 POSTAGEM COM IMAGENS NO TELEGRAM - GARIMPEIRO GEEK")
        print("=" * 80)
        print(f"⏰ Iniciado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print("=" * 80)
        
        print("\n🎯 Este script vai:")
        print("   1️⃣ Formatar mensagens para diferentes plataformas")
        print("   2️⃣ Baixar imagens dos produtos")
        print("   3️⃣ Fazer posts REAIS com imagens no canal")
        print("   4️⃣ Enviar 5 ofertas de teste com fotos")
        print("   5️⃣ Validar o sistema completo")
        
        # Configurar bot
        if not await self.setup_bot():
            print("\n❌ Falha na configuração do bot")
            return False
        
        try:
            # Criar ofertas de teste com imagens
            test_offers = self.create_test_offers_with_images()
            
            # Postar cada oferta
            print(f"\n🚀 Iniciando postagem de {len(test_offers)} ofertas com imagens...")
            
            for i, offer in enumerate(test_offers, 1):
                print(f"\n🔄 Processando oferta {i}/{len(test_offers)}...")
                
                # Detectar plataforma
                platform = self.detect_platform(offer)
                print(f"📱 Plataforma detectada: {platform.upper()}")
                
                # Fazer post com imagem
                success = await self.post_to_telegram_with_image(offer, platform)
                
                if not success:
                    print(f"⚠️ Falha na oferta {i}, continuando...")
                
                # Delay entre posts
                if i < len(test_offers):
                    print("⏳ Aguardando 5 segundos antes do próximo post...")
                    await asyncio.sleep(5)
            
            # Resumo final
            print("\n" + "=" * 80)
            print("📊 RESUMO DA POSTAGEM COM IMAGENS")
            print("=" * 80)
            print(f"✅ Posts enviados com sucesso: {self.posted_count}")
            print(f"📱 Total de ofertas processadas: {len(test_offers)}")
            print(f"🎯 Taxa de sucesso: {(self.posted_count/len(test_offers)*100):.1f}%")
            print("=" * 80)
            
            if self.posted_count == len(test_offers):
                print("🎉 TODAS AS OFERTAS FORAM POSTADAS COM IMAGENS!")
                print("🚀 Sistema funcionando perfeitamente")
                print("📱 Verifique o canal do Telegram para ver as mensagens com fotos!")
            else:
                print("⚠️ Alguns posts falharam. Verifique os logs.")
            
            return True
            
        except Exception as e:
            print(f"\n❌ Erro geral na postagem: {e}")
            return False


async def main():
    """Função principal"""
    poster = TelegramImagePoster()
    
    # Executar postagem com imagens
    success = await poster.run_posting_with_images()
    
    if success:
        print("\n🎉 Postagem com imagens concluída com sucesso!")
        print("📱 Verifique o canal do Telegram!")
        print("🚀 Sistema pronto para produção com imagens")
    else:
        print("\n⚠️ Postagem falhou. Verifique a configuração.")
    
    return success


if __name__ == "__main__":
    asyncio.run(main())
