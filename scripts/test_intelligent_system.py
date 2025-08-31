#!/usr/bin/env python3
"""
Script de Teste para Sistema Inteligente de Coleta Automática
Testa AwinOffersCollector, Pipeline de Ingestão e Filtros Automáticos
"""

import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime
from decimal import Decimal

# Adicionar src ao path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from core.models import Offer
from affiliate.awin_api import AwinOffersCollector, AwinAdvertiser
from pipelines.ingest_awin_offers import AwinIngestPipeline, IngestConfig
from pipelines.auto_filters import AutoFilterEngine, AutoFilter, FilterType, FilterOperator

async def test_awin_offers_collector():
    """Testa o coletor de ofertas Awin"""
    print("\n🧪 TESTANDO AwinOffersCollector")
    print("=" * 50)
    
    try:
        # Criar coletor de teste (sem credenciais reais)
        collector = AwinOffersCollector("test_publisher", "test_token")
        
        # Verificar configuração dos anunciantes
        print(f"✅ Anunciantes configurados: {len(collector.advertisers)}")
        for key, advertiser in collector.advertisers.items():
            print(f"   - {advertiser.name}: MID {advertiser.mid}, Categoria {advertiser.category}")
        
        # Verificar filtros automáticos
        print(f"✅ Filtros automáticos: {collector.filters}")
        
        # Testar atualização de filtros
        collector.update_filters(min_discount=20, max_price=2000.0)
        print(f"✅ Filtros atualizados: {collector.filters}")
        
        # Verificar estatísticas
        stats = collector.get_stats()
        print(f"✅ Estatísticas: {stats}")
        
        print("✅ AwinOffersCollector: TESTE PASSOU")
        return True
        
    except Exception as e:
        print(f"❌ AwinOffersCollector: ERRO - {e}")
        return False

async def test_auto_filter_engine():
    """Testa o motor de filtros automáticos"""
    print("\n🧪 TESTANDO AutoFilterEngine")
    print("=" * 50)
    
    try:
        # Obter instância do motor
        engine = AutoFilterEngine()
        
        # Verificar filtros padrão
        print(f"✅ Filtros padrão carregados: {len(engine.filters)}")
        for name, filter_obj in engine.filters.items():
            print(f"   - {name}: {filter_obj.description}")
        
        # Criar filtros personalizados
        custom_filter = AutoFilter(
            name="test_custom_filter",
            filter_type=FilterType.PRICE,
            operator=FilterOperator.BETWEEN,
            value=100.0,
            secondary_value=500.0,
            description="Preço entre R$ 100 e R$ 500"
        )
        
        engine.add_filter(custom_filter)
        print(f"✅ Filtro personalizado adicionado: {custom_filter.name}")
        
        # Verificar estatísticas
        stats = engine.get_stats()
        print(f"✅ Estatísticas: {stats}")
        
        print("✅ AutoFilterEngine: TESTE PASSOU")
        return True
        
    except Exception as e:
        print(f"❌ AutoFilterEngine: ERRO - {e}")
        return False

async def test_awin_ingest_pipeline():
    """Testa o pipeline de ingestão Awin"""
    print("\n🧪 TESTANDO AwinIngestPipeline")
    print("=" * 50)
    
    try:
        # Criar configuração de teste
        config = IngestConfig(
            enabled=True,
            collection_interval=60,  # 1 minuto para teste
            max_offers_per_run=50,
            auto_post=False,  # Desabilitar postagem automática para teste
            quality_threshold=0.7,
            deduplication=True,
            backup_enabled=True
        )
        
        # Criar pipeline
        pipeline = AwinIngestPipeline(config)
        
        # Verificar configuração
        print(f"✅ Configuração: {pipeline.config}")
        print(f"✅ Filtros automáticos: {pipeline.auto_filters}")
        
        # Testar atualização de filtros
        pipeline.update_auto_filters(min_discount=25, max_price=3000.0)
        print(f"✅ Filtros atualizados: {pipeline.auto_filters}")
        
        # Verificar estatísticas
        stats = pipeline.get_stats()
        print(f"✅ Estatísticas: {stats}")
        
        print("✅ AwinIngestPipeline: TESTE PASSOU")
        return True
        
    except Exception as e:
        print(f"❌ AwinIngestPipeline: ERRO - {e}")
        return False

