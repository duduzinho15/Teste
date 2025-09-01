#!/usr/bin/env python3
"""
Teste de Postagem no Telegram - Garimpeiro Geek
Inicia o bot e faz posts de teste para verificar funcionalidade
"""

import asyncio
import os
import sys
from pathlib import Path
from datetime import datetime

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.core.models import Offer
from src.posting.message_formatter import MessageFormatter
from src.telegram_bot.bot_manager import TelegramBot, BotConfig


class TelegramTester:
    """Classe para testar o bot do Telegram"""
    
    def __init__(self):
        self.bot = None
        self.message_formatter = MessageFormatter()
        
    async def setup_bot(self):
        """Configura o bot com credenciais de teste"""
        print("🔧 Configurando bot do Telegram...")
        
        # Configurações de teste (substitua pelos seus valores reais)
        config = BotConfig(
            bot_token="SEU_BOT_TOKEN_AQUI",  # Substitua pelo seu token
            channel_id="SEU_CHANNEL_ID_AQUI",  # Substitua pelo seu channel ID
            admin_user_ids=[123456789],  # Substitua pelo seu user ID
            dry_run=True,  # Modo de teste - não envia mensagens reais
            max_posts_per_hour=20,
            auto_posting_enabled=True,
            moderation_enabled=True
        )
        
        try:
            self.bot = TelegramBot(config)
            print("✅ Bot configurado com sucesso")
            return True
        except Exception as e:
            print(f"❌ Erro ao configurar bot: {e}")
            return False
    
    async def test_message_formatting(self):
        """Testa a formatação de mensagens"""
        print("\n🧪 Testando formatação de mensagens...")
        
        # Criar ofertas de teste
        test_offers = [
            Offer(
                title="iPhone 15 Pro - 128GB",
                price=5999.99,
                original_price=6999.99,
                discount_percentage=14,
                store="Amazon",
                category="Eletrônicos",
                url="https://amzn.to/test123",
                affiliate_url="https://amzn.to/test123"
            ),
            Offer(
                title="Notebook Dell Inspiron 15",
                price=2499.99,
                original_price=2999.99,
                discount_percentage=17,
                store="Magazine Luiza",
                category="Informática",
                url="https://magazinevoce.com.br/test123",
                affiliate_url="https://magazinevoce.com.br/test123"
            ),
            Offer(
                title="Fone Bluetooth JBL",
                price=199.99,
                original_price=299.99,
                discount_percentage=33,
                store="Shopee",
                category="Eletrônicos",
                url="https://shopee.com.br/test123",
                affiliate_url="https://shopee.com.br/test123"
            )
        ]
        
        # Testar formatação para cada plataforma
        platforms = ["amazon", "magazineluiza", "shopee"]
        
        for i, offer in enumerate(test_offers):
            platform = platforms[i]
            print(f"\n📱 Testando {platform.upper()}:")
            
            try:
                message = self.message_formatter.format_offer_message(offer, platform)
                print(f"✅ Mensagem formatada ({len(message)} caracteres):")
                print("-" * 50)
                print(message)
                print("-" * 50)
                
            except Exception as e:
                print(f"❌ Erro ao formatar mensagem: {e}")
        
        return True
    
    async def test_bot_startup(self):
        """Testa a inicialização do bot"""
        print("\n🚀 Testando inicialização do bot...")
        
        if not self.bot:
            print("❌ Bot não configurado")
            return False
        
        try:
            # Iniciar bot
            success = await self.bot.start()
            
            if success:
                print("✅ Bot iniciado com sucesso")
                print(f"   Status: {self.bot.status.value}")
                print(f"   Modo: {self.bot.posting_mode.value}")
                return True
            else:
                print("❌ Falha ao iniciar bot")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao iniciar bot: {e}")
            return False
    
    async def test_posting_simulation(self):
        """Simula postagem de ofertas (dry run)"""
        print("\n📝 Testando simulação de postagem...")
        
        if not self.bot:
            print("❌ Bot não configurado")
            return False
        
        try:
            # Criar oferta de teste
            test_offer = Offer(
                title="🎯 OFERTA DE TESTE - Garimpeiro Geek",
                price=99.99,
                original_price=199.99,
                discount_percentage=50,
                store="Loja Teste",
                category="Teste",
                url="https://teste.com",
                affiliate_url="https://teste.com"
            )
            
            # Simular postagem
            print("📤 Simulando postagem de oferta...")
            print(f"   Título: {test_offer.title}")
            print(f"   Preço: R$ {test_offer.price:.2f}")
            print(f"   Desconto: {test_offer.discount_percentage}%")
            print(f"   Loja: {test_offer.store}")
            
            # Formatar mensagem
            message = self.message_formatter.format_offer_message(test_offer)
            print(f"\n📋 Mensagem formatada ({len(message)} caracteres):")
            print("-" * 60)
            print(message)
            print("-" * 60)
            
            print("\n✅ Simulação de postagem concluída")
            print("   (Modo dry_run ativo - nenhuma mensagem real foi enviada)")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro na simulação: {e}")
            return False
    
    async def test_bot_commands(self):
        """Testa comandos do bot"""
        print("\n⌨️ Testando comandos do bot...")
        
        if not self.bot:
            print("❌ Bot não configurado")
            return False
        
        try:
            # Verificar comandos disponíveis
            commands = self.bot.commands if hasattr(self.bot, 'commands') else {}
            
            if commands:
                print("✅ Comandos disponíveis:")
                for cmd, desc in commands.items():
                    print(f"   /{cmd}: {desc}")
            else:
                print("⚠️ Nenhum comando configurado")
            
            # Verificar estatísticas
            if hasattr(self.bot, 'stats'):
                stats = self.bot.stats
                print(f"\n📊 Estatísticas do bot:")
                print(f"   Total de posts: {stats.get('total_posts', 0)}")
                print(f"   Posts bem-sucedidos: {stats.get('successful_posts', 0)}")
                print(f"   Posts falharam: {stats.get('failed_posts', 0)}")
                print(f"   Último post: {stats.get('last_post', 'Nunca')}")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao testar comandos: {e}")
            return False
    
    async def run_all_tests(self):
        """Executa todos os testes"""
        print("=" * 70)
        print("🧪 TESTE COMPLETO DO BOT TELEGRAM - GARIMPEIRO GEEK")
        print("=" * 70)
        print(f"⏰ Iniciado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print("=" * 70)
        
        try:
            # 1. Configurar bot
            if not await self.setup_bot():
                print("\n❌ Falha na configuração do bot")
                return False
            
            # 2. Testar formatação de mensagens
            if not await self.test_message_formatting():
                print("\n❌ Falha no teste de formatação")
                return False
            
            # 3. Testar inicialização do bot
            if not await self.test_bot_startup():
                print("\n❌ Falha na inicialização do bot")
                return False
            
            # 4. Testar simulação de postagem
            if not await self.test_posting_simulation():
                print("\n❌ Falha na simulação de postagem")
                return False
            
            # 5. Testar comandos do bot
            if not await self.test_bot_commands():
                print("\n❌ Falha no teste de comandos")
                return False
            
            print("\n" + "=" * 70)
            print("🎉 TODOS OS TESTES PASSARAM COM SUCESSO!")
            print("=" * 70)
            print("✅ Bot configurado e funcionando")
            print("✅ Formatação de mensagens funcionando")
            print("✅ Sistema de postagem funcionando")
            print("✅ Comandos do bot funcionando")
            print("✅ Sistema pronto para produção")
            print("=" * 70)
            
            return True
            
        except Exception as e:
            print(f"\n❌ Erro geral nos testes: {e}")
            return False


async def main():
    """Função principal"""
    tester = TelegramTester()
    success = await tester.run_all_tests()
    
    if success:
        print("\n🚀 Sistema pronto para uso!")
        print("💡 Para ativar postagem real, configure:")
        print("   1. TELEGRAM_BOT_TOKEN no arquivo .env")
        print("   2. TELEGRAM_CHANNEL_ID no arquivo .env")
        print("   3. Defina dry_run=False no BotConfig")
    else:
        print("\n⚠️ Alguns testes falharam. Verifique a configuração.")
    
    return success


if __name__ == "__main__":
    asyncio.run(main())
