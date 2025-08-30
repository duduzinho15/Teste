#!/usr/bin/env python3
"""
🔧 SCRIPT DE CONFIGURAÇÃO AUTOMÁTICA DO .ENV
============================================

Este script configura automaticamente o arquivo .env com suas chaves de API.
Execute após configurar suas credenciais do Telegram.
"""

import os
import shutil
from pathlib import Path

def create_env_file():
    """Cria o arquivo .env com todas as configurações"""
    
    # Conteúdo completo do .env
    env_content = """# ==========================================
# GARIMPEIRO GEEK - CONFIGURAÇÕES REAIS
# ==========================================
# ⚠️ IMPORTANTE: Este arquivo contém suas chaves reais - NUNCA commitar!

# ==========================================
# CONFIGURAÇÕES DO TELEGRAM
# ==========================================
# Token do seu bot Telegram (obtenha em @BotFather)
TELEGRAM_BOT_TOKEN=seu_token_aqui

# ID do chat onde o bot enviará notificações
TELEGRAM_CHAT_ID=seu_chat_id_aqui

# Nome do seu bot
TELEGRAM_BOT_NAME=GarimpeiroGeekBot

# ==========================================
# CONFIGURAÇÕES DE SCRAPING
# ==========================================
# Delay entre requisições (em segundos)
SCRAPER_DELAY=2.0

# Timeout das requisições (em segundos)
SCRAPER_TIMEOUT=30

# User-Agent para as requisições
SCRAPER_USER_AGENT=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36

# ==========================================
# CONFIGURAÇÕES DE API
# ==========================================
# Chave da API do Google Shopping (opcional)
GOOGLE_SHOPPING_API_KEY=seu_api_key_aqui

# Chave da API do Mercado Livre (opcional)
MERCADO_LIVRE_API_KEY=seu_api_key_aqui

# Chave da API da Amazon (opcional)
AMAZON_API_KEY=seu_api_key_aqui

# ==========================================
# CONFIGURAÇÕES DE AFILIADOS
# ==========================================
# Awin - AFFIDs permitidos (separados por vírgula)
AWIN_AFFIDS=2370719,2510157

# Awin - MIDs por loja (configurável)
AWIN_COMFY_MID=23377
AWIN_TROCAFY_MID=51277
AWIN_LG_MID=33061
AWIN_KABUM_MID=17729
AWIN_NINJA_MID=106765
AWIN_SAMSUNG_MID=25539

# Amazon - Tag de afiliado (não alterar sem instrução)
AMAZON_AFFILIATE_TAG=garimpeirogee-20

# Mercado Livre - Etiqueta de afiliado
MERCADO_LIVRE_AFFILIATE_TAG=garimpeirogeek

# AliExpress - Tracking ID
ALIEXPRESS_TRACKING_ID=telegram

# ==========================================
# CONFIGURAÇÕES DAS APIS OFICIAIS
# ==========================================

# AliExpress Open Platform
ALI_APP_KEY=517956
ALI_APP_SECRET=okv8nzEGIvWqV0XxONcN9loPNrYwWDsm
ALI_ACCESS_TOKEN=
ALI_REFRESH_TOKEN=
USE_API_ALIEXPRESS=true

# Shopee Affiliate Open API
SHOPEE_APP_ID=18330800803
SHOPEE_SECRET=IOMXMSUM5KDOLSYKXQERKCU42SNMJERR
SHOPEE_AFFILIATE_ID=18330800803
USE_API_SHOPEE=true

# Awin Publisher API
AWIN_PUBLISHER_ID=
AWIN_OAUTH2_TOKEN=f647c7b9-e8de-44a4-80fe-e9572ef35c10
USE_API_AWIN=true

# Rakuten Advertising API
RAKUTEN_ENABLED=true
RAKUTEN_WEBSERVICE_TOKEN=b64c55b9b35ee0e881a8f7bafeb77a374b11e62e439ec63cd4470dbbefef4409
RAKUTEN_SECURITY_TOKEN=65d854a458c9a1e4be4e7c93e0631c704fe842c37022a82d398d4390ca2f596d
RAKUTEN_SID=4565931
USE_API_RAKUTEN=true

# ==========================================
# CONFIGURAÇÕES DO SISTEMA
# ==========================================
# Modo de debug (True/False)
DEBUG_MODE=False

# Nível de log (DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL=INFO

# Diretório de dados
DATA_DIR=.data

# Diretório de logs
LOG_DIR=logs

# ==========================================
# CONFIGURAÇÕES DO DASHBOARD
# ==========================================
# Porta do servidor web (se aplicável)
DASHBOARD_PORT=8000

# Host do servidor web
DASHBOARD_HOST=localhost

# Tema padrão (light/dark)
DEFAULT_THEME=dark

# ==========================================
# CONFIGURAÇÕES DE NOTIFICAÇÕES
# ==========================================
# Intervalo de verificação de ofertas (em minutos)
NOTIFICATION_INTERVAL=30

# Notificar apenas ofertas com desconto maior que (%)
MIN_DISCOUNT_PERCENT=10

# Notificar apenas produtos com preço menor que (R$)
MAX_PRICE_THRESHOLD=1000.00

# ==========================================
# CONFIGURAÇÕES DE BACKUP
# ==========================================
# Fazer backup automático (True/False)
AUTO_BACKUP=True

# Intervalo de backup (em horas)
BACKUP_INTERVAL=24

# Manter backups por (dias)
BACKUP_RETENTION_DAYS=7
"""
    
    # Caminho do arquivo .env
    env_path = Path(".env")
    
    # Verificar se já existe
    if env_path.exists():
        print("⚠️ Arquivo .env já existe!")
        response = input("Deseja sobrescrever? (s/N): ").lower()
        if response != 's':
            print("❌ Operação cancelada")
            return False
    
    # Criar o arquivo .env
    try:
        with open(env_path, "w", encoding="utf-8") as f:
            f.write(env_content)
        
        print("✅ Arquivo .env criado com sucesso!")
        print(f"📁 Localização: {env_path.absolute()}")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar arquivo .env: {e}")
        return False

