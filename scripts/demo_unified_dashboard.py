#!/usr/bin/env python3
"""
Demonstração do Sistema Unificado de Dashboard
Integra todos os sistemas implementados em uma interface única
"""

import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime
import json

# Adicionar o diretório raiz ao Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.app.unified_dashboard import UnifiedDashboard, unified_dashboard


class UnifiedDashboardDemo:
    """Demonstração do sistema unificado"""
    
    def __init__(self):
        self.dashboard = unified_dashboard
        self.results = {}
    
    async def run_demo(self):
        """Executa demonstração completa"""
        print("🚀 Iniciando Demonstração do Sistema Unificado")
        print("=" * 60)
        
        # 1. Verificar status inicial dos sistemas
        await self.check_initial_status()
        
        # 2. Executar verificação completa do sistema
        await self.run_full_system_check()
        
        # 3. Demonstrar funcionalidades individuais
        await self.demonstrate_individual_features()
        
        # 4. Gerar relatório final
        await self.generate_final_report()
        
        print("\n✅ Demonstração concluída com sucesso!")
    
    async def check_initial_status(self):
        """Verifica status inicial dos sistemas"""
        print("\n📊 Verificando Status Inicial dos Sistemas")
        print("-" * 40)
        
        status = await self.dashboard.get_system_status()
        
        for system_name, system_status in status.items():
            status_icon = {
                "active": "🟢",
                "inactive": "⚪",
                "error": "🔴",
                "running": "🟡"
            }.get(system_status.status, "❓")
            
            print(f"{status_icon} {system_name}: {system_status.status}")
            if system_status.error_message:
                print(f"   Erro: {system_status.error_message}")
        
        metrics = await self.dashboard.get_consolidated_metrics()
        print(f"\n📈 Métricas Consolidadas:")
        print(f"   Saúde do Sistema: {metrics.system_health}")
        print(f"   Ofertas Processadas: {metrics.total_offers_processed}")
        print(f"   Taxa Conversão Geek: {metrics.conversion_rate_geek:.2%}")
        print(f"   Taxa Conversão Geral: {metrics.conversion_rate_general:.2%}")
        print(f"   Score de Feedback: {metrics.feedback_score:.2f}")
        print(f"   Categorias Expandidas: {metrics.categories_expanded}")
        print(f"   Precisão IA: {metrics.ai_model_accuracy:.3f}")
    
    async def run_full_system_check(self):
        """Executa verificação completa do sistema"""
        print("\n🔍 Executando Verificação Completa do Sistema")
        print("-" * 40)
        
        print("🔄 Iniciando verificação de todos os sistemas...")
        results = await self.dashboard.run_full_system_check()
        
        for check_name, result in results.items():
            if check_name == "health_report":
                continue
                
            status_icon = "✅" if result.get("success", False) else "❌"
            print(f"{status_icon} {check_name}: {result.get('message', 'Verificado')}")
            
            if not result.get("success", False):
                print(f"   Erro: {result.get('error', 'Erro desconhecido')}")
        
        # Relatório de saúde
        health_report = results.get("health_report", {})
        print(f"\n🏥 Relatório de Saúde do Sistema:")
        print(f"   Saúde Geral: {health_report.get('overall_health', 'unknown')}")
        print(f"   Sistemas Ativos: {health_report.get('active_systems', 0)}/{health_report.get('total_systems', 0)}")
    
    async def demonstrate_individual_features(self):
        """Demonstra funcionalidades individuais"""
        print("\n🎯 Demonstrando Funcionalidades Individuais")
        print("-" * 40)
        
        # 1. Teste de Produção
        print("\n🧪 Teste de Produção:")
        result = await self.dashboard.run_production_test(quick=True)
        if result["success"]:
            print("   ✅ Teste executado com sucesso")
            if "result" in result and hasattr(result["result"], "summary"):
                print(f"   📋 Resumo: {result['result'].summary}")
        else:
            print(f"   ❌ Erro: {result['error']}")
        
        # 2. Tracking de Conversões
        print("\n📊 Tracking de Conversões:")
        result = await self.dashboard.start_conversion_tracking()
        if result["success"]:
            print("   ✅ Tracking iniciado com sucesso")
        else:
            print(f"   ❌ Erro: {result['error']}")
        
        # 3. Coleta de Feedback
        print("\n💬 Coleta de Feedback:")
        result = await self.dashboard.collect_user_feedback()
        if result["success"]:
            stats = result["stats"]
            print(f"   ✅ Feedback coletado: {stats.total_feedback} respostas")
            print(f"   📈 Taxa Positiva: {stats.positive_rate:.1%}")
        else:
            print(f"   ❌ Erro: {result['error']}")
        
        # 4. Expansão de Categorias
        print("\n📂 Expansão de Categorias:")
        result = await self.dashboard.expand_categories()
        if result["success"]:
            expand_result = result["result"]
            print(f"   ✅ Categorias expandidas: {expand_result.expanded_count}")
            print(f"   🆕 Novas categorias: {len(expand_result.new_categories)}")
        else:
            print(f"   ❌ Erro: {result['error']}")
        
        # 5. Treinamento de IA
        print("\n🤖 Treinamento de Modelos de IA:")
        result = await self.dashboard.train_ai_models()
        if result["success"]:
            train_result = result["result"]
            print(f"   ✅ Modelos treinados: {len(train_result.training_results)}")
            print(f"   🏆 Melhor modelo: {train_result.best_model}")
            print(f"   📊 Precisão: {train_result.best_metrics.r2_score:.3f}")
        else:
            print(f"   ❌ Erro: {result['error']}")
        
        # 6. Otimização de Ofertas
        print("\n🎯 Otimização de Ofertas:")
        result = await self.dashboard.optimize_offers()
        if result["success"]:
            opt_result = result["result"]
            print(f"   ✅ Ofertas otimizadas: {opt_result.optimized_count}")
            print(f"   📈 Melhoria média: {opt_result.average_improvement:.2f}")
        else:
            print(f"   ❌ Erro: {result['error']}")
    
    async def generate_final_report(self):
        """Gera relatório final"""
        print("\n📋 Gerando Relatório Final")
        print("-" * 40)
        
        # Status final dos sistemas
        status = await self.dashboard.get_system_status()
        metrics = await self.dashboard.get_consolidated_metrics()
        
        print("📊 Status Final dos Sistemas:")
        active_count = sum(1 for s in status.values() if s.status == "active")
        error_count = sum(1 for s in status.values() if s.status == "error")
        
        print(f"   🟢 Sistemas Ativos: {active_count}")
        print(f"   🔴 Sistemas com Erro: {error_count}")
        print(f"   📈 Total de Sistemas: {len(status)}")
        
        print(f"\n🎯 Métricas Finais:")
        print(f"   🏥 Saúde do Sistema: {metrics.system_health}")
        print(f"   📦 Ofertas Processadas: {metrics.total_offers_processed:,}")
        print(f"   🎮 Conversão Geek: {metrics.conversion_rate_geek:.2%}")
        print(f"   🌐 Conversão Geral: {metrics.conversion_rate_general:.2%}")
        print(f"   💬 Score Feedback: {metrics.feedback_score:.2f}/5.0")
        print(f"   📂 Categorias: {metrics.categories_expanded}")
        print(f"   🤖 Precisão IA: {metrics.ai_model_accuracy:.3f}")
        
        # Salvar relatório
        report = {
            "timestamp": datetime.now().isoformat(),
            "system_status": {name: {
                "status": s.status,
                "last_run": s.last_run.isoformat() if s.last_run else None,
                "error_message": s.error_message
            } for name, s in status.items()},
            "metrics": {
                "total_offers_processed": metrics.total_offers_processed,
                "conversion_rate_geek": metrics.conversion_rate_geek,
                "conversion_rate_general": metrics.conversion_rate_general,
                "feedback_score": metrics.feedback_score,
                "categories_expanded": metrics.categories_expanded,
                "ai_model_accuracy": metrics.ai_model_accuracy,
                "system_health": metrics.system_health
            },
            "summary": {
                "active_systems": active_count,
                "error_systems": error_count,
                "total_systems": len(status),
                "overall_health": metrics.system_health
            }
        }
        
        # Salvar em arquivo
        report_file = f"unified_dashboard_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Relatório salvo em: {report_file}")
    
    async def quick_test(self):
        """Executa teste rápido"""
        print("⚡ Teste Rápido do Sistema Unificado")
        print("=" * 40)
        
        # Verificar status
        status = await self.dashboard.get_system_status()
        active_systems = sum(1 for s in status.values() if s.status == "active")
        
        print(f"📊 Sistemas Ativos: {active_systems}/{len(status)}")
        
        # Métricas básicas
        metrics = await self.dashboard.get_consolidated_metrics()
        print(f"🏥 Saúde do Sistema: {metrics.system_health}")
        print(f"📈 Conversão Geek: {metrics.conversion_rate_geek:.2%}")
        print(f"🤖 Precisão IA: {metrics.ai_model_accuracy:.3f}")
        
        print("\n✅ Teste rápido concluído!")


async def main():
    """Função principal"""
    if len(sys.argv) > 1 and sys.argv[1] == "quick":
        demo = UnifiedDashboardDemo()
        await demo.quick_test()
    else:
        demo = UnifiedDashboardDemo()
        await demo.run_demo()


if __name__ == "__main__":
    asyncio.run(main())
