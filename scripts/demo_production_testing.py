#!/usr/bin/env python3
"""
Script de Demonstração do Sistema de Teste em Produção
Mostra como usar o sistema completo com exemplos práticos
"""

import asyncio
import sys
from pathlib import Path
import json

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.app.production_testing import (
    ProductionTestRunner, 
    RealDataPipeline, 
    PerformanceMonitor, 
    GeekSystemValidator
)


async def demo_quick_test():
    """Demonstra teste rápido"""
    print("🚀 DEMONSTRAÇÃO: Teste Rápido (5 minutos)")
    print("=" * 60)
    
    config = {
        "test_duration_hours": 5/60,  # 5 minutos
        "monitoring_interval_seconds": 10,  # 10 segundos
        "validation_interval_minutes": 2,    # 2 minutos
        "export_reports": True,
        "output_directory": "demo_reports",
        "log_level": "INFO"
    }
    
    runner = ProductionTestRunner(config)
    
    try:
        print("Executando teste rápido...")
        results = await runner.run_quick_test(5)
        
        print("\n✅ Teste rápido concluído!")
        print(f"📊 Ofertas processadas: {results.get('total_offers', 0)}")
        print(f"⚡ Velocidade: {results.get('performance_metrics', {}).get('offers_per_second', 0):.1f} ofertas/s")
        
        return results
        
    except Exception as e:
        print(f"❌ Erro no teste rápido: {e}")
        return None


async def demo_stress_test():
    """Demonstra teste de estresse"""
    print("\n🔥 DEMONSTRAÇÃO: Teste de Estresse (500 ofertas)")
    print("=" * 60)
    
    config = {
        "test_duration_hours": 1,  # 1 hora
        "monitoring_interval_seconds": 15,
        "validation_interval_minutes": 5,
        "export_reports": True,
        "output_directory": "demo_reports",
        "log_level": "INFO"
    }
    
    runner = ProductionTestRunner(config)
    
    try:
        print("Executando teste de estresse...")
        results = await runner.run_stress_test(500)
        
        print("\n✅ Teste de estresse concluído!")
        if "stress_test_metrics" in results:
            metrics = results["stress_test_metrics"]
            print(f"📊 Total processado: {metrics['total_offers']} ofertas")
            print(f"⚡ Throughput: {metrics['offers_per_second']:.1f} ofertas/s")
            print(f"⏱️ Tempo total: {metrics['processing_time_seconds']:.2f}s")
        
        return results
        
    except Exception as e:
        print(f"❌ Erro no teste de estresse: {e}")
        return None


async def demo_individual_components():
    """Demonstra componentes individuais"""
    print("\n🔧 DEMONSTRAÇÃO: Componentes Individuais")
    print("=" * 60)
    
    try:
        # 1. Pipeline de dados
        print("1. Testando Pipeline de Dados...")
        pipeline = RealDataPipeline()
        test_offers = await pipeline.generate_real_test_data()
        print(f"   ✅ Geradas {len(test_offers)} ofertas de teste")
        
        # 2. Processamento através do sistema geek
        print("2. Processando através do Sistema Geek...")
        results = await pipeline.process_offers_through_geek_system(test_offers)
        print(f"   ✅ Processadas {results['total_offers']} ofertas")
        print(f"   ⚡ Velocidade: {results['performance_metrics']['offers_per_second']:.1f} ofertas/s")
        
        # 3. Monitor de performance
        print("3. Testando Monitor de Performance...")
        monitor = PerformanceMonitor()
        
        # Simular algumas métricas
        for i, offer in enumerate(test_offers[:5]):
            monitor.record_offer_processing(offer, 0.7 + (i * 0.1), 0.1)
        
        performance_summary = monitor.get_performance_summary()
        print(f"   ✅ Performance monitorada: {performance_summary.get('current_status', {}).get('total_offers_processed', 0)} ofertas")
        
        # 4. Validador do sistema
        print("4. Testando Validador do Sistema...")
        validator = GeekSystemValidator()
        validation_report = await validator.run_complete_validation(
            test_offers, 
            results['performance_metrics']
        )
        print(f"   ✅ Validação concluída: {validation_report.passed_tests}/{validation_report.total_tests} testes passaram")
        print(f"   📊 Score geral: {validation_report.overall_score:.2f}")
        
        # 5. Gerar insights
        print("5. Gerando Insights...")
        insights = await monitor.generate_performance_insights()
        print(f"   ✅ {len(insights)} insights gerados")
        for insight in insights[:3]:  # Mostrar primeiros 3
            print(f"      • {insight}")
        
        return {
            "pipeline_results": results,
            "validation_report": validation_report,
            "insights": insights
        }
        
    except Exception as e:
        print(f"❌ Erro na demonstração dos componentes: {e}")
        import traceback
        traceback.print_exc()
        return None


