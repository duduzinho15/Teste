"""
Gerador de Carga
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

from .models import (
    TestType, TestStatus, PerformanceMetrics, LoadTestConfig, 
    TestResult
)
from .performance_monitor import performance_monitor


@dataclass
class LoadStep:
    """Passo de carga"""
    step_number: int
    users: int
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_ms: Optional[float] = None
    requests_total: int = 0
    requests_successful: int = 0
    requests_failed: int = 0
    avg_response_time_ms: float = 0.0
    throughput_rps: float = 0.0
    error_rate_percent: float = 0.0


class LoadGenerator:
    """Gerador de carga para testes de carga progressiva"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.active_tests: Dict[str, TestResult] = {}
        self.test_history: List[TestResult] = []
        self.load_steps: List[LoadStep] = []
        
        # Configurar cenários padrão
        self._setup_default_scenarios()
    
    def _setup_default_scenarios(self) -> None:
        """Configura cenários padrão de carga"""
        self.default_scenarios = {
            "scraping": {
                "function": self._simulate_scraping_request,
                "async_function": self._simulate_scraping_request_async,
                "weight": 0.4
            },
            "processing": {
                "function": self._simulate_processing_request,
                "async_function": self._simulate_processing_request_async,
                "weight": 0.3
            },
            "posting": {
                "function": self._simulate_posting_request,
                "async_function": self._simulate_posting_request_async,
                "weight": 0.2
            },
            "validation": {
                "function": self._simulate_validation_request,
                "async_function": self._simulate_validation_request_async,
                "weight": 0.1
            }
        }
    
    def run_load_test(self, config: LoadTestConfig) -> TestResult:
        """Executa um teste de carga"""
        test_id = f"load_{int(time.time())}"
        test_result = TestResult(
            test_id=test_id,
            test_name=config.test_name,
            test_type=TestType.LOAD,
            status=TestStatus.RUNNING,
            start_time=datetime.now(),
            config=config.to_dict()
        )
        
        self.active_tests[test_id] = test_result
        self.logger.info(f"Iniciando teste de carga: {config.test_name}")
        
        try:
            # Iniciar monitoramento
            performance_monitor.start_monitoring(interval_seconds=0.5)
            
            # Executar teste
            metrics = self._execute_load_test(config)
            
            # Finalizar teste
            test_result.end_time = datetime.now()
            test_result.duration_ms = (test_result.end_time - test_result.start_time).total_seconds() * 1000
            test_result.metrics = metrics
            test_result.status = TestStatus.COMPLETED
            
            # Parar monitoramento
            performance_monitor.stop_monitoring()
            
            self.logger.info(f"Teste de carga concluído: {config.test_name}")
            
        except Exception as e:
            test_result.status = TestStatus.FAILED
            test_result.errors.append(str(e))
            test_result.end_time = datetime.now()
            performance_monitor.stop_monitoring()
            self.logger.error(f"Erro no teste de carga: {e}")
        
        # Adicionar ao histórico
        self.test_history.append(test_result)
        del self.active_tests[test_id]
        
        return test_result
    
    async def run_load_test_async(self, config: LoadTestConfig) -> TestResult:
        """Executa um teste de carga assíncrono"""
        test_id = f"load_async_{int(time.time())}"
        test_result = TestResult(
            test_id=test_id,
            test_name=config.test_name,
            test_type=TestType.LOAD,
            status=TestStatus.RUNNING,
            start_time=datetime.now(),
            config=config.to_dict()
        )
        
        self.active_tests[test_id] = test_result
        self.logger.info(f"Iniciando teste de carga assíncrono: {config.test_name}")
        
        try:
            # Iniciar monitoramento
            performance_monitor.start_monitoring(interval_seconds=0.5)
            
            # Executar teste assíncrono
            metrics = await self._execute_load_test_async(config)
            
            # Finalizar teste
            test_result.end_time = datetime.now()
            test_result.duration_ms = (test_result.end_time - test_result.start_time).total_seconds() * 1000
            test_result.metrics = metrics
            test_result.status = TestStatus.COMPLETED
            
            # Parar monitoramento
            performance_monitor.stop_monitoring()
            
            self.logger.info(f"Teste de carga assíncrono concluído: {config.test_name}")
            
        except Exception as e:
            test_result.status = TestStatus.FAILED
            test_result.errors.append(str(e))
            test_result.end_time = datetime.now()
            performance_monitor.stop_monitoring()
            self.logger.error(f"Erro no teste de carga assíncrono: {e}")
        
        # Adicionar ao histórico
        self.test_history.append(test_result)
        del self.active_tests[test_id]
        
        return test_result
    
    def _execute_load_test(self, config: LoadTestConfig) -> PerformanceMetrics:
        """Executa o teste de carga"""
        start_time = datetime.now()
        all_response_times = []
        total_requests = 0
        total_successful = 0
        total_failed = 0
        
        # Calcular passos de carga
        current_users = config.initial_users
        step_number = 1
        
        while current_users <= config.max_users:
            self.logger.info(f"Executando passo {step_number}: {current_users} usuários")
            
            # Criar passo
            load_step = LoadStep(
                step_number=step_number,
                users=current_users,
                start_time=datetime.now()
            )
            
            # Executar passo
            step_metrics = self._execute_load_step(current_users, config.step_duration_seconds)
            
            # Atualizar passo
            load_step.end_time = datetime.now()
            load_step.duration_ms = (load_step.end_time - load_step.start_time).total_seconds() * 1000
            load_step.requests_total = step_metrics["requests_total"]
            load_step.requests_successful = step_metrics["requests_successful"]
            load_step.requests_failed = step_metrics["requests_failed"]
            load_step.avg_response_time_ms = step_metrics["avg_response_time_ms"]
            load_step.throughput_rps = step_metrics["throughput_rps"]
            load_step.error_rate_percent = step_metrics["error_rate_percent"]
            
            # Adicionar ao histórico
            self.load_steps.append(load_step)
            
            # Acumular métricas
            all_response_times.extend(step_metrics["response_times"])
            total_requests += step_metrics["requests_total"]
            total_successful += step_metrics["requests_successful"]
            total_failed += step_metrics["requests_failed"]
            
            # Verificar se deve parar
            if step_metrics["error_rate_percent"] > config.error_threshold_percent:
                self.logger.warning(f"Taxa de erro {step_metrics['error_rate_percent']:.2f}% excedeu threshold de {config.error_threshold_percent}%")
                break
            
            if step_metrics["avg_response_time_ms"] > config.max_response_time_ms:
                self.logger.warning(f"Tempo de resposta {step_metrics['avg_response_time_ms']:.2f}ms excedeu limite de {config.max_response_time_ms}ms")
                break
            
            # Próximo passo
            current_users += config.step_users
            step_number += 1
        
        # Executar passo de sustentação se especificado
        if config.hold_duration_seconds > 0:
            self.logger.info(f"Executando passo de sustentação: {current_users - config.step_users} usuários por {config.hold_duration_seconds}s")
            
            hold_step = LoadStep(
                step_number=step_number,
                users=current_users - config.step_users,
                start_time=datetime.now()
            )
            
            hold_metrics = self._execute_load_step(current_users - config.step_users, config.hold_duration_seconds)
            
            hold_step.end_time = datetime.now()
            hold_step.duration_ms = (hold_step.end_time - hold_step.start_time).total_seconds() * 1000
            hold_step.requests_total = hold_metrics["requests_total"]
            hold_step.requests_successful = hold_metrics["requests_successful"]
            hold_step.requests_failed = hold_metrics["requests_failed"]
            hold_step.avg_response_time_ms = hold_metrics["avg_response_time_ms"]
            hold_step.throughput_rps = hold_metrics["throughput_rps"]
            hold_step.error_rate_percent = hold_metrics["error_rate_percent"]
            
            self.load_steps.append(hold_step)
            
            # Acumular métricas
            all_response_times.extend(hold_metrics["response_times"])
            total_requests += hold_metrics["requests_total"]
            total_successful += hold_metrics["requests_successful"]
            total_failed += hold_metrics["requests_failed"]
        
        # Calcular métricas finais
        end_time = datetime.now()
        duration_ms = (end_time - start_time).total_seconds() * 1000
        
        if all_response_times:
            all_response_times.sort()
            avg_response_time = statistics.mean(all_response_times)
            min_response_time = min(all_response_times)
            max_response_time = max(all_response_times)
            p50_response_time = all_response_times[len(all_response_times) // 2]
            p95_response_time = all_response_times[int(len(all_response_times) * 0.95)]
            p99_response_time = all_response_times[int(len(all_response_times) * 0.99)]
        else:
            avg_response_time = min_response_time = max_response_time = 0.0
            p50_response_time = p95_response_time = p99_response_time = 0.0
        
        throughput_rps = total_requests / (duration_ms / 1000) if duration_ms > 0 else 0.0
        error_rate = (total_failed / total_requests * 100) if total_requests > 0 else 0.0
        
        # Obter métricas do sistema
        system_metrics = performance_monitor.get_current_metrics()
        
        return PerformanceMetrics(
            test_name=config.test_name,
            test_type=TestType.LOAD,
            start_time=start_time,
            end_time=end_time,
            duration_ms=duration_ms,
            requests_total=total_requests,
            requests_successful=total_successful,
            requests_failed=total_failed,
            requests_timeout=0,  # Não aplicável para carga
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
            concurrent_users=config.max_users,
            test_config=config.to_dict()
        )
    
    async def _execute_load_test_async(self, config: LoadTestConfig) -> PerformanceMetrics:
        """Executa o teste de carga assíncrono"""
        start_time = datetime.now()
        all_response_times = []
        total_requests = 0
        total_successful = 0
        total_failed = 0
        
        # Calcular passos de carga
        current_users = config.initial_users
        step_number = 1
        
        while current_users <= config.max_users:
            self.logger.info(f"Executando passo assíncrono {step_number}: {current_users} usuários")
            
            # Criar passo
            load_step = LoadStep(
                step_number=step_number,
                users=current_users,
                start_time=datetime.now()
            )
            
            # Executar passo assíncrono
            step_metrics = await self._execute_load_step_async(current_users, config.step_duration_seconds)
            
            # Atualizar passo
            load_step.end_time = datetime.now()
            load_step.duration_ms = (load_step.end_time - load_step.start_time).total_seconds() * 1000
            load_step.requests_total = step_metrics["requests_total"]
            load_step.requests_successful = step_metrics["requests_successful"]
            load_step.requests_failed = step_metrics["requests_failed"]
            load_step.avg_response_time_ms = step_metrics["avg_response_time_ms"]
            load_step.throughput_rps = step_metrics["throughput_rps"]
            load_step.error_rate_percent = step_metrics["error_rate_percent"]
            
            # Adicionar ao histórico
            self.load_steps.append(load_step)
            
            # Acumular métricas
            all_response_times.extend(step_metrics["response_times"])
            total_requests += step_metrics["requests_total"]
            total_successful += step_metrics["requests_successful"]
            total_failed += step_metrics["requests_failed"]
            
            # Verificar se deve parar
            if step_metrics["error_rate_percent"] > config.error_threshold_percent:
                self.logger.warning(f"Taxa de erro {step_metrics['error_rate_percent']:.2f}% excedeu threshold de {config.error_threshold_percent}%")
                break
            
            if step_metrics["avg_response_time_ms"] > config.max_response_time_ms:
                self.logger.warning(f"Tempo de resposta {step_metrics['avg_response_time_ms']:.2f}ms excedeu limite de {config.max_response_time_ms}ms")
                break
            
            # Próximo passo
            current_users += config.step_users
            step_number += 1
        
        # Executar passo de sustentação se especificado
        if config.hold_duration_seconds > 0:
            self.logger.info(f"Executando passo de sustentação assíncrono: {current_users - config.step_users} usuários por {config.hold_duration_seconds}s")
            
            hold_step = LoadStep(
                step_number=step_number,
                users=current_users - config.step_users,
                start_time=datetime.now()
            )
            
            hold_metrics = await self._execute_load_step_async(current_users - config.step_users, config.hold_duration_seconds)
            
            hold_step.end_time = datetime.now()
            hold_step.duration_ms = (hold_step.end_time - hold_step.start_time).total_seconds() * 1000
            hold_step.requests_total = hold_metrics["requests_total"]
            hold_step.requests_successful = hold_metrics["requests_successful"]
            hold_step.requests_failed = hold_metrics["requests_failed"]
            hold_step.avg_response_time_ms = hold_metrics["avg_response_time_ms"]
            hold_step.throughput_rps = hold_metrics["throughput_rps"]
            hold_step.error_rate_percent = hold_metrics["error_rate_percent"]
            
            self.load_steps.append(hold_step)
            
            # Acumular métricas
            all_response_times.extend(hold_metrics["response_times"])
            total_requests += hold_metrics["requests_total"]
            total_successful += hold_metrics["requests_successful"]
            total_failed += hold_metrics["requests_failed"]
        
        # Calcular métricas finais (mesmo código do método síncrono)
        end_time = datetime.now()
        duration_ms = (end_time - start_time).total_seconds() * 1000
        
        if all_response_times:
            all_response_times.sort()
            avg_response_time = statistics.mean(all_response_times)
            min_response_time = min(all_response_times)
            max_response_time = max(all_response_times)
            p50_response_time = all_response_times[len(all_response_times) // 2]
            p95_response_time = all_response_times[int(len(all_response_times) * 0.95)]
            p99_response_time = all_response_times[int(len(all_response_times) * 0.99)]
        else:
            avg_response_time = min_response_time = max_response_time = 0.0
            p50_response_time = p95_response_time = p99_response_time = 0.0
        
        throughput_rps = total_requests / (duration_ms / 1000) if duration_ms > 0 else 0.0
        error_rate = (total_failed / total_requests * 100) if total_requests > 0 else 0.0
        
        # Obter métricas do sistema
        system_metrics = performance_monitor.get_current_metrics()
        
        return PerformanceMetrics(
            test_name=config.test_name,
            test_type=TestType.LOAD,
            start_time=start_time,
            end_time=end_time,
            duration_ms=duration_ms,
            requests_total=total_requests,
            requests_successful=total_successful,
            requests_failed=total_failed,
            requests_timeout=0,  # Não aplicável para carga
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
            concurrent_users=config.max_users,
            test_config=config.to_dict()
        )
    
    def _execute_load_step(self, users: int, duration_seconds: int) -> Dict[str, Any]:
        """Executa um passo de carga"""
        start_time = time.time()
        response_times = []
        successful_requests = 0
        failed_requests = 0
        
        # Calcular distribuição de cenários
        scenario_weights = [s["weight"] for s in self.default_scenarios.values()]
        total_weight = sum(scenario_weights)
        scenario_probabilities = [w / total_weight for w in scenario_weights]
        
        # Executar requisições durante a duração
        while time.time() - start_time < duration_seconds:
            # Criar threads para usuários concorrentes
            threads = []
            for _ in range(users):
                # Selecionar cenário baseado em probabilidade
                scenario_name = random.choices(list(self.default_scenarios.keys()), weights=scenario_probabilities)[0]
                scenario = self.default_scenarios[scenario_name]
                
                thread = threading.Thread(
                    target=self._execute_single_request,
                    args=(scenario["function"], response_times, successful_requests, failed_requests)
                )
                threads.append(thread)
                thread.start()
            
            # Aguardar conclusão
            for thread in threads:
                thread.join(timeout=5)  # Timeout reduzido para 5 segundos
        
        # Calcular métricas do passo
        step_duration_ms = (time.time() - start_time) * 1000
        total_requests = successful_requests + failed_requests
        avg_response_time = statistics.mean(response_times) if response_times else 0.0
        throughput_rps = total_requests / (step_duration_ms / 1000) if step_duration_ms > 0 else 0.0
        error_rate = (failed_requests / total_requests * 100) if total_requests > 0 else 0.0
        
        return {
            "requests_total": total_requests,
            "requests_successful": successful_requests,
            "requests_failed": failed_requests,
            "avg_response_time_ms": avg_response_time,
            "throughput_rps": throughput_rps,
            "error_rate_percent": error_rate,
            "response_times": response_times
        }
    
    async def _execute_load_step_async(self, users: int, duration_seconds: int) -> Dict[str, Any]:
        """Executa um passo de carga assíncrono"""
        start_time = time.time()
        response_times = []
        successful_requests = 0
        failed_requests = 0
        
        # Calcular distribuição de cenários
        scenario_weights = [s["weight"] for s in self.default_scenarios.values()]
        total_weight = sum(scenario_weights)
        scenario_probabilities = [w / total_weight for w in scenario_weights]
        
        # Executar requisições durante a duração
        while time.time() - start_time < duration_seconds:
            # Criar tarefas assíncronas para usuários concorrentes
            tasks = []
            for _ in range(users):
                # Selecionar cenário baseado em probabilidade
                scenario_name = random.choices(list(self.default_scenarios.keys()), weights=scenario_probabilities)[0]
                scenario = self.default_scenarios[scenario_name]
                
                task = asyncio.create_task(
                    self._execute_single_request_async(scenario["async_function"], response_times, successful_requests, failed_requests)
                )
                tasks.append(task)
            
            # Aguardar conclusão
            await asyncio.gather(*tasks, return_exceptions=True)
        
        # Calcular métricas do passo
        step_duration_ms = (time.time() - start_time) * 1000
        total_requests = successful_requests + failed_requests
        avg_response_time = statistics.mean(response_times) if response_times else 0.0
        throughput_rps = total_requests / (step_duration_ms / 1000) if step_duration_ms > 0 else 0.0
        error_rate = (failed_requests / total_requests * 100) if total_requests > 0 else 0.0
        
        return {
            "requests_total": total_requests,
            "requests_successful": successful_requests,
            "requests_failed": failed_requests,
            "avg_response_time_ms": avg_response_time,
            "throughput_rps": throughput_rps,
            "error_rate_percent": error_rate,
            "response_times": response_times
        }
    
    def _execute_single_request(self, request_func: Callable, response_times: List[float],
                              successful_requests: int, failed_requests: int) -> None:
        """Executa uma única requisição"""
        start_time = time.time()
        
        try:
            request_func()
            
            duration_ms = (time.time() - start_time) * 1000
            response_times.append(duration_ms)
            successful_requests += 1
            
            # Registrar no monitor de performance
            performance_monitor.record_response_time(duration_ms, success=True)
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            response_times.append(duration_ms)
            failed_requests += 1
            
            # Registrar no monitor de performance
            performance_monitor.record_response_time(duration_ms, success=False, error_message=str(e))
    
    async def _execute_single_request_async(self, request_func: Callable, response_times: List[float],
                                          successful_requests: int, failed_requests: int) -> None:
        """Executa uma única requisição assíncrona"""
        start_time = time.time()
        
        try:
            await request_func()
            
            duration_ms = (time.time() - start_time) * 1000
            response_times.append(duration_ms)
            successful_requests += 1
            
            # Registrar no monitor de performance
            performance_monitor.record_response_time(duration_ms, success=True)
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            response_times.append(duration_ms)
            failed_requests += 1
            
            # Registrar no monitor de performance
            performance_monitor.record_response_time(duration_ms, success=False, error_message=str(e))
    
    # Funções de simulação de requisições
    def _simulate_scraping_request(self) -> None:
        """Simula requisição de scraping"""
        delay = random.uniform(0.1, 2.0)
        time.sleep(delay)
        
        # Simular falha ocasional
        if random.random() < 0.05:
            raise Exception("Erro de scraping simulado")
    
    async def _simulate_scraping_request_async(self) -> None:
        """Simula requisição de scraping assíncrona"""
        delay = random.uniform(0.1, 2.0)
        await asyncio.sleep(delay)
        
        # Simular falha ocasional
        if random.random() < 0.05:
            raise Exception("Erro de scraping simulado")
    
    def _simulate_processing_request(self) -> None:
        """Simula requisição de processamento"""
        delay = random.uniform(0.1, 1.0)
        time.sleep(delay)
        
        # Simular falha ocasional
        if random.random() < 0.02:
            raise Exception("Erro de processamento simulado")
    
    async def _simulate_processing_request_async(self) -> None:
        """Simula requisição de processamento assíncrona"""
        delay = random.uniform(0.1, 1.0)
        await asyncio.sleep(delay)
        
        # Simular falha ocasional
        if random.random() < 0.02:
            raise Exception("Erro de processamento simulado")
    
    def _simulate_posting_request(self) -> None:
        """Simula requisição de posting"""
        delay = random.uniform(0.2, 1.5)
        time.sleep(delay)
        
        # Simular falha ocasional
        if random.random() < 0.03:
            raise Exception("Erro de posting simulado")
    
    async def _simulate_posting_request_async(self) -> None:
        """Simula requisição de posting assíncrona"""
        delay = random.uniform(0.2, 1.5)
        await asyncio.sleep(delay)
        
        # Simular falha ocasional
        if random.random() < 0.03:
            raise Exception("Erro de posting simulado")
    
    def _simulate_validation_request(self) -> None:
        """Simula requisição de validação"""
        delay = random.uniform(0.01, 0.2)
        time.sleep(delay)
        
        # Simular falha ocasional
        if random.random() < 0.01:
            raise Exception("Erro de validação simulado")
    
    async def _simulate_validation_request_async(self) -> None:
        """Simula requisição de validação assíncrona"""
        delay = random.uniform(0.01, 0.2)
        await asyncio.sleep(delay)
        
        # Simular falha ocasional
        if random.random() < 0.01:
            raise Exception("Erro de validação simulado")
    
    def get_load_statistics(self) -> Dict[str, Any]:
        """Obtém estatísticas dos passos de carga"""
        if not self.load_steps:
            return {
                "total_steps": 0,
                "max_users_reached": 0,
                "total_requests": 0,
                "avg_throughput_rps": 0.0,
                "avg_error_rate_percent": 0.0,
                "steps": []
            }
        
        # Estatísticas gerais
        total_steps = len(self.load_steps)
        max_users = max(step.users for step in self.load_steps) if self.load_steps else 0
        total_requests = sum(step.requests_total for step in self.load_steps)
        
        # Médias
        avg_throughput = statistics.mean([step.throughput_rps for step in self.load_steps if step.throughput_rps > 0])
        avg_error_rate = statistics.mean([step.error_rate_percent for step in self.load_steps])
        
        return {
            "total_steps": total_steps,
            "max_users_reached": max_users,
            "total_requests": total_requests,
            "avg_throughput_rps": avg_throughput,
            "avg_error_rate_percent": avg_error_rate,
            "steps": [
                {
                    "step_number": step.step_number,
                    "users": step.users,
                    "duration_ms": step.duration_ms,
                    "requests_total": step.requests_total,
                    "requests_successful": step.requests_successful,
                    "requests_failed": step.requests_failed,
                    "avg_response_time_ms": step.avg_response_time_ms,
                    "throughput_rps": step.throughput_rps,
                    "error_rate_percent": step.error_rate_percent
                }
                for step in self.load_steps
            ]
        }
    
    def get_test_history(self) -> List[TestResult]:
        """Obtém histórico de testes"""
        return self.test_history.copy()
    
    def get_active_tests(self) -> Dict[str, TestResult]:
        """Obtém testes ativos"""
        return self.active_tests.copy()
    
    def clear_history(self) -> None:
        """Limpa histórico de testes e passos"""
        self.test_history.clear()
        self.load_steps.clear()
        self.logger.info("Histórico de testes e passos de carga limpo")
