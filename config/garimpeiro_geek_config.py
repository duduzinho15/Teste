#!/usr/bin/env python3
"""
🔑 CONFIGURAÇÃO COMPLETA DO GARIMPEIRO GEEK
============================================

Este arquivo contém todas as suas chaves de API reais.
IMPORTANTE: NUNCA commitar este arquivo no GitHub!

Para usar: copie este arquivo para config/local_config.py
"""

# ==========================================
# CONFIGURAÇÕES DO TELEGRAM
# ==========================================
TELEGRAM_CONFIG = {
    "bot_token": "seu_token_aqui",  # Obtenha em @BotFather
    "chat_id": "seu_chat_id_aqui",  # ID do chat onde o bot enviará notificações
    "bot_name": "GarimpeiroGeekBot"
}

# ==========================================
# CONFIGURAÇÕES DE AFILIADOS
# ==========================================
AFFILIATE_CONFIG = {
    # Awin - AFFIDs permitidos
    "awin_affids": ["2370719", "2510157"],
    
    # Awin - MIDs por loja
    "awin_mids": {
        "comfy": "23377",
        "trocafy": "51277", 
        "lg": "33061",
        "kabum": "17729",
        "ninja": "106765",
        "samsung": "25539"
    },
    
    # Amazon
    "amazon_tag": "garimpeirogee-20",
    
    # Mercado Livre
    "mercadolivre_tag": "garimpeirogeek",
    
    # AliExpress
    "aliexpress_tracking_id": "telegram"
}

# ==========================================
# CONFIGURAÇÕES DAS APIS OFICIAIS
# ==========================================

# AliExpress Open Platform
ALIEXPRESS_API_CONFIG = {
    "app_key": "517956",
    "app_secret": "okv8nzEGIvWqV0XxONcN9loPNrYwWDsm",
    "app_name": "Garimpeiro Geek Bot",
    "app_category": "Affiliates API",
    "tracking_id": "telegram",
    "access_token": "",  # Preencher quando disponível
    "refresh_token": "",  # Preencher quando disponível
    "enabled": True,
    "permissions": [
        "Standard API for Publishers",
        "Advanced API", 
        "SKU Dimension API",
        "Get Xinghe Merchant License"
    ]
}

# Shopee Affiliate Open API
SHOPEE_API_CONFIG = {
    "app_id": "18330800803",
    "secret": "IOMXMSUM5KDOLSYKXQERKCU42SNMJERR",
    "affiliate_id": "18330800803",
    "enabled": True,
    "api_type": "GraphQL",
    "base_url": "https://graphql.org/code/#graphql-clients"
}

# Awin Publisher API
AWIN_API_CONFIG = {
    "publisher_id": "2370719",  # Publisher ID principal
    "oauth2_token": "f647c7b9-e8de-44a4-80fe-e9572ef35c10",
    "enabled": True,
    "api_type": "OAuth2"
}

# Rakuten Advertising API
RAKUTEN_API_CONFIG = {
    "enabled": True,
    "webservice_token": "b64c55b9b35ee0e881a8f7bafeb77a374b11e62e439ec63cd4470dbbefef4409",
    "security_token": "65d854a458c9a1e4be4e7c93e0631c704fe842c37022a82d398d4390ca2f596d",
    "sid": "4565931",
    "permissions": [
        "Advanced Reports",
        "Advertiser Search", 
        "Coupons",
        "Deep Links",
        "Events",
        "Link Locator",
        "Product Search"
    ],
    # Lojas específicas com seus MIDs
    "stores": {
        "hype_games": {
            "name": "Hype Games",
            "mid": "53304",
            "category": "games",
            "enabled": True,
            "description": "Loja especializada em jogos e acessórios gaming"
        },
        "nuuvem": {
            "name": "Nuuvem",
            "mid": "46796", 
            "category": "games",
            "enabled": True,
            "description": "Plataforma digital de jogos e software"
        }
    }
}

