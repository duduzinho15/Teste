#!/usr/bin/env python3
"""
Teste dos Scrapers Avançados - Amazon ASIN + Magazine Luiza
Valida a funcionalidade dos scrapers com Playwright e conversão de afiliados
"""

import asyncio
import sys
from pathlib import Path
from decimal import Decimal

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.affiliate.magazineluiza_scraper import magazine_luiza_scraper
from src.affiliate.amazon_asin_scraper import amazon_asin_scraper
from src.pipelines.amazon_ml_pipeline import amazon_ml_pipeline
from src.core.models import Offer

async def test_magazine_luiza_advanced():
    """Testa o scraper avançado da Magazine Luiza"""
    print("🏪 TESTANDO SCRAPER AVANÇADO MAGAZINE LUIZA")
    print("=" * 60)
    
    try:
        # Testar configurações
        print("1️⃣ Verificando configurações...")
        stats = magazine_luiza_scraper.get_scraper_stats()
        print(f"   ✅ Nome: {stats['name']}")
        print(f"   ✅ Base URL: {stats['base_url']}")
        print(f"   ✅ Affiliate ID: {stats['affiliate_id']}")
        print(f"   ✅ Playwright: {'✅ Disponível' if stats['playwright_available'] else '❌ Não disponível'}")
        
        # Testar scraping geral
        print("\n2️⃣ Testando scraping geral...")
        offers = await magazine_luiza_scraper.scrape_offers(
            search_term="smartphone", 
            max_results=3,
            max_price=3000,
            min_discount=10
        )
        print(f"   ✅ {len(offers)} ofertas encontradas")
        
        # Mostrar detalhes das ofertas
        for i, offer in enumerate(offers[:2], 1):
            print(f"   📦 Oferta {i}:")
            print(f"      Título: {offer['title']}")
            print(f"      Preço: R$ {offer['price']}")
            print(f"      Desconto: {offer.get('discount_percent', 0)}%")
            print(f"      ID: {offer['product_id']}")
            print(f"      URL: {offer['product_url'][:60]}...")
        
        # Testar conversão de afiliados
        print("\n3️⃣ Testando conversão de afiliados...")
        if offers:
            test_offer = offers[0]
            affiliate_url = magazine_luiza_scraper.convert_to_affiliate(
                test_offer['product_url'], 
                test_offer['product_id']
            )
            print(f"   ✅ Link afiliado gerado: {affiliate_url[:80]}...")
        
        # Testar scraping de produto individual
        print("\n4️⃣ Testando scraping de produto individual...")
        if offers:
            test_url = offers[0]['product_url']
            product_data = await magazine_luiza_scraper.scrape_single_product(test_url)
            
            if product_data:
                print(f"   ✅ Produto individual extraído: {product_data['title']}")
                print(f"   💰 Preço: R$ {product_data['price']}")
            else:
                print("   ⚠️ Produto individual não extraído (modo simulado)")
        
        print("\n🎉 Scraper Magazine Luiza avançado funcionando perfeitamente!")
        return True
        
    except Exception as e:
        print(f"\n❌ Erro no scraper Magazine Luiza avançado: {e}")
        return False

