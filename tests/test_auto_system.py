#!/usr/bin/env python3
"""
Teste do Sistema Automático - Garimpeiro Geek
Testa a funcionalidade do sistema automático de postagem
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from auto_telegram_system import AutoTelegramSystem

async def test_auto_system():
    """Testa o sistema automático"""
    print("🧪 TESTE DO SISTEMA AUTOMÁTICO - GARIMPEIRO GEEK")
    print("=" * 60)
    
    # Criar sistema
    auto_system = AutoTelegramSystem()
    
    try:
        print("1️⃣ Testando configuração do bot...")
        bot_ok = await auto_system.setup_telegram_bot()
        
        if not bot_ok:
            print("❌ Falha na configuração do bot")
            return False
        
        print("✅ Bot configurado com sucesso")
        
        print("\n2️⃣ Testando criação de ofertas...")
        offers = auto_system.create_sample_offers()
        print(f"✅ {len(offers)} ofertas criadas")
        
        print("\n3️⃣ Testando detecção de plataformas...")
        for offer in offers[:3]:  # Testar apenas 3
            platform = auto_system.detect_platform(offer)
            print(f"   {offer.store} → {platform}")
        
        print("\n4️⃣ Testando jobs...")
        
        # Testar job de coleta
        print("   🎯 Testando coleta de ofertas...")
        await auto_system.collect_offers_job()
        print(f"   ✅ Fila de ofertas: {len(auto_system.offer_queue)} ofertas")
        
        # Testar job de postagem
        print("   📝 Testando postagem de ofertas...")
        await auto_system.post_offers_job()
        print(f"   ✅ Ofertas postadas: {auto_system.posted_count}")
        
        print("\n5️⃣ Verificando status do sistema...")
        status = auto_system.get_system_status()
        print(f"   Status: {status}")
        
        print("\n🎉 TODOS OS TESTES PASSARAM COM SUCESSO!")
        print("🚀 Sistema automático funcionando perfeitamente")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Erro nos testes: {e}")
        return False

async def demo_auto_system():
    """Demonstra o sistema automático funcionando"""
    print("\n🎬 DEMONSTRAÇÃO DO SISTEMA AUTOMÁTICO")
    print("=" * 60)
    
    auto_system = AutoTelegramSystem()
    
    try:
        print("🚀 Iniciando demonstração...")
        
        # Configurar bot
        await auto_system.setup_telegram_bot()
        
        # Executar alguns ciclos de demonstração
        for cycle in range(3):
            print(f"\n🔄 Ciclo {cycle + 1}/3")
            
            # Coletar ofertas
            await auto_system.collect_offers_job()
            print(f"   📊 Ofertas na fila: {len(auto_system.offer_queue)}")
            
            # Postar algumas ofertas
            for i in range(2):
                if auto_system.offer_queue:
                    await auto_system.post_offers_job()
                    await asyncio.sleep(2)  # Delay entre posts
            
            print(f"   ✅ Total postado: {auto_system.posted_count}")
            await asyncio.sleep(3)  # Delay entre ciclos
        
        print(f"\n🎉 Demonstração concluída!")
        print(f"📊 Resumo: {auto_system.posted_count} ofertas postadas")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Erro na demonstração: {e}")
        return False

async def main():
    """Função principal"""
    print("🧪 TESTE E DEMONSTRAÇÃO DO SISTEMA AUTOMÁTICO")
    print("=" * 60)
    
    # Executar testes
    print("\n1️⃣ EXECUTANDO TESTES...")
    tests_ok = await test_auto_system()
    
    if not tests_ok:
        print("\n❌ Testes falharam. Verifique a configuração.")
        return
    
    # Executar demonstração
    print("\n2️⃣ EXECUTANDO DEMONSTRAÇÃO...")
    demo_ok = await demo_auto_system()
    
    if demo_ok:
        print("\n🎉 SISTEMA AUTOMÁTICO FUNCIONANDO PERFEITAMENTE!")
        print("🚀 Pronto para ativação em produção!")
        print("\n💡 Para ativar o sistema completo, execute:")
        print("   python auto_telegram_system.py")
    else:
        print("\n⚠️ Demonstração falhou. Verifique os logs.")


if __name__ == "__main__":
    asyncio.run(main())
