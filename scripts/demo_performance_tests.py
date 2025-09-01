#!/usr/bin/env python3
"""
Demonstração do Sistema de Testes de Performance
Sistema de Recomendações de Ofertas - Garimpeiro Geek
"""

import asyncio
import time
import json
from datetime import datetime
from pathlib import Path

# Importar componentes do sistema de performance
from src.tests.performance import (
    StressTester, PerformanceMonitor, ConcurrencyTester, MemoryProfiler,
    NetworkSimulator, LoadGenerator, BenchmarkRunner
)
from src.tests.performance.models import (
    StressTestConfig, LoadTestConfig, ConcurrencyTestConfig, 
    MemoryTestConfig, NetworkTestConfig, BenchmarkConfig
)


class PerformanceTestDemo:
    """Demonstração do sistema de testes de performance"""
    
    def __init__(self):
        self.stress_tester = StressTester()
        self.performance_monitor = PerformanceMonitor()
        self.concurrency_tester = ConcurrencyTester()
        self.memory_profiler = MemoryProfiler()
        self.network_simulator = NetworkSimulator()
        self.load_generator = LoadGenerator()
        self.benchmark_runner = BenchmarkRunner()
        
        # Resultados dos testes
        self.test_results = []
    
    async def run_full_demo(self) -> None:
        """Executa demonstração completa do sistema"""
        print("🚀 SISTEMA DE TESTES DE PERFORMANCE - GARIMPEIRO GEEK")
        print("=" * 60)
        print(f"📅 Início: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        try:
            # 1. Teste de Stress
            await self._demo_stress_test()
            
            # 2. Teste de Carga
            await self._demo_load_test()
            
            # 3. Teste de Concorrência
            await self._demo_concurrency_test()
            
            # 4. Teste de Memória
            await self._demo_memory_test()
            
            # 5. Teste de Rede
            await self._demo_network_test()
            
            # 6. Benchmark
            await self._demo_benchmark()
            
            # 7. Gerar relatório final
            await self._generate_final_report()
            
        except Exception as e:
            print(f"❌ Erro na demonstração: {e}")
            raise
    
    async def run_quick_demo(self) -> None:
        """Executa demonstração rápida"""
        print("⚡ DEMONSTRAÇÃO RÁPIDA - SISTEMA DE TESTES DE PERFORMANCE")
        print("=" * 60)
        print(f"📅 Início: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        try:
            # Configurações rápidas
            quick_configs = {
                "stress": StressTestConfig(
                    test_name="Stress Test Rápido",
                    duration_seconds=5,
                    concurrent_users=3,
                    ramp_up_seconds=1,
                    ramp_down_seconds=1
                ),
                "load": LoadTestConfig(
                    test_name="Load Test Rápido",
                    initial_users=1,
                    max_users=3,
                    step_users=1,
                    step_duration_seconds=2,
                    hold_duration_seconds=1
                ),
                "concurrency": ConcurrencyTestConfig(
                    test_name="Concurrency Test Rápido",
                    concurrent_tasks=3,
                    task_duration_seconds=3
                ),
                "memory": MemoryTestConfig(
                    test_name="Memory Test Rápido",
                    duration_seconds=5,
                    check_interval_seconds=1
                ),
                "network": NetworkTestConfig(
                    test_name="Network Test Rápido",
                    duration_seconds=5,
                    latency_ms=50,
                    packet_loss_percent=0.5
                ),
                "benchmark": BenchmarkConfig(
                    test_name="Benchmark Rápido",
                    iterations=50,
                    warmup_iterations=5
                )
            }
            
            # Executar testes rápidos
            print("🧪 Executando testes rápidos...")
            
            # Stress test
            print("  📊 Teste de Stress...")
            result = self.stress_tester.run_stress_test(quick_configs["stress"])
            self.test_results.append(result)
            print(f"    ✅ Concluído: {result.metrics.throughput_rps:.2f} RPS")
            
            # Load test
            print("  📈 Teste de Carga...")
            result = self.load_generator.run_load_test(quick_configs["load"])
            self.test_results.append(result)
            if result.metrics:
                print(f"    ✅ Concluído: {result.metrics.throughput_rps:.2f} RPS")
            else:
                print(f"    ❌ Falhou: {result.errors}")
            
            # Concurrency test
            print("  🔄 Teste de Concorrência...")
            result = self.concurrency_tester.run_concurrency_test(quick_configs["concurrency"])
            self.test_results.append(result)
            if result.metrics:
                print(f"    ✅ Concluído: {result.metrics.throughput_rps:.2f} RPS")
            else:
                print(f"    ❌ Falhou: {result.errors}")
            
            # Memory test
            print("  💾 Teste de Memória...")
            result = self.memory_profiler.run_memory_test(quick_configs["memory"])
            self.test_results.append(result)
            if result.metrics:
                print(f"    ✅ Concluído: {result.metrics.memory_usage_mb:.2f} MB")
            else:
                print(f"    ❌ Falhou: {result.errors}")
            
            # Network test
            print("  🌐 Teste de Rede...")
            result = self.network_simulator.run_network_test(quick_configs["network"])
            self.test_results.append(result)
            if result.metrics:
                print(f"    ✅ Concluído: {result.metrics.avg_response_time_ms:.2f} ms")
            else:
                print(f"    ❌ Falhou: {result.errors}")
            
            # Benchmark
            print("  ⚡ Benchmark...")
            result = self.benchmark_runner.run_benchmark(quick_configs["benchmark"])
            self.test_results.append(result)
            if result.metrics:
                print(f"    ✅ Concluído: {result.metrics.duration_ms:.2f} ms")
            else:
                print(f"    ❌ Falhou: {result.errors}")
            
            # Relatório rápido
            await self._generate_quick_report()
            
        except Exception as e:
            print(f"❌ Erro na demonstração rápida: {e}")
            raise
    
    async def _demo_stress_test(self) -> None:
        """Demonstração do teste de stress"""
        print("🧪 TESTE DE STRESS")
        print("-" * 30)
        
        config = StressTestConfig(
            test_name="Stress Test Completo",
            duration_seconds=60,
            concurrent_users=20,
            ramp_up_seconds=10,
            ramp_down_seconds=10,
            target_rps=50.0,
            max_response_time_ms=3000,
            error_threshold_percent=5.0
        )
        
        print(f"📋 Configuração:")
        print(f"   • Duração: {config.duration_seconds}s")
        print(f"   • Usuários concorrentes: {config.concurrent_users}")
        print(f"   • Target RPS: {config.target_rps}")
        print(f"   • Max response time: {config.max_response_time_ms}ms")
        print()
        
        print("🚀 Executando teste de stress...")
        result = self.stress_tester.run_stress_test(config)
        self.test_results.append(result)
        
        if result.status.value == "completed":
            print("✅ Teste de stress concluído com sucesso!")
            print(f"   📊 Throughput: {result.metrics.throughput_rps:.2f} RPS")
            print(f"   ⏱️  Tempo médio: {result.metrics.avg_response_time_ms:.2f} ms")
            print(f"   ❌ Taxa de erro: {result.metrics.error_rate_percent:.2f}%")
            print(f"   💾 Memória: {result.metrics.memory_usage_mb:.2f} MB")
            print(f"   🔥 CPU: {result.metrics.cpu_usage_percent:.2f}%")
        else:
            print(f"❌ Teste de stress falhou: {result.errors}")
        
        print()
    
    async def _demo_load_test(self) -> None:
        """Demonstração do teste de carga"""
        print("📈 TESTE DE CARGA")
        print("-" * 30)
        
        config = LoadTestConfig(
            test_name="Load Test Completo",
            initial_users=1,
            max_users=50,
            step_users=5,
            step_duration_seconds=30,
            hold_duration_seconds=60,
            target_rps=100.0,
            max_response_time_ms=2000,
            error_threshold_percent=2.0
        )
        
        print(f"📋 Configuração:")
        print(f"   • Usuários iniciais: {config.initial_users}")
        print(f"   • Usuários máximos: {config.max_users}")
        print(f"   • Incremento: {config.step_users} usuários")
        print(f"   • Duração por passo: {config.step_duration_seconds}s")
        print(f"   • Duração de sustentação: {config.hold_duration_seconds}s")
        print()
        
        print("🚀 Executando teste de carga...")
        result = self.load_generator.run_load_test(config)
        self.test_results.append(result)
        
        if result.status.value == "completed":
            print("✅ Teste de carga concluído com sucesso!")
            print(f"   📊 Throughput: {result.metrics.throughput_rps:.2f} RPS")
            print(f"   ⏱️  Tempo médio: {result.metrics.avg_response_time_ms:.2f} ms")
            print(f"   ❌ Taxa de erro: {result.metrics.error_rate_percent:.2f}%")
            print(f"   💾 Memória: {result.metrics.memory_usage_mb:.2f} MB")
            print(f"   🔥 CPU: {result.metrics.cpu_usage_percent:.2f}%")
        else:
            print(f"❌ Teste de carga falhou: {result.errors}")
        
        print()
    
    async def _demo_concurrency_test(self) -> None:
        """Demonstração do teste de concorrência"""
        print("🔄 TESTE DE CONCORRÊNCIA")
        print("-" * 30)
        
        config = ConcurrencyTestConfig(
            test_name="Concurrency Test Completo",
            concurrent_tasks=30,
            task_duration_seconds=45,
            max_concurrent_tasks=100,
            task_types=["scraping", "processing", "posting", "validation"],
            timeout_seconds=30
        )
        
        print(f"📋 Configuração:")
        print(f"   • Tarefas concorrentes: {config.concurrent_tasks}")
        print(f"   • Duração: {config.task_duration_seconds}s")
        print(f"   • Tipos de tarefa: {', '.join(config.task_types)}")
        print(f"   • Timeout: {config.timeout_seconds}s")
        print()
        
        print("🚀 Executando teste de concorrência...")
        result = self.concurrency_tester.run_concurrency_test(config)
        self.test_results.append(result)
        
        if result.status.value == "completed":
            print("✅ Teste de concorrência concluído com sucesso!")
            print(f"   📊 Throughput: {result.metrics.throughput_rps:.2f} RPS")
            print(f"   ⏱️  Tempo médio: {result.metrics.avg_response_time_ms:.2f} ms")
            print(f"   ❌ Taxa de erro: {result.metrics.error_rate_percent:.2f}%")
            print(f"   💾 Memória: {result.metrics.memory_usage_mb:.2f} MB")
            print(f"   🔥 CPU: {result.metrics.cpu_usage_percent:.2f}%")
        else:
            print(f"❌ Teste de concorrência falhou: {result.errors}")
        
        print()
    
    async def _demo_memory_test(self) -> None:
        """Demonstração do teste de memória"""
        print("💾 TESTE DE MEMÓRIA")
        print("-" * 30)
        
        config = MemoryTestConfig(
            test_name="Memory Test Completo",
            duration_seconds=120,
            check_interval_seconds=5,
            memory_threshold_mb=500.0,
            gc_enabled=True,
            memory_profiling=True,
            leak_detection=True
        )
        
        print(f"📋 Configuração:")
        print(f"   • Duração: {config.duration_seconds}s")
        print(f"   • Intervalo de verificação: {config.check_interval_seconds}s")
        print(f"   • Threshold de memória: {config.memory_threshold_mb} MB")
        print(f"   • Profiling de memória: {'Sim' if config.memory_profiling else 'Não'}")
        print(f"   • Detecção de vazamentos: {'Sim' if config.leak_detection else 'Não'}")
        print()
        
        print("🚀 Executando teste de memória...")
        result = self.memory_profiler.run_memory_test(config)
        self.test_results.append(result)
        
        if result.status.value == "completed":
            print("✅ Teste de memória concluído com sucesso!")
            print(f"   💾 Memória final: {result.metrics.memory_usage_mb:.2f} MB")
            print(f"   🔥 CPU: {result.metrics.cpu_usage_percent:.2f}%")
            
            # Estatísticas de memória
            memory_stats = self.memory_profiler.get_memory_statistics()
            print(f"   📊 Snapshots coletados: {memory_stats['snapshots_count']}")
            print(f"   📈 Memória média: {memory_stats['avg_memory_used_mb']:.2f} MB")
            print(f"   📉 Memória mínima: {memory_stats['min_memory_used_mb']:.2f} MB")
            print(f"   📈 Memória máxima: {memory_stats['max_memory_used_mb']:.2f} MB")
            
            # Vazamentos detectados
            leaks = memory_stats['memory_leaks']
            if leaks:
                print(f"   ⚠️  Vazamentos detectados: {len(leaks)}")
                for leak in leaks[:3]:  # Mostrar apenas os 3 primeiros
                    print(f"      • {leak['severity']}: {leak['increase_rate_mb_per_min']:.2f} MB/min")
            else:
                print("   ✅ Nenhum vazamento detectado")
        else:
            print(f"❌ Teste de memória falhou: {result.errors}")
        
        print()
    
    async def _demo_network_test(self) -> None:
        """Demonstração do teste de rede"""
        print("🌐 TESTE DE REDE")
        print("-" * 30)
        
        config = NetworkTestConfig(
            test_name="Network Test Completo",
            duration_seconds=90,
            latency_ms=150,
            jitter_ms=75,
            packet_loss_percent=2.0,
            bandwidth_mbps=10.0,
            connection_drops=True,
            drop_interval_seconds=45
        )
        
        print(f"📋 Configuração:")
        print(f"   • Duração: {config.duration_seconds}s")
        print(f"   • Latência: {config.latency_ms}ms")
        print(f"   • Jitter: {config.jitter_ms}ms")
        print(f"   • Perda de pacotes: {config.packet_loss_percent}%")
        print(f"   • Largura de banda: {config.bandwidth_mbps} Mbps")
        print(f"   • Quedas de conexão: {'Sim' if config.connection_drops else 'Não'}")
        print()
        
        print("🚀 Executando teste de rede...")
        result = self.network_simulator.run_network_test(config)
        self.test_results.append(result)
        
        if result.status.value == "completed":
            print("✅ Teste de rede concluído com sucesso!")
            print(f"   📊 Throughput: {result.metrics.throughput_rps:.2f} RPS")
            print(f"   ⏱️  Tempo médio: {result.metrics.avg_response_time_ms:.2f} ms")
            print(f"   ❌ Taxa de erro: {result.metrics.error_rate_percent:.2f}%")
            print(f"   💾 Memória: {result.metrics.memory_usage_mb:.2f} MB")
            print(f"   🔥 CPU: {result.metrics.cpu_usage_percent:.2f}%")
            
            # Estatísticas de rede
            network_stats = self.network_simulator.get_network_statistics()
            print(f"   📦 Pacotes enviados: {network_stats['packets_sent']}")
            print(f"   📦 Pacotes recebidos: {network_stats['packets_received']}")
            print(f"   📦 Pacotes perdidos: {network_stats['packets_dropped']}")
            print(f"   📊 Taxa de perda: {network_stats['packet_loss_rate']:.2f}%")
            print(f"   🔌 Conexões perdidas: {network_stats['connections_dropped']}")
        else:
            print(f"❌ Teste de rede falhou: {result.errors}")
        
        print()
    
    async def _demo_benchmark(self) -> None:
        """Demonstração do benchmark"""
        print("⚡ BENCHMARK")
        print("-" * 30)
        
        config = BenchmarkConfig(
            test_name="Benchmark Completo",
            iterations=500,
            warmup_iterations=50,
            timeout_seconds=300,
            memory_profiling=True,
            cpu_profiling=True,
            detailed_reporting=True
        )
        
        print(f"📋 Configuração:")
        print(f"   • Iterações: {config.iterations}")
        print(f"   • Warmup: {config.warmup_iterations}")
        print(f"   • Timeout: {config.timeout_seconds}s")
        print(f"   • Profiling de memória: {'Sim' if config.memory_profiling else 'Não'}")
        print(f"   • Profiling de CPU: {'Sim' if config.cpu_profiling else 'Não'}")
        print()
        
        # Executar benchmark específico
        benchmark_name = "scraping_benchmark"
        print(f"🚀 Executando benchmark: {benchmark_name}")
        result = self.benchmark_runner.run_benchmark(config, benchmark_name)
        self.test_results.append(result)
        
        if result.status.value == "completed":
            print("✅ Benchmark concluído com sucesso!")
            print(f"   ⏱️  Duração total: {result.metrics.duration_ms:.2f} ms")
            print(f"   💾 Memória: {result.metrics.memory_usage_mb:.2f} MB")
            print(f"   🔥 CPU: {result.metrics.cpu_usage_percent:.2f}%")
            
            # Detalhes do benchmark
            test_config = result.metrics.test_config
            print(f"   📊 Iterações completadas: {test_config.get('iterations_completed', 0)}")
            print(f"   ⏱️  Tempo médio de execução: {test_config.get('avg_execution_time_ms', 0):.4f} ms")
            print(f"   📈 Tempo máximo: {test_config.get('max_execution_time_ms', 0):.4f} ms")
            print(f"   📉 Tempo mínimo: {test_config.get('min_execution_time_ms', 0):.4f} ms")
            print(f"   📊 P95: {test_config.get('p95_execution_time_ms', 0):.4f} ms")
            print(f"   📊 P99: {test_config.get('p99_execution_time_ms', 0):.4f} ms")
            
            # Informações de memória
            memory_before = test_config.get('memory_before_mb', 0)
            memory_after = test_config.get('memory_after_mb', 0)
            memory_increase = test_config.get('memory_increase_mb', 0)
            print(f"   💾 Memória antes: {memory_before:.2f} MB")
            print(f"   💾 Memória depois: {memory_after:.2f} MB")
            print(f"   📈 Aumento de memória: {memory_increase:.2f} MB")
        else:
            print(f"❌ Benchmark falhou: {result.errors}")
        
        print()
    
    async def _generate_final_report(self) -> None:
        """Gera relatório final da demonstração"""
        print("📊 RELATÓRIO FINAL")
        print("=" * 60)
        
        # Estatísticas gerais
        total_tests = len(self.test_results)
        successful_tests = len([r for r in self.test_results if r.status.value == "completed"])
        failed_tests = total_tests - successful_tests
        
        print(f"📈 RESUMO GERAL:")
        print(f"   • Total de testes: {total_tests}")
        print(f"   • Testes bem-sucedidos: {successful_tests}")
        print(f"   • Testes falharam: {failed_tests}")
        print(f"   • Taxa de sucesso: {(successful_tests/total_tests*100):.1f}%")
        print()
        
        # Estatísticas por tipo de teste
        test_types = {}
        for result in self.test_results:
            test_type = result.test_type.value
            if test_type not in test_types:
                test_types[test_type] = {"total": 0, "successful": 0}
            test_types[test_type]["total"] += 1
            if result.status.value == "completed":
                test_types[test_type]["successful"] += 1
        
        print("📊 ESTATÍSTICAS POR TIPO:")
        for test_type, stats in test_types.items():
            success_rate = (stats["successful"] / stats["total"] * 100) if stats["total"] > 0 else 0
            print(f"   • {test_type.title()}: {stats['successful']}/{stats['total']} ({success_rate:.1f}%)")
        print()
        
        # Métricas de performance agregadas
        successful_results = [r for r in self.test_results if r.status.value == "completed" and r.metrics]
        if successful_results:
            avg_throughput = sum(r.metrics.throughput_rps for r in successful_results) / len(successful_results)
            avg_response_time = sum(r.metrics.avg_response_time_ms for r in successful_results) / len(successful_results)
            avg_error_rate = sum(r.metrics.error_rate_percent for r in successful_results) / len(successful_results)
            avg_memory = sum(r.metrics.memory_usage_mb for r in successful_results) / len(successful_results)
            avg_cpu = sum(r.metrics.cpu_usage_percent for r in successful_results) / len(successful_results)
            
            print("📊 MÉTRICAS DE PERFORMANCE MÉDIAS:")
            print(f"   • Throughput: {avg_throughput:.2f} RPS")
            print(f"   • Tempo de resposta: {avg_response_time:.2f} ms")
            print(f"   • Taxa de erro: {avg_error_rate:.2f}%")
            print(f"   • Uso de memória: {avg_memory:.2f} MB")
            print(f"   • Uso de CPU: {avg_cpu:.2f}%")
            print()
        
        # Salvar relatório em arquivo
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "failed_tests": failed_tests,
                "success_rate": (successful_tests/total_tests*100) if total_tests > 0 else 0
            },
            "test_types": test_types,
            "results": [
                {
                    "test_id": r.test_id,
                    "test_name": r.test_name,
                    "test_type": r.test_type.value,
                    "status": r.status.value,
                    "duration_ms": r.duration_ms,
                    "errors": r.errors,
                    "metrics": r.metrics.to_dict() if r.metrics else None
                }
                for r in self.test_results
            ]
        }
        
        report_file = Path("performance_test_report.json")
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Relatório salvo em: {report_file}")
        print()
        print("🎉 Demonstração concluída com sucesso!")
        print(f"📅 Fim: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    async def _generate_quick_report(self) -> None:
        """Gera relatório rápido da demonstração"""
        print("📊 RELATÓRIO RÁPIDO")
        print("=" * 60)
        
        # Estatísticas básicas
        total_tests = len(self.test_results)
        successful_tests = len([r for r in self.test_results if r.status.value == "completed"])
        
        print(f"📈 RESUMO:")
        print(f"   • Testes executados: {total_tests}")
        print(f"   • Testes bem-sucedidos: {successful_tests}")
        print(f"   • Taxa de sucesso: {(successful_tests/total_tests*100):.1f}%")
        print()
        
        # Resultados por teste
        print("📊 RESULTADOS:")
        for result in self.test_results:
            status_icon = "✅" if result.status.value == "completed" else "❌"
            print(f"   {status_icon} {result.test_name}")
            if result.metrics:
                print(f"      • Throughput: {result.metrics.throughput_rps:.2f} RPS")
                print(f"      • Tempo médio: {result.metrics.avg_response_time_ms:.2f} ms")
                print(f"      • Taxa de erro: {result.metrics.error_rate_percent:.2f}%")
        
        print()
        print("🎉 Demonstração rápida concluída!")


async def main():
    """Função principal"""
    import sys
    
    demo = PerformanceTestDemo()
    
    if len(sys.argv) > 1 and sys.argv[1] == "quick":
        await demo.run_quick_demo()
    else:
        await demo.run_full_demo()


if __name__ == "__main__":
    asyncio.run(main())