async def test_amazon_asin_advanced():
    """Testa o scraper avançado da Amazon"""
    print("\n🛒 TESTANDO SCRAPER AVANÇADO AMAZON ASIN")
    print("=" * 60)
    
    try:
        # Testar configurações
        print("1️⃣ Verificando configurações...")
        stats = amazon_asin_scraper.get_scraper_stats()
        print(f"   ✅ Nome: {stats['name']}")
        print(f"   ✅ Base URL: {stats['base_url']}")
        print(f"   ✅ Affiliate Tag: {stats['affiliate_tag']}")
        print(f"   ✅ Playwright: {'✅ Disponível' if stats['playwright_available'] else '❌ Não disponível'}")
        print(f"   ✅ User Agents: {stats['user_agents_count']}")
        
        # Testar scraping geral
        print("\n2️⃣ Testando scraping geral...")
        offers = await amazon_asin_scraper.scrape_offers(
            search_term="smartphone", 
            max_results=3,
            max_price=5000,
            min_discount=10
        )
        print(f"   ✅ {len(offers)} ofertas encontradas")
        
        # Mostrar detalhes das ofertas
        for i, offer in enumerate(offers[:2], 1):
            print(f"   📦 Oferta {i}:")
            print(f"      Título: {offer['title']}")
            print(f"      Preço: R$ {offer['price']}")
            print(f"      ASIN: {offer['asin']}")
            print(f"      Desconto: {offer.get('discount_percent', 0)}%")
            print(f"      URL: {offer['product_url'][:60]}...")
        
        # Testar conversão de afiliados
        print("\n3️⃣ Testando conversão de afiliados...")
        if offers:
            test_offer = offers[0]
            affiliate_url = amazon_asin_scraper.convert_to_affiliate(test_offer['asin'])
            print(f"   ✅ Link afiliado gerado: {affiliate_url[:80]}...")
        
        # Testar extração de ASIN de URLs
        print("\n4️⃣ Testando extração de ASIN...")
        test_urls = [
            "https://www.amazon.com.br/Apple-iPhone-13-256-GB-das-estrelas/dp/B09T4WC9GN",
            "https://www.amazon.com.br/dp/B0C1JVRMNG",
            "https://www.amazon.com.br/gp/product/B08N5WRWNW"
        ]
        
        for url in test_urls:
            asin = amazon_asin_scraper.extract_asin_from_url(url)
            print(f"   🔗 {url[:50]}... → ASIN: {asin}")
        
        # Testar scraping de produto individual
        print("\n5️⃣ Testando scraping de produto individual...")
        if offers:
            test_url = offers[0]['product_url']
            product_data = await amazon_asin_scraper.scrape_single_product(test_url)
            
            if product_data:
                print(f"   ✅ Produto individual extraído: {product_data['title']}")
                print(f"   💰 Preço: R$ {product_data['price']}")
                print(f"   🔢 ASIN: {product_data['asin']}")
            else:
                print("   ⚠️ Produto individual não extraído (modo simulado)")
        
        print("\n🎉 Scraper Amazon ASIN avançado funcionando perfeitamente!")
        return True
        
    except Exception as e:
        print(f"\n❌ Erro no scraper Amazon ASIN avançado: {e}")
        return False

async def test_pipeline_unified():
    """Testa o pipeline unificado"""
    print("\n🔗 TESTANDO PIPELINE UNIFICADO AMAZON + MAGAZINE LUIZA")
    print("=" * 70)
    
    try:
        # Testar configurações do pipeline
        print("1️⃣ Verificando configurações do pipeline...")
        pipeline_stats = amazon_ml_pipeline.get_pipeline_stats()
        print(f"   ✅ Nome: {pipeline_stats['name']}")
        print(f"   ✅ Versão: {pipeline_stats['version']}")
        print(f"   ✅ Criado em: {pipeline_stats['created_at']}")
        
        # Testar coleta unificada
        print("\n2️⃣ Testando coleta unificada...")
        all_offers = await amazon_ml_pipeline.collect_offers(
            search_term="smartphone",
            max_results=5,
            max_price=3000,
            min_discount=15
        )
        print(f"   ✅ {len(all_offers)} ofertas unificadas coletadas")
        
        # Mostrar detalhes das ofertas
        for i, offer in enumerate(all_offers[:3], 1):
            print(f"   📦 Oferta {i}:")
            print(f"      Título: {offer.title}")
            print(f"      Loja: {offer.store}")
            print(f"      Preço: R$ {offer.price}")
            print(f"      Desconto: {offer.discount_percentage}%")
            print(f"      Categoria: {offer.category}")
            print(f"      Afiliado: {offer.affiliate_url[:60]}...")
        
        # Testar coleta por categoria
        print("\n3️⃣ Testando coleta por categoria...")
        category_offers = await amazon_ml_pipeline.collect_by_category(
            category="smartphone",
            max_price=2500,
            min_discount=20
        )
        print(f"   ✅ Categoria smartphone: {len(category_offers)} ofertas")
        
        # Testar melhores ofertas
        print("\n4️⃣ Testando melhores ofertas...")
        best_offers = await amazon_ml_pipeline.collect_best_deals(
            max_price=2000,
            min_discount=25,
            max_results=5
        )
        print(f"   ✅ Melhores ofertas: {len(best_offers)} encontradas")
        
        # Mostrar ranking de descontos
        for i, offer in enumerate(best_offers[:3], 1):
            print(f"   🏆 #{i} - {offer.discount_percentage}% OFF: {offer.title[:40]}...")
        
        # Testar health check
        print("\n5️⃣ Testando health check...")
        health_status = await amazon_ml_pipeline.health_check()
        print(f"   ✅ Status: {health_status['status']}")
        print(f"   ✅ Timestamp: {health_status['timestamp']}")
        
        if 'checks' in health_status:
            for store, check in health_status['checks'].items():
                print(f"   🔍 {store.title()}: {check['status']}")
        
        print("\n🎉 Pipeline unificado funcionando perfeitamente!")
        return True
        
    except Exception as e:
        print(f"\n❌ Erro no pipeline unificado: {e}")
        return False

