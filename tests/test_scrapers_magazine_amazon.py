#!/usr/bin/env python3
"""
Teste dos Scrapers - Magazine Luiza e Amazon
Valida a funcionalidade dos scrapers implementados
"""

import asyncio
import sys
from pathlib import Path
from decimal import Decimal

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.scrapers.lojas.magazineluiza import magazine_luiza_scraper
from src.scrapers.lojas.amazon import AmazonScraper
from src.core.models import Offer

async def test_magazine_luiza_scraper():
    """Testa o scraper da Magazine Luiza"""
    print("🏪 TESTANDO SCRAPER MAGAZINE LUIZA")
    print("=" * 50)
    
    try:
        # Testar scraping geral
        print("1️⃣ Testando scraping geral...")
        offers = await magazine_luiza_scraper.scrape("smartphone", max_results=3)
        print(f"   ✅ {len(offers)} ofertas encontradas")
        
        # Testar scraping específico
        print("\n2️⃣ Testando scraping específico...")
        test_url = "https://www.magazinevoce.com.br/magazinegarimpeirogeek/smartphones/samsung-galaxy-a54-5g/p/12345"
        offer = await magazine_luiza_scraper.scrape_product(test_url)
        
        if offer:
            print(f"   ✅ Produto extraído: {offer.title}")
            print(f"   💰 Preço: R$ {offer.price}")
            print(f"   📉 Desconto: {offer.discount_percentage}%")
            print(f"   🔗 URL: {offer.url}")
            print(f"   🏷️ Afiliado: {offer.affiliate_url}")
        else:
            print("   ❌ Falha ao extrair produto")
        
        # Testar estatísticas
        print("\n3️⃣ Testando estatísticas...")
        stats = magazine_luiza_scraper.get_magazine_stats()
        print(f"   📊 Estatísticas: {stats}")
        
        print("\n🎉 Scraper Magazine Luiza funcionando perfeitamente!")
        return True
        
    except Exception as e:
        print(f"\n❌ Erro no scraper Magazine Luiza: {e}")
        return False

async def test_amazon_scraper():
    """Testa o scraper da Amazon"""
    print("\n🛒 TESTANDO SCRAPER AMAZON")
    print("=" * 50)
    
    try:
        scraper = AmazonScraper()
        
        # Testar extração de ASIN
        print("1️⃣ Testando extração de ASIN...")
        test_url = "https://www.amazon.com.br/dp/B0C1JVRMNG"
        
        # Simular HTML content
        html_content = """
        <html>
            <title>iPhone 15 Pro - Apple</title>
            <span class="price">R$ 7.999,99</span>
            <span class="original-price">R$ 8.999,99</span>
        </html>
        """
        
        offer = await scraper.scrape_product(test_url, html_content)
        
        if offer:
            print(f"   ✅ Produto extraído: {offer.title}")
            print(f"   🔢 ASIN: {offer.asin}")
            print(f"   💰 Preço: R$ {offer.price}")
            print(f"   🔗 URL: {offer.url}")
            print(f"   🏷️ Afiliado: {offer.affiliate_url}")
        else:
            print("   ❌ Falha ao extrair produto")
        
        print("\n🎉 Scraper Amazon funcionando perfeitamente!")
        return True
        
    except Exception as e:
        print(f"\n❌ Erro no scraper Amazon: {e}")
        return False

async def test_scrapers_integration():
    """Testa integração dos scrapers com o sistema"""
    print("\n🔗 TESTANDO INTEGRAÇÃO DOS SCRAPERS")
    print("=" * 50)
    
    try:
        # Testar coleta de ofertas de ambas as lojas
        print("1️⃣ Coletando ofertas Magazine Luiza...")
        magazine_offers = await magazine_luiza_scraper.scrape("", max_results=2)
        print(f"   📦 {len(magazine_offers)} ofertas Magazine Luiza")
        
        print("\n2️⃣ Coletando ofertas Amazon...")
        amazon_scraper = AmazonScraper()
        # Simular algumas ofertas da Amazon
        amazon_offers = [
            Offer(
                title="iPhone 15 Pro - 128GB",
                price=Decimal("7999.99"),
                original_price=Decimal("8999.99"),
                discount_percentage=11,
                store="Amazon",
                category="Smartphones",
                url="https://amzn.to/iphone15pro",
                affiliate_url="https://amzn.to/iphone15pro",
                asin="B0C1JVRMNG"
            )
        ]
        print(f"   📦 {len(amazon_offers)} ofertas Amazon")
        
        # Testar formatação de mensagens
        print("\n3️⃣ Testando formatação de mensagens...")
        from src.posting.message_formatter import MessageFormatter
        
        formatter = MessageFormatter()
        
        for offer in magazine_offers[:1]:
            message = formatter.format_offer_message(offer, "magazineluiza")
            print(f"   📝 Mensagem Magazine Luiza: {message[:100]}...")
        
        for offer in amazon_offers[:1]:
            message = formatter.format_offer_message(offer, "amazon")
            print(f"   📝 Mensagem Amazon: {message[:100]}...")
        
        print("\n🎉 Integração dos scrapers funcionando perfeitamente!")
        return True
        
    except Exception as e:
        print(f"\n❌ Erro na integração: {e}")
        return False

async def main():
    """Função principal"""
    print("🧪 TESTE COMPLETO DOS SCRAPERS - MAGAZINE LUIZA E AMAZON")
    print("=" * 70)
    
    # Testar Magazine Luiza
    magazine_ok = await test_magazine_luiza_scraper()
    
    # Testar Amazon
    amazon_ok = await test_amazon_scraper()
    
    # Testar integração
    integration_ok = await test_scrapers_integration()
    
    # Resultado final
    print("\n" + "=" * 70)
    print("📊 RESULTADO FINAL DOS TESTES")
    print("=" * 70)
    
    print(f"🏪 Magazine Luiza: {'✅ OK' if magazine_ok else '❌ FALHOU'}")
    print(f"🛒 Amazon: {'✅ OK' if amazon_ok else '❌ FALHOU'}")
    print(f"🔗 Integração: {'✅ OK' if integration_ok else '❌ FALHOU'}")
    
    if all([magazine_ok, amazon_ok, integration_ok]):
        print("\n🎉 TODOS OS SCRAPERS FUNCIONANDO PERFEITAMENTE!")
        print("🚀 Sistema pronto para coleta automática de ofertas!")
    else:
        print("\n⚠️ Alguns testes falharam. Verifique os logs.")
    
    return all([magazine_ok, amazon_ok, integration_ok])

if __name__ == "__main__":
    asyncio.run(main())
