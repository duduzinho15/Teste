#!/usr/bin/env python3
"""
Configuração do Bot Telegram - Garimpeiro Geek
Configure suas credenciais aqui para ativar postagem real
"""

import os
from pathlib import Path

# Configurações do Bot Telegram
TELEGRAM_CONFIG = {
    # ========================================
    # CONFIGURAÇÕES OBRIGATÓRIAS
    # ========================================
    
    # Token do seu bot (obtido do @BotFather)
    "BOT_TOKEN": "8478680741:AAHguaQAL1bTDTqr3AQke1BqAqLeiv1TXnQ",
    
    # ID do canal onde as mensagens serão postadas
    "CHANNEL_ID": "-1002853967960",
    
    # Seu User ID do Telegram (para comandos admin)
    "ADMIN_USER_ID": 123456789,  # Substitua pelo seu ID real
    
    # ========================================
    # CONFIGURAÇÕES DE POSTAGEM
    # ========================================
    
    # Modo de teste (True = não envia mensagens reais)
    "DRY_RUN": False,
    
    # Máximo de posts por hora
    "MAX_POSTS_PER_HOUR": 20,
    
    # Postagem automática habilitada
    "AUTO_POSTING_ENABLED": True,
    
    # Moderação habilitada
    "MODERATION_ENABLED": True,
    
    # ========================================
    # CONFIGURAÇÕES DE MENSAGEM
    # ========================================
    
    # Incluir emojis nas mensagens
    "INCLUDE_EMOJIS": True,
    
    # Incluir preço original
    "SHOW_ORIGINAL_PRICE": True,
    
    # Incluir porcentagem de desconto
    "SHOW_DISCOUNT_PERCENTAGE": True,
    
    # Incluir categoria do produto
    "SHOW_CATEGORY": True,
    
    # Incluir nome da loja
    "SHOW_STORE": True,
    
    # ========================================
    # CONFIGURAÇÕES DE SEGURANÇA
    # ========================================
    
    # Validar URLs antes de postar
    "VALIDATE_URLS": True,
    
    # Bloquear categorias proibidas
    "BLOCK_FORBIDDEN_CATEGORIES": True,
    
    # Categorias proibidas
    "FORBIDDEN_CATEGORIES": [
        "apostas",
        "jogos de azar",
        "conteúdo adulto",
        "drogas",
        "armas"
    ],
    
    # ========================================
    # CONFIGURAÇÕES DE LOG
    # ========================================
    
    # Nível de log
    "LOG_LEVEL": "INFO",
    
    # Arquivo de log
    "LOG_FILE": "logs/telegram_bot.log",
    
    # Log de mensagens enviadas
    "LOG_SENT_MESSAGES": True,
    
    # Log de erros
    "LOG_ERRORS": True
}

# Função para obter configuração
def get_telegram_config():
    """Retorna configuração do Telegram"""
    return TELEGRAM_CONFIG.copy()

# Função para validar configuração
def validate_telegram_config():
    """Valida se a configuração está correta"""
    config = get_telegram_config()
    
    errors = []
    
    # Verificar token
    if not config["BOT_TOKEN"] or config["BOT_TOKEN"] == "SEU_BOT_TOKEN_AQUI":
        errors.append("BOT_TOKEN não configurado")
    
    # Verificar channel ID
    if not config["CHANNEL_ID"] or config["CHANNEL_ID"] == "SEU_CHANNEL_ID_AQUI":
        errors.append("CHANNEL_ID não configurado")
    
    # Verificar admin user ID
    if config["ADMIN_USER_ID"] == 123456789:
        errors.append("ADMIN_USER_ID não configurado")
    
    if errors:
        print("❌ Erros na configuração do Telegram:")
        for error in errors:
            print(f"   - {error}")
        print("\n💡 Configure as credenciais em telegram_config.py")
        return False
    
    print("✅ Configuração do Telegram válida")
    return True

# Função para mostrar configuração atual
def show_telegram_config():
    """Mostra configuração atual do Telegram"""
    config = get_telegram_config()
    
    print("🔧 Configuração Atual do Bot Telegram:")
    print("=" * 50)
    
    # Configurações principais
    print(f"🤖 Bot Token: {'✅ Configurado' if config['BOT_TOKEN'] != 'SEU_BOT_TOKEN_AQUI' else '❌ Não configurado'}")
    print(f"📢 Channel ID: {'✅ Configurado' if config['CHANNEL_ID'] != 'SEU_CHANNEL_ID_AQUI' else '❌ Não configurado'}")
    print(f"👤 Admin User ID: {'✅ Configurado' if config['ADMIN_USER_ID'] != 123456789 else '❌ Não configurado'}")
    
    # Configurações de postagem
    print(f"🧪 Modo Teste: {'✅ Ativo' if config['DRY_RUN'] else '❌ Desativado'}")
    print(f"📤 Postagem Automática: {'✅ Habilitada' if config['AUTO_POSTING_ENABLED'] else '❌ Desabilitada'}")
    print(f"🛡️ Moderação: {'✅ Habilitada' if config['MODERATION_ENABLED'] else '❌ Desabilitada'}")
    
    # Configurações de mensagem
    print(f"😊 Emojis: {'✅ Habilitados' if config['INCLUDE_EMOJIS'] else '❌ Desabilitados'}")
    print(f"💰 Preço Original: {'✅ Mostrado' if config['SHOW_ORIGINAL_PRICE'] else '❌ Oculto'}")
    print(f"🎯 Desconto: {'✅ Mostrado' if config['SHOW_DISCOUNT_PERCENTAGE'] else '❌ Oculto'}")
    
    print("=" * 50)
    
    if config["DRY_RUN"]:
        print("⚠️ ATENÇÃO: Modo teste ativo - mensagens não serão enviadas")
        print("💡 Para ativar postagem real, defina DRY_RUN=False")
    else:
        print("🚀 Modo produção ativo - mensagens serão enviadas para o canal")

if __name__ == "__main__":
    show_telegram_config()
    print()
    validate_telegram_config()
