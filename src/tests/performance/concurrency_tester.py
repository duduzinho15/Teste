"""
Testador de Concorrência
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
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

from .models import (
    TestType, TestStatus, PerformanceMetrics, ConcurrencyTestConfig, 
    TestResult
)
from .performance_monitor import performance_monitor


@dataclass
class ConcurrencyTask:
    """Tarefa de concorrência"""
    task_id: str
    task_type: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_ms: Optional[float] = None
    success: bool = True
    error_message: Optional[str] = None
    thread_id: Optional[int] = None
    process_id: Optional[int] = None


class ConcurrencyTester:
    """Testador de concorrência para o sistema"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.active_tests: Dict[str, TestResult] = {}
        self.test_history: List[TestResult] = []
        self.task_history: List[ConcurrencyTask] = []
        
        # Executores
        self.thread_executor: Optional[ThreadPoolExecutor] = None
        self.process_executor: Optional[ProcessPoolExecutor] = None
        
        # Configurar tarefas padrão
        self._setup_default_tasks()
    
    def _setup_default_tasks(self) -> None:
        """Configura tarefas padrão de teste"""
        self.default_tasks = {
            "scraping": {
                "function": self._simulate_scraping_task,
                "async_function": self._simulate_scraping_task_async,
                "weight": 0.4
            },
            "processing": {
                "function": self._simulate_processing_task,
                "async_function": self._simulate_processing_task_async,
                "weight": 0.3
            },
            "posting": {
                "function": self._simulate_posting_task,
                "async_function": self._simulate_posting_task_async,
                "weight": 0.2
            },
            "validation": {
                "function": self._simulate_validation_task,
                "async_function": self._simulate_validation_task_async,
                "weight": 0.1
            }
        }
    
    def run_concurrency_test(self, config: ConcurrencyTestConfig) -> TestResult:
        """Executa um teste de concorrência"""
        test_id = f"concurrency_{int(time.time())}"
        test_result = TestResult(
            test_id=test_id,
            test_name=config.test_name,
            test_type=TestType.CONCURRENCY,
            status=TestStatus.RUNNING,
            start_time=datetime.now(),
            config=config.to_dict()
        )
        
        self.active_tests[test_id] = test_result
        self.logger.info(f"Iniciando teste de concorrência: {config.test_name}")
        
        try:
            # Iniciar monitoramento
            performance_monitor.start_monitoring(interval_seconds=0.5)
            
            # Executar teste
            metrics = self._execute_concurrency_test(config)
            
            # Finalizar teste
            test_result.end_time = datetime.now()
            test_result.duration_ms = (test_result.end_time - test_result.start_time).total_seconds() * 1000
            test_result.metrics = metrics
            test_result.status = TestStatus.COMPLETED
            
            # Parar monitoramento
            performance_monitor.stop_monitoring()
            
            self.logger.info(f"Teste de concorrência concluído: {config.test_name}")
            
        except Exception as e:
            test_result.status = TestStatus.FAILED
            test_result.errors.append(str(e))
            test_result.end_time = datetime.now()
            performance_monitor.stop_monitoring()
            self.logger.error(f"Erro no teste de concorrência: {e}")
        
        # Adicionar ao histórico
        self.test_history.append(test_result)
        del self.active_tests[test_id]
        
        return test_result
    
    async def run_concurrency_test_async(self, config: ConcurrencyTestConfig) -> TestResult:
        """Executa um teste de concorrência assíncrono"""
        test_id = f"concurrency_async_{int(time.time())}"
        test_result = TestResult(
            test_id=test_id,
            test_name=config.test_name,
            test_type=TestType.CONCURRENCY,
            status=TestStatus.RUNNING,
            start_time=datetime.now(),
            config=config.to_dict()
        )
        
        self.active_tests[test_id] = test_result
        self.logger.info(f"Iniciando teste de concorrência assíncrono: {config.test_name}")
        
        try:
            # Iniciar monitoramento
            performance_monitor.start_monitoring(interval_seconds=0.5)
            
            # Executar teste assíncrono
            metrics = await self._execute_concurrency_test_async(config)
            
            # Finalizar teste
            test_result.end_time = datetime.now()
            test_result.duration_ms = (test_result.end_time - test_result.start_time).total_seconds() * 1000
            test_result.metrics = metrics
            test_result.status = TestStatus.COMPLETED
            
            # Parar monitoramento
            performance_monitor.stop_monitoring()
            
            self.logger.info(f"Teste de concorrência assíncrono concluído: {config.test_name}")
            
        except Exception as e:
            test_result.status = TestStatus.FAILED
            test_result.errors.append(str(e))
            test_result.end_time = datetime.now()
            performance_monitor.stop_monitoring()
            self.logger.error(f"Erro no teste de concorrência assíncrono: {e}")
        
        # Adicionar ao histórico
        self.test_history.append(test_result)
        del self.active_tests[test_id]
        
        return test_result
    
    def _execute_concurrency_test(self, config: ConcurrencyTestConfig) -> PerformanceMetrics:
        """Executa o teste de concorrência"""
        start_time = datetime.now()
        tasks = []
        
        # Criar executor de threads
        max_workers = min(config.concurrent_tasks, config.max_concurrent_tasks)
        self.thread_executor = ThreadPoolExecutor(max_workers=max_workers)
        
        try:
            # Distribuir tarefas por tipo
            task_distribution = self._distribute_tasks(config.concurrent_tasks, config.task_types)
            
            # Submeter tarefas
            for task_type, count in task_distribution.items():
                if task_type in self.default_tasks:
                    task_func = self.default_tasks[task_type]["function"]
                    for i in range(count):
                        task_id = f"{task_type}_{i}"
                        future = self.thread_executor.submit(self._execute_task, task_id, task_type, task_func)
                        tasks.append(future)
            
            # Aguardar conclusão
            completed_tasks = []
            for future in tasks:
                try:
                    task_result = future.result(timeout=config.timeout_seconds)
                    completed_tasks.append(task_result)
                except Exception as e:
                    self.logger.error(f"Tarefa falhou: {e}")
            
            # Calcular métricas
            metrics = self._calculate_concurrency_metrics(completed_tasks, start_time, config)
            
            return metrics
            
        finally:
            if self.thread_executor:
                self.thread_executor.shutdown(wait=True)
    
    async def _execute_concurrency_test_async(self, config: ConcurrencyTestConfig) -> PerformanceMetrics:
        """Executa o teste de concorrência assíncrono"""
        start_time = datetime.now()
        tasks = []
        
        # Distribuir tarefas por tipo
        task_distribution = self._distribute_tasks(config.concurrent_tasks, config.task_types)
        
        # Criar tarefas assíncronas
        for task_type, count in task_distribution.items():
            if task_type in self.default_tasks:
                task_func = self.default_tasks[task_type]["async_function"]
                for i in range(count):
                    task_id = f"{task_type}_{i}"
                    task = asyncio.create_task(
                        self._execute_task_async(task_id, task_type, task_func)
                    )
                    tasks.append(task)
        
        # Aguardar conclusão
        completed_tasks = []
        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for result in results:
                if isinstance(result, ConcurrencyTask):
                    completed_tasks.append(result)
                else:
                    self.logger.error(f"Tarefa assíncrona falhou: {result}")
        except Exception as e:
            self.logger.error(f"Erro no teste assíncrono: {e}")
        
        # Calcular métricas
        metrics = self._calculate_concurrency_metrics(completed_tasks, start_time, config)
        
        return metrics
    
    def _distribute_tasks(self, total_tasks: int, task_types: List[str]) -> Dict[str, int]:
        """Distribui tarefas por tipo baseado em pesos"""
        distribution = {}
        
        # Filtrar tipos válidos
        valid_types = [t for t in task_types if t in self.default_tasks]
        if not valid_types:
            valid_types = list(self.default_tasks.keys())
        
        # Calcular pesos
        weights = [self.default_tasks[t]["weight"] for t in valid_types]
        total_weight = sum(weights)
        
        # Distribuir tarefas
        remaining_tasks = total_tasks
        for i, task_type in enumerate(valid_types):
            if i == len(valid_types) - 1:
                # Último tipo recebe todas as tarefas restantes
                distribution[task_type] = remaining_tasks
            else:
                # Distribuir proporcionalmente ao peso
                task_count = int((weights[i] / total_weight) * total_tasks)
                distribution[task_type] = min(task_count, remaining_tasks)
                remaining_tasks -= distribution[task_type]
        
        return distribution
    
    def _execute_task(self, task_id: str, task_type: str, task_func: Callable) -> ConcurrencyTask:
        """Executa uma tarefa individual"""
        task = ConcurrencyTask(
            task_id=task_id,
            task_type=task_type,
            start_time=datetime.now(),
            thread_id=threading.get_ident()
        )
        
        try:
            # Executar tarefa
            task_func()
            
            # Registrar sucesso
            task.end_time = datetime.now()
            task.duration_ms = (task.end_time - task.start_time).total_seconds() * 1000
            task.success = True
            
            # Registrar no monitor de performance
            performance_monitor.record_response_time(task.duration_ms, success=True)
            
        except Exception as e:
            # Registrar falha
            task.end_time = datetime.now()
            task.duration_ms = (task.end_time - task.start_time).total_seconds() * 1000
            task.success = False
            task.error_message = str(e)
            
            # Registrar no monitor de performance
            performance_monitor.record_response_time(task.duration_ms, success=False, error_message=str(e))
        
        # Adicionar ao histórico
        self.task_history.append(task)
        
        return task
    
    async def _execute_task_async(self, task_id: str, task_type: str, task_func: Callable) -> ConcurrencyTask:
        """Executa uma tarefa individual assíncrona"""
        task = ConcurrencyTask(
            task_id=task_id,
            task_type=task_type,
            start_time=datetime.now()
        )
        
        try:
            # Executar tarefa assíncrona
            await task_func()
            
            # Registrar sucesso
            task.end_time = datetime.now()
            task.duration_ms = (task.end_time - task.start_time).total_seconds() * 1000
            task.success = True
            
            # Registrar no monitor de performance
            performance_monitor.record_response_time(task.duration_ms, success=True)
            
        except Exception as e:
            # Registrar falha
            task.end_time = datetime.now()
            task.duration_ms = (task.end_time - task.start_time).total_seconds() * 1000
            task.success = False
            task.error_message = str(e)
            
            # Registrar no monitor de performance
            performance_monitor.record_response_time(task.duration_ms, success=False, error_message=str(e))
        
        # Adicionar ao histórico
        self.task_history.append(task)
        
        return task
    
    def _calculate_concurrency_metrics(self, completed_tasks: List[ConcurrencyTask], 
                                     start_time: datetime, config: ConcurrencyTestConfig) -> PerformanceMetrics:
        """Calcula métricas de concorrência"""
        end_time = datetime.now()
        duration_ms = (end_time - start_time).total_seconds() * 1000
        
        if not completed_tasks:
            return PerformanceMetrics(
                test_name=config.test_name,
                test_type=TestType.CONCURRENCY,
                start_time=start_time,
                end_time=end_time,
                duration_ms=duration_ms,
                concurrent_users=config.concurrent_tasks,
                test_config=config.to_dict()
            )
        
        # Estatísticas de tarefas
        successful_tasks = [t for t in completed_tasks if t.success]
        failed_tasks = [t for t in completed_tasks if not t.success]
        
        total_tasks = len(completed_tasks)
        successful_count = len(successful_tasks)
        failed_count = len(failed_tasks)
        
        # Tempos de resposta
        durations = [t.duration_ms for t in completed_tasks if t.duration_ms]
        if durations:
            durations.sort()
            avg_response_time = statistics.mean(durations)
            min_response_time = min(durations)
            max_response_time = max(durations)
            p50_response_time = durations[len(durations) // 2]
            p95_response_time = durations[int(len(durations) * 0.95)]
            p99_response_time = durations[int(len(durations) * 0.99)]
        else:
            avg_response_time = min_response_time = max_response_time = 0.0
            p50_response_time = p95_response_time = p99_response_time = 0.0
        
        # Throughput e taxa de erro
        throughput_rps = total_tasks / (duration_ms / 1000) if duration_ms > 0 else 0.0
        error_rate = (failed_count / total_tasks * 100) if total_tasks > 0 else 0.0
        
        # Métricas do sistema
        system_metrics = performance_monitor.get_current_metrics()
        
        return PerformanceMetrics(
            test_name=config.test_name,
            test_type=TestType.CONCURRENCY,
            start_time=start_time,
            end_time=end_time,
            duration_ms=duration_ms,
            requests_total=total_tasks,
            requests_successful=successful_count,
            requests_failed=failed_count,
            requests_timeout=0,  # Não aplicável para concorrência
            avg_response_time_ms=avg_response_time,
            min_response_time_ms=min_response_time,
            max_response_time_ms=max_response_time,
            p50_response_time_ms=p50_response_time,
            p95_response_time_ms=p95_response_time,
            p99_response_time_ms=p99_response_time,
            throughput_rps=throughput_rps,
            memory_usage_mb=system_metrics.memory_used_mb,
            cpu_usage_percent=system_metrics.cpu_percent,
            error_rate_percent=error_rate,
            concurrent_users=config.concurrent_tasks,
            test_config=config.to_dict()
        )
    
    # Funções de simulação de tarefas
    def _simulate_scraping_task(self) -> None:
        """Simula tarefa de scraping"""
        delay = random.uniform(0.1, 2.0)
        time.sleep(delay)
        
        # Simular falha ocasional
        if random.random() < 0.05:
            raise Exception("Erro de scraping simulado")
    
    async def _simulate_scraping_task_async(self) -> None:
        """Simula tarefa de scraping assíncrona"""
        delay = random.uniform(0.1, 2.0)
        await asyncio.sleep(delay)
        
        # Simular falha ocasional
        if random.random() < 0.05:
            raise Exception("Erro de scraping simulado")
    
    def _simulate_processing_task(self) -> None:
        """Simula tarefa de processamento"""
        delay = random.uniform(0.1, 1.0)
        time.sleep(delay)
        
        # Simular falha ocasional
        if random.random() < 0.02:
            raise Exception("Erro de processamento simulado")
    
    async def _simulate_processing_task_async(self) -> None:
        """Simula tarefa de processamento assíncrona"""
        delay = random.uniform(0.1, 1.0)
        await asyncio.sleep(delay)
        
        # Simular falha ocasional
        if random.random() < 0.02:
            raise Exception("Erro de processamento simulado")
    
    def _simulate_posting_task(self) -> None:
        """Simula tarefa de posting"""
        delay = random.uniform(0.2, 1.5)
        time.sleep(delay)
        
        # Simular falha ocasional
        if random.random() < 0.03:
            raise Exception("Erro de posting simulado")
    
    async def _simulate_posting_task_async(self) -> None:
        """Simula tarefa de posting assíncrona"""
        delay = random.uniform(0.2, 1.5)
        await asyncio.sleep(delay)
        
        # Simular falha ocasional
        if random.random() < 0.03:
            raise Exception("Erro de posting simulado")
    
    def _simulate_validation_task(self) -> None:
        """Simula tarefa de validação"""
        delay = random.uniform(0.01, 0.2)
        time.sleep(delay)
        
        # Simular falha ocasional
        if random.random() < 0.01:
            raise Exception("Erro de validação simulado")
    
    async def _simulate_validation_task_async(self) -> None:
        """Simula tarefa de validação assíncrona"""
        delay = random.uniform(0.01, 0.2)
        await asyncio.sleep(delay)
        
        # Simular falha ocasional
        if random.random() < 0.01:
            raise Exception("Erro de validação simulado")
    
    def get_task_statistics(self) -> Dict[str, Any]:
        """Obtém estatísticas das tarefas"""
        if not self.task_history:
            return {
                "total_tasks": 0,
                "successful_tasks": 0,
                "failed_tasks": 0,
                "avg_duration_ms": 0.0,
                "task_types": {}
            }
        
        # Estatísticas gerais
        total_tasks = len(self.task_history)
        successful_tasks = len([t for t in self.task_history if t.success])
        failed_tasks = len([t for t in self.task_history if not t.success])
        
        # Durações
        durations = [t.duration_ms for t in self.task_history if t.duration_ms]
        avg_duration = statistics.mean(durations) if durations else 0.0
        
        # Estatísticas por tipo
        task_types = {}
        for task in self.task_history:
            task_type = task.task_type
            if task_type not in task_types:
                task_types[task_type] = {
                    "total": 0,
                    "successful": 0,
                    "failed": 0,
                    "durations": []
                }
            
            task_types[task_type]["total"] += 1
            if task.success:
                task_types[task_type]["successful"] += 1
            else:
                task_types[task_type]["failed"] += 1
            
            if task.duration_ms:
                task_types[task_type]["durations"].append(task.duration_ms)
        
        # Calcular médias por tipo
        for task_type, stats in task_types.items():
            if stats["durations"]:
                stats["avg_duration_ms"] = statistics.mean(stats["durations"])
                stats["min_duration_ms"] = min(stats["durations"])
                stats["max_duration_ms"] = max(stats["durations"])
            else:
                stats["avg_duration_ms"] = stats["min_duration_ms"] = stats["max_duration_ms"] = 0.0
            
            stats["success_rate"] = (stats["successful"] / stats["total"] * 100) if stats["total"] > 0 else 0.0
            del stats["durations"]  # Remover lista de durações
        
        return {
            "total_tasks": total_tasks,
            "successful_tasks": successful_tasks,
            "failed_tasks": failed_tasks,
            "success_rate": (successful_tasks / total_tasks * 100) if total_tasks > 0 else 0.0,
            "avg_duration_ms": avg_duration,
            "task_types": task_types
        }
    
    def get_test_history(self) -> List[TestResult]:
        """Obtém histórico de testes"""
        return self.test_history.copy()
    
    def get_active_tests(self) -> Dict[str, TestResult]:
        """Obtém testes ativos"""
        return self.active_tests.copy()
    
    def clear_history(self) -> None:
        """Limpa histórico de testes e tarefas"""
        self.test_history.clear()
        self.task_history.clear()
        self.logger.info("Histórico de testes e tarefas limpo")
