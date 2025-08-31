#!/usr/bin/env python3
"""
Teste dos Scrapers de Produção
Verifica funcionamento dos scrapers Amazon e Magazine Luiza com configurações reais
"""

import asyncio
import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from src.scrapers.lojas.magazineluiza import MagazineLuizaScraper
from src.affiliate.amazon_asin_scraper import AmazonASINScraper
from src.pipelines.amazon_ml_pipeline import AmazonMLPipeline

# Carregar variáveis do .env
load_dotenv()

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/production_test.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("ProductionTest")

async def test_individual_scrapers():
    """Testa cada scraper individualmente"""
    logger.info("🧪 TESTANDO SCRAPERS INDIVIDUAIS")
    print("=" * 60)
    
    # Teste Magazine Luiza
    print("📱 TESTE MAGAZINE LUIZA")
    print("-" * 30)
    
    ml_scraper = MagazineLuizaScraper()
    
    try:
        # Health check
        ml_health = await ml_scraper.health_check()
        print(f"✅ Health Check: {'OK' if ml_health else 'FALHOU'}")
        
        # Scraping de teste
        ml_offers = await ml_scraper.scrape_offers(
            search_term="smartphone",
            max_price=2000,
            min_discount=15
        )
        
        print(f"📊 Ofertas coletadas: {len(ml_offers)}")
        
        if ml_offers:
            for i, offer in enumerate(ml_offers[:3]):
                print(f"   {i+1}. {offer.title}")
                print(f"      💰 R$ {offer.price}")
                print(f"      🏪 {offer.store}")
                print(f"      🔗 {offer.affiliate_url[:50]}...")
                print()
        
    except Exception as e:
        print(f"❌ Erro Magazine Luiza: {e}")
        logger.error(f"Erro Magazine Luiza: {e}")
    
    print("=" * 60)
    
    # Teste Amazon
    print("🛒 TESTE AMAZON")
    print("-" * 20)
    
    amazon_scraper = AmazonASINScraper()
    
    try:
        # Health check
        amazon_health = await amazon_scraper.health_check()
        print(f"✅ Health Check: {'OK' if amazon_health else 'FALHOU'}")
        
        # Scraping de teste
        amazon_offers = await amazon_scraper.scrape_offers(
            search_term="smartphone",
            max_price=2000,
            min_discount=15
        )
        
        print(f"📊 Ofertas coletadas: {len(amazon_offers)}")
        
        if amazon_offers:
            for i, offer in enumerate(amazon_offers[:3]):
                print(f"   {i+1}. {offer.title}")
                print(f"      💰 R$ {offer.price}")
                print(f"      🏪 {offer.store}")
                print(f"      🔗 {offer.affiliate_url[:50]}...")
                print()
        
    except Exception as e:
        print(f"❌ Erro Amazon: {e}")
        logger.error(f"Erro Amazon: {e}")

async def test_unified_pipeline():
    """Testa o pipeline unificado"""
    logger.info("🔄 TESTANDO PIPELINE UNIFICADO")
    print("=" * 60)
    print("🔄 TESTE PIPELINE UNIFICADO")
    print("-" * 30)
    
    pipeline = AmazonMLPipeline()
    
    try:
        # Health check
        health = await pipeline.health_check()
        print(f"✅ Pipeline Health: {health['pipeline']}")
        print(f"✅ Amazon Scraper: {'OK' if health['amazon_scraper'] else 'FALHOU'}")
        print(f"✅ ML Scraper: {'OK' if health['ml_scraper'] else 'FALHOU'}")
        
        # Teste do pipeline
        pipeline_test = await pipeline.test_pipeline()
        print(f"✅ Pipeline Test: {'OK' if pipeline_test else 'FALHOU'}")
        
        # Coleta de ofertas
        print("\n📊 COLETANDO OFERTAS UNIFICADAS...")
        offers = await pipeline.collect_offers("smartphone")
        
        print(f"📈 Total de ofertas: {len(offers)}")
        
        if offers:
            for i, offer in enumerate(offers[:5]):
                print(f"\n   {i+1}. {offer.title}")
                print(f"      💰 R$ {offer.price}")
                if offer.original_price:
                    print(f"      💸 R$ {offer.original_price}")
                if offer.discount_percentage:
                    print(f"      🎯 {offer.discount_percentage:.0f}% OFF")
                print(f"      🏪 {offer.store}")
                print(f"      📂 {offer.category}")
                print(f"      🔗 {offer.affiliate_url[:60]}...")
        
        # Estatísticas
        stats = pipeline.get_pipeline_stats()
        print(f"\n📊 ESTATÍSTICAS:")
        print(f"   Amazon: {stats['amazon_offers']} ofertas")
        print(f"   Magazine Luiza: {stats['ml_offers']} ofertas")
        print(f"   Total: {stats['total_offers']} ofertas")
        print(f"   Filtradas: {stats['filtered_offers']} ofertas")
        print(f"   Erros: {stats['errors']} erros")
        
    except Exception as e:
        print(f"❌ Erro Pipeline: {e}")
        logger.error(f"Erro Pipeline: {e}")