# ==========================================
# CONFIGURAÇÕES DE CATEGORIAS GEEK/GAMER
# ==========================================
GEEK_CATEGORIES_CONFIG = {
    "enabled": True,
    "priority_boost": 0.3,  # Boost maior para categorias geek (vs 0.1 para tech geral)
    
    # Categorias PRIMÁRIAS (foco principal do Garimpeiro Geek)
    "primary_categories": {
        "gaming": {
            "name": "Gaming",
            "keywords": ["gaming", "game", "jogo", "gamer", "esports"],
            "subcategories": [
                "consoles", "notebooks_gamer", "pcs_gamer", "acessorios_gaming",
                "perifericos_gaming", "jogos", "streaming_gaming"
            ],
            "priority_score": 1.0,
            "emoji": "🎮"
        },
        "tech_geek": {
            "name": "Tech Geek",
            "keywords": ["tech", "tecnologia", "geek", "nerd", "otaku"],
            "subcategories": [
                "smartphones_premium", "tablets_tech", "smartwatches", "smart_tvs",
                "audio_premium", "cameras_tech", "drones"
            ],
            "priority_score": 0.9,
            "emoji": "⚡"
        },
        "pc_gaming": {
            "name": "PC Gaming",
            "keywords": ["pc gamer", "desktop gaming", "workstation", "custom pc"],
            "subcategories": [
                "processadores", "placas_video", "memorias_ram", "ssds_nvme",
                "gabinetes_gaming", "fontes_gaming", "coolers_gaming"
            ],
            "priority_score": 0.95,
            "emoji": "🖥️"
        },
        "smart_home_tech": {
            "name": "Smart Home & IoT",
            "keywords": ["smart home", "iot", "automacao", "casa inteligente", "smart tv", "smart speaker"],
            "subcategories": [
                "smart_tvs", "smart_speakers", "smart_lights", "smart_plugs",
                "smart_thermostats", "smart_security", "smart_appliances"
            ],
            "priority_score": 0.85,
            "emoji": "🏠"
        },
        "audio_tech": {
            "name": "Audio & Som Premium",
            "keywords": ["audio", "som", "headphone", "headset", "bluetooth", "wireless", "noise cancelling"],
            "subcategories": [
                "headphones_premium", "headsets_gaming", "bluetooth_speakers", "soundbars",
                "microphones", "audio_interfaces", "wireless_audio"
            ],
            "priority_score": 0.8,
            "emoji": "🎧"
        },
        "anime_otaku": {
            "name": "Anime & Otaku",
            "keywords": ["anime", "otaku", "manga", "cosplay", "figuras"],
            "subcategories": [
                "figuras_action", "mangas", "cosplay", "merchandise_anime",
                "posters_anime", "acessorios_otaku"
            ],
            "priority_score": 0.85,
            "emoji": "🌸"
        },
        "collectibles": {
            "name": "Collectibles & Hobbies",
            "keywords": ["collectible", "hobby", "colecionavel", "edicao limitada"],
            "subcategories": [
                "action_figures", "statues", "vinyl_toys", "trading_cards",
                "model_kits", "dioramas"
            ],
            "priority_score": 0.8,
            "emoji": "🏆"
        }
    },
    
    # Categorias SECUNDÁRIAS (importantes mas não prioritárias)
    "secondary_categories": {
        "home_appliances": {
            "name": "Eletrodomésticos Tech",
            "keywords": ["eletrodomestico", "microondas", "geladeira", "maquina de lavar", "smart appliance"],
            "subcategories": [
                "microondas", "geladeiras", "maquinas_lavar", "fornos_eletricos",
                "aspiradores_robot", "cafeteiras_espresso", "liquidificadores"
            ],
            "priority_score": 0.6,
            "emoji": "🔌"
        },
        "mobile_tech": {
            "name": "Mobile & Wearables",
            "keywords": ["mobile", "smartphone", "tablet", "smartwatch", "fitness tracker"],
            "subcategories": [
                "smartphones", "tablets", "smartwatches", "fitness_trackers",
                "power_banks", "carregadores", "cases_protetores"
            ],
            "priority_score": 0.7,
            "emoji": "📱"
        },
        "fitness_tech": {
            "name": "Fitness & Saúde Tech",
            "keywords": ["fitness", "saude", "wearable", "smartwatch", "health"],
            "subcategories": [
                "smartwatches", "fitness_trackers", "smart_scales", "blood_pressure_monitors",
                "sleep_trackers", "meditation_apps", "workout_equipment"
            ],
            "priority_score": 0.5,
            "emoji": "💪"
        },
        "general_electronics": {
            "name": "Eletrônicos Gerais",
            "keywords": ["eletronico", "gadget", "acessorio", "tech"],
            "subcategories": [
                "cables", "adapters", "chargers", "power_supplies",
                "storage_devices", "networking", "gaming_accessories"
            ],
            "priority_score": 0.4,
            "emoji": "📱"
        }
    },
    
    # Configurações de priorização
    "prioritization": {
        "min_geek_score": 0.7,  # Score mínimo para ser considerado "geek"
        "geek_boost_multiplier": 1.5,  # Multiplicador para ofertas geek
        "category_matching_weight": 0.4,  # Peso da categoria no score final
        "keyword_matching_weight": 0.3,  # Peso das palavras-chave
        "price_quality_weight": 0.3,  # Peso da qualidade/preço
    },
    
    # Palavras-chave específicas para detectar produtos geek
    "geek_keywords": [
        # Gaming
        "gaming", "gamer", "esports", "competitive", "pro gaming", "streaming",
        "rgb", "mechanical", "wireless", "bluetooth", "noise cancelling",
        
        # Tech Geek
        "premium", "flagship", "latest", "newest", "cutting edge", "innovative",
        "high-end", "professional", "enthusiast", "overclock", "custom",
        
        # Smart Home & IoT
        "smart tv", "smart speaker", "smart home", "iot", "automacao", "casa inteligente",
        "smart appliance", "smart light", "smart plug", "smart thermostat",
        
        # Audio & Som
        "headphone", "headset", "bluetooth", "wireless", "noise cancelling",
        "soundbar", "speaker", "microphone", "audio interface", "wireless audio",
        
        # Mobile & Wearables
        "smartphone", "tablet", "smartwatch", "fitness tracker", "wearable",
        "mobile", "premium mobile", "flagship phone",
        
        # Eletrodomésticos Tech
        "eletrodomestico", "microondas", "geladeira", "maquina de lavar",
        "smart appliance", "aspirador robot", "cafeteira espresso",
        
        # Anime/Otaku
        "anime", "otaku", "manga", "cosplay", "kawaii", "kawaii", "moe",
        "limited edition", "collector", "exclusive", "rare",
        
        # Collectibles
        "collectible", "limited", "exclusive", "numbered", "signed", "autographed",
        "variant", "chase", "rare", "vintage", "retro"
    ],
    
    # Produtos que SEMPRE devem ser priorizados
    "always_priority": [
        # Gaming
        "playstation", "xbox", "nintendo", "switch", "steam deck",
        "rtx", "gtx", "ryzen", "intel i9", "i7", "ssd nvme",
        "mechanical keyboard", "gaming mouse", "gaming headset",
        "gaming monitor", "gaming chair", "streaming setup",
        
        # Smart Home & IoT
        "smart tv", "smart speaker", "smart home", "iot", "automacao",
        "smart appliance", "smart light", "smart plug", "smart thermostat",
        
        # Audio Premium
        "headphone", "headset", "bluetooth", "wireless", "noise cancelling",
        "soundbar", "speaker", "microphone", "audio interface",
        
        # Mobile Premium
        "smartphone", "tablet", "smartwatch", "fitness tracker", "wearable",
        "premium mobile", "flagship phone",
        
        # Eletrodomésticos Tech
        "eletrodomestico", "microondas", "geladeira", "maquina de lavar",
        "smart appliance", "aspirador robot", "cafeteira espresso"
    ]
}

