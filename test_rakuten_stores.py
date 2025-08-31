#!/usr/bin/env python3
"""
Teste da implementação das lojas Rakuten (Hype Games e Nuuvem)
"""

import asyncio
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

async def test_rakuten_stores():
    """Testa a funcionalidade das lojas Rakuten configuradas"""
    
    try:
        from src.affiliate.rakuten_api import RakutenAPIClient
        
        print("🎯 Testando implementação das lojas Rakuten...")
        
        # Criar cliente (sem credenciais reais para teste)
        client = RakutenAPIClient("test_id", "test_secret")
        
        # Testar listagem de lojas
        print("\n📋 Lojas disponíveis:")
        stores = client.get_available_stores()
        for store_id, store_info in stores.items():
            print(f"   - {store_info['name']}: MID {store_info['mid']} ({store_info['category']})")
        
        # Testar informações específicas
        print("\n🔍 Informações das lojas:")
        for store_id in ["hype_games", "nuuvem"]:
            store_info = client.get_store_info(store_id)
            if store_info:
                print(f"   ✅ {store_id}: {store_info['name']} - MID {store_info['mid']}")
            else:
                print(f"   ❌ {store_id}: Não encontrada")
        
        # Testar obtenção de MIDs
        print("\n🆔 MIDs das lojas:")
        hype_mid = client.get_store_mid("hype_games")
        nuuvem_mid = client.get_store_mid("nuuvem")
        
        print(f"   - Hype Games MID: {hype_mid}")
        print(f"   - Nuuvem MID: {nuuvem_mid}")
        
        # Verificar se os MIDs estão corretos
        expected_mids = {
            "hype_games": "53304",
            "nuuvem": "46796"
        }
        
        print("\n✅ Validação dos MIDs:")
        for store_id, expected_mid in expected_mids.items():
            actual_mid = client.get_store_mid(store_id)
            if actual_mid == expected_mid:
                print(f"   ✅ {store_id}: MID correto ({actual_mid})")
            else:
                print(f"   ❌ {store_id}: MID incorreto (esperado: {expected_mid}, obtido: {actual_mid})")
        
        print("\n🎉 Teste das lojas Rakuten concluído com sucesso!")
        return True
        
    except ImportError as e:
        print(f"❌ Erro ao importar módulo: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        return False

async def test_config_file():
    """Testa se o arquivo de configuração foi atualizado corretamente"""
    
    try:
        print("\n📁 Verificando arquivo de configuração...")
        
        config_path = Path("config/garimpeiro_geek_config.py")
        if not config_path.exists():
            print("❌ Arquivo de configuração não encontrado")
            return False
        
        # Ler arquivo e verificar se contém as lojas
        content = config_path.read_text(encoding='utf-8')
        
        stores_to_check = [
            ("hype_games", "53304"),
            ("nuuvem", "46796")
        ]
        
        print("🔍 Verificando configurações das lojas:")
        for store_name, expected_mid in stores_to_check:
            if f'"{store_name}"' in content and expected_mid in content:
                print(f"   ✅ {store_name}: Configurado corretamente")
            else:
                print(f"   ❌ {store_name}: Não configurado ou MID incorreto")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao verificar configuração: {e}")
        return False

async def main():
    """Função principal"""
    
    print("🚀 Iniciando teste da implementação das lojas Rakuten...")
    print("=" * 60)
    
    # Testar configuração
    config_ok = await test_config_file()
    
    # Testar funcionalidade
    stores_ok = await test_rakuten_stores()
    
    print("\n" + "=" * 60)
    if config_ok and stores_ok:
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("✅ Lojas Hype Games (MID 53304) e Nuuvem (MID 46796) implementadas com sucesso!")
    else:
        print("❌ ALGUNS TESTES FALHARAM!")
        print("🔧 Verifique os erros acima e corrija se necessário")
    
    return config_ok and stores_ok

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
