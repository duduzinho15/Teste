#!/usr/bin/env python3
"""
Script para atualização automática do README.md
Monitora mudanças no projeto e mantém a documentação sempre atualizada
"""

import os
import sys
import json
import hashlib
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Tuple
import re

# Adicionar src ao path para imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

class ReadmeUpdater:
    """Classe para atualização automática do README.md"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.src_dir = project_root / "src"
        self.apps_dir = project_root / "apps"
        self.readme_path = project_root / "README.md"
        self.structure_cache_file = project_root / ".readme_structure_cache.json"
        
    def get_file_structure(self) -> Dict[str, List[str]]:
        """Obtém a estrutura atual de arquivos do projeto"""
        structure = {
            "src": [],
            "apps": [],
            "config": [],
            "tests": [],
            "docs": [],
            "scripts": []
        }
        
        # Mapear estrutura src/
        if self.src_dir.exists():
            for item in self.src_dir.rglob("*"):
                if item.is_file() and item.suffix == ".py":
                    relative_path = str(item.relative_to(self.src_dir))
                    structure["src"].append(relative_path)
        
        # Mapear estrutura apps/
        if self.apps_dir.exists():
            for item in self.apps_dir.rglob("*"):
                if item.is_file() and item.suffix == ".py":
                    relative_path = str(item.relative_to(self.apps_dir))
                    structure["apps"].append(relative_path)
        
        # Mapear outros diretórios
        for dir_name in ["config", "tests", "docs", "scripts"]:
            dir_path = self.project_root / dir_name
            if dir_path.exists():
                for item in dir_path.rglob("*"):
                    if item.is_file():
                        relative_path = str(item.relative_to(self.project_root))
                        structure[dir_name].append(relative_path)
        
        return structure
    
    def get_structure_hash(self, structure: Dict[str, List[str]]) -> str:
        """Gera hash da estrutura para detectar mudanças"""
        structure_str = json.dumps(structure, sort_keys=True)
        return hashlib.md5(structure_str.encode()).hexdigest()
    
    def load_cached_structure(self) -> Tuple[Dict[str, List[str]], str]:
        """Carrega estrutura em cache se existir"""
        if self.structure_cache_file.exists():
            try:
                cache_data = json.loads(self.structure_cache_file.read_text())
                return cache_data["structure"], cache_data["hash"]
            except (json.JSONDecodeError, KeyError):
                pass
        return {}, ""
    
    def save_structure_cache(self, structure: Dict[str, List[str]], structure_hash: str):
        """Salva estrutura em cache"""
        cache_data = {
            "structure": structure,
            "hash": structure_hash,
            "timestamp": datetime.now().isoformat()
        }
        self.structure_cache_file.write_text(json.dumps(cache_data, indent=2))
    
    def has_structure_changed(self) -> bool:
        """Verifica se a estrutura do projeto mudou"""
        current_structure = self.get_file_structure()
        current_hash = self.get_structure_hash(current_structure)
        
        cached_structure, cached_hash = self.load_cached_structure()
        
        if not cached_hash or current_hash != cached_hash:
            self.save_structure_cache(current_structure, current_hash)
            return True
        
        return False
    
    def update_readme_structure(self):
        """Atualiza a seção de arquitetura do README"""
        if not self.readme_path.exists():
            print("README.md nao encontrado!")
            return False
        
        readme_content = self.readme_path.read_text(encoding='utf-8')
        
        # Gerar nova estrutura
        structure = self.get_file_structure()
        new_structure = self.generate_structure_text(structure)
        
        # Atualizar seção de arquitetura
        pattern = r'(## 🏗️ Arquitetura Completa\s*\n```\n).*?(\n```\n)'
        replacement = r'\1' + new_structure + r'\2'
        
        if re.search(pattern, readme_content, re.DOTALL):
            updated_content = re.sub(pattern, replacement, readme_content, flags=re.DOTALL)
            
            # Atualizar timestamp
            timestamp_pattern = r'(\*\*Última atualização\*\*: ).*?(\n)'
            timestamp_replacement = r'\1' + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + r'\2'
            updated_content = re.sub(timestamp_pattern, timestamp_replacement, updated_content)
            
            self.readme_path.write_text(updated_content, encoding='utf-8')
            print("README.md atualizado com sucesso!")
            return True
        else:
            print("Secao de arquitetura nao encontrada no README")
            return False
    
    def generate_structure_text(self, structure: Dict[str, List[str]]) -> str:
        """Gera texto da estrutura para o README"""
        lines = []
        
        # Estrutura src/
        lines.append("src/")
        lines.append("├── affiliate/          # Conversores de afiliados")
        lines.append("│   ├── amazon.py      # Conversor Amazon (ASIN-first + fallback)")
        lines.append("│   ├── mercadolivre.py # Conversor Mercado Livre")
        lines.append("│   ├── shopee.py      # Conversor Shopee")
        lines.append("│   ├── magazineluiza.py # Conversor Magazine Luiza")
        lines.append("│   ├── aliexpress.py  # Conversor AliExpress")
        lines.append("│   ├── awin.py        # Conversor Awin")
        lines.append("│   ├── rakuten.py     # Conversor Rakuten")
        lines.append("│   ├── *_api.py       # Clientes de API oficiais")
        lines.append("│   └── base_api.py    # Classe base para APIs")
        
        lines.append("├── app/                # Aplicação principal")
        lines.append("│   ├── queue/         # Sistema de fila de ofertas")
        lines.append("│   │   ├── offer_queue.py      # Fila principal")
        lines.append("│   │   ├── moderation_system.py # Sistema de moderação")
        lines.append("│   │   ├── quality_controller.py # Controle de qualidade")
        lines.append("│   │   └── queue_manager.py    # Gerenciador da fila")
        lines.append("│   ├── scheduler/     # Agendador cron")
        lines.append("│   │   ├── cron_manager.py     # Gerenciador de cron jobs")
        lines.append("│   │   ├── job_scheduler.py    # Agendador de tarefas")
        lines.append("│   │   ├── task_runner.py     # Executor de tarefas")
        lines.append("│   │   └── post_scheduler.py  # Agendador de postagens")
        lines.append("│   ├── dashboard/     # Dashboard interno")
        lines.append("│   └── bot/           # Bot interno")
        
        lines.append("├── core/               # Componentes principais")
        lines.append("│   ├── models.py      # Modelos de dados (Offer, etc.)")
        lines.append("│   ├── settings.py    # Configurações (.env)")
        lines.append("│   ├── database.py    # Banco de dados SQLite")
        lines.append("│   ├── db_init.py     # Inicialização do banco")
        lines.append("│   ├── affiliate_*.py # Sistema de afiliados")
        lines.append("│   ├── conversion_metrics.py  # Métricas de conversão")
        lines.append("│   ├── failure_alerts.py      # Sistema de alertas")
        lines.append("│   ├── optimization_engine.py # Motor de otimização")
        lines.append("│   ├── performance_logger.py  # Logger de performance")
        lines.append("│   ├── enhanced_metrics.py    # Métricas avançadas")
        lines.append("│   ├── alert_system.py        # Sistema de alertas")
        lines.append("│   ├── analytics_queries.py   # Queries analíticas")
        lines.append("│   ├── cache_config.py        # Configuração de cache")
        lines.append("│   ├── deduplication.py       # Sistema de deduplicação")
        lines.append("│   ├── rate_limiter.py        # Rate limiting")
        lines.append("│   ├── affiliate_cache.py     # Cache de afiliados")
        lines.append("│   ├── offer_pipeline.py      # Pipeline de ofertas")
        lines.append("│   ├── affiliate_converter.py # Conversor de afiliados")
        lines.append("│   ├── matchers.py            # Sistema de matching")
        lines.append("│   ├── metrics.py             # Métricas básicas")
        lines.append("│   ├── platforms.py           # Configurações de plataformas")
        lines.append("│   ├── live_logs.py           # Logs em tempo real")
        lines.append("│   ├── logging_setup.py       # Configuração de logs")
        lines.append("│   ├── storage.py             # Sistema de armazenamento")
        lines.append("│   ├── monitoring/            # Sistema de monitoramento")
        lines.append("│   └── cache/                 # Sistema de cache")
        
        lines.append("├── pipelines/          # Pipelines de processamento")
        lines.append("│   ├── ingest_offers_api.py   # Ingestão via APIs")
        lines.append("│   ├── enrich_offers_api.py   # Enriquecimento de dados")
        lines.append("│   ├── price_collect.py       # Coleta de preços")
        lines.append("│   ├── price_enrich.py        # Enriquecimento de preços")
        lines.append("│   └── price_aggregate.py     # Agregação de preços")
        
        lines.append("├── posting/            # Sistema de postagem")
        lines.append("│   ├── message_formatter.py   # Formatação de mensagens")
        lines.append("│   └── posting_manager.py     # Gerenciador de postagens")
        
        lines.append("├── scrapers/           # Sistema de scrapers")
        lines.append("│   ├── base_scraper.py        # Classe base para scrapers")
        lines.append("│   ├── lojas/                 # Scrapers de lojas")
        lines.append("│   ├── comunidades/           # Scrapers de comunidades")
        lines.append("│   │   ├── promobit/          # Scraper Promobit")
        lines.append("│   │   ├── pelando/           # Scraper Pelando")
        lines.append("│   │   └── meupc/             # Scraper MeuPC")
        lines.append("│   └── precos/                # Scrapers de preços")
        lines.append("│       ├── zoom/              # Scraper Zoom")
        lines.append("│       └── buscape/           # Scraper Buscapé")
        
        lines.append("├── telegram_bot/       # Bot do Telegram")
        lines.append("│   ├── bot.py                 # Bot principal")
        lines.append("│   ├── bot_manager.py         # Gerenciador do bot")
        lines.append("│   ├── message_builder.py     # Construtor de mensagens")
        lines.append("│   └── notification_manager.py # Gerenciador de notificações")
        
        lines.append("├── utils/              # Utilitários")
        lines.append("│   ├── anti_bot.py            # Medidas anti-bot")
        lines.append("│   ├── affiliate_validator.py # Validador de URLs")
        lines.append("│   ├── asin_cache.py          # Cache de ASINs")
        lines.append("│   ├── url_utils.py           # Utilitários de URL")
        lines.append("│   └── sqlite_helpers.py      # Helpers para SQLite")
        
        lines.append("├── diagnostics/        # Sistema de diagnóstico")
        lines.append("│   └── ui_reporter.py         # Relatórios de UI")
        
        lines.append("├── recommender/        # Sistema de recomendação")
        
        lines.append("├── db/                 # Banco de dados")
        lines.append("│   ├── garimpeiro_geek.db    # Banco principal")
        lines.append("│   ├── aff_cache.sqlite       # Cache de afiliados")
        lines.append("│   └── analytics.sqlite       # Banco de analytics")
        
        lines.append("├── logs/               # Logs do sistema")
        lines.append("├── exports/            # Exportações de dados")
        
        lines.append("└── tests/              # Testes automatizados")
        lines.append("    ├── unit/           # Testes unitários")
        lines.append("    ├── e2e/            # Testes end-to-end")
        lines.append("    ├── api/            # Testes de API")
        lines.append("    ├── helpers/        # Helpers para testes")
        lines.append("    └── data/           # Dados de teste")
        
        lines.append("")
        lines.append("apps/")
        lines.append("└── flet_dashboard/     # Dashboard Flet")
        lines.append("    ├── main.py         # Aplicação principal")
        lines.append("    ├── ui_components.py # Componentes de UI")
        lines.append("    └── run_dashboard.py # Script de execução")
        
        return "\n".join(lines)
    
    def run(self) -> bool:
        """Executa a atualização do README"""
        print("Verificando mudancas na estrutura do projeto...")
        
        if self.has_structure_changed():
            print("Estrutura do projeto mudou, atualizando README...")
            return self.update_readme_structure()
        else:
            print("README ja esta atualizado!")
            return True

def main():
    """Função principal"""
    project_root = Path(__file__).parent.parent
    updater = ReadmeUpdater(project_root)
    
    try:
        success = updater.run()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"Erro ao atualizar README: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
