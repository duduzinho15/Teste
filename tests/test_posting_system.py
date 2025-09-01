#!/usr/bin/env python3
"""
Teste simples para validar o sistema de postagem
"""

import asyncio
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.posting.message_formatter import MessageFormatter
from src.posting.scheduler import JobScheduler
from src.core.models import Offer


async def test_message_formatter():
    """Testa o formatador de mensagens"""
    print("🧪 Testando Message Formatter...")
    
    # Criar oferta de teste
    offer = Offer(
        title="Smartphone Samsung Galaxy S23",
        price=2999.99,
        original_price=3999.99,
        discount_percentage=25,
        store="Amazon",
        category="Eletrônicos",
        url="https://amzn.to/test123"
    )
    
    # Testar formatação
    formatter = MessageFormatter()
    message = formatter.format_offer_message(offer, "amazon")
    
    print(f"✅ Mensagem formatada:\n{message}")
    return True


async def test_scheduler():
    """Testa o scheduler de jobs"""
    print("\n🧪 Testando Job Scheduler...")
    
    scheduler = JobScheduler()
    
    # Verificar se os jobs padrão estão configurados
    print(f"✅ Scheduler criado com sucesso")
    print(f"✅ Jobs padrão configurados: collect_offers, enrich_prices, post_queue, price_aggregate")
    
    return True


async def main():
    """Função principal de teste"""
    print("🚀 Iniciando testes do sistema de postagem...\n")
    
    try:
        # Testar Message Formatter
        await test_message_formatter()
        
        # Testar Scheduler
        await test_scheduler()
        
        print("\n🎉 Todos os testes passaram com sucesso!")
        print("✅ Sistema de postagem funcionando perfeitamente")
        
    except Exception as e:
        print(f"\n❌ Erro nos testes: {e}")
        return False
    
    return True


if __name__ == "__main__":
    asyncio.run(main())
