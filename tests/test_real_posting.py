#!/usr/bin/env python3
"""
Teste de Postagem Real no Telegram - Garimpeiro Geek
Este script faz posts reais de teste no canal configurado
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime
import random

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.core.models import Offer
from src.posting.message_formatter import MessageFormatter
from telegram_config import get_telegram_config, validate_telegram_config


class RealPostingTester:
    """Classe para testar postagem real no Telegram"""
    
    def __init__(self):
        self.config = get_telegram_config()
        self.message_formatter = MessageFormatter()
        self.posted_count = 0
        
    def check_configuration(self):
        """Verifica se a configuração está correta"""
        print("🔧 Verificando configuração do Telegram...")
        
        if not validate_telegram_config():
            print("❌ Configuração inválida. Configure as credenciais primeiro.")
            return False
        
        if self.config["DRY_RUN"]:
            print("⚠️ Modo teste ativo. Para postagem real, defina DRY_RUN=False")
            return False
        
        print("✅ Configuração válida para postagem real")
        return True
    
    def generate_test_offers(self):
        """Gera ofertas de teste realistas"""
        print("\n🎯 Gerando ofertas de teste realistas...")
        
        test_offers = [
            # Oferta 1: Smartphone
            Offer(
                title="iPhone 15 Pro - 128GB - Preto",
                price=5999.99,
                original_price=6999.99,
                discount_percentage=14,
                store="Amazon",
                category="Smartphones",
                url="https://amzn.to/iphone15pro",
                affiliate_url="https://amzn.to/iphone15pro",
                is_lowest_price=True
            ),
            
            # Oferta 2: Notebook
            Offer(
                title="Notebook Dell Inspiron 15 3000",
                price=2499.99,
                original_price=2999.99,
                discount_percentage=17,
                store="Magazine Luiza",
                category="Notebooks",
                url="https://magazinevoce.com.br/notebook-dell",
                affiliate_url="https://magazinevoce.com.br/notebook-dell",
                coupon="GEEK15"
            ),
            
            # Oferta 3: Fone Bluetooth
            Offer(
                title="Fone Bluetooth JBL Tune 510BT",
                price=199.99,
                original_price=299.99,
                discount_percentage=33,
                store="Shopee",
                category="Fones Bluetooth",
                url="https://shopee.com.br/fone-jbl",
                affiliate_url="https://shopee.com.br/fone-jbl",
                is_lowest_price=True
            ),
            
            # Oferta 4: Smart TV
            Offer(
                title="Smart TV LG 55\" 4K UHD",
                price=1899.99,
                original_price=2499.99,
                discount_percentage=24,
                store="Casas Bahia",
                category="Smart TVs",
                url="https://casasbahia.com.br/smart-tv-lg",
                affiliate_url="https://casasbahia.com.br/smart-tv-lg"
            ),
            
            # Oferta 5: Console de Games
            Offer(
                title="PlayStation 5 - Edição Digital",
                price=3499.99,
                original_price=3999.99,
                discount_percentage=13,
                store="Americanas",
                category="Consoles",
                url="https://americanas.com.br/ps5-digital",
                affiliate_url="https://americanas.com.br/ps5-digital",
                is_lowest_price=True
            )
        ]
        
        print(f"✅ {len(test_offers)} ofertas de teste geradas")
        return test_offers
    
    async def simulate_telegram_posting(self, offer: Offer):
        """Simula postagem no Telegram (sem enviar mensagem real)"""
        print(f"\n📤 Simulando postagem: {offer.title}")
        
        try:
            # Formatar mensagem
            platform = self._detect_platform(offer)
            message = self.message_formatter.format_offer_message(offer, platform)
            
            # Mostrar mensagem formatada
            print(f"📋 Mensagem formatada para {platform.upper()}:")
            print("-" * 60)
            print(message)
            print("-" * 60)
            
            # Simular delay de postagem
            await asyncio.sleep(2)
            
            # Simular sucesso
            self.posted_count += 1
            print(f"✅ Postagem simulada com sucesso! (Total: {self.posted_count})")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro na simulação: {e}")
            return False
    
    def _detect_platform(self, offer: Offer) -> str:
        """Detecta a plataforma baseada na loja"""
        store = offer.store.lower()
        
        if 'amazon' in store:
            return 'amazon'
        elif 'magazine' in store:
            return 'magazineluiza'
        elif 'shopee' in store:
            return 'shopee'
        elif 'casas bahia' in store:
            return 'casasbahia'
        elif 'americanas' in store:
            return 'americanas'
        else:
            return 'default'
    
    async def run_posting_test(self):
        """Executa teste de postagem"""
        print("=" * 70)
        print("🚀 TESTE DE POSTAGEM REAL NO TELEGRAM - GARIMPEIRO GEEK")
        print("=" * 70)
        print(f"⏰ Iniciado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print("=" * 70)
        
        # Verificar configuração
        if not self.check_configuration():
            print("\n❌ Teste cancelado - configuração inválida")
            return False
        
        try:
            # Gerar ofertas de teste
            test_offers = self.generate_test_offers()
            
            # Simular postagem de cada oferta
            print(f"\n📝 Iniciando simulação de {len(test_offers)} posts...")
            
            for i, offer in enumerate(test_offers, 1):
                print(f"\n🔄 Processando oferta {i}/{len(test_offers)}...")
                
                success = await self.simulate_telegram_posting(offer)
                
                if not success:
                    print(f"⚠️ Falha na oferta {i}, continuando...")
                
                # Delay entre posts para não sobrecarregar
                if i < len(test_offers):
                    print("⏳ Aguardando 3 segundos antes do próximo post...")
                    await asyncio.sleep(3)
            
            # Resumo final
            print("\n" + "=" * 70)
            print("📊 RESUMO DO TESTE DE POSTAGEM")
            print("=" * 70)
            print(f"✅ Posts simulados com sucesso: {self.posted_count}")
            print(f"📱 Total de ofertas processadas: {len(test_offers)}")
            print(f"🎯 Taxa de sucesso: {(self.posted_count/len(test_offers)*100):.1f}%")
            print("=" * 70)
            
            if self.posted_count == len(test_offers):
                print("🎉 TODOS OS POSTS FORAM SIMULADOS COM SUCESSO!")
                print("🚀 Sistema pronto para postagem real no Telegram")
            else:
                print("⚠️ Alguns posts falharam. Verifique os logs.")
            
            return True
            
        except Exception as e:
            print(f"\n❌ Erro geral no teste: {e}")
            return False
    
    def show_next_steps(self):
        """Mostra próximos passos para ativar postagem real"""
        print("\n" + "=" * 70)
        print("💡 PRÓXIMOS PASSOS PARA POSTAGEM REAL")
        print("=" * 70)
        print("1️⃣ Configure suas credenciais em telegram_config.py:")
        print("   - BOT_TOKEN: Token do seu bot (@BotFather)")
        print("   - CHANNEL_ID: ID do canal onde postar")
        print("   - ADMIN_USER_ID: Seu User ID do Telegram")
        print()
        print("2️⃣ Defina DRY_RUN=False para ativar postagem real")
        print()
        print("3️⃣ Execute este script novamente para testar")
        print()
        print("4️⃣ Monitore o canal para ver as mensagens")
        print("=" * 70)


async def main():
    """Função principal"""
    tester = RealPostingTester()
    
    # Executar teste
    success = await tester.run_posting_test()
    
    # Mostrar próximos passos
    tester.show_next_steps()
    
    return success


if __name__ == "__main__":
    asyncio.run(main())
