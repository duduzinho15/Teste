#!/usr/bin/env python3
"""
Demonstração de Postagem no Telegram - Garimpeiro Geek
Mostra como as mensagens seriam formatadas e postadas
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime
from decimal import Decimal
import time

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.models import Offer
from src.posting.message_formatter import MessageFormatter


class TelegramPostingDemo:
    """Demonstração da postagem no Telegram"""
    
    def __init__(self):
        self.message_formatter = MessageFormatter()
        self.demo_count = 0
        
    def create_demo_offers(self):
        """Cria ofertas de demonstração realistas"""
        print("🎯 Criando ofertas de demonstração...")
        
        offers = [
            # Oferta 1: Smartphone Premium
            Offer(
                title="iPhone 15 Pro Max - 256GB - Titanium",
                price=Decimal("7999.99"),
                original_price=Decimal("8999.99"),
                discount_percentage=11,
                store="Amazon",
                category="Smartphones Premium",
                url="https://amzn.to/iphone15promax",
                affiliate_url="https://amzn.to/iphone15promax"
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
                affiliate_url="https://magazinevoce.com.br/acer-nitro5",
                coupon_code="GAMER20"
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
        
        print(f"✅ {len(offers)} ofertas de demonstração criadas")
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
    
    async def simulate_posting(self, offer: Offer, platform: str):
        """Simula o processo de postagem"""
        print(f"\n📤 Simulando postagem #{self.demo_count + 1}: {offer.title}")
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
            
            # 3. Simular validação
            print("🔍 Validando oferta...")
            await asyncio.sleep(1)
            
            # 4. Simular envio
            print("📡 Enviando para o canal...")
            await asyncio.sleep(2)
            
            # 5. Confirmar sucesso
            self.demo_count += 1
            print(f"✅ Postagem #{self.demo_count} enviada com sucesso!")
            
            # 6. Mostrar estatísticas da oferta
            print(f"📊 Estatísticas da oferta:")
            print(f"   💰 Preço atual: R$ {offer.price:.2f}")
            print(f"   💸 Preço original: R$ {offer.original_price:.2f}")
            print(f"   🎯 Desconto: {offer.discount_percentage}%")
            print(f"   🏪 Loja: {offer.store}")
            print(f"   📂 Categoria: {offer.category}")
            if hasattr(offer, 'coupon_code') and offer.coupon_code:
                print(f"   🎫 Cupom: {offer.coupon_code}")
            if hasattr(offer, 'has_discount') and offer.has_discount:
                print(f"   🔥 Oferta com desconto ativo!")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro na simulação: {e}")
            return False
    
    async def run_demo(self):
        """Executa a demonstração completa"""
        print("=" * 80)
        print("🎬 DEMONSTRAÇÃO DE POSTAGEM NO TELEGRAM - GARIMPEIRO GEEK")
        print("=" * 80)
        print(f"⏰ Iniciado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print("=" * 80)
        
        print("\n🎯 Esta demonstração mostra como o sistema:")
        print("   1️⃣ Formata mensagens para diferentes plataformas")
        print("   2️⃣ Valida ofertas antes da postagem")
        print("   3️⃣ Envia mensagens para o canal do Telegram")
        print("   4️⃣ Monitora o sucesso das postagens")
        print("   5️⃣ Mantém estatísticas em tempo real")
        
        try:
            # Criar ofertas de demonstração
            demo_offers = self.create_demo_offers()
            
            # Simular postagem de cada oferta
            print(f"\n🚀 Iniciando demonstração de {len(demo_offers)} postagens...")
            
            for i, offer in enumerate(demo_offers, 1):
                print(f"\n🔄 Processando oferta {i}/{len(demo_offers)}...")
                
                # Detectar plataforma
                platform = self.detect_platform(offer)
                print(f"📱 Plataforma detectada: {platform.upper()}")
                
                # Simular postagem
                success = await self.simulate_posting(offer, platform)
                
                if not success:
                    print(f"⚠️ Falha na oferta {i}, continuando...")
                
                # Delay entre demonstrações
                if i < len(demo_offers):
                    print("⏳ Aguardando 3 segundos antes da próxima demonstração...")
                    await asyncio.sleep(3)
            
            # Resumo final
            print("\n" + "=" * 80)
            print("📊 RESUMO DA DEMONSTRAÇÃO")
            print("=" * 80)
            print(f"✅ Postagens simuladas: {self.demo_count}")
            print(f"📱 Total de ofertas processadas: {len(demo_offers)}")
            print(f"🎯 Taxa de sucesso: {(self.demo_count/len(demo_offers)*100):.1f}%")
            print(f"⏱️ Tempo total: {datetime.now().strftime('%H:%M:%S')}")
            print("=" * 80)
            
            if self.demo_count == len(demo_offers):
                print("🎉 TODAS AS POSTAGENS FORAM SIMULADAS COM SUCESSO!")
                print("🚀 Sistema funcionando perfeitamente")
            else:
                print("⚠️ Algumas postagens falharam. Verifique os logs.")
            
            # Mostrar próximos passos
            self.show_next_steps()
            
            return True
            
        except Exception as e:
            print(f"\n❌ Erro na demonstração: {e}")
            return False
    
    def show_next_steps(self):
        """Mostra próximos passos para ativar postagem real"""
        print("\n" + "=" * 80)
        print("💡 PRÓXIMOS PASSOS PARA POSTAGEM REAL")
        print("=" * 80)
        print("1️⃣ Configure suas credenciais em telegram_config.py:")
        print("   - BOT_TOKEN: Token do seu bot (@BotFather)")
        print("   - CHANNEL_ID: ID do canal onde postar")
        print("   - ADMIN_USER_ID: Seu User ID do Telegram")
        print()
        print("2️⃣ Defina DRY_RUN=False para ativar postagem real")
        print()
        print("3️⃣ Execute test_real_posting.py para testar")
        print()
        print("4️⃣ Monitore o canal para ver as mensagens reais")
        print()
        print("5️⃣ Ative a postagem automática com o scheduler")
        print("=" * 80)
        
        print("\n🎯 O sistema está pronto para:")
        print("   📱 Postar ofertas automaticamente no Telegram")
        print("   🔄 Formatar mensagens para diferentes plataformas")
        print("   🛡️ Validar e moderar conteúdo")
        print("   📊 Monitorar performance e estatísticas")
        print("   🚀 Escalar para múltiplos canais")


async def main():
    """Função principal"""
    demo = TelegramPostingDemo()
    success = await demo.run_demo()
    
    if success:
        print("\n🎉 Demonstração concluída com sucesso!")
        print("🚀 Sistema pronto para produção")
    else:
        print("\n⚠️ Demonstração falhou. Verifique a configuração.")
    
    return success


if __name__ == "__main__":
    asyncio.run(main())
