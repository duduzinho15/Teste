"""
Configurações do sistema Garimpeiro Geek
Carrega variáveis de ambiente do arquivo .env
"""

import os
from pathlib import Path
from typing import Any, Dict

import yaml
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
ENV_FILE = Path(__file__).parent.parent.parent / ".env"
if ENV_FILE.exists():
    load_dotenv(ENV_FILE)

# Carregar configurações adicionais do arquivo settings.yaml
SETTINGS_FILE = Path(__file__).parent.parent.parent / "settings.yaml"


def _load_yaml_settings() -> Dict[str, Any]:
    if SETTINGS_FILE.exists():
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {}


YAML_SETTINGS = _load_yaml_settings()


class Settings:
    """Configurações centralizadas do sistema"""

    # Configurações do Telegram
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHANNEL_ID: str = os.getenv("TELEGRAM_CHANNEL_ID", "")
    TELEGRAM_ADMIN_USER_ID: str = os.getenv("TELEGRAM_ADMIN_USER_ID", "")
    TELEGRAM_ADMIN_IDS: str = os.getenv("TELEGRAM_ADMIN_IDS", "")

    # Configurações de banco de dados
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///garimpeiro_geek.db")
    DATABASE_PATH: str = os.getenv("DATABASE_PATH", "src/db/garimpeiro_geek.db")

    # Configurações de logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "src/logs/garimpeiro_geek.log")
    LOG_MAX_SIZE: str = os.getenv("LOG_MAX_SIZE", "10MB")  # String para permitir "10MB"
    LOG_BACKUP_COUNT: int = int(os.getenv("LOG_BACKUP_COUNT", "5"))

    # Configurações de scraping
    SCRAPING_TIMEOUT: int = int(os.getenv("SCRAPING_TIMEOUT", "30"))
    SCRAPING_RETRY_ATTEMPTS: int = int(os.getenv("SCRAPING_RETRY_ATTEMPTS", "3"))
    SCRAPING_DELAY: float = float(os.getenv("SCRAPING_DELAY", "1.0"))
    SCRAPING_MAX_CONCURRENT: int = int(os.getenv("SCRAPING_MAX_CONCURRENT", "5"))

    # Configurações de afiliados
    AFFILIATE_AMAZON_TAG: str = os.getenv("AFFILIATE_AMAZON_TAG", "garimpeirogee-20")
    AFFILIATE_MAGALU_TAG: str = os.getenv("AFFILIATE_MAGALU_TAG", "")
    AFFILIATE_AWIN_PUBLISHER_ID: str = os.getenv("AFFILIATE_AWIN_PUBLISHER_ID", "")
    AFFILIATE_RAKUTEN_ID: str = os.getenv("AFFILIATE_RAKUTEN_ID", "")
    AFFILIATE_RAKUTEN_MERCHANT_ID: str = os.getenv("AFFILIATE_RAKUTEN_MERCHANT_ID", "")

    # Configurações de Pontuação de Ofertas
    DEAL_SCORE_CRITICAL: float = float(os.getenv("DEAL_SCORE_CRITICAL", "0.85"))
    DEAL_SCORE_HIGH: float = float(os.getenv("DEAL_SCORE_HIGH", "0.75"))
    
    # Limiares de desconto por categoria (em decimal: 0.20 = 20%)
    ELECTRONICS_MIN_DISC: float = float(os.getenv("ELECTRONICS_MIN_DISC", "0.20"))
    PERIPHERALS_MIN_DISC: float = float(os.getenv("PERIPHERALS_MIN_DISC", "0.25"))
    APPLIANCES_MIN_DISC: float = float(os.getenv("APPLIANCES_MIN_DISC", "0.18"))
    
    # Vendedores confiáveis (separados por vírgula)
    TRUSTED_SELLERS: str = os.getenv("TRUSTED_SELLERS", "Magazine Luiza,Kabum,Pichau,Americanas,Submarino")
    
    # Configurações de Rate Limiting do Telegram
    TG_MIN_INTERVAL_CRITICAL: int = int(os.getenv("TG_MIN_INTERVAL_CRITICAL", "20"))  # segundos
    TG_MIN_INTERVAL_HIGH: int = int(os.getenv("TG_MIN_INTERVAL_HIGH", "120"))  # segundos
    TG_MAX_PER_HOUR: int = int(os.getenv("TG_MAX_PER_HOUR", "20"))

    # Configurações de postagem
    POSTING_MIN_DELAY_SECONDS: int = int(
        YAML_SETTINGS.get("posting", {}).get("min_delay_seconds", 180)
    )
    
    # Janelas de pico (horários em que as ofertas têm maior engajamento)
    PEAK_HOURS: str = os.getenv("PEAK_HOURS", "07:30-09:30,12:00-14:00,19:00-22:30")
    
    # Configurações Rakuten (desabilitado por padrão)
    RAKUTEN_ENABLED: bool = os.getenv("RAKUTEN_ENABLED", "false").lower() == "true"
    RAKUTEN_WEBSERVICE_TOKEN: str = os.getenv("RAKUTEN_WEBSERVICE_TOKEN", "")
    RAKUTEN_SECURITY_TOKEN: str = os.getenv("RAKUTEN_SECURITY_TOKEN", "")
    RAKUTEN_SID: str = os.getenv("RAKUTEN_SID", "")

    # Configurações das APIs oficiais
    # AliExpress Open Platform
    ALI_APP_KEY: str = os.getenv("ALI_APP_KEY", "")
    ALI_APP_SECRET: str = os.getenv("ALI_APP_SECRET", "")
    ALI_ACCESS_TOKEN: str = os.getenv("ALI_ACCESS_TOKEN", "")
    ALI_REFRESH_TOKEN: str = os.getenv("ALI_REFRESH_TOKEN", "")

    # Rakuten Advertising
    RKTN_CLIENT_ID: str = os.getenv("RKTN_CLIENT_ID", "")
    RKTN_CLIENT_SECRET: str = os.getenv("RKTN_CLIENT_SECRET", "")
    RKTN_ACCESS_TOKEN: str = os.getenv("RKTN_ACCESS_TOKEN", "")

    # Shopee Affiliate Open API
    SHOPEE_APP_ID: str = os.getenv("SHOPEE_APP_ID", "")
    SHOPEE_SECRET: str = os.getenv("SHOPEE_SECRET", "")
    SHOPEE_ACCESS_TOKEN: str = os.getenv("SHOPEE_ACCESS_TOKEN", "")

    # Awin Publisher API
    AWIN_PUBLISHER_ID: str = os.getenv("AWIN_PUBLISHER_ID", "")
    AWIN_ACCESS_TOKEN: str = os.getenv("AWIN_ACCESS_TOKEN", "")

    # Flags de controle das APIs
    USE_API_ALIEXPRESS: bool = (
        os.getenv("USE_API_ALIEXPRESS", "false").lower() == "true"
    )
    USE_API_RAKUTEN: bool = os.getenv("USE_API_RAKUTEN", "false").lower() == "true"
    USE_API_SHOPEE: bool = os.getenv("USE_API_SHOPEE", "false").lower() == "true"
    USE_API_AWIN: bool = os.getenv("USE_API_AWIN", "false").lower() == "true"

    # Flags "API-first" (forçar uso da API quando disponível)
    USE_API_FIRST_SHOPEE: bool = (
        os.getenv("USE_API_FIRST_SHOPEE", "true").lower() == "true"
    )
    USE_API_FIRST_ALIEXPRESS: bool = (
        os.getenv("USE_API_FIRST_ALIEXPRESS", "true").lower() == "true"
    )

    # DRY-RUN de postagem (padrão: True)
    DRY_RUN: bool = os.getenv("DRY_RUN", "true").lower() == "true"

    @classmethod
    def is_dry_run(cls) -> bool:
        """Retorna se o sistema está em DRY_RUN (não publica de fato)."""
        return cls.DRY_RUN

    @classmethod
    def get_admin_ids(cls) -> list:
        """Retorna lista de admin IDs (strings) a partir do env.

        Usa TELEGRAM_ADMIN_IDS (separado por vírgulas) e TELEGRAM_ADMIN_USER_ID como fallback.
        """
        ids = []
        if cls.TELEGRAM_ADMIN_IDS:
            ids.extend([x.strip() for x in cls.TELEGRAM_ADMIN_IDS.split(",") if x.strip()])
        if cls.TELEGRAM_ADMIN_USER_ID:
            ids.append(cls.TELEGRAM_ADMIN_USER_ID.strip())
        # normalizar para únicos
        return list(dict.fromkeys(ids))

    # Configurações de notificações
    NOTIFICATIONS_ENABLED: bool = (
        os.getenv("NOTIFICATIONS_ENABLED", "true").lower() in ("1", "true", "yes", "on")
    )
    NOTIFICATION_INTERVAL: int = int(
        os.getenv("NOTIFICATION_INTERVAL", "3600")
    )  # segundos

    # Configurações de desenvolvimento
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    TESTING: bool = os.getenv("TESTING", "false").lower() == "true"

    # Configurações de cache
    CACHE_ENABLED: bool = os.getenv("CACHE_ENABLED", "true").lower() == "true"
    CACHE_TTL: int = int(os.getenv("CACHE_TTL", "300"))  # segundos

    # Configurações de rate limiting
    RATE_LIMIT_ENABLED: bool = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
    RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
    RATE_LIMIT_WINDOW: int = int(os.getenv("RATE_LIMIT_WINDOW", "3600"))  # segundos

    # Configurações de monitoramento
    MONITORING_ENABLED: bool = os.getenv("MONITORING_ENABLED", "true").lower() == "true"
    METRICS_COLLECTION_INTERVAL: int = int(
        os.getenv("METRICS_COLLECTION_INTERVAL", "300")
    )  # segundos

    # Configurações de backup
    BACKUP_ENABLED: bool = os.getenv("BACKUP_ENABLED", "true").lower() == "true"
    BACKUP_INTERVAL: int = int(os.getenv("BACKUP_INTERVAL", "86400"))  # segundos (24h)
    BACKUP_RETENTION_DAYS: int = int(os.getenv("BACKUP_RETENTION_DAYS", "30"))

    @classmethod
    def get_telegram_config(cls) -> Dict[str, Any]:
        """Retorna configurações do Telegram"""
        return {
            "bot_token": cls.TELEGRAM_BOT_TOKEN,
            "channel_id": cls.TELEGRAM_CHANNEL_ID,
            "admin_user_id": cls.TELEGRAM_ADMIN_USER_ID,
        }

    @classmethod
    def get_database_config(cls) -> Dict[str, Any]:
        """Retorna configurações do banco de dados"""
        return {
            "url": cls.DATABASE_URL,
            "path": cls.DATABASE_PATH,
        }

    @classmethod
    def get_api_config(cls) -> Dict[str, Any]:
        """Retorna configurações das APIs oficiais"""
        return {
            "aliexpress": {
                "enabled": cls.USE_API_ALIEXPRESS,
                "app_key": cls.ALI_APP_KEY,
                "app_secret": cls.ALI_APP_SECRET,
                "access_token": cls.ALI_ACCESS_TOKEN,
                "refresh_token": cls.ALI_REFRESH_TOKEN,
            },
            "rakuten": {
                "enabled": cls.USE_API_RAKUTEN,
                "client_id": cls.RKTN_CLIENT_ID,
                "client_secret": cls.RKTN_CLIENT_SECRET,
                "access_token": cls.RKTN_ACCESS_TOKEN,
            },
            "shopee": {
                "enabled": cls.USE_API_SHOPEE,
                "app_id": cls.SHOPEE_APP_ID,
                "secret": cls.SHOPEE_SECRET,
                "access_token": cls.SHOPEE_ACCESS_TOKEN,
            },
            "awin": {
                "enabled": cls.USE_API_AWIN,
                "publisher_id": cls.AWIN_PUBLISHER_ID,
                "access_token": cls.AWIN_ACCESS_TOKEN,
            },
        }

    @classmethod
    def get_available_apis(cls) -> Dict[str, bool]:
        """Retorna APIs disponíveis baseado nas configurações"""
        api_config = cls.get_api_config()
        return {
            name: config["enabled"]
            and bool(
                config.get("app_key")
                or config.get("client_id")
                or config.get("app_id")
                or config.get("publisher_id")
            )
            for name, config in api_config.items()
        }

    @classmethod
    def get_logging_config(cls) -> Dict[str, Any]:
        """Retorna configurações de logging"""
        return {
            "level": cls.LOG_LEVEL,
            "file": cls.LOG_FILE,
            "max_size": cls.LOG_MAX_SIZE,
            "backup_count": cls.LOG_BACKUP_COUNT,
        }

    @classmethod
    def get_scraping_config(cls) -> Dict[str, Any]:
        """Retorna configurações de scraping"""
        return {
            "timeout": cls.SCRAPING_TIMEOUT,
            "retry_attempts": cls.SCRAPING_RETRY_ATTEMPTS,
            "delay": cls.SCRAPING_DELAY,
            "max_concurrent": cls.SCRAPING_MAX_CONCURRENT,
        }

    @classmethod
    def get_affiliate_config(cls) -> Dict[str, Any]:
        """Retorna configurações de afiliados"""
        return {
            "amazon_tag": cls.AFFILIATE_AMAZON_TAG,
            "magalu_tag": cls.AFFILIATE_MAGALU_TAG,
            "awin_publisher_id": cls.AFFILIATE_AWIN_PUBLISHER_ID,
            "rakuten_id": cls.AFFILIATE_RAKUTEN_ID,
            "rakuten_merchant_id": cls.AFFILIATE_RAKUTEN_MERCHANT_ID,
        }

    @classmethod
    def get_posting_config(cls) -> Dict[str, Any]:
        """Retorna configurações de postagem"""
        return {
            "min_delay_seconds": cls.POSTING_MIN_DELAY_SECONDS,
        }

    @classmethod
    def validate_required_settings(cls) -> bool:
        """Valida se as configurações obrigatórias estão definidas"""
        required_settings = [
            cls.TELEGRAM_BOT_TOKEN,
            cls.DATABASE_PATH,
        ]

        missing_settings = [setting for setting in required_settings if not setting]

        if missing_settings:
            print(f"❌ Configurações obrigatórias não definidas: {missing_settings}")
            return False

        return True

    @classmethod
    def print_current_config(cls) -> None:
        """Imprime a configuração atual (sem dados sensíveis)"""
        print("🔧 Configurações atuais do Garimpeiro Geek:")
        print(
            f"  📱 Telegram: {'✅ Configurado' if cls.TELEGRAM_BOT_TOKEN else '❌ Não configurado'}"
        )
        print(f"  🗄️  Banco: {cls.DATABASE_PATH}")
        print(f"  📝 Log: {cls.LOG_LEVEL} -> {cls.LOG_FILE}")
        print(
            f"  🕷️  Scraping: {cls.SCRAPING_TIMEOUT}s timeout, {cls.SCRAPING_RETRY_ATTEMPTS} retries"
        )
        print(f"  🔗 Afiliados: Amazon ({cls.AFFILIATE_AMAZON_TAG})")
        print(f"  🔔 Notificações: {'✅' if cls.NOTIFICATIONS_ENABLED else '❌'}")
        print(f"  🐛 Debug: {'✅' if cls.DEBUG else '❌'}")
        print(f"  📊 Monitoramento: {'✅' if cls.MONITORING_ENABLED else '❌'}")
        print(f"  💾 Backup: {'✅' if cls.BACKUP_ENABLED else '❌'}")


# Instância global das configurações
settings = Settings()


def get_settings() -> Settings:
    """Retorna a instância global das configurações"""
    return settings


def reload_settings() -> None:
    """Recarrega as configurações do arquivo .env"""
    global settings
    if ENV_FILE.exists():
        load_dotenv(ENV_FILE, override=True)
    settings = Settings()


# Validação automática ao importar o módulo
if __name__ == "__main__":
    settings.print_current_config()
    if not settings.validate_required_settings():
        print("\n⚠️  Algumas configurações obrigatórias não estão definidas!")
        print(
            "   Crie um arquivo .env na raiz do projeto com as configurações necessárias."
        )
    else:
        print("\n✅ Todas as configurações obrigatórias estão definidas!")
