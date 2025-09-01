#!/usr/bin/env python3
"""
Script Principal para Executar Testes em Produção do Sistema Geek
Permite executar testes completos, rápidos ou de estresse com dados reais
"""

import asyncio
import argparse
import sys
import os
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.app.production_testing import ProductionTestRunner


async def main():
    """Função principal"""
    parser = argparse.ArgumentParser(
        description="Sistema de Teste em Produção - Garimpeiro Geek",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:

  # Teste rápido de 30 minutos
  python run_production_tests.py --quick --duration 30

  # Teste completo de 24 horas
  python run_production_tests.py --full

  # Teste de estresse com 2000 ofertas
  python run_production_tests.py --stress --offers 2000

  # Teste customizado
  python run_production_tests.py --custom --duration 12 --monitoring-interval 60
        """
    )
    
    # Modos de teste
    test_group = parser.add_mutually_exclusive_group(required=True)
    test_group.add_argument(
        "--quick", 
        action="store_true",
        help="Executa teste rápido (padrão: 30 minutos)"
    )
    test_group.add_argument(
        "--full", 
        action="store_true",
        help="Executa teste completo de produção (24 horas)"
    )
    test_group.add_argument(
        "--stress", 
        action="store_true",
        help="Executa teste de estresse com grande volume de dados"
    )
    test_group.add_argument(
        "--custom", 
        action="store_true",
        help="Executa teste com configurações customizadas"
    )
    
    # Parâmetros gerais
    parser.add_argument(
        "--duration", 
        type=int, 
        default=30,
        help="Duração do teste em minutos (padrão: 30)"
    )
    parser.add_argument(
        "--offers", 
        type=int, 
        default=1000,
        help="Número de ofertas para teste de estresse (padrão: 1000)"
    )
    parser.add_argument(
        "--monitoring-interval", 
        type=int, 
        default=30,
        help="Intervalo de monitoramento em segundos (padrão: 30)"
    )
    parser.add_argument(
        "--validation-interval", 
        type=int, 
        default=60,
        help="Intervalo de validação em minutos (padrão: 60)"
    )
    parser.add_argument(
        "--output-dir", 
        type=str, 
        default="production_test_reports",
        help="Diretório de saída para relatórios (padrão: production_test_reports)"
    )
    parser.add_argument(
        "--log-level", 
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Nível de logging (padrão: INFO)"
    )
    parser.add_argument(
        "--no-reports", 
        action="store_true",
        help="Não exportar relatórios"
    )
    parser.add_argument(
        "--no-monitoring", 
        action="store_true",
        help="Desabilitar monitoramento de performance"
    )
    parser.add_argument(
        "--no-validation", 
        action="store_true",
        help="Desabilitar validações do sistema"
    )
    
    args = parser.parse_args()
    
    # Configuração baseada nos argumentos
    config = {
        "test_duration_hours": args.duration / 60,
        "monitoring_interval_seconds": args.monitoring_interval,
        "validation_interval_minutes": args.validation_interval,
        "export_reports": not args.no_reports,
        "output_directory": args.output_dir,
        "log_level": args.log_level,
        "enable_real_time_monitoring": not args.no_monitoring,
        "enable_validation": not args.no_validation,
        "enable_performance_tracking": not args.no_monitoring
    }
    
    print("🚀 SISTEMA DE TESTE EM PRODUÇÃO - GARIMPEIRO GEEK")
    print("=" * 80)
    print(f"📋 Configuração:")
    print(f"   • Duração: {config['test_duration_hours']:.1f} horas")
    print(f"   • Monitoramento: {'✅' if config['enable_real_time_monitoring'] else '❌'}")
    print(f"   • Validação: {'✅' if config['enable_validation'] else '❌'}")
    print(f"   • Relatórios: {'✅' if config['export_reports'] else '❌'}")
    print(f"   • Log level: {config['log_level']}")
    print(f"   • Diretório de saída: {config['output_directory']}")
    print("=" * 80)
    
    try:
        # Criar runner
        runner = ProductionTestRunner(config)
        
        # Executar teste baseado no modo
        if args.quick:
            print(f"⚡ Executando teste rápido de {args.duration} minutos...")
            results = await runner.run_quick_test(args.duration)
            
        elif args.full:
            print("🌙 Executando teste completo de produção...")
            results = await runner.run_complete_production_test()
            
        elif args.stress:
            print(f"🔥 Executando teste de estresse com {args.offers} ofertas...")
            results = await runner.run_stress_test(args.offers)
            
        elif args.custom:
            print("⚙️ Executando teste customizado...")
            results = await runner.run_complete_production_test()
        
        # Salvar resultados
        runner.test_results = results
        
        # Gerar e exibir resumo
        print("\n" + "=" * 80)
        print("📊 RESULTADOS DOS TESTES")
        print("=" * 80)
        
        summary = await runner.generate_test_summary()
        print(summary)
        
        # Informações adicionais
        if args.stress and "stress_test_metrics" in results:
            stress_metrics = results["stress_test_metrics"]
            print(f"\n🔥 MÉTRICAS DE ESTRESSE:")
            print(f"   • Total processado: {stress_metrics['total_offers']} ofertas")
            print(f"   • Tempo total: {stress_metrics['processing_time_seconds']:.2f}s")
            print(f"   • Throughput: {stress_metrics['offers_per_second']:.1f} ofertas/s")
            print(f"   • Uso de memória: {stress_metrics['memory_usage_mb']:.1f}MB")
            print(f"   • Uso de CPU: {stress_metrics['cpu_usage_percent']:.1f}%")
        
        # Status final
        print(f"\n✅ Teste concluído com sucesso!")
        if config["export_reports"]:
            print(f"📁 Relatórios salvos em: {config['output_directory']}")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n⚠️ Teste interrompido pelo usuário")
        return 1
        
    except Exception as e:
        print(f"\n❌ Erro durante execução: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⚠️ Programa interrompido pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro fatal: {e}")
        sys.exit(1)
