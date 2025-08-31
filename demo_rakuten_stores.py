#!/usr/bin/env python3
"""
Demonstração das funcionalidades das lojas Rakuten configuradas
Hype Games (MID 53304) e Nuuvem (MID 46796)
"""

import asyncio
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

async def demo_rakuten_stores():
    """Demonstra as funcionalidades das lojas Rakuten"""
    
    try:
        from src.affiliate.rakuten_api import RakutenAPIClient
        
        print("🎮 DEMONSTRAÇÃO DAS LOJAS RAKUTEN CONFIGURADAS")
        print("=" * 60)
        
        # Criar cliente (sem credenciais reais para demonstração)
        client = RakutenAPIClient("demo_id", "demo_secret")
        
        # 1. Listar todas as lojas disponíveis
        print("\n📋 1. LOJAS DISPONÍVEIS:")
        stores = client.get_available_stores()
        for store_id, store_info in stores.items():
            print(f"   🏪 {store_info['name']}")
            print(f"      - ID: {store_id}")
            print(f"      - MID: {store_info['mid']}")
            print(f"      - Categoria: {store_info['category']}")
            print(f"      - Status: {'✅ Ativa' if store_info['enabled'] else '❌ Inativa'}")
            print()
        
        # 2. Informações específicas de cada loja
        print("🔍 2. INFORMAÇÕES DETALHADAS:")
        for store_id in ["hype_games", "nuuvem"]:
            store_info = client.get_store_info(store_id)
            if store_info:
                print(f"   🏪 {store_info['name']} ({store_id})")
                print(f"      - MID: {store_info['mid']}")
                print(f"      - Categoria: {store_info['category']}")
                print(f"      - Descrição: {store_info.get('description', 'N/A')}")
                print()
        
        # 3. Obter MIDs específicos
        print("🆔 3. MIDs DAS LOJAS:")
        hype_mid = client.get_store_mid("hype_games")
        nuuvem_mid = client.get_store_mid("nuuvem")
        
        print(f"   🎮 Hype Games: MID {hype_mid}")
        print(f"   💻 Nuuvem: MID {nuuvem_mid}")
        
        # 4. Exemplo de uso prático
        print("\n💡 4. EXEMPLO DE USO PRÁTICO:")
        print("   # Para gerar deeplink da Hype Games:")
        print("   deeplink = await client.build_store_deeplink(")
        print('       "hype_games",')
        print('       "https://www.hypegames.com.br/produto/123",')
        print('       "telegram"')
        print("   )")
        print()
        print("   # Para gerar deeplink da Nuuvem:")
        print("   deeplink = await client.build_store_deeplink(")
        print('       "nuuvem",')
        print('       "https://www.nuuvem.com.br/produto/456",')
        print('       "telegram"')
        print("   )")
        
        # 5. Verificação de configuração
        print("\n✅ 5. VERIFICAÇÃO DE CONFIGURAÇÃO:")
        config_ok = True
        
        # Verificar se todas as lojas estão configuradas
        for store_id in ["hype_games", "nuuvem"]:
            store_info = client.get_store_info(store_id)
            if not store_info:
                print(f"   ❌ {store_id}: Não configurada")
                config_ok = False
            elif not store_info.get("enabled"):
                print(f"   ⚠️ {store_id}: Configurada mas desabilitada")
                config_ok = False
            else:
                print(f"   ✅ {store_id}: Configurada e ativa")
        
        # Verificar se os MIDs estão corretos
        expected_mids = {
            "hype_games": "53304",
            "nuuvem": "46796"
        }
        
        for store_id, expected_mid in expected_mids.items():
            actual_mid = client.get_store_mid(store_id)
            if actual_mid == expected_mid:
                print(f"   ✅ {store_id}: MID correto ({actual_mid})")
            else:
                print(f"   ❌ {store_id}: MID incorreto")
                config_ok = False
        
        print("\n" + "=" * 60)
        if config_ok:
            print("🎉 CONFIGURAÇÃO COMPLETA E FUNCIONAL!")
            print("✅ Todas as lojas Rakuten estão configuradas corretamente")
            print("🚀 Sistema pronto para gerar deeplinks das lojas configuradas")
        else:
            print("⚠️ ALGUNS PROBLEMAS NA CONFIGURAÇÃO")
            print("🔧 Verifique as configurações das lojas acima")
        
        return config_ok
        
    except ImportError as e:
        print(f"❌ Erro ao importar módulo: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro durante a demonstração: {e}")
        return False

async def main():
    """Função principal"""
    
    print("🚀 Iniciando demonstração das lojas Rakuten...")
    
    success = await demo_rakuten_stores()
    
    if success:
        print("\n🎯 PRÓXIMOS PASSOS RECOMENDADOS:")
        print("1. Testar dashboard com nova aba de controles avançados")
        print("2. Configurar alertas para Telegram/email")
        print("3. Implementar agendamentos automáticos")
        print("4. Personalizar thresholds de alertas")
        print("5. Treinar equipe nas novas funcionalidades")
    
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
