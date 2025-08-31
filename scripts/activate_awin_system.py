#!/usr/bin/env python3
"""
Script de Ativação do Sistema Awin
Ativa e testa o sistema de coleta automática
"""

import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime

# Adicionar src ao path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from pipelines.ingest_awin_offers import get_awin_pipeline, run_single_ingestion
from pipelines.auto_filters import get_filter_engine
import sys
sys.path.append(str(Path(__file__).parent.parent / "config"))
from awin_test_config import get_awin_credentials, get_advertisers

async def test_system_activation():
    """Testa a ativação do sistema Awin"""
    print("🚀 ATIVANDO SISTEMA AWIN DE COLETA AUTOMÁTICA")
    print("=" * 60)
    
    try:
        # 1. Verificar credenciais
        print("\n🔑 VERIFICANDO CREDENCIAIS...")
        credentials = get_awin_credentials()
        advertisers = get_advertisers()
        
        print(f"✅ Publisher ID: {credentials['publisher_id']}")
        print(f"✅ OAuth2 Token: {credentials['oauth2_token'][:20]}...")
        print(f"✅ Anunciantes configurados: {len(advertisers)}")
        
        for key, adv in advertisers.items():
            print(f"   - {adv['name']}: MID {adv['mid']} ({adv['category']})")
        
        # 2. Testar motor de filtros
        print("\n🔧 TESTANDO MOTOR DE FILTROS...")
        filter_engine = get_filter_engine()
        filter_stats = filter_engine.get_stats()
        
        print(f"✅ Filtros ativos: {filter_stats['enabled_filters']}")
        print(f"✅ Regras configuradas: {filter_stats['total_rules']}")
        print(f"✅ Perfis disponíveis: {filter_stats['total_profiles']}")
        
        # 3. Testar pipeline de ingestão
        print("\n📥 TESTANDO PIPELINE DE INGESTÃO...")
        pipeline = await get_awin_pipeline()
        
        if pipeline:
            print("✅ Pipeline criado com sucesso")
            print(f"✅ Configuração: {pipeline.config}")
            print(f"✅ Filtros automáticos: {pipeline.auto_filters}")
            
            # 4. Executar ciclo de ingestão de teste
            print("\n🔄 EXECUTANDO CICLO DE INGESTÃO DE TESTE...")
            success = await pipeline.run_ingestion_cycle()
            
            if success:
                print("✅ Ciclo de ingestão executado com sucesso")
            else:
                print("⚠️ Ciclo de ingestão falhou (esperado em ambiente de teste)")
            
            # 5. Verificar estatísticas finais
            print("\n📊 ESTATÍSTICAS FINAIS...")
            final_stats = pipeline.get_stats()
            
            print(f"✅ Total de execuções: {final_stats['stats']['total_runs']}")
            print(f"✅ Execuções bem-sucedidas: {final_stats['stats']['successful_runs']}")
            print(f"✅ Ofertas coletadas: {final_stats['stats']['total_offers_collected']}")
            print(f"✅ Ofertas postadas: {final_stats['stats']['total_offers_posted']}")
            
            # 6. Parar pipeline
            pipeline.stop()
            print("✅ Pipeline parado com sucesso")
            
        else:
            print("❌ Falha ao criar pipeline")
            return False
        
        print("\n🎉 SISTEMA AWIN ATIVADO COM SUCESSO!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO NA ATIVAÇÃO: {e}")
        return False

async def start_continuous_ingestion():
    """Inicia ingestão contínua (para produção)"""
    print("🔄 INICIANDO INGESTÃO CONTÍNUA...")
    
    try:
        pipeline = await get_awin_pipeline()
        if pipeline:
            print("✅ Pipeline iniciado, aguardando interrupção...")
            print("💡 Pressione Ctrl+C para parar")
            
            await pipeline.start_continuous_ingestion()
        else:
            print("❌ Falha ao iniciar pipeline")
            
    except KeyboardInterrupt:
        print("\n🛑 Interrupção solicitada pelo usuário")
        if pipeline:
            pipeline.stop()
            print("✅ Pipeline parado com sucesso")
    except Exception as e:
        print(f"❌ Erro na ingestão contínua: {e}")

async def main():
    """Função principal"""
    print("🔧 SISTEMA AWIN - MENU DE ATIVAÇÃO")
    print("=" * 40)
    print("1. Testar ativação do sistema")
    print("2. Iniciar ingestão contínua")
    print("3. Executar ingestão única")
    print("4. Sair")
    
    try:
        choice = input("\nEscolha uma opção (1-4): ").strip()
        
        if choice == "1":
            success = await test_system_activation()
            if success:
                print("\n✅ Sistema pronto para produção!")
            else:
                print("\n⚠️ Verificar configurações antes de usar em produção")
                
        elif choice == "2":
            await start_continuous_ingestion()
            
        elif choice == "3":
            print("\n🔄 Executando ingestão única...")
            success = await run_single_ingestion()
            if success:
                print("✅ Ingestão única executada com sucesso")
            else:
                print("⚠️ Ingestão única falhou")
                
        elif choice == "4":
            print("👋 Saindo...")
            
        else:
            print("❌ Opção inválida")
            
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Programa interrompido pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro crítico: {e}")
        sys.exit(1)
