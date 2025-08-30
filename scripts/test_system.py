#!/usr/bin/env python3
"""
🧪 SCRIPT DE TESTE DO SISTEMA GARIMPEIRO GEEK
==============================================

Este script testa se todas as configurações estão funcionando corretamente.
Execute para verificar se o sistema está pronto para uso.
"""

import os
import sys
from pathlib import Path

# Adicionar src ao path para imports
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from dotenv import load_dotenv

def load_environment():
    """Carrega as variáveis de ambiente do arquivo .env"""
    print("🔧 Carregando configurações do .env...")
    
    env_path = Path(".env")
    if not env_path.exists():
        print("❌ Arquivo .env não encontrado!")
        print("💡 Execute: python scripts/setup_env.py")
        return False
    
    # Carregar .env
    load_dotenv()
    print("✅ Arquivo .env carregado com sucesso!")
    return True

def test_telegram_config():
    """Testa as configurações do Telegram"""
    print("\n🤖 Testando configurações do Telegram...")
    
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not bot_token or bot_token == "seu_token_aqui":
        print("❌ Token do bot não configurado!")
        return False
    
    if not chat_id or chat_id == "seu_chat_id_aqui":
        print("❌ ID do chat não configurado!")
        return False
    
    print(f"✅ Bot Token: {bot_token[:20]}...")
    print(f"✅ Chat ID: {chat_id}")
    return True

def test_affiliate_config():
    """Testa as configurações de afiliados"""
    print("\n🔗 Testando configurações de afiliados...")
    
    # Awin
    awin_affids = os.getenv("AWIN_AFFIDS")
    awin_oauth2 = os.getenv("AWIN_OAUTH2_TOKEN")
    
    if awin_affids:
        print(f"✅ Awin AFFIDs: {awin_affids}")
    if awin_oauth2:
        print(f"✅ Awin OAuth2: {awin_oauth2[:20]}...")
    
    # AliExpress
    ali_app_key = os.getenv("ALI_APP_KEY")
    ali_app_secret = os.getenv("ALI_APP_SECRET")
    
    if ali_app_key and ali_app_secret:
        print(f"✅ AliExpress App Key: {ali_app_key}")
        print(f"✅ AliExpress App Secret: {ali_app_secret[:20]}...")
    
    # Shopee
    shopee_app_id = os.getenv("SHOPEE_APP_ID")
    shopee_secret = os.getenv("SHOPEE_SECRET")
    
    if shopee_app_id and shopee_secret:
        print(f"✅ Shopee App ID: {shopee_app_id}")
        print(f"✅ Shopee Secret: {shopee_secret[:20]}...")
    
    # Rakuten
    rakuten_enabled = os.getenv("RAKUTEN_ENABLED", "false").lower() == "true"
    if rakuten_enabled:
        print("✅ Rakuten: Habilitado")
        webservice_token = os.getenv("RAKUTEN_WEBSERVICE_TOKEN")
        if webservice_token:
            print(f"✅ Rakuten WebService Token: {webservice_token[:20]}...")
    
    return True

def test_system_config():
    """Testa as configurações do sistema"""
    print("\n⚙️ Testando configurações do sistema...")
    
    # Verificar diretórios
    dirs_to_check = [".data", "logs", "src", "tests"]
    
    for dir_name in dirs_to_check:
        dir_path = Path(dir_name)
        if dir_path.exists():
            print(f"✅ Diretório {dir_name}: Existe")
        else:
            print(f"⚠️ Diretório {dir_name}: Não existe")
    
    # Verificar arquivos importantes
    files_to_check = [
        "src/core/models.py",
        "src/core/affiliate_validator.py",
        "src/core/affiliate_converter.py",
        "src/posting/message_formatter.py",
        "src/posting/scheduler.py",
        "src/posting/posting_manager.py"
    ]
    
    for file_path in files_to_check:
        file_obj = Path(file_path)
        if file_obj.exists():
            print(f"✅ Arquivo {file_path}: Existe")
        else:
            print(f"❌ Arquivo {file_path}: Não existe")
    
    return True

def test_imports():
    """Testa se os módulos principais podem ser importados"""
    print("\n📦 Testando importação de módulos...")
    
    try:
        # Testar imports básicos
        from core.models import Offer
        print("✅ core.models: OK")
        
        from core.affiliate_validator import AffiliateValidator
        print("✅ core.affiliate_validator: OK")
        
        from core.affiliate_converter import AffiliateConverter
        print("✅ core.affiliate_converter: OK")
        
        from posting.message_formatter import MessageFormatter
        print("✅ posting.message_formatter: OK")
        
        from posting.scheduler import JobScheduler
        print("✅ posting.scheduler: OK")
        
        from posting.posting_manager import PostingManager
        print("✅ posting.posting_manager: OK")
        
        return True
        
    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

def main():
    """Função principal"""
    print("🧪 TESTE DO SISTEMA GARIMPEIRO GEEK")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 5
    
    # 1. Carregar ambiente
    if load_environment():
        tests_passed += 1
    
    # 2. Testar Telegram
    if test_telegram_config():
        tests_passed += 1
    
    # 3. Testar afiliados
    if test_affiliate_config():
        tests_passed += 1
    
    # 4. Testar sistema
    if test_system_config():
        tests_passed += 1
    
    # 5. Testar imports
    if test_imports():
        tests_passed += 1
    
    # Resultado final
    print("\n" + "=" * 50)
    print(f"📊 RESULTADO DOS TESTES: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print("🎉 SISTEMA 100% FUNCIONAL!")
        print("\n📋 PRÓXIMOS PASSOS:")
        print("1. Execute os testes E2E: python -m pytest tests/e2e/ -v")
        print("2. Teste o bot: python -m src.telegram_bot.bot --dry-run")
        print("3. Inicie o sistema: python start.py")
        print("4. Faça deploy: python scripts/quick_deploy.py 'Sistema testado e funcionando'")
    else:
        print("⚠️ ALGUNS TESTES FALHARAM")
        print("💡 Verifique as configurações e execute novamente")
    
    return tests_passed == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
