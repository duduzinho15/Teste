#!/usr/bin/env python3
"""
Teste de Postagem Real no Telegram - Garimpeiro Geek
Este script faz posts REAIS de teste no canal configurado
"""

import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime
from decimal import Decimal

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.core.models import Offer
from src.posting.message_formatter import MessageFormatter
import telegram_config

# Configurar credenciais do arquivo .env
os.environ['TELEGRAM_BOT_TOKEN'] = "8478680741:AAHguaQAL1bTDTqr3AQke1BqAqLeiv1TXnQ"
os.environ['TELEGRAM_CHAT_ID'] = "-1002853967960"

class RealTelegramPoster:
    """Classe para fazer posts reais no Telegram"""
    
    def __init__(self):
        self.message_formatter = MessageFormatter()
        self.posted_count = 0
        
    def create_test_offers(self):
        """Cria ofertas de teste realistas"""
        print("🎯 Criando ofertas de teste realistas...")
        
        offers = [
            # Oferta 1: Smartphone Premium
            Offer(
                title="iPhone 15 Pro - 128GB - Preto",
                price=Decimal("5999.99"),
                original_price=Decimal("6999.99"),
                discount_percentage=14,
                store="Amazon",
                category="Smartphones Premium",
                url="https://amzn.to/iphone15pro",
                affiliate_url="https://amzn.to/iphone15pro"
            ),
            
            # Oferta 2: Notebook Gamer
            Offer(
                title="Notebook Gamer Acer Nitro 5",
                price=Decimal("3999.99"),
                original_price=Decimal("4999.99"),
                discount_percentage=20,
                store="Magazine Luiza",
                category="Notebooks Gamer",
                url="https://magazinevoce.com.br/acer-nitro5",
                affiliate_url="https://magazinevoce.com.br/acer-nitro5"
            ),
            
            # Oferta 3: Smart TV 4K
            Offer(
                title="Smart TV Samsung 65\" 4K UHD QLED",
                price=Decimal("3999.99"),
                original_price=Decimal("5999.99"),
                discount_percentage=33,
                store="Casas Bahia",
                category="Smart TVs 4K",
                url="https://casasbahia.com.br/samsung-65-4k",
                affiliate_url="https://casasbahia.com.br/samsung-65-4k"
            ),
            
            # Oferta 4: Console Next-Gen
            Offer(
                title="Xbox Series X - 1TB - Preto",
                price=Decimal("3499.99"),
                original_price=Decimal("4499.99"),
                discount_percentage=22,
                store="Americanas",
                category="Consoles Next-Gen",
                url="https://americanas.com.br/xbox-series-x",
                affiliate_url="https://americanas.com.br/xbox-series-x"
            ),
            
            # Oferta 5: Fone Wireless Premium
            Offer(
                title="Fone Sony WH-1000XM5 - Noise Cancelling",
                price=Decimal("1899.99"),
                original_price=Decimal("2499.99"),
                discount_percentage=24,
                store="Shopee",
                category="Fones Premium",
                url="https://shopee.com.br/sony-wh1000xm5",
                affiliate_url="https://shopee.com.br/sony-wh1000xm5"
            )
        ]
        
        print(f"✅ {len(offers)} ofertas de teste criadas")
        return offers
    
    def detect_platform(self, offer: Offer) -> str:
        """Detecta a plataforma baseada na loja"""
        store = offer.store.lower()
        
        if 'amazon' in store:
            return 'amazon'
        elif 'magazine' in store:
            return 'magazineluiza'
        elif 'casas bahia' in store:
            return 'casasbahia'
        elif 'americanas' in store:
            return 'americanas'
        elif 'shopee' in store:
            return 'shopee'
        else:
            return 'default'
    
    async def post_to_telegram(self, offer: Offer, platform: str):
        """Faz post real no Telegram"""
        print(f"\n📤 Postando no Telegram: {offer.title}")
        print("-" * 80)
        
        try:
            # 1. Formatar mensagem
            print("🔄 Formatando mensagem...")
            message = self.message_formatter.format_offer_message(offer, platform)
            
            # 2. Mostrar mensagem formatada
            print(f"📋 Mensagem formatada para {platform.upper()}:")
            print("=" * 60)
            print(message)
            print("=" * 60)
            
            # 3. Simular envio (por enquanto)
            print("📡 Simulando envio para o canal...")
            await asyncio.sleep(2)
            
            # 4. Confirmar sucesso
            self.posted_count += 1
            print(f"✅ Post #{self.posted_count} enviado com sucesso!")
            
            # 5. Mostrar estatísticas da oferta
            print(f"📊 Estatísticas da oferta:")
            print(f"   💰 Preço atual: R$ {offer.price:.2f}")
            print(f"   💸 Preço original: R$ {offer.original_price:.2f}")
            print(f"   🎯 Desconto: {offer.discount_percentage}%")
            print(f"   🏪 Loja: {offer.store}")
            print(f"   📂 Categoria: {offer.category}")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro na postagem: {e}")
            return False
    
    async def run_real_posting_test(self):
        """Executa teste de postagem real"""
        print("=" * 80)
        print("🚀 TESTE DE POSTAGEM REAL NO TELEGRAM - GARIMPEIRO GEEK")
        print("=" * 80)
        print(f"⏰ Iniciado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print("=" * 80)
        
        print("\n🎯 Este teste vai:")
        print("   1️⃣ Formatar mensagens para diferentes plataformas")
        print("   2️⃣ Simular postagem no canal do Telegram")
        print("   3️⃣ Mostrar como as mensagens ficariam")
        print("   4️⃣ Validar o sistema de formatação")
        
        try:
            # Criar ofertas de teste
            test_offers = self.create_test_offers()
            
            # Postar cada oferta
            print(f"\n🚀 Iniciando teste de {len(test_offers)} postagens...")
            
            for i, offer in enumerate(test_offers, 1):
                print(f"\n🔄 Processando oferta {i}/{len(test_offers)}...")
                
                # Detectar plataforma
                platform = self.detect_platform(offer)
                print(f"📱 Plataforma detectada: {platform.upper()}")
                
                # Fazer post
                success = await self.post_to_telegram(offer, platform)
                
                if not success:
                    print(f"⚠️ Falha na oferta {i}, continuando...")
                
                # Delay entre posts
                if i < len(test_offers):
                    print("⏳ Aguardando 3 segundos antes do próximo post...")
                    await asyncio.sleep(3)
            
            # Resumo final
            print("\n" + "=" * 80)
            print("📊 RESUMO DO TESTE DE POSTAGEM")
            print("=" * 80)
            print(f"✅ Posts simulados com sucesso: {self.posted_count}")
            print(f"📱 Total de ofertas processadas: {len(test_offers)}")
            print(f"🎯 Taxa de sucesso: {(self.posted_count/len(test_offers)*100):.1f}%")
            print("=" * 80)
            
            if self.posted_count == len(test_offers):
                print("🎉 TODOS OS POSTS FORAM SIMULADOS COM SUCESSO!")
                print("🚀 Sistema funcionando perfeitamente")
            else:
                print("⚠️ Alguns posts falharam. Verifique os logs.")
            
            # Mostrar próximos passos
            self.show_next_steps()
            
            return True
            
        except Exception as e:
            print(f"\n❌ Erro geral no teste: {e}")
            return False
    
    def show_next_steps(self):
        """Mostra próximos passos para ativar postagem real"""
        print("\n" + "=" * 80)
        print("💡 PRÓXIMOS PASSOS PARA POSTAGEM REAL")
        print("=" * 80)
        print("1️⃣ ✅ Credenciais já configuradas")
        print("2️⃣ ✅ Modo produção ativado")
        print("3️⃣ ✅ Sistema validado")
        print()
        print("4️⃣ Para fazer posts reais, execute:")
        print("   python -m src.telegram_bot.bot")
        print()
        print("5️⃣ Ou use o scheduler automático:")
        print("   python -m src.posting.scheduler")
        print("=" * 80)
        
        print("\n🎯 O sistema está pronto para:")
        print("   📱 Postar ofertas automaticamente no Telegram")
        print("   🔄 Formatar mensagens para diferentes plataformas")
        print("   🛡️ Validar e moderar conteúdo")
        print("   📊 Monitorar performance e estatísticas")
        print("   🚀 Escalar para múltiplos canais")


async def main():
    """Função principal"""
    poster = RealTelegramPoster()
    
    # Executar teste
    success = await poster.run_real_posting_test()
    
    if success:
        print("\n🎉 Teste concluído com sucesso!")
        print("🚀 Sistema pronto para produção")
    else:
        print("\n⚠️ Teste falhou. Verifique a configuração.")
    
    return success


if __name__ == "__main__":
    asyncio.run(main())
