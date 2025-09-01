"""
Runner de Benchmarks
Sistema de Recomendações de Ofertas - Garimpeiro Geek
"""

import asyncio
import time
import random
import threading
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime
from dataclasses import dataclass
import logging
import statistics
import cProfile
import pstats
import io
import gc

from .models import (
    TestType, TestStatus, PerformanceMetrics, BenchmarkConfig, 
    TestResult
)
from .performance_monitor import performance_monitor


@dataclass
class BenchmarkFunction:
    """Função de benchmark"""
    name: str
    function: Callable
    async_function: Optional[Callable] = None
    description: str = ""
    category: str = "general"


@dataclass
class BenchmarkResult:
    """Resultado de um benchmark individual"""
    function_name: str
    iterations: int
    total_time_ms: float
    avg_time_ms: float
    min_time_ms: float
    max_time_ms: float
    p50_time_ms: float
    p95_time_ms: float
    p99_time_ms: float
    memory_before_mb: float
    memory_after_mb: float
    memory_increase_mb: float
    cpu_profile: Optional[Dict[str, Any]] = None


class BenchmarkRunner:
    """Runner de benchmarks para testes de performance específicos"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.active_tests: Dict[str, TestResult] = {}
        self.test_history: List[TestResult] = []
        self.benchmark_functions: Dict[str, BenchmarkFunction] = {}
        
        # Configurar benchmarks padrão
        self._setup_default_benchmarks()
    
    def _setup_default_benchmarks(self) -> None:
        """Configura benchmarks padrão"""
        # Benchmark de scraping
        self.add_benchmark(BenchmarkFunction(
            name="scraping_benchmark",
            function=self._benchmark_scraping,
            async_function=self._benchmark_scraping_async,
            description="Benchmark de operações de scraping",
            category="scraping"
        ))
        
        # Benchmark de processamento
        self.add_benchmark(BenchmarkFunction(
            name="processing_benchmark",
            function=self._benchmark_processing,
            async_function=self._benchmark_processing_async,
            description="Benchmark de processamento de dados",
            category="processing"
        ))
        
        # Benchmark de validação
        self.add_benchmark(BenchmarkFunction(
            name="validation_benchmark",
            function=self._benchmark_validation,
            async_function=self._benchmark_validation_async,
            description="Benchmark de validação de dados",
            category="validation"
        ))
        
        # Benchmark de memória
        self.add_benchmark(BenchmarkFunction(
            name="memory_benchmark",
            function=self._benchmark_memory,
            async_function=self._benchmark_memory_async,
            description="Benchmark de uso de memória",
            category="memory"
        ))
        
        # Benchmark de CPU
        self.add_benchmark(BenchmarkFunction(
            name="cpu_benchmark",
            function=self._benchmark_cpu,
            async_function=self._benchmark_cpu_async,
            description="Benchmark de uso de CPU",
            category="cpu"
        ))
    
    def add_benchmark(self, benchmark: BenchmarkFunction) -> None:
        """Adiciona uma função de benchmark"""
        self.benchmark_functions[benchmark.name] = benchmark
        self.logger.info(f"Benchmark adicionado: {benchmark.name} ({benchmark.category})")
    
    def remove_benchmark(self, benchmark_name: str) -> None:
        """Remove uma função de benchmark"""
        if benchmark_name in self.benchmark_functions:
            del self.benchmark_functions[benchmark_name]
            self.logger.info(f"Benchmark removido: {benchmark_name}")
    
    def run_benchmark(self, config: BenchmarkConfig, benchmark_name: Optional[str] = None) -> TestResult:
        """Executa um benchmark específico"""
        test_id = f"benchmark_{int(time.time())}"
        test_result = TestResult(
            test_id=test_id,
            test_name=config.test_name,
            test_type=TestType.BENCHMARK,
            status=TestStatus.RUNNING,
            start_time=datetime.now(),
            config=config.to_dict()
        )
        
        self.active_tests[test_id] = test_result
        self.logger.info(f"Iniciando benchmark: {config.test_name}")
        
        try:
            # Iniciar monitoramento
            performance_monitor.start_monitoring(interval_seconds=0.5)
            
            # Executar benchmark
            if benchmark_name:
                metrics = self._execute_single_benchmark(config, benchmark_name)
            else:
                metrics = self._execute_all_benchmarks(config)
            
            # Finalizar teste
            test_result.end_time = datetime.now()
            test_result.duration_ms = (test_result.end_time - test_result.start_time).total_seconds() * 1000
            test_result.metrics = metrics
            test_result.status = TestStatus.COMPLETED
            
            # Parar monitoramento
            performance_monitor.stop_monitoring()
            
            self.logger.info(f"Benchmark concluído: {config.test_name}")
            
        except Exception as e:
            test_result.status = TestStatus.FAILED
            test_result.errors.append(str(e))
            test_result.end_time = datetime.now()
            performance_monitor.stop_monitoring()
            self.logger.error(f"Erro no benchmark: {e}")
        
        # Adicionar ao histórico
        self.test_history.append(test_result)
        del self.active_tests[test_id]
        
        return test_result
    
    async def run_benchmark_async(self, config: BenchmarkConfig, benchmark_name: Optional[str] = None) -> TestResult:
        """Executa um benchmark específico assíncrono"""
        test_id = f"benchmark_async_{int(time.time())}"
        test_result = TestResult(
            test_id=test_id,
            test_name=config.test_name,
            test_type=TestType.BENCHMARK,
            status=TestStatus.RUNNING,
            start_time=datetime.now(),
            config=config.to_dict()
        )
        
        self.active_tests[test_id] = test_result
        self.logger.info(f"Iniciando benchmark assíncrono: {config.test_name}")
        
        try:
            # Iniciar monitoramento
            performance_monitor.start_monitoring(interval_seconds=0.5)
            
            # Executar benchmark assíncrono
            if benchmark_name:
                metrics = await self._execute_single_benchmark_async(config, benchmark_name)
            else:
                metrics = await self._execute_all_benchmarks_async(config)
            
            # Finalizar teste
            test_result.end_time = datetime.now()
            test_result.duration_ms = (test_result.end_time - test_result.start_time).total_seconds() * 1000
            test_result.metrics = metrics
            test_result.status = TestStatus.COMPLETED
            
            # Parar monitoramento
            performance_monitor.stop_monitoring()
            
            self.logger.info(f"Benchmark assíncrono concluído: {config.test_name}")
            
        except Exception as e:
            test_result.status = TestStatus.FAILED
            test_result.errors.append(str(e))
            test_result.end_time = datetime.now()
            performance_monitor.stop_monitoring()
            self.logger.error(f"Erro no benchmark assíncrono: {e}")
        
        # Adicionar ao histórico
        self.test_history.append(test_result)
        del self.active_tests[test_id]
        
        return test_result
    
    def _execute_single_benchmark(self, config: BenchmarkConfig, benchmark_name: str) -> PerformanceMetrics:
        """Executa um benchmark específico"""
        if benchmark_name not in self.benchmark_functions:
            raise ValueError(f"Benchmark '{benchmark_name}' não encontrado")
        
        benchmark = self.benchmark_functions[benchmark_name]
        start_time = datetime.now()
        
        # Executar warmup
        if config.warmup_iterations > 0:
            self.logger.info(f"Executando warmup: {config.warmup_iterations} iterações")
            for _ in range(config.warmup_iterations):
                benchmark.function()
        
        # Executar benchmark
        self.logger.info(f"Executando benchmark: {config.iterations} iterações")
        
        # Profiling de CPU se habilitado
        profiler = None
        if config.cpu_profiling:
            profiler = cProfile.Profile()
            profiler.enable()
        
        # Medir memória antes
        memory_before = performance_monitor.get_current_metrics().memory_used_mb
        
        # Executar iterações
        execution_times = []
        for i in range(config.iterations):
            iteration_start = time.time()
            benchmark.function()
            iteration_time = (time.time() - iteration_start) * 1000
            execution_times.append(iteration_time)
            
            # Log de progresso
            if (i + 1) % 100 == 0:
                self.logger.info(f"Progresso: {i + 1}/{config.iterations} iterações")
        
        # Parar profiling
        if profiler:
            profiler.disable()
            cpu_stats = self._get_cpu_profile_stats(profiler)
        else:
            cpu_stats = None
        
        # Medir memória depois
        memory_after = performance_monitor.get_current_metrics().memory_used_mb
        
        # Calcular estatísticas
        end_time = datetime.now()
        duration_ms = (end_time - start_time).total_seconds() * 1000
        
        if execution_times:
            execution_times.sort()
            avg_time = statistics.mean(execution_times)
            min_time = min(execution_times)
            max_time = max(execution_times)
            p50_time = execution_times[len(execution_times) // 2]
            p95_time = execution_times[int(len(execution_times) * 0.95)]
            p99_time = execution_times[int(len(execution_times) * 0.99)]
        else:
            avg_time = min_time = max_time = 0.0
            p50_time = p95_time = p99_time = 0.0
        
        # Obter métricas do sistema
        system_metrics = performance_monitor.get_current_metrics()
        
        return PerformanceMetrics(
            test_name=config.test_name,
            test_type=TestType.BENCHMARK,
            start_time=start_time,
            end_time=end_time,
            duration_ms=duration_ms,
            memory_usage_mb=memory_after,
            cpu_usage_percent=system_metrics.cpu_percent,
            concurrent_users=1,  # Não aplicável para benchmark
            test_config={
                **config.to_dict(),
                "benchmark_name": benchmark_name,
                "iterations_completed": len(execution_times),
                "avg_execution_time_ms": avg_time,
                "min_execution_time_ms": min_time,
                "max_execution_time_ms": max_time,
                "p50_execution_time_ms": p50_time,
                "p95_execution_time_ms": p95_time,
                "p99_execution_time_ms": p99_time,
                "memory_before_mb": memory_before,
                "memory_after_mb": memory_after,
                "memory_increase_mb": memory_after - memory_before,
                "cpu_profile": cpu_stats
            }
        )
    
    async def _execute_single_benchmark_async(self, config: BenchmarkConfig, benchmark_name: str) -> PerformanceMetrics:
        """Executa um benchmark específico assíncrono"""
        if benchmark_name not in self.benchmark_functions:
            raise ValueError(f"Benchmark '{benchmark_name}' não encontrado")
        
        benchmark = self.benchmark_functions[benchmark_name]
        if not benchmark.async_function:
            raise ValueError(f"Benchmark '{benchmark_name}' não possui versão assíncrona")
        
        start_time = datetime.now()
        
        # Executar warmup
        if config.warmup_iterations > 0:
            self.logger.info(f"Executando warmup assíncrono: {config.warmup_iterations} iterações")
            for _ in range(config.warmup_iterations):
                await benchmark.async_function()
        
        # Executar benchmark
        self.logger.info(f"Executando benchmark assíncrono: {config.iterations} iterações")
        
        # Medir memória antes
        memory_before = performance_monitor.get_current_metrics().memory_used_mb
        
        # Executar iterações
        execution_times = []
        for i in range(config.iterations):
            iteration_start = time.time()
            await benchmark.async_function()
            iteration_time = (time.time() - iteration_start) * 1000
            execution_times.append(iteration_time)
            
            # Log de progresso
            if (i + 1) % 100 == 0:
                self.logger.info(f"Progresso assíncrono: {i + 1}/{config.iterations} iterações")
        
        # Medir memória depois
        memory_after = performance_monitor.get_current_metrics().memory_used_mb
        
        # Calcular estatísticas (mesmo código do método síncrono)
        end_time = datetime.now()
        duration_ms = (end_time - start_time).total_seconds() * 1000
        
        if execution_times:
            execution_times.sort()
            avg_time = statistics.mean(execution_times)
            min_time = min(execution_times)
            max_time = max(execution_times)
            p50_time = execution_times[len(execution_times) // 2]
            p95_time = execution_times[int(len(execution_times) * 0.95)]
            p99_time = execution_times[int(len(execution_times) * 0.99)]
        else:
            avg_time = min_time = max_time = 0.0
            p50_time = p95_time = p99_time = 0.0
        
        # Obter métricas do sistema
        system_metrics = performance_monitor.get_current_metrics()
        
        return PerformanceMetrics(
            test_name=config.test_name,
            test_type=TestType.BENCHMARK,
            start_time=start_time,
            end_time=end_time,
            duration_ms=duration_ms,
            memory_usage_mb=memory_after,
            cpu_usage_percent=system_metrics.cpu_percent,
            concurrent_users=1,  # Não aplicável para benchmark
            test_config={
                **config.to_dict(),
                "benchmark_name": benchmark_name,
                "iterations_completed": len(execution_times),
                "avg_execution_time_ms": avg_time,
                "min_execution_time_ms": min_time,
                "max_execution_time_ms": max_time,
                "p50_execution_time_ms": p50_time,
                "p95_execution_time_ms": p95_time,
                "p99_execution_time_ms": p99_time,
                "memory_before_mb": memory_before,
                "memory_after_mb": memory_after,
                "memory_increase_mb": memory_after - memory_before
            }
        )
    
    def _execute_all_benchmarks(self, config: BenchmarkConfig) -> PerformanceMetrics:
        """Executa todos os benchmarks"""
        start_time = datetime.now()
        all_results = []
        
        for benchmark_name in self.benchmark_functions:
            self.logger.info(f"Executando benchmark: {benchmark_name}")
            try:
                result = self._execute_single_benchmark(config, benchmark_name)
                all_results.append(result)
            except Exception as e:
                self.logger.error(f"Erro no benchmark {benchmark_name}: {e}")
        
        # Calcular métricas agregadas
        end_time = datetime.now()
        duration_ms = (end_time - start_time).total_seconds() * 1000
        
        if all_results:
            avg_memory = statistics.mean([r.memory_usage_mb for r in all_results])
            avg_cpu = statistics.mean([r.cpu_usage_percent for r in all_results])
        else:
            avg_memory = avg_cpu = 0.0
        
        # Obter métricas do sistema
        system_metrics = performance_monitor.get_current_metrics()
        
        return PerformanceMetrics(
            test_name=config.test_name,
            test_type=TestType.BENCHMARK,
            start_time=start_time,
            end_time=end_time,
            duration_ms=duration_ms,
            memory_usage_mb=avg_memory,
            cpu_usage_percent=avg_cpu,
            concurrent_users=1,  # Não aplicável para benchmark
            test_config={
                **config.to_dict(),
                "benchmarks_executed": len(all_results),
                "benchmark_names": list(self.benchmark_functions.keys())
            }
        )
    
    async def _execute_all_benchmarks_async(self, config: BenchmarkConfig) -> PerformanceMetrics:
        """Executa todos os benchmarks assíncronos"""
        start_time = datetime.now()
        all_results = []
        
        for benchmark_name, benchmark in self.benchmark_functions.items():
            if benchmark.async_function:
                self.logger.info(f"Executando benchmark assíncrono: {benchmark_name}")
                try:
                    result = await self._execute_single_benchmark_async(config, benchmark_name)
                    all_results.append(result)
                except Exception as e:
                    self.logger.error(f"Erro no benchmark assíncrono {benchmark_name}: {e}")
        
        # Calcular métricas agregadas (mesmo código do método síncrono)
        end_time = datetime.now()
        duration_ms = (end_time - start_time).total_seconds() * 1000
        
        if all_results:
            avg_memory = statistics.mean([r.memory_usage_mb for r in all_results])
            avg_cpu = statistics.mean([r.cpu_usage_percent for r in all_results])
        else:
            avg_memory = avg_cpu = 0.0
        
        # Obter métricas do sistema
        system_metrics = performance_monitor.get_current_metrics()
        
        return PerformanceMetrics(
            test_name=config.test_name,
            test_type=TestType.BENCHMARK,
            start_time=start_time,
            end_time=end_time,
            duration_ms=duration_ms,
            memory_usage_mb=avg_memory,
            cpu_usage_percent=avg_cpu,
            concurrent_users=1,  # Não aplicável para benchmark
            test_config={
                **config.to_dict(),
                "benchmarks_executed": len(all_results),
                "benchmark_names": [name for name, b in self.benchmark_functions.items() if b.async_function]
            }
        )
    
    def _get_cpu_profile_stats(self, profiler: cProfile.Profile) -> Dict[str, Any]:
        """Obtém estatísticas do profiling de CPU"""
        try:
            s = io.StringIO()
            ps = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
            ps.print_stats(10)  # Top 10 funções
            
            return {
                "profile_output": s.getvalue(),
                "total_calls": ps.total_calls,
                "total_time": ps.total_tt
            }
        except Exception as e:
            self.logger.error(f"Erro ao obter estatísticas de CPU: {e}")
            return {"error": str(e)}
    
    # Funções de benchmark padrão
    def _benchmark_scraping(self) -> None:
        """Benchmark de scraping"""
        # Simular operação de scraping
        data = []
        for i in range(1000):
            data.append(f"item_{i}")
        
        # Simular processamento
        processed = [item.upper() for item in data]
        
        # Simular delay
        time.sleep(0.001)
    
    async def _benchmark_scraping_async(self) -> None:
        """Benchmark de scraping assíncrono"""
        # Simular operação de scraping
        data = []
        for i in range(1000):
            data.append(f"item_{i}")
        
        # Simular processamento
        processed = [item.upper() for item in data]
        
        # Simular delay
        await asyncio.sleep(0.001)
    
    def _benchmark_processing(self) -> None:
        """Benchmark de processamento"""
        # Simular processamento intensivo
        numbers = list(range(10000))
        
        # Operações matemáticas
        squared = [x ** 2 for x in numbers]
        filtered = [x for x in squared if x % 2 == 0]
        total = sum(filtered)
    
    async def _benchmark_processing_async(self) -> None:
        """Benchmark de processamento assíncrono"""
        # Simular processamento intensivo
        numbers = list(range(10000))
        
        # Operações matemáticas
        squared = [x ** 2 for x in numbers]
        filtered = [x for x in squared if x % 2 == 0]
        total = sum(filtered)
        
        # Simular operação assíncrona
        await asyncio.sleep(0.0001)
    
    def _benchmark_validation(self) -> None:
        """Benchmark de validação"""
        # Simular validação de dados
        data = [random.randint(1, 1000) for _ in range(1000)]
        
        # Validações
        valid_count = 0
        for item in data:
            if 1 <= item <= 1000:
                valid_count += 1
        
        # Simular delay
        time.sleep(0.0005)
    
    async def _benchmark_validation_async(self) -> None:
        """Benchmark de validação assíncrono"""
        # Simular validação de dados
        data = [random.randint(1, 1000) for _ in range(1000)]
        
        # Validações
        valid_count = 0
        for item in data:
            if 1 <= item <= 1000:
                valid_count += 1
        
        # Simular delay
        await asyncio.sleep(0.0005)
    
    def _benchmark_memory(self) -> None:
        """Benchmark de memória"""
        # Simular alocação de memória
        large_list = [i for i in range(10000)]
        large_dict = {i: f"value_{i}" for i in range(10000)}
        
        # Simular operações de memória
        processed = [str(item) for item in large_list]
        filtered = {k: v for k, v in large_dict.items() if k % 2 == 0}
        
        # Forçar garbage collection
        gc.collect()
    
    async def _benchmark_memory_async(self) -> None:
        """Benchmark de memória assíncrono"""
        # Simular alocação de memória
        large_list = [i for i in range(10000)]
        large_dict = {i: f"value_{i}" for i in range(10000)}
        
        # Simular operações de memória
        processed = [str(item) for item in large_list]
        filtered = {k: v for k, v in large_dict.items() if k % 2 == 0}
        
        # Forçar garbage collection
        gc.collect()
        
        # Simular operação assíncrona
        await asyncio.sleep(0.0001)
    
    def _benchmark_cpu(self) -> None:
        """Benchmark de CPU"""
        # Simular operações intensivas de CPU
        result = 0
        for i in range(10000):
            result += i ** 2
            result = result % 1000000
        
        # Simular delay
        time.sleep(0.001)
    
    async def _benchmark_cpu_async(self) -> None:
        """Benchmark de CPU assíncrono"""
        # Simular operações intensivas de CPU
        result = 0
        for i in range(10000):
            result += i ** 2
            result = result % 1000000
        
        # Simular delay
        await asyncio.sleep(0.001)
    
    def get_available_benchmarks(self) -> List[Dict[str, Any]]:
        """Obtém lista de benchmarks disponíveis"""
        return [
            {
                "name": name,
                "description": benchmark.description,
                "category": benchmark.category,
                "has_async": benchmark.async_function is not None
            }
            for name, benchmark in self.benchmark_functions.items()
        ]
    
    def get_test_history(self) -> List[TestResult]:
        """Obtém histórico de testes"""
        return self.test_history.copy()
    
    def get_active_tests(self) -> Dict[str, TestResult]:
        """Obtém testes ativos"""
        return self.active_tests.copy()
    
    def clear_history(self) -> None:
        """Limpa histórico de testes"""
        self.test_history.clear()
        self.logger.info("Histórico de benchmarks limpo")