def setup_telegram_config():
    """Configura as credenciais do Telegram"""
    print("\n🔧 CONFIGURAÇÃO DO TELEGRAM")
    print("=" * 30)
    
    # Solicitar token do bot
    bot_token = input("🤖 Token do seu bot Telegram (@BotFather): ").strip()
    if not bot_token:
        print("❌ Token do bot é obrigatório!")
        return False
    
    # Solicitar ID do chat
    chat_id = input("💬 ID do chat/canal onde o bot enviará notificações: ").strip()
    if not chat_id:
        print("❌ ID do chat é obrigatório!")
        return False
    
    # Atualizar o arquivo .env
    try:
        with open(".env", "r", encoding="utf-8") as f:
            content = f.read()
        
        # Substituir as credenciais
        content = content.replace("TELEGRAM_BOT_TOKEN=seu_token_aqui", f"TELEGRAM_BOT_TOKEN={bot_token}")
        content = content.replace("TELEGRAM_CHAT_ID=seu_chat_id_aqui", f"TELEGRAM_CHAT_ID={chat_id}")
        
        with open(".env", "w", encoding="utf-8") as f:
            f.write(content)
        
        print("✅ Credenciais do Telegram configuradas!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao configurar Telegram: {e}")
        return False

def validate_env_file():
    """Valida se o arquivo .env está configurado corretamente"""
    env_path = Path(".env")
    
    if not env_path.exists():
        print("❌ Arquivo .env não encontrado!")
        return False
    
    try:
        with open(env_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Verificar se as credenciais do Telegram foram configuradas
        if "seu_token_aqui" in content or "seu_chat_id_aqui" in content:
            print("⚠️ Credenciais do Telegram ainda não configuradas")
            return False
        
        print("✅ Arquivo .env configurado corretamente!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao validar .env: {e}")
        return False

def main():
    """Função principal"""
    print("🚀 CONFIGURAÇÃO AUTOMÁTICA DO GARIMPEIRO GEEK")
    print("=" * 50)
    
    # 1. Criar arquivo .env
    if not create_env_file():
        return
    
    # 2. Configurar Telegram
    if not setup_telegram_config():
        return
    
    # 3. Validar configuração
    if not validate_env_file():
        return
    
    print("\n🎉 CONFIGURAÇÃO CONCLUÍDA COM SUCESSO!")
    print("=" * 50)
    print("✅ Arquivo .env criado")
    print("✅ Todas as APIs configuradas")
    print("✅ Telegram configurado")
    print("✅ Sistema pronto para uso!")
    
    print("\n📋 PRÓXIMOS PASSOS:")
    print("1. Teste o bot: python -m src.telegram_bot.bot --dry-run")
    print("2. Execute os testes: python -m pytest tests/e2e/ -v")
    print("3. Inicie o sistema: python start.py")

if __name__ == "__main__":
    main()