# ==========================================
# CONFIGURAÇÕES DO SISTEMA
# ==========================================
SYSTEM_CONFIG = {
    "debug_mode": False,
    "log_level": "INFO",
    "data_dir": ".data",
    "log_dir": "logs",
    "dashboard_port": 8000,
    "dashboard_host": "localhost",
    "default_theme": "dark",
    "notification_interval": 30,
    "min_discount_percent": 10,
    "max_price_threshold": 1000.00,
    "auto_backup": True,
    "backup_interval": 24,
    "backup_retention_days": 7
}

# ==========================================
# CONFIGURAÇÕES DE SCRAPING
# ==========================================
SCRAPING_CONFIG = {
    "delay": 2.0,
    "timeout": 30,
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "retry_attempts": 3,
    "max_concurrent": 5
}

# ==========================================
# FUNÇÃO PARA VALIDAR CONFIGURAÇÕES
# ==========================================
def validate_config():
    """Valida se todas as configurações obrigatórias estão presentes"""
    required_configs = [
        ("TELEGRAM", TELEGRAM_CONFIG, ["bot_token", "chat_id"]),
        ("ALIEXPRESS", ALIEXPRESS_API_CONFIG, ["app_key", "app_secret"]),
        ("SHOPEE", SHOPEE_API_CONFIG, ["app_id", "secret"]),
        ("AWIN", AFFILIATE_CONFIG, ["awin_affids"]),
        ("RAKUTEN", RAKUTEN_API_CONFIG, ["webservice_token", "security_token"])
    ]
    
    missing_configs = []
    
    for name, config, required_fields in required_configs:
        for field in required_fields:
            if field not in config or not config[field]:
                missing_configs.append(f"{name}.{field}")
    
    if missing_configs:
        print("⚠️ Configurações obrigatórias ausentes:")
        for config in missing_configs:
            print(f"   - {config}")
        return False
    
    print("✅ Todas as configurações obrigatórias estão presentes!")
    return True

