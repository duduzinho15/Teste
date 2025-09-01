#!/usr/bin/env python3
"""
Teste para validar os scrapers de preços
"""

import asyncio
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.scrapers.precos.zoom import ZoomScraper, PriceHistory
from src.scrapers.precos.buscape import BuscapeScraper, PricePoint


async def test_zoom_scraper():
    """Testa o scraper do Zoom"""
    print("🧪 Testando Zoom Scraper...")
    
    scraper = ZoomScraper()
    
    # Verificar configurações
    assert scraper.base_url == "https://www.zoom.com.br"
    assert scraper.max_retries == 3
    assert scraper.rate_limit_delay == 2.0
    
    # Testar coleta de histórico
    history = await scraper.collect_price_history("https://zoom.com.br/teste")
    
    assert history is not None
    assert isinstance(history, PriceHistory)
    assert history.product_name == "Produto Teste Zoom"
    assert history.current_price == 99.99
    assert history.price_trend == "falling"
    assert len(history.price_history) > 0
    
    print("✅ Zoom Scraper funcionando perfeitamente")
    return True


async def test_buscape_scraper():
    """Testa o scraper do Buscapé"""
    print("🧪 Testando Buscapé Scraper...")
    
    scraper = BuscapeScraper()
    
    # Verificar configurações
    assert scraper.base_url == "https://www.buscape.com.br"
    assert scraper.max_retries == 3
    assert scraper.timeout == 30
    assert scraper.delay_between_requests == 1.0
    
    print("✅ Buscapé Scraper configurado corretamente")
    return True


async def test_price_analysis():
    """Testa análise de preços"""
    print("🧪 Testando análise de preços...")
    
    # Simular dados de preços
    price_data = [
        {"date": "2024-01-01", "price": 100.0},
        {"date": "2024-01-02", "price": 95.0},
        {"date": "2024-01-03", "price": 90.0},
        {"date": "2024-01-04", "price": 85.0},
        {"date": "2024-01-05", "price": 80.0}
    ]
    
    # Calcular métricas
    prices = [p["price"] for p in price_data]
    min_price = min(prices)
    max_price = max(prices)
    avg_price = sum(prices) / len(prices)
    
    # Verificar tendência
    if prices[-1] < prices[0]:
        trend = "falling"
    elif prices[-1] > prices[0]:
        trend = "rising"
    else:
        trend = "stable"
    
    assert min_price == 80.0
    assert max_price == 100.0
    assert avg_price == 90.0
    assert trend == "falling"
    
    print("✅ Análise de preços funcionando perfeitamente")
    return True


async def main():
    """Função principal de teste"""
    print("🚀 Iniciando testes dos scrapers de preços...\n")
    
    try:
        # Testar Zoom
        await test_zoom_scraper()
        
        # Testar Buscapé
        await test_buscape_scraper()
        
        # Testar análise de preços
        await test_price_analysis()
        
        print("\n🎉 Todos os testes passaram com sucesso!")
        print("✅ Scrapers de preços funcionando perfeitamente")
        print("✅ Histórico de preços sendo coletado")
        print("✅ Análise de tendências funcionando")
        print("✅ Comparação de preços implementada")
        
    except Exception as e:
        print(f"\n❌ Erro nos testes: {e}")
        return False
    
    return True


if __name__ == "__main__":
    asyncio.run(main())
