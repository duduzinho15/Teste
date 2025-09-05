"""
Demonstração das APIs e scrapers reais implementados.
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta

# Adicionar src ao path
sys.path.append('src')

async def demo_scrapers():
    """Demonstração dos scrapers reais."""
    print("🔍 === DEMONSTRAÇÃO DOS SCRAPERS REAIS ===\n")
    
    try:
        from scrapers.real_scrapers import ScrapingManager
        
        manager = ScrapingManager()
        
        print("🛍️ Fazendo scraping de ofertas...")
        offers = await manager.scrape_all_stores(category="gaming", limit_per_store=2)
        
        print(f"\n📊 Total de ofertas encontradas: {len(offers)}")
        
        for i, offer in enumerate(offers, 1):
            print(f"\n{i}. {offer.title}")
            print(f"   💰 R$ {offer.price:.2f}")
            if offer.original_price:
                print(f"   💸 De R$ {offer.original_price:.2f} ({offer.discount_percent}% OFF)")
            print(f"   🏪 {offer.store}")
            print(f"   🔗 {offer.affiliate_url}")
            
    except Exception as e:
        print(f"❌ Erro na demonstração dos scrapers: {e}")

async def demo_affiliate_apis():
    """Demonstração das APIs de afiliados."""
    print("\n🔗 === DEMONSTRAÇÃO DAS APIs DE AFILIADOS ===\n")
    
    try:
        from affiliate.real_affiliate_apis import AffiliateManager, AmazonAssociatesAPI, AwinAPI
        
        manager = AffiliateManager()
        
        # Adicionar redes de afiliados suportadas
        manager.add_network("amazon", AmazonAssociatesAPI("fake_key", "fake_secret", "garimpeirogeek-20"))
        manager.add_network("awin", AwinAPI("fake_key", "fake_secret", "123456"))
        
        print(" Testando criação de links de afiliado...")
        
        test_urls = [
            "https://www.amazon.com.br/dp/B08N5WRWNW",
            "https://www.magazineluiza.com.br/produto/123456",
            "https://www.mercadolivre.com.br/produto/123456"
        ]
        
        for url in test_urls:
            print(f"\n Processando: {url}")
            link = await manager.create_affiliate_link(url, preferred_network="amazon")
            if link:
                print(f"   Link criado: {link.network}")
                print(f"   URL: {link.affiliate_url}")
                print(f"   ✅ Link criado: {link.network}")
                print(f"   🔗 URL: {link.affiliate_url}")
                
                # Validar link
                is_valid = await manager.validate_affiliate_link(link.affiliate_url)
                print(f"   ✅ Válido: {'Sim' if is_valid else 'Não'}")
            else:
                print(f"   ❌ Falha ao criar link")
        
        print("\n📊 Obtendo estatísticas...")
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        stats = await manager.get_all_stats(start_date, end_date)
        
        for stat in stats:
            print(f"\n📈 {stat.network}:")
            print(f"   Cliques: {stat.total_clicks}")
            print(f"   Conversões: {stat.total_conversions}")
            print(f"   Taxa: {stat.conversion_rate:.1f}%")
            print(f"   Ganhos: R$ {stat.earnings:.2f}")
            
    except Exception as e:
        print(f"❌ Erro na demonstração das APIs de afiliados: {e}")

async def demo_telegram_bot():
    """Demonstração do bot do Telegram."""
    print("\n🤖 === DEMONSTRAÇÃO DO BOT DO TELEGRAM ===\n")
    
    try:
        from telegram_bot.real_telegram_bot import TelegramBotManager, TelegramOffer
        
        # Token fictício para demonstração
        token = "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
        bot_manager = TelegramBotManager(token)
        
        print("🤖 Iniciando bot do Telegram...")
        success = await bot_manager.start_bot()
        
        if success:
            print("✅ Bot iniciado com sucesso!")
            
            # Simular usuários se inscrevendo
            print("\n👥 Simulando usuários se inscrevendo...")
            bot_manager.subscribers.add(123456789)
            bot_manager.subscribers.add(987654321)
            print(f"✅ {len(bot_manager.subscribers)} usuários inscritos")
            
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
            
            sent_count = await bot_manager.send_offer_to_subscribers(offer)
            print(f"✅ Oferta enviada para {sent_count} usuários")
            
            # Mostrar estatísticas
            print("\n📊 Estatísticas do bot:")
            stats = bot_manager.get_stats()
            for key, value in stats.items():
                print(f"   {key}: {value}")
            
            # Parar bot
            print("\n⏹️ Parando bot...")
            await bot_manager.stop_bot()
            print("✅ Bot parado com sucesso!")
        else:
            print("❌ Falha ao iniciar bot")
            
    except Exception as e:
        print(f"❌ Erro na demonstração do bot do Telegram: {e}")

async def main():
    """Função principal de demonstração."""
    print("🚀 === DEMONSTRAÇÃO DAS APIs E SCRAPERS REAIS ===\n")
    print("Este script demonstra as funcionalidades reais implementadas:\n")
    print("1. 🔍 Scrapers de ofertas (Amazon, Magazine Luiza, Mercado Livre)")
    print("2. 🔗 APIs de afiliados (Amazon Associates, Awin, Rakuten, Shopee, AliExpress)")
    print("3. 🤖 Bot do Telegram funcional")
    print("\n" + "="*60 + "\n")
    
    # Executar demonstrações
    await demo_scrapers()
    await demo_affiliate_apis()
    await demo_telegram_bot()
    
    print("\n" + "="*60)
    print("✅ Demonstração concluída!")
    print("\n💡 Próximos passos:")
    print("   • Configure credenciais reais nas APIs")
    print("   • Adicione token real do Telegram")
    print("   • Personalize scrapers para suas necessidades")
    print("   • Integre com banco de dados real")

if __name__ == "__main__":
    asyncio.run(main())
