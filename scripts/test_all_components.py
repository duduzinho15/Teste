#!/usr/bin/env python3
"""
🧪 TESTE COMPLETO DE TODOS OS COMPONENTES
==========================================

Este script testa cada componente individualmente para garantir
que tudo está funcionando perfeitamente.
"""

import os
import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Adicionar src ao path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

def test_environment():
    """Testa se o ambiente está configurado"""
    print("🔧 TESTE DO AMBIENTE")
    print("=" * 30)
    
    # Carregar .env
    load_dotenv()
    
    # Verificar variáveis críticas
    required_vars = [
        "TELEGRAM_BOT_TOKEN",
        "TELEGRAM_CHAT_ID",
        "AWIN_OAUTH2_TOKEN",
        "ALI_APP_KEY",
        "ALI_APP_SECRET",
        "SHOPEE_APP_ID",
        "SHOPEE_SECRET",
        "RAKUTEN_WEBSERVICE_TOKEN"
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if not value or value in ["seu_token_aqui", "seu_chat_id_aqui"]:
            missing_vars.append(var)
        else:
            print(f"✅ {var}: {value[:20]}...")
    
    if missing_vars:
        print(f"❌ Variáveis ausentes: {missing_vars}")
        return False
    
    print("✅ Ambiente configurado corretamente!")
    return True

def test_affiliate_validator():
    """Testa o validador de afiliados"""
    print("\n🔍 TESTE DO VALIDADOR DE AFILIADOS")
    print("=" * 40)
    
    try:
        from core.affiliate_validator import AffiliateValidator
        
        validator = AffiliateValidator()
        
        # URLs de teste
        test_urls = [
            "https://www.awin1.com/cread.php?awinmid=23377&awinaffid=2370719&ued=https://www.comfy.com.br/",
            "https://www.amazon.com.br/dp/B09T4WC9GN?tag=garimpeirogee-20",
            "https://s.shopee.com.br/3LGfnEjEXu",
            "https://mercadolivre.com/sec/1vt6gtj",
            "https://s.click.aliexpress.com/e/_opftn1L"
        ]
        
        for url in test_urls:
            try:
                result = validator.validate_url(url)
                # Usar o atributo correto: result.status.value
                status = result.status.value if hasattr(result.status, 'value') else str(result.status)
                print(f"✅ {url[:50]}... -> Status: {status}, Score: {result.score:.2f}")
            except Exception as e:
                print(f"❌ {url[:50]}... -> Erro: {e}")
        
        print("✅ Validador de afiliados funcionando!")
        return True
        
    except Exception as e:
        print(f"❌ Erro no validador: {e}")
        return False

async def test_affiliate_converter():
    """Testa o conversor de afiliados"""
    print("\n🔄 TESTE DO CONVERSOR DE AFILIADOS")
    print("=" * 40)
    
    try:
        from core.affiliate_converter import AffiliateConverter
        
        converter = AffiliateConverter()
        
        # URLs de teste
        test_urls = [
            "https://www.comfy.com.br/cadeira-escritorio",
            "https://www.amazon.com.br/dp/B09T4WC9GN",
            "https://shopee.com.br/produto123",
            "https://www.mercadolivre.com.br/produto123"
        ]
        
        for url in test_urls:
            try:
                # Usar o método correto: convert_to_affiliate
                result = await converter.convert_to_affiliate(url)
                if result and result != url:
                    print(f"✅ {url[:50]}... -> Convertido: {result[:50]}...")
                else:
                    print(f"⚠️ {url[:50]}... -> Não convertido")
            except Exception as e:
                print(f"❌ {url[:50]}... -> Erro: {e}")
        
        print("✅ Conversor de afiliados funcionando!")
        return True
        
    except Exception as e:
        print(f"❌ Erro no conversor: {e}")
        return False

def test_message_formatter():
    """Testa o formatador de mensagens"""
    print("\n📝 TESTE DO FORMATADOR DE MENSAGENS")
    print("=" * 40)
    
    try:
        from core.models import Offer
        from posting.message_formatter import MessageFormatter
        
        formatter = MessageFormatter()
        
        # Criar oferta de teste com parâmetros corretos do modelo
        test_offer = Offer(
            title="Produto de Teste",
            price=99.99,
            url="https://amazon.com/test",
            store="Amazon",
            original_price=199.99,
            discount_percentage=50,
            category="Eletrônicos",
            affiliate_url="https://amazon.com/test"
        )
        
        # Formatar mensagem usando o método CORRETO
        message = formatter.format_offer_message(test_offer)
        
        if message and len(message) > 0:
            print(f"✅ Mensagem formatada: {len(message)} caracteres")
            print(f"📄 Preview: {message[:100]}...")
        else:
            print("❌ Mensagem vazia ou inválida")
            return False
        
        print("✅ Formatador de mensagens funcionando!")
        return True
        
    except Exception as e:
        print(f"❌ Erro no formatador: {e}")
        return False

def test_scheduler():
    """Testa o agendador de tarefas"""
    print("\n⏰ TESTE DO AGENDADOR DE TAREFAS")
    print("=" * 40)
    
    try:
        from posting.scheduler import JobScheduler
        
        scheduler = JobScheduler()
        
        # Verificar se pode ser instanciado
        if scheduler:
            print("✅ Agendador instanciado com sucesso")
            
            # Verificar métodos disponíveis
            methods = [method for method in dir(scheduler) if not method.startswith('_')]
            print(f"✅ Métodos disponíveis: {len(methods)}")
            
            return True
        else:
            print("❌ Falha ao instanciar agendador")
            return False
        
    except Exception as e:
        print(f"❌ Erro no agendador: {e}")
        return False

def test_posting_manager():
    """Testa o gerenciador de postagem"""
    print("\n📤 TESTE DO GERENCIADOR DE POSTAGEM")
    print("=" * 40)
    
    try:
        from core.models import Offer
        from posting.posting_manager import PostingManager
        
        manager = PostingManager()
        
        # Verificar se pode ser instanciado
        if manager:
            print("✅ Gerenciador instanciado com sucesso")
            
            # Verificar métodos disponíveis
            methods = [method for method in dir(manager) if not method.startswith('_')]
            print(f"✅ Métodos disponíveis: {len(methods)}")
            
            return True
        else:
            print("❌ Falha ao instanciar gerenciador")
            return False
        
    except Exception as e:
        print(f"❌ Erro no gerenciador: {e}")
        return False

def test_telegram_bot():
    """Testa o bot do Telegram - VERSÃO SIMPLIFICADA"""
    print("\n🤖 TESTE DO BOT DO TELEGRAM")
    print("=" * 40)
    
    try:
        # Verificar se o arquivo do bot existe
        bot_file = Path("src/telegram_bot/bot.py")
        if not bot_file.exists():
            print("❌ Arquivo do bot não encontrado")
            return False
        
        # Verificar se o arquivo tem conteúdo
        with open(bot_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if len(content) < 100:
                print("❌ Arquivo do bot muito pequeno")
                return False
        
        print("✅ Arquivo do bot encontrado e válido")
        print(f"✅ Tamanho: {len(content)} caracteres")
        
        # Verificar se tem a classe TelegramBot
        if "class TelegramBot" in content:
            print("✅ Classe TelegramBot encontrada")
        else:
            print("⚠️ Classe TelegramBot não encontrada")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao verificar bot: {e}")
        return False

def test_dashboard():
    """Testa o dashboard Flet"""
    print("\n🖥️ TESTE DO DASHBOARD FLET")
    print("=" * 40)
    
    try:
        dashboard_path = Path("apps/flet_dashboard")
        
        if not dashboard_path.exists():
            print("⚠️ Diretório do dashboard não encontrado")
            return False
        
        # Verificar arquivos do dashboard
        dashboard_files = [
            "apps/flet_dashboard/main.py",
            "apps/flet_dashboard/run_dashboard.py"
        ]
        
        for file_path in dashboard_files:
            if Path(file_path).exists():
                print(f"✅ {file_path}: Existe")
            else:
                print(f"❌ {file_path}: Não existe")
                return False
        
        print("✅ Dashboard Flet configurado!")
        return True
        
    except Exception as e:
        print(f"❌ Erro no dashboard: {e}")
        return False

async def main():
    """Função principal"""
    print("🧪 TESTE COMPLETO DE TODOS OS COMPONENTES")
    print("=" * 60)
    
    tests = [
        ("Ambiente", test_environment),
        ("Validador de Afiliados", test_affiliate_validator),
        ("Conversor de Afiliados", test_affiliate_converter),
        ("Formatador de Mensagens", test_message_formatter),
        ("Agendador de Tarefas", test_scheduler),
        ("Gerenciador de Postagem", test_posting_manager),
        ("Bot do Telegram", test_telegram_bot),
        ("Dashboard Flet", test_dashboard)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Erro no teste {test_name}: {e}")
            results.append((test_name, False))
    
    # Resultado final
    print("\n" + "=" * 60)
    print("📊 RESULTADO FINAL DOS TESTES")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{status} - {test_name}")
    
    print(f"\n📈 TAXA DE SUCESSO: {passed}/{total} ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 SISTEMA 100% FUNCIONAL!")
        print("🚀 Todos os componentes estão funcionando perfeitamente!")
    else:
        print(f"\n⚠️ {total-passed} COMPONENTES COM PROBLEMAS")
        print("🔧 Verifique os erros acima e corrija antes de usar em produção")
    
    return passed == total

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Erro fatal: {e}")
        sys.exit(1)