# ==========================================
# FUNÇÃO PARA EXPORTAR PARA .ENV
# ==========================================
def export_to_env():
    """Exporta as configurações para formato .env"""
    env_content = []
    
    # Telegram
    env_content.append("# ==========================================")
    env_content.append("# CONFIGURAÇÕES DO TELEGRAM")
    env_content.append("# ==========================================")
    env_content.append(f"TELEGRAM_BOT_TOKEN={TELEGRAM_CONFIG['bot_token']}")
    env_content.append(f"TELEGRAM_CHAT_ID={TELEGRAM_CONFIG['chat_id']}")
    env_content.append(f"TELEGRAM_BOT_NAME={TELEGRAM_CONFIG['bot_name']}")
    env_content.append("")
    
    # AliExpress
    env_content.append("# ==========================================")
    env_content.append("# ALIEXPRESS OPEN PLATFORM")
    env_content.append("# ==========================================")
    env_content.append(f"ALI_APP_KEY={ALIEXPRESS_API_CONFIG['app_key']}")
    env_content.append(f"ALI_APP_SECRET={ALIEXPRESS_API_CONFIG['app_secret']}")
    env_content.append(f"ALI_ACCESS_TOKEN={ALIEXPRESS_API_CONFIG['access_token']}")
    env_content.append(f"ALI_REFRESH_TOKEN={ALIEXPRESS_API_CONFIG['refresh_token']}")
    env_content.append(f"USE_API_ALIEXPRESS={ALIEXPRESS_API_CONFIG['enabled']}")
    env_content.append("")
    
    # Shopee
    env_content.append("# ==========================================")
    env_content.append("# SHOPEE AFFILIATE OPEN API")
    env_content.append("# ==========================================")
    env_content.append(f"SHOPEE_APP_ID={SHOPEE_API_CONFIG['app_id']}")
    env_content.append(f"SHOPEE_SECRET={SHOPEE_API_CONFIG['secret']}")
    env_content.append(f"SHOPEE_AFFILIATE_ID={SHOPEE_API_CONFIG['affiliate_id']}")
    env_content.append(f"USE_API_SHOPEE={SHOPEE_API_CONFIG['enabled']}")
    env_content.append("")
    
    # Awin
    env_content.append("# ==========================================")
    env_content.append("# AWIN PUBLISHER API")
    env_content.append("# ==========================================")
    env_content.append(f"AWIN_OAUTH2_TOKEN={AWIN_API_CONFIG['oauth2_token']}")
    env_content.append(f"USE_API_AWIN={AWIN_API_CONFIG['enabled']}")
    env_content.append("")
    
    # Rakuten
    env_content.append("# ==========================================")
    env_content.append("# RAKUTEN ADVERTISING API")
    env_content.append("# ==========================================")
    env_content.append(f"RAKUTEN_ENABLED={RAKUTEN_API_CONFIG['enabled']}")
    env_content.append(f"RAKUTEN_WEBSERVICE_TOKEN={RAKUTEN_API_CONFIG['webservice_token']}")
    env_content.append(f"RAKUTEN_SECURITY_TOKEN={RAKUTEN_API_CONFIG['security_token']}")
    env_content.append(f"RAKUTEN_SID={RAKUTEN_API_CONFIG['sid']}")
    env_content.append(f"USE_API_RAKUTEN={RAKUTEN_API_CONFIG['enabled']}")
    env_content.append("")
    
    return "\n".join(env_content)

if __name__ == "__main__":
    print("🔑 CONFIGURAÇÃO DO GARIMPEIRO GEEK")
    print("=" * 40)
    
    # Validar configurações
    if validate_config():
        print("\n📝 Exportando para formato .env...")
        env_content = export_to_env()
        
        # Salvar em arquivo temporário
        with open("config/temp_env.txt", "w", encoding="utf-8") as f:
            f.write(env_content)
        
        print("✅ Configurações exportadas para config/temp_env.txt")
        print("📋 Copie o conteúdo para seu arquivo .env")
    else:
        print("\n❌ Configure as chaves obrigatórias antes de continuar")