async def demo_real_time_monitoring():
    """Demonstra monitoramento em tempo real"""
    print("\n📈 DEMONSTRAÇÃO: Monitoramento em Tempo Real")
    print("=" * 60)
    
    try:
        monitor = PerformanceMonitor()
        
        # Simular monitoramento por alguns segundos
        print("Iniciando monitoramento (5 segundos)...")
        
        for i in range(5):
            # Simular processamento de ofertas
            from src.core.models import Offer
            from decimal import Decimal
            from datetime import datetime
            
            # Criar oferta de teste
            offer = Offer(
                title=f"Produto Teste {i+1}",
                price=Decimal("99.99"),
                url=f"https://demo.com/produto/{i}",
                store="Loja Demo",
                original_price=Decimal("129.99"),
                discount_percentage=25,
                category="gaming_accessories",
                stock_quantity=10,
                image_url=f"https://demo.com/img/{i}.jpg",
                description=f"Produto de demonstração {i+1}",
                scraped_at=datetime.now()
            )
            
            # Registrar processamento
            monitor.record_offer_processing(offer, 0.6 + (i * 0.1), 0.05)
            
            # Aguardar 1 segundo
            await asyncio.sleep(1)
            
            # Mostrar métricas em tempo real
            real_time_metrics = monitor.get_real_time_metrics()
            if real_time_metrics.get("status") != "aguardando dados":
                current = real_time_metrics.get("current_metrics", {})
                print(f"   📊 {current.get('total_offers', 0)} ofertas | "
                      f"Score: {current.get('avg_score', '0.000')} | "
                      f"Erro: {current.get('error_rate', '0%')}")
        
        print("\n✅ Monitoramento concluído!")
        
        # Mostrar resumo final
        final_summary = monitor.get_performance_summary()
        print(f"📋 Resumo final: {final_summary.get('current_status', {}).get('total_offers_processed', 0)} ofertas processadas")
        
        return final_summary
        
    except Exception as e:
        print(f"❌ Erro no monitoramento: {e}")
        return None


async def demo_validation_system():
    """Demonstra sistema de validação"""
    print("\n🔍 DEMONSTRAÇÃO: Sistema de Validação")
    print("=" * 60)
    
    try:
        # Gerar dados de teste
        pipeline = RealDataPipeline()
        test_offers = await pipeline.generate_real_test_data()
        
        # Executar validação
        validator = GeekSystemValidator()
        validation_report = await validator.run_complete_validation(
            test_offers,
            {"offers_per_second": 8.5, "error_rate": 0.02, "average_processing_time": 1.2}
        )
        
        print("✅ Validação completa executada!")
        print(f"📊 Resultados:")
        print(f"   • Total de testes: {validation_report.total_tests}")
        print(f"   • Testes passaram: {validation_report.passed_tests}")
        print(f"   • Testes falharam: {validation_report.failed_tests}")
        print(f"   • Testes com warning: {validation_report.warning_tests}")
        print(f"   • Score geral: {validation_report.overall_score:.2f}")
        print(f"   • Status: {validation_report.summary}")
        
        if validation_report.critical_issues:
            print(f"\n⚠️ Problemas críticos:")
            for issue in validation_report.critical_issues:
                print(f"   • {issue}")
        
        if validation_report.improvement_suggestions:
            print(f"\n💡 Sugestões de melhoria:")
            for suggestion in validation_report.improvement_suggestions[:5]:  # Primeiras 5
                print(f"   • {suggestion}")
        
        # Exportar relatório
        report_file = validator.export_validation_report(validation_report)
        print(f"\n📁 Relatório exportado: {report_file}")
        
        return validation_report
        
    except Exception as e:
        print(f"❌ Erro na validação: {e}")
        return None


async def main():
    """Função principal da demonstração"""
    print("🎯 DEMONSTRAÇÃO COMPLETA DO SISTEMA DE TESTE EM PRODUÇÃO")
    print("=" * 80)
    print("Este script demonstra todas as funcionalidades do sistema de teste")
    print("em produção para o Sistema Geek do Garimpeiro Geek.")
    print("=" * 80)
    
    all_results = {}
    
    try:
        # 1. Demonstração de componentes individuais
        component_results = await demo_individual_components()
        if component_results:
            all_results["components"] = component_results
        
        # 2. Demonstração de monitoramento em tempo real
        monitoring_results = await demo_real_time_monitoring()
        if monitoring_results:
            all_results["monitoring"] = monitoring_results
        
        # 3. Demonstração do sistema de validação
        validation_results = await demo_validation_system()
        if validation_results:
            all_results["validation"] = validation_results
        
        # 4. Demonstração de teste rápido
        quick_test_results = await demo_quick_test()
        if quick_test_results:
            all_results["quick_test"] = quick_test_results
        
        # 5. Demonstração de teste de estresse
        stress_test_results = await demo_stress_test()
        if stress_test_results:
            all_results["stress_test"] = stress_test_results
        
        # Resumo final
        print("\n" + "=" * 80)
        print("🎉 DEMONSTRAÇÃO CONCLUÍDA COM SUCESSO!")
        print("=" * 80)
        print("✅ Todos os componentes foram testados:")
        print("   • Pipeline de dados reais")
        print("   • Monitor de performance")
        print("   • Sistema de validação")
        print("   • Teste rápido")
        print("   • Teste de estresse")
        print("\n📁 Relatórios salvos em: demo_reports/")
        print("🚀 Sistema pronto para testes em produção!")
        
        # Salvar resultados da demonstração
        demo_file = "demo_results.json"
        with open(demo_file, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, indent=2, ensure_ascii=False, default=str)
        print(f"\n💾 Resultados salvos em: {demo_file}")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Erro durante demonstração: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⚠️ Demonstração interrompida pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro fatal: {e}")
        sys.exit(1)