async def test_configuration():
    """Testa as configurações do .env"""
    logger.info("⚙️ TESTANDO CONFIGURAÇÕES")
    print("=" * 60)
    print("⚙️ TESTE DE CONFIGURAÇÕES")
    print("-" * 30)
    
    # Verificar variáveis críticas
    critical_vars = [
        "ENABLE_REAL_SCRAPING",
        "SCRAPER_DELAY",
        "SCRAPER_MAX_RETRIES",
        "MAX_OFFER_PRICE",
        "MIN_OFFER_DISCOUNT",
        "AMAZON_AFFILIATE_TAG",
        "MAGAZINELUIZA_AFFILIATE_ID"
    ]
    
    print("🔍 Variáveis de Configuração:")
    for var in critical_vars:
        value = os.getenv(var, "NÃO DEFINIDA")
        status = "✅" if value != "NÃO DEFINIDA" else "❌"
        print(f"   {status} {var}: {value}")
    
    # Verificar configurações do Playwright
    playwright_vars = [
        "PLAYWRIGHT_HEADLESS",
        "PLAYWRIGHT_TIMEOUT",
        "PLAYWRIGHT_VIEWPORT_WIDTH",
        "PLAYWRIGHT_VIEWPORT_HEIGHT"
    ]
    
    print("\n🎭 Configurações Playwright:")
    for var in playwright_vars:
        value = os.getenv(var, "NÃO DEFINIDA")
        status = "✅" if value != "NÃO DEFINIDA" else "❌"
        print(f"   {status} {var}: {value}")
    
    # Verificar configurações de produção
    production_vars = [
        "PRODUCTION_MODE",
        "ENABLE_AUTO_POSTING",
        "POSTING_INTERVAL",
        "MAX_OFFERS_PER_POST"
    ]
    
    print("\n🚀 Configurações de Produção:")
    for var in production_vars:
        value = os.getenv(var, "NÃO DEFINIDA")
        status = "✅" if value != "NÃO DEFINIDA" else "❌"
        print(f"   {status} {var}: {value}")

async def main():
    """Função principal de teste"""
    logger.info("🚀 INICIANDO TESTES DE PRODUÇÃO")
    print("🚀 TESTES DE PRODUÇÃO - SCRAPERS AVANÇADOS")
    print("=" * 60)
    print(f"⏰ Início: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Testar configurações
        await test_configuration()
        print()
        
        # Testar scrapers individuais
        await test_individual_scrapers()
        print()
        
        # Testar pipeline unificado
        await test_unified_pipeline()
        print()
        
        logger.info("✅ TODOS OS TESTES CONCLUÍDOS COM SUCESSO")
        print("✅ TODOS OS TESTES CONCLUÍDOS COM SUCESSO!")
        print(f"⏰ Fim: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    except Exception as e:
        logger.error(f"❌ ERRO CRÍTICO NOS TESTES: {e}")
        print(f"❌ ERRO CRÍTICO NOS TESTES: {e}")
        raise

if __name__ == "__main__":
    # Criar diretório de logs se não existir
    os.makedirs("logs", exist_ok=True)
    
    # Executar testes
    asyncio.run(main())