async def test_integration():
    """Testa integração entre componentes"""
    print("\n🧪 TESTANDO INTEGRAÇÃO")
    print("=" * 50)
    
    try:
        # Criar ofertas de teste
        test_offers = [
            Offer(
                title="Smartphone Samsung Galaxy S23",
                price=Decimal("2999.99"),
                original_price=Decimal("3999.99"),
                discount_percentage=25,
                store="Samsung",
                category="eletronicos",
                url="https://exemplo.com/produto1",
                affiliate_url="https://awin.com/affiliate1",
                image_url="https://exemplo.com/imagem1.jpg",
                source="awin",
                scraped_at=datetime.now()
            ),
            Offer(
                title="Notebook Dell Inspiron 15",
                price=Decimal("2499.99"),
                original_price=Decimal("3499.99"),
                discount_percentage=29,
                store="COMFY",
                category="informatica",
                url="https://exemplo.com/produto2",
                affiliate_url="https://awin.com/affiliate2",
                image_url="https://exemplo.com/imagem2.jpg",
                source="awin",
                scraped_at=datetime.now()
            ),
            Offer(
                title="Console PlayStation 5",
                price=Decimal("3999.99"),
                original_price=Decimal("4999.99"),
                discount_percentage=20,
                store="Kabum",
                category="games",
                url="https://exemplo.com/produto3",
                affiliate_url="https://awin.com/affiliate3",
                image_url="https://exemplo.com/imagem3.jpg",
                source="awin",
                scraped_at=datetime.now()
            )
        ]
        
        print(f"✅ Ofertas de teste criadas: {len(test_offers)}")
        
        # Testar filtros automáticos
        from pipelines.auto_filters import apply_auto_filters
        
        filtered_offers = await apply_auto_filters(test_offers)
        print(f"✅ Filtros aplicados: {len(filtered_offers)}/{len(test_offers)} ofertas passaram")
        
        # Verificar estatísticas do motor de filtros
        from pipelines.auto_filters import get_filter_engine
        filter_engine = get_filter_engine()
        filter_stats = filter_engine.get_stats()
        print(f"✅ Estatísticas dos filtros: {filter_stats}")
        
        print("✅ INTEGRAÇÃO: TESTE PASSOU")
        return True
        
    except Exception as e:
        print(f"❌ INTEGRAÇÃO: ERRO - {e}")
        return False

async def test_performance():
    """Testa performance do sistema"""
    print("\n🧪 TESTANDO PERFORMANCE")
    print("=" * 50)
    
    try:
        import time
        
        # Testar performance dos filtros
        filter_engine = AutoFilterEngine()
        
        # Criar muitas ofertas de teste
        many_offers = []
        for i in range(1000):
            offer = Offer(
                title=f"Produto Teste {i}",
                price=Decimal(str(100.0 + (i % 100))),
                discount_percentage=10 + (i % 20),
                store=f"Loja {i % 10}",
                category=["eletronicos", "informatica", "games", "casa"][i % 4],
                url=f"https://exemplo.com/produto{i}",
                affiliate_url=f"https://awin.com/affiliate{i}",
                source="awin",
                scraped_at=datetime.now()
            )
            many_offers.append(offer)
        
        print(f"✅ {len(many_offers)} ofertas de teste criadas")
        
        # Medir tempo de filtragem
        start_time = time.time()
        filtered = await filter_engine.apply_filters(many_offers)
        end_time = time.time()
        
        processing_time = end_time - start_time
        offers_per_second = len(many_offers) / processing_time
        
        print(f"✅ Performance: {len(filtered)} ofertas filtradas em {processing_time:.2f}s")
        print(f"✅ Velocidade: {offers_per_second:.0f} ofertas/segundo")
        
        print("✅ PERFORMANCE: TESTE PASSOU")
        return True
        
    except Exception as e:
        print(f"❌ PERFORMANCE: ERRO - {e}")
        return False

async def main():
    """Função principal de teste"""
    print("🚀 INICIANDO TESTES DO SISTEMA INTELIGENTE")
    print("=" * 60)
    
    test_results = []
    
    # Executar testes
    tests = [
        ("AwinOffersCollector", test_awin_offers_collector),
        ("AutoFilterEngine", test_auto_filter_engine),
        ("AwinIngestPipeline", test_awin_ingest_pipeline),
        ("Integração", test_integration),
        ("Performance", test_performance)
    ]
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            test_results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name}: ERRO CRÍTICO - {e}")
            test_results.append((test_name, False))
    
    # Relatório final
    print("\n📊 RELATÓRIO FINAL DOS TESTES")
    print("=" * 60)
    
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{status}: {test_name}")
    
    print(f"\n🎯 RESULTADO FINAL: {passed}/{total} testes passaram")
    
    if passed == total:
        print("🎉 TODOS OS TESTES PASSARAM! Sistema inteligente funcionando perfeitamente!")
        return True
    else:
        print("⚠️ Alguns testes falharam. Verificar implementação.")
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 Testes interrompidos pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro crítico nos testes: {e}")
        sys.exit(1)