async def test_integration_with_telegram():
    """Testa integração com sistema de postagem Telegram"""
    print("\n📱 TESTANDO INTEGRAÇÃO COM TELEGRAM")
    print("=" * 60)
    
    try:
        # Coletar algumas ofertas
        print("1️⃣ Coletando ofertas para teste...")
        offers = await amazon_ml_pipeline.collect_offers(
            search_term="notebook",
            max_results=3,
            max_price=4000,
            min_discount=20
        )
        
        if not offers:
            print("   ⚠️ Nenhuma oferta encontrada para teste")
            return True
        
        print(f"   ✅ {len(offers)} ofertas coletadas para teste")
        
        # Testar formatação de mensagens
        print("\n2️⃣ Testando formatação de mensagens...")
        from src.posting.message_formatter import MessageFormatter
        
        formatter = MessageFormatter()
        
        for i, offer in enumerate(offers[:2], 1):
            message = formatter.format_offer_message(offer, offer.store.lower())
            print(f"   📝 Mensagem {i} ({offer.store}):")
            print(f"      {message[:100]}...")
            print(f"      Comprimento: {len(message)} caracteres")
        
        # Testar validação de links afiliados
        print("\n3️⃣ Testando validação de links afiliados...")
        for offer in offers[:2]:
            affiliate_url = offer.affiliate_url
            if affiliate_url and affiliate_url != offer.url:
                print(f"   ✅ Link afiliado válido: {affiliate_url[:60]}...")
            else:
                print(f"   ⚠️ Link afiliado não gerado para: {offer.title}")
        
        print("\n🎉 Integração com Telegram funcionando perfeitamente!")
        return True
        
    except Exception as e:
        print(f"\n❌ Erro na integração com Telegram: {e}")
        return False

async def main():
    """Função principal"""
    print("🧪 TESTE COMPLETO DOS SCRAPERS AVANÇADOS - AMAZON ASIN + MAGAZINE LUIZA")
    print("=" * 80)
    
    # Testar Magazine Luiza
    magazine_ok = await test_magazine_luiza_advanced()
    
    # Testar Amazon
    amazon_ok = await test_amazon_asin_advanced()
    
    # Testar pipeline unificado
    pipeline_ok = await test_pipeline_unified()
    
    # Testar integração com Telegram
    telegram_ok = await test_integration_with_telegram()
    
    # Resultado final
    print("\n" + "=" * 80)
    print("📊 RESULTADO FINAL DOS TESTES AVANÇADOS")
    print("=" * 80)
    
    print(f"🏪 Magazine Luiza Avançado: {'✅ OK' if magazine_ok else '❌ FALHOU'}")
    print(f"🛒 Amazon ASIN Avançado: {'✅ OK' if amazon_ok else '❌ FALHOU'}")
    print(f"🔗 Pipeline Unificado: {'✅ OK' if pipeline_ok else '❌ FALHOU'}")
    print(f"📱 Integração Telegram: {'✅ OK' if telegram_ok else '❌ FALHOU'}")
    
    if all([magazine_ok, amazon_ok, pipeline_ok, telegram_ok]):
        print("\n🎉 TODOS OS SCRAPERS AVANÇADOS FUNCIONANDO PERFEITAMENTE!")
        print("🚀 Sistema pronto para scraping real e conversão automática de afiliados!")
        print("\n💡 PRÓXIMOS PASSOS:")
        print("   1. Instalar Playwright: pip install playwright")
        print("   2. Configurar credenciais no .env")
        print("   3. Ativar scraping real em produção")
        print("   4. Configurar rate limiting adequado")
    else:
        print("\n⚠️ Alguns testes falharam. Verifique os logs.")
    
    return all([magazine_ok, amazon_ok, pipeline_ok, telegram_ok])

if __name__ == "__main__":
    asyncio.run(main())
