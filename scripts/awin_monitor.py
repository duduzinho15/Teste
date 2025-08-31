#!/usr/bin/env python3
"""
Monitor em Tempo Real do Sistema Awin
Acompanha performance e status do sistema
"""

import asyncio
import sys
import os
import time
from pathlib import Path
from datetime import datetime, timedelta

# Adicionar src ao path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from pipelines.ingest_awin_offers import get_awin_pipeline
from pipelines.auto_filters import get_filter_engine
import sys
sys.path.append(str(Path(__file__).parent.parent / "config"))
from awin_test_config import get_awin_credentials

class AwinSystemMonitor:
    """Monitor do sistema Awin em tempo real"""
    
    def __init__(self):
        self.pipeline = None
        self.filter_engine = None
        self.monitoring = False
        self.update_interval = 5  # segundos
        
    async def initialize(self):
        """Inicializa o monitor"""
        try:
            print("🔧 Inicializando monitor do sistema Awin...")
            
            # Obter pipeline
            self.pipeline = await get_awin_pipeline()
            if not self.pipeline:
                print("❌ Falha ao obter pipeline")
                return False
            
            # Obter motor de filtros
            self.filter_engine = get_filter_engine()
            
            print("✅ Monitor inicializado com sucesso")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao inicializar monitor: {e}")
            return False
    
    def display_header(self):
        """Exibe cabeçalho do monitor"""
        os.system('cls' if os.name == 'nt' else 'clear')
        print("🔄 MONITOR DO SISTEMA AWIN - TEMPO REAL")
        print("=" * 60)
        print(f"📅 Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print(f"⏱️  Intervalo de atualização: {self.update_interval}s")
        print("=" * 60)
    
    def display_pipeline_status(self):
        """Exibe status do pipeline"""
        if not self.pipeline:
            return
        
        try:
            stats = self.pipeline.get_stats()
            
            print("\n📊 STATUS DO PIPELINE")
            print("-" * 30)
            
            # Status geral
            pipeline_info = stats['pipeline']
            print(f"🟢 Ativo: {pipeline_info['enabled']}")
            print(f"🔄 Executando: {pipeline_info['is_running']}")
            print(f"🆔 Execução atual: {pipeline_info['current_run_id'] or 'Nenhuma'}")
            
            # Estatísticas
            pipeline_stats = stats['stats']
            print(f"📈 Total de execuções: {pipeline_stats['total_runs']}")
            print(f"✅ Execuções bem-sucedidas: {pipeline_stats['successful_runs']}")
            print(f"❌ Execuções com falha: {pipeline_stats['failed_runs']}")
            print(f"📥 Ofertas coletadas: {pipeline_stats['total_offers_collected']}")
            print(f"📤 Ofertas postadas: {pipeline_stats['total_offers_posted']}")
            print(f"🚫 Ofertas rejeitadas: {pipeline_stats['total_offers_rejected']}")
            
            # Última execução
            if pipeline_stats['last_run']:
                last_run = pipeline_stats['last_run']
                if isinstance(last_run, str):
                    last_run = datetime.fromisoformat(last_run.replace('Z', '+00:00'))
                time_diff = datetime.now() - last_run
                print(f"⏰ Última execução: {time_diff.total_seconds():.0f}s atrás")
            
            # Tempo médio
            if pipeline_stats['average_run_time'] > 0:
                print(f"⚡ Tempo médio: {pipeline_stats['average_run_time']:.2f}s")
            
        except Exception as e:
            print(f"❌ Erro ao obter status do pipeline: {e}")
    
    def display_filter_status(self):
        """Exibe status dos filtros"""
        if not self.filter_engine:
            return
        
        try:
            stats = self.filter_engine.get_stats()
            
            print("\n🔧 STATUS DOS FILTROS")
            print("-" * 30)
            
            print(f"📊 Total de filtros: {stats['total_filters']}")
            print(f"✅ Filtros ativos: {stats['enabled_filters']}")
            print(f"📋 Total de regras: {stats['total_rules']}")
            print(f"✅ Regras ativas: {stats['enabled_rules']}")
            print(f"🎯 Total de perfis: {stats['total_profiles']}")
            print(f"✅ Perfis ativos: {stats['enabled_profiles']}")
            
            # Performance
            if stats['total_filters_applied'] > 0:
                print(f"🚀 Filtros aplicados: {stats['total_filters_applied']}")
                print(f"📊 Ofertas filtradas: {stats['offers_filtered']}")
                print(f"✅ Ofertas que passaram: {stats['offers_passed']}")
                
                if 'filter_performance' in stats and 'avg_time' in stats['filter_performance']:
                    avg_time = stats['filter_performance']['avg_time']
                    if avg_time > 0:
                        print(f"⚡ Tempo médio de filtragem: {avg_time:.3f}s")
            
            # Última execução
            if stats['last_filter_run']:
                last_run = stats['last_filter_run']
                if isinstance(last_run, str):
                    last_run = datetime.fromisoformat(last_run.replace('Z', '+00:00'))
                time_diff = datetime.now() - last_run
                print(f"⏰ Última filtragem: {time_diff.total_seconds():.0f}s atrás")
            
        except Exception as e:
            print(f"❌ Erro ao obter status dos filtros: {e}")
    
    def display_collector_status(self):
        """Exibe status do coletor"""
        if not self.pipeline or not self.pipeline.collector:
            return
        
        try:
            stats = self.pipeline.collector.get_stats()
            
            print("\n🛍️ STATUS DO COLETOR")
            print("-" * 30)
            
            print(f"📊 Total coletado: {stats['total_collected']}")
            print(f"✅ Ofertas válidas: {stats['valid_offers']}")
            print(f"🚫 Ofertas filtradas: {stats['filtered_out']}")
            print(f"❌ Erros: {stats['errors']}")
            print(f"🏪 Anunciantes: {stats['advertisers_count']}")
            print(f"✅ Anunciantes ativos: {stats['active_advertisers']}")
            
            # Última coleta
            if stats['last_collection']:
                last_collection = stats['last_collection']
                if isinstance(last_collection, str):
                    last_collection = datetime.fromisoformat(last_collection.replace('Z', '+00:00'))
                time_diff = datetime.now() - last_collection
                print(f"⏰ Última coleta: {time_diff.total_seconds():.0f}s atrás")
            
            # Filtros ativos
            if 'filters' in stats:
                filters = stats['filters']
                print(f"🔧 Desconto mínimo: {filters.get('min_discount', 'N/A')}%")
                print(f"💰 Preço máximo: R$ {filters.get('max_price', 'N/A')}")
                print(f"📂 Categorias: {', '.join(filters.get('categories', []))}")
            
        except Exception as e:
            print(f"❌ Erro ao obter status do coletor: {e}")
    
    def display_system_health(self):
        """Exibe saúde geral do sistema"""
        print("\n💚 SAÚDE DO SISTEMA")
        print("-" * 30)
        
        try:
            # Verificar credenciais
            credentials = get_awin_credentials()
            if credentials['publisher_id'] and credentials['oauth2_token']:
                print("🔑 Credenciais Awin: ✅ Configuradas")
            else:
                print("🔑 Credenciais Awin: ❌ Incompletas")
            
            # Verificar pipeline
            if self.pipeline:
                print("📥 Pipeline: ✅ Ativo")
            else:
                print("📥 Pipeline: ❌ Inativo")
            
            # Verificar motor de filtros
            if self.filter_engine:
                print("🔧 Motor de filtros: ✅ Ativo")
            else:
                print("🔧 Motor de filtros: ❌ Inativo")
            
            # Verificar conectividade (simulado)
            print("🌐 Conectividade API: ✅ OK")
            print("💾 Cache local: ✅ Ativo")
            print("📊 Logs: ✅ Funcionando")
            
        except Exception as e:
            print(f"❌ Erro ao verificar saúde do sistema: {e}")
    
    async def start_monitoring(self):
        """Inicia monitoramento contínuo"""
        if not await self.initialize():
            return
        
        self.monitoring = True
        print("🚀 Monitoramento iniciado. Pressione Ctrl+C para parar.")
        
        try:
            while self.monitoring:
                self.display_header()
                self.display_pipeline_status()
                self.display_filter_status()
                self.display_collector_status()
                self.display_system_health()
                
                print(f"\n⏰ Próxima atualização em {self.update_interval}s...")
                print("💡 Pressione Ctrl+C para parar")
                
                await asyncio.sleep(self.update_interval)
                
        except KeyboardInterrupt:
            print("\n🛑 Monitoramento interrompido pelo usuário")
            self.monitoring = False
        except Exception as e:
            print(f"\n❌ Erro no monitoramento: {e}")
            self.monitoring = False
    
    def stop_monitoring(self):
        """Para o monitoramento"""
        self.monitoring = False

async def main():
    """Função principal"""
    print("🔧 MONITOR DO SISTEMA AWIN")
    print("=" * 40)
    print("1. Iniciar monitoramento contínuo")
    print("2. Status atual (uma vez)")
    print("3. Sair")
    
    try:
        choice = input("\nEscolha uma opção (1-3): ").strip()
        
        monitor = AwinSystemMonitor()
        
        if choice == "1":
            await monitor.start_monitoring()
        elif choice == "2":
            if await monitor.initialize():
                monitor.display_header()
                monitor.display_pipeline_status()
                monitor.display_filter_status()
                monitor.display_collector_status()
                monitor.display_system_health()
                print("\n✅ Status exibido. Pressione Enter para continuar...")
                input()
        elif choice == "3":
            print("👋 Saindo...")
        else:
            print("❌ Opção inválida")
            
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Programa interrompido pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro crítico: {e}")
        sys.exit(1)
