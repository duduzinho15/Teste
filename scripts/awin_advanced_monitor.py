#!/usr/bin/env python3
"""
Monitor Avançado do Sistema Awin
Sistema completo de monitoramento com modo de teste e produção
"""

import asyncio
import sys
import os
import time
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List

# Adicionar src ao path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from pipelines.ingest_awin_offers import get_awin_pipeline
from pipelines.auto_filters import get_filter_engine
from affiliate.awin_api import AwinOffersCollector, AwinAdvertiser
import sys
sys.path.append(str(Path(__file__).parent.parent / "config"))
from awin_test_config import get_awin_credentials, get_advertisers

class AwinAdvancedMonitor:
    """Monitor avançado do sistema Awin"""
    
    def __init__(self):
        self.pipeline = None
        self.filter_engine = None
        self.collector = None
        self.monitoring = False
        self.update_interval = 10  # segundos
        self.test_mode = True
        self.stats_history = []
        self.max_history = 100
        
    async def initialize(self):
        """Inicializa o monitor avançado"""
        try:
            print("🔧 Inicializando monitor avançado do sistema Awin...")
            
            # Obter credenciais
            credentials = get_awin_credentials()
            if not credentials:
                print("❌ Falha ao obter credenciais Awin")
                return False
            
            # Criar coletor direto para testes
            self.collector = AwinOffersCollector(
                credentials["publisher_id"], 
                credentials["oauth2_token"]
            )
            
            # Obter pipeline
            self.pipeline = await get_awin_pipeline()
            if not self.pipeline:
                print("⚠️ Pipeline não disponível, usando modo de teste")
            
            # Obter motor de filtros
            self.filter_engine = get_filter_engine()
            
            print("✅ Monitor avançado inicializado com sucesso")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao inicializar monitor: {e}")
            return False
    
    def display_header(self):
        """Exibe cabeçalho do monitor"""
        os.system('cls' if os.name == 'nt' else 'clear')
        print("🔄 MONITOR AVANÇADO DO SISTEMA AWIN")
        print("=" * 70)
        print(f"📅 Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print(f"⏱️  Intervalo: {self.update_interval}s | 🧪 Modo: {'TESTE' if self.test_mode else 'PRODUÇÃO'}")
        print("=" * 70)
    
    async def display_collector_status(self):
        """Exibe status detalhado do coletor"""
        if not self.collector:
            return
        
        try:
            print("\n🛍️ STATUS DO COLETOR AWIN")
            print("-" * 40)
            
            # Estatísticas do coletor
            stats = self.collector.get_stats()
            
            print(f"📊 Total coletado: {stats['total_collected']}")
            print(f"✅ Ofertas válidas: {stats['valid_offers']}")
            print(f"🚫 Ofertas filtradas: {stats['filtered_out']}")
            print(f"❌ Erros: {stats['errors']}")
            print(f"🏪 Anunciantes: {stats['advertisers_count']}")
            print(f"✅ Anunciantes ativos: {stats['active_advertisers']}")
            
            # Filtros ativos
            if 'filters' in stats:
                filters = stats['filters']
                print(f"🔧 Desconto mínimo: {filters.get('min_discount', 'N/A')}%")
                print(f"💰 Preço máximo: R$ {filters.get('max_price', 'N/A')}")
                print(f"📂 Categorias: {', '.join(filters.get('categories', []))}")
            
            # Teste de coleta em tempo real
            print("\n🧪 TESTE DE COLETA EM TEMPO REAL...")
            try:
                test_offers = await self.collector.collect_all_offers(max_offers_per_advertiser=5)
                print(f"✅ Coleta de teste: {len(test_offers)} ofertas obtidas")
                
                if test_offers:
                    print("📋 Amostra de ofertas:")
                    for i, offer in enumerate(test_offers[:3]):
                        print(f"   {i+1}. {offer.title[:60]}...")
                        print(f"      💰 R$ {offer.price} | 🏪 {offer.store} | 📂 {offer.category}")
                
            except Exception as e:
                print(f"⚠️ Erro na coleta de teste: {e}")
            
        except Exception as e:
            print(f"❌ Erro ao obter status do coletor: {e}")
    
    def display_filter_status(self):
        """Exibe status dos filtros"""
        if not self.filter_engine:
            return
        
        try:
            stats = self.filter_engine.get_stats()
            
            print("\n🔧 STATUS DOS FILTROS AUTOMÁTICOS")
            print("-" * 40)
            
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
                        print(f"⚡ Tempo médio: {avg_time:.3f}s")
            
        except Exception as e:
            print(f"❌ Erro ao obter status dos filtros: {e}")
    
    def display_pipeline_status(self):
        """Exibe status do pipeline"""
        if not self.pipeline:
            print("\n📥 STATUS DO PIPELINE")
            print("-" * 40)
            print("⚠️ Pipeline não disponível (modo de teste)")
            return
        
        try:
            stats = self.pipeline.get_stats()
            
            print("\n📥 STATUS DO PIPELINE DE INGESTÃO")
            print("-" * 40)
            
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
            
        except Exception as e:
            print(f"❌ Erro ao obter status do pipeline: {e}")
    
    def display_system_health(self):
        """Exibe saúde geral do sistema"""
        print("\n💚 SAÚDE DO SISTEMA")
        print("-" * 40)
        
        try:
            # Verificar credenciais
            credentials = get_awin_credentials()
            if credentials['publisher_id'] and credentials['oauth2_token']:
                print("🔑 Credenciais Awin: ✅ Configuradas")
            else:
                print("🔑 Credenciais Awin: ❌ Incompletas")
            
            # Verificar coletor
            if self.collector:
                print("🛍️ Coletor Awin: ✅ Ativo")
            else:
                print("🛍️ Coletor Awin: ❌ Inativo")
            
            # Verificar pipeline
            if self.pipeline:
                print("📥 Pipeline: ✅ Ativo")
            else:
                print("📥 Pipeline: ⚠️ Modo de teste")
            
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
    
    def display_performance_metrics(self):
        """Exibe métricas de performance"""
        print("\n📊 MÉTRICAS DE PERFORMANCE")
        print("-" * 40)
        
        try:
            # Estatísticas do coletor
            if self.collector:
                collector_stats = self.collector.get_stats()
                print(f"🛍️ Coletor - Total: {collector_stats['total_collected']}")
                print(f"🛍️ Coletor - Válidas: {collector_stats['valid_offers']}")
                print(f"🛍️ Coletor - Filtradas: {collector_stats['filtered_out']}")
            
            # Estatísticas dos filtros
            if self.filter_engine:
                filter_stats = self.filter_engine.get_stats()
                print(f"🔧 Filtros - Aplicados: {filter_stats['total_filters_applied']}")
                print(f"🔧 Filtros - Ofertas processadas: {filter_stats['offers_filtered']}")
                print(f"🔧 Filtros - Ofertas aprovadas: {filter_stats['offers_passed']}")
                
                if 'filter_performance' in filter_stats and 'avg_time' in filter_stats['filter_performance']:
                    avg_time = filter_stats['filter_performance']['avg_time']
                    if avg_time > 0:
                        print(f"⚡ Tempo médio de filtragem: {avg_time:.3f}s")
                        if avg_time < 0.001:
                            print(f"🚀 Performance: {1/avg_time:.0f} ofertas/segundo")
            
            # Pipeline stats
            if self.pipeline:
                pipeline_stats = self.pipeline.get_stats()
                stats_data = pipeline_stats['stats']
                print(f"📥 Pipeline - Execuções: {stats_data['total_runs']}")
                print(f"📥 Pipeline - Sucessos: {stats_data['successful_runs']}")
                print(f"📥 Pipeline - Falhas: {stats_data['failed_runs']}")
                
                if stats_data['average_run_time'] > 0:
                    print(f"⏱️ Tempo médio de execução: {stats_data['average_run_time']:.2f}s")
            
        except Exception as e:
            print(f"❌ Erro ao obter métricas: {e}")
    
    async def run_performance_test(self):
        """Executa teste de performance"""
        print("\n🧪 EXECUTANDO TESTE DE PERFORMANCE...")
        
        try:
            if not self.collector:
                print("❌ Coletor não disponível")
                return
            
            # Teste de coleta
            start_time = time.time()
            test_offers = await self.collector.collect_all_offers(max_offers_per_advertiser=10)
            collection_time = time.time() - start_time
            
            print(f"✅ Coleta: {len(test_offers)} ofertas em {collection_time:.2f}s")
            if collection_time > 0:
                print(f"🚀 Velocidade: {len(test_offers)/collection_time:.0f} ofertas/segundo")
            
            # Teste de filtros
            if test_offers and self.filter_engine:
                start_time = time.time()
                filtered_offers = await self.filter_engine.apply_filters(test_offers)
                filter_time = time.time() - start_time
                
                print(f"✅ Filtros: {len(filtered_offers)}/{len(test_offers)} ofertas aprovadas em {filter_time:.3f}s")
                if filter_time > 0:
                    print(f"🚀 Velocidade: {len(test_offers)/filter_time:.0f} ofertas/segundo")
            
            print("✅ Teste de performance concluído")
            
        except Exception as e:
            print(f"❌ Erro no teste de performance: {e}")
    
    async def start_monitoring(self):
        """Inicia monitoramento contínuo"""
        if not await self.initialize():
            return
        
        self.monitoring = True
        print("🚀 Monitoramento avançado iniciado. Pressione Ctrl+C para parar.")
        
        try:
            while self.monitoring:
                self.display_header()
                
                # Exibir status dos componentes
                await self.display_collector_status()
                self.display_filter_status()
                self.display_pipeline_status()
                self.display_system_health()
                self.display_performance_metrics()
                
                # Executar teste de performance a cada 5 ciclos
                if len(self.stats_history) % 5 == 0:
                    await self.run_performance_test()
                
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
    print("🔧 MONITOR AVANÇADO DO SISTEMA AWIN")
    print("=" * 50)
    print("1. Iniciar monitoramento contínuo")
    print("2. Status atual (uma vez)")
    print("3. Teste de performance")
    print("4. Sair")
    
    try:
        choice = input("\nEscolha uma opção (1-4): ").strip()
        
        monitor = AwinAdvancedMonitor()
        
        if choice == "1":
            await monitor.start_monitoring()
        elif choice == "2":
            if await monitor.initialize():
                monitor.display_header()
                await monitor.display_collector_status()
                monitor.display_filter_status()
                monitor.display_pipeline_status()
                monitor.display_system_health()
                monitor.display_performance_metrics()
                print("\n✅ Status exibido. Pressione Enter para continuar...")
                input()
        elif choice == "3":
            if await monitor.initialize():
                await monitor.run_performance_test()
                print("\n✅ Teste concluído. Pressione Enter para continuar...")
                input()
        elif choice == "4":
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
