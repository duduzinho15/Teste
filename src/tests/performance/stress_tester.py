"""
Testador de Stress
Sistema de Recomendações de Ofertas - Garimpeiro Geek
"""

import asyncio
import time
import random
import threading
from typing import Dict, List, Optional, Callable, Any, Coroutine
from datetime import datetime, timedelta
from dataclasses import dataclass
import logging
import statistics

from .models import (
    TestType, TestStatus, PerformanceMetrics, StressTestConfig, 
    TestResult, PerformanceReport
)
from .performance_monitor import performance_monitor


@dataclass
class StressTestScenario:
    """Cenário de teste de stress"""
    name: str
    weight: float = 1.0  # Peso para distribuição de carga
    target_function: Optional[Callable] = None
    async_target_function: Optional[Callable] = None
    parameters: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.parameters is None:
            self.parameters = {}


class StressTester:
    """Testador de stress para o sistema"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.active_tests: Dict[str, TestResult] = {}
        self.test_history: List[TestResult] = []
        self.scenarios: Dict[str, StressTestScenario] = {}
        
        # Configurar cenários padrão
        self._setup_default_scenarios()
    
    def _setup_default_scenarios(self) -> None:
        """Configura cenários padrão de teste"""
        # Cenário 1: Teste de scraping
        self.add_scenario(StressTestScenario(
            name="scraping_test",
            weight=0.4,
            target_function=self._simulate_scraping,
            parameters={"delay_range": (0.1, 2.0)}
        ))
        
        # Cenário 2: Teste de processamento
        self.add_scenario(StressTestScenario(
            name="processing_test", 
            weight=0.3,
            target_function=self._simulate_processing,
            parameters={"complexity": "medium"}
        ))
        
        # Cenário 3: Teste de posting
        self.add_scenario(StressTestScenario(
            name="posting_test",
            weight=0.2,
            target_function=self._simulate_posting,
            parameters={"message_size": "large"}
        ))
        
        # Cenário 4: Teste de validação
        self.add_scenario(StressTestScenario(
            name="validation_test",
            weight=0.1,
            target_function=self._simulate_validation,
            parameters={"strict_mode": True}
        ))
    
    def add_scenario(self, scenario: StressTestScenario) -> None:
        """Adiciona um cenário de teste"""
        self.scenarios[scenario.name] = scenario
        self.logger.info(f"Cenário adicionado: {scenario.name} (peso: {scenario.weight})")
    
    def remove_scenario(self, scenario_name: str) -> None:
        """Remove um cenário de teste"""
        if scenario_name in self.scenarios:
            del self.scenarios[scenario_name]
            self.logger.info(f"Cenário removido: {scenario_name}")
    
    def run_stress_test(self, config: StressTestConfig) -> TestResult:
        """Executa um teste de stress"""
        test_id = f"stress_{int(time.time())}"
        test_result = TestResult(
            test_id=test_id,
            test_name=config.test_name,
            test_type=TestType.STRESS,
            status=TestStatus.RUNNING,
            start_time=datetime.now(),
            config=config.to_dict()
        )
        
        self.active_tests[test_id] = test_result
        self.logger.info(f"Iniciando teste de stress: {config.test_name}")
        
        try:
            # Iniciar monitoramento
            performance_monitor.start_monitoring(interval_seconds=0.5)
            
            # Executar teste
            metrics = self._execute_stress_test(config)
            
            # Finalizar teste
            test_result.end_time = datetime.now()
            test_result.duration_ms = (test_result.end_time - test_result.start_time).total_seconds() * 1000
            test_result.metrics = metrics
            test_result.status = TestStatus.COMPLETED
            
            # Parar monitoramento
            performance_monitor.stop_monitoring()
            
            self.logger.info(f"Teste de stress concluído: {config.test_name}")
            
        except Exception as e:
            test_result.status = TestStatus.FAILED
            test_result.errors.append(str(e))
            test_result.end_time = datetime.now()
            performance_monitor.stop_monitoring()
            self.logger.error(f"Erro no teste de stress: {e}")
        
        # Adicionar ao histórico
        self.test_history.append(test_result)
        del self.active_tests[test_id]
        
        return test_result
    
    async def run_stress_test_async(self, config: StressTestConfig) -> TestResult:
        """Executa um teste de stress assíncrono"""
        test_id = f"stress_async_{int(time.time())}"
        test_result = TestResult(
            test_id=test_id,
            test_name=config.test_name,
            test_type=TestType.STRESS,
            status=TestStatus.RUNNING,
            start_time=datetime.now(),
            config=config.to_dict()
        )
        
        self.active_tests[test_id] = test_result
        self.logger.info(f"Iniciando teste de stress assíncrono: {config.test_name}")
        
        try:
            # Iniciar monitoramento
            performance_monitor.start_monitoring(interval_seconds=0.5)
            
            # Executar teste assíncrono
            metrics = await self._execute_stress_test_async(config)
            
            # Finalizar teste
            test_result.end_time = datetime.now()
            test_result.duration_ms = (test_result.end_time - test_result.start_time).total_seconds() * 1000
            test_result.metrics = metrics
            test_result.status = TestStatus.COMPLETED
            
            # Parar monitoramento
            performance_monitor.stop_monitoring()
            
            self.logger.info(f"Teste de stress assíncrono concluído: {config.test_name}")
            
        except Exception as e:
            test_result.status = TestStatus.FAILED
            test_result.errors.append(str(e))
            test_result.end_time = datetime.now()
            performance_monitor.stop_monitoring()
            self.logger.error(f"Erro no teste de stress assíncrono: {e}")
        
        # Adicionar ao histórico
        self.test_history.append(test_result)
        del self.active_tests[test_id]
        
        return test_result
    
    def _execute_stress_test(self, config: StressTestConfig) -> PerformanceMetrics:
        """Executa o teste de stress"""
        start_time = datetime.now()
        response_times = []
        successful_requests = 0
        failed_requests = 0
        timeout_requests = 0
        
        # Calcular distribuição de cenários
        scenario_weights = [s.weight for s in self.scenarios.values()]
        total_weight = sum(scenario_weights)
        scenario_probabilities = [w / total_weight for w in scenario_weights]
        
        # Ramp-up
        self.logger.info(f"Iniciando ramp-up de {config.ramp_up_seconds} segundos")
        ramp_up_start = time.time()
        
        while time.time() - ramp_up_start < config.ramp_up_seconds:
            current_users = int((time.time() - ramp_up_start) / config.ramp_up_seconds * config.concurrent_users)
            if current_users > 0:
                self._execute_concurrent_requests(current_users, scenario_probabilities, response_times, 
                                                successful_requests, failed_requests, timeout_requests)
            time.sleep(0.1)
        
        # Teste principal
        self.logger.info(f"Iniciando teste principal de {config.duration_seconds} segundos")
        test_start = time.time()
        
        while time.time() - test_start < config.duration_seconds:
            self._execute_concurrent_requests(config.concurrent_users, scenario_probabilities, response_times,
                                            successful_requests, failed_requests, timeout_requests)
            
            # Verificar limites
            if config.memory_limit_mb:
                current_memory = performance_monitor.get_current_metrics().memory_used_mb
                if current_memory > config.memory_limit_mb:
                    self.logger.warning(f"Limite de memória atingido: {current_memory:.2f}MB")
                    break
            
            if config.cpu_limit_percent:
                current_cpu = performance_monitor.get_current_metrics().cpu_percent
                if current_cpu > config.cpu_limit_percent:
                    self.logger.warning(f"Limite de CPU atingido: {current_cpu:.2f}%")
                    break
        
        # Ramp-down
        self.logger.info(f"Iniciando ramp-down de {config.ramp_down_seconds} segundos")
        ramp_down_start = time.time()
        
        while time.time() - ramp_down_start < config.ramp_down_seconds:
            remaining_users = int((1 - (time.time() - ramp_down_start) / config.ramp_down_seconds) * config.concurrent_users)
            if remaining_users > 0:
                self._execute_concurrent_requests(remaining_users, scenario_probabilities, response_times,
                                                successful_requests, failed_requests, timeout_requests)
            time.sleep(0.1)
        
        # Calcular métricas
        end_time = datetime.now()
        duration_ms = (end_time - start_time).total_seconds() * 1000
        
        if response_times:
            response_times.sort()
            avg_response_time = statistics.mean(response_times)
            min_response_time = min(response_times)
            max_response_time = max(response_times)
            p50_response_time = response_times[len(response_times) // 2]
            p95_response_time = response_times[int(len(response_times) * 0.95)]
            p99_response_time = response_times[int(len(response_times) * 0.99)]
        else:
            avg_response_time = min_response_time = max_response_time = 0.0
            p50_response_time = p95_response_time = p99_response_time = 0.0
        
        total_requests = successful_requests + failed_requests + timeout_requests
        throughput_rps = total_requests / (duration_ms / 1000) if duration_ms > 0 else 0.0
        error_rate = ((failed_requests + timeout_requests) / total_requests * 100) if total_requests > 0 else 0.0
        
        # Obter métricas do sistema
        system_metrics = performance_monitor.get_current_metrics()
        
        return PerformanceMetrics(
            test_name=config.test_name,
            test_type=TestType.STRESS,
            start_time=start_time,
            end_time=end_time,
            duration_ms=duration_ms,
            requests_total=total_requests,
            requests_successful=successful_requests,
            requests_failed=failed_requests,
            requests_timeout=timeout_requests,
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
            concurrent_users=config.concurrent_users,
            test_config=config.to_dict()
        )
    
    async def _execute_stress_test_async(self, config: StressTestConfig) -> PerformanceMetrics:
        """Executa o teste de stress assíncrono"""
        start_time = datetime.now()
        response_times = []
        successful_requests = 0
        failed_requests = 0
        timeout_requests = 0
        
        # Calcular distribuição de cenários
        scenario_weights = [s.weight for s in self.scenarios.values()]
        total_weight = sum(scenario_weights)
        scenario_probabilities = [w / total_weight for w in scenario_weights]
        
        # Ramp-up
        self.logger.info(f"Iniciando ramp-up assíncrono de {config.ramp_up_seconds} segundos")
        ramp_up_start = time.time()
        
        while time.time() - ramp_up_start < config.ramp_up_seconds:
            current_users = int((time.time() - ramp_up_start) / config.ramp_up_seconds * config.concurrent_users)
            if current_users > 0:
                await self._execute_concurrent_requests_async(current_users, scenario_probabilities, response_times,
                                                            successful_requests, failed_requests, timeout_requests)
            await asyncio.sleep(0.1)
        
        # Teste principal
        self.logger.info(f"Iniciando teste principal assíncrono de {config.duration_seconds} segundos")
        test_start = time.time()
        
        while time.time() - test_start < config.duration_seconds:
            await self._execute_concurrent_requests_async(config.concurrent_users, scenario_probabilities, response_times,
                                                        successful_requests, failed_requests, timeout_requests)
            
            # Verificar limites
            if config.memory_limit_mb:
                current_memory = performance_monitor.get_current_metrics().memory_used_mb
                if current_memory > config.memory_limit_mb:
                    self.logger.warning(f"Limite de memória atingido: {current_memory:.2f}MB")
                    break
            
            if config.cpu_limit_percent:
                current_cpu = performance_monitor.get_current_metrics().cpu_percent
                if current_cpu > config.cpu_limit_percent:
                    self.logger.warning(f"Limite de CPU atingido: {current_cpu:.2f}%")
                    break
        
        # Ramp-down
        self.logger.info(f"Iniciando ramp-down assíncrono de {config.ramp_down_seconds} segundos")
        ramp_down_start = time.time()
        
        while time.time() - ramp_down_start < config.ramp_down_seconds:
            remaining_users = int((1 - (time.time() - ramp_down_start) / config.ramp_down_seconds) * config.concurrent_users)
            if remaining_users > 0:
                await self._execute_concurrent_requests_async(remaining_users, scenario_probabilities, response_times,
                                                            successful_requests, failed_requests, timeout_requests)
            await asyncio.sleep(0.1)
        
        # Calcular métricas (mesmo código do método síncrono)
        end_time = datetime.now()
        duration_ms = (end_time - start_time).total_seconds() * 1000
        
        if response_times:
            response_times.sort()
            avg_response_time = statistics.mean(response_times)
            min_response_time = min(response_times)
            max_response_time = max(response_times)
            p50_response_time = response_times[len(response_times) // 2]
            p95_response_time = response_times[int(len(response_times) * 0.95)]
            p99_response_time = response_times[int(len(response_times) * 0.99)]
        else:
            avg_response_time = min_response_time = max_response_time = 0.0
            p50_response_time = p95_response_time = p99_response_time = 0.0
        
        total_requests = successful_requests + failed_requests + timeout_requests
        throughput_rps = total_requests / (duration_ms / 1000) if duration_ms > 0 else 0.0
        error_rate = ((failed_requests + timeout_requests) / total_requests * 100) if total_requests > 0 else 0.0
        
        # Obter métricas do sistema
        system_metrics = performance_monitor.get_current_metrics()
        
        return PerformanceMetrics(
            test_name=config.test_name,
            test_type=TestType.STRESS,
            start_time=start_time,
            end_time=end_time,
            duration_ms=duration_ms,
            requests_total=total_requests,
            requests_successful=successful_requests,
            requests_failed=failed_requests,
            requests_timeout=timeout_requests,
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
            concurrent_users=config.concurrent_users,
            test_config=config.to_dict()
        )
    
    def _execute_concurrent_requests(self, num_users: int, scenario_probabilities: List[float],
                                   response_times: List[float], successful_requests: int, 
                                   failed_requests: int, timeout_requests: int) -> None:
        """Executa requisições concorrentes"""
        threads = []
        
        for _ in range(num_users):
            # Selecionar cenário baseado em probabilidade
            scenario_name = random.choices(list(self.scenarios.keys()), weights=scenario_probabilities)[0]
            scenario = self.scenarios[scenario_name]
            
            thread = threading.Thread(
                target=self._execute_single_request,
                args=(scenario, response_times, successful_requests, failed_requests, timeout_requests)
            )
            threads.append(thread)
            thread.start()
        
        # Aguardar conclusão
        for thread in threads:
            thread.join(timeout=30)  # Timeout de 30 segundos
    
    async def _execute_concurrent_requests_async(self, num_users: int, scenario_probabilities: List[float],
                                               response_times: List[float], successful_requests: int,
                                               failed_requests: int, timeout_requests: int) -> None:
        """Executa requisições concorrentes assíncronas"""
        tasks = []
        
        for _ in range(num_users):
            # Selecionar cenário baseado em probabilidade
            scenario_name = random.choices(list(self.scenarios.keys()), weights=scenario_probabilities)[0]
            scenario = self.scenarios[scenario_name]
            
            task = asyncio.create_task(
                self._execute_single_request_async(scenario, response_times, successful_requests, 
                                                 failed_requests, timeout_requests)
            )
            tasks.append(task)
        
        # Aguardar conclusão
        await asyncio.gather(*tasks, return_exceptions=True)
    
    def _execute_single_request(self, scenario: StressTestScenario, response_times: List[float],
                              successful_requests: int, failed_requests: int, timeout_requests: int) -> None:
        """Executa uma única requisição"""
        start_time = time.time()
        
        try:
            if scenario.target_function:
                scenario.target_function(**scenario.parameters)
            
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
    
    async def _execute_single_request_async(self, scenario: StressTestScenario, response_times: List[float],
                                          successful_requests: int, failed_requests: int, timeout_requests: int) -> None:
        """Executa uma única requisição assíncrona"""
        start_time = time.time()
        
        try:
            if scenario.async_target_function:
                await scenario.async_target_function(**scenario.parameters)
            elif scenario.target_function:
                # Executar função síncrona em thread separada
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, scenario.target_function, **scenario.parameters)
            
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
    
    # Funções de simulação
    def _simulate_scraping(self, delay_range: tuple = (0.1, 2.0)) -> None:
        """Simula operação de scraping"""
        delay = random.uniform(*delay_range)
        time.sleep(delay)
        
        # Simular falha ocasional
        if random.random() < 0.05:  # 5% de chance de falha
            raise Exception("Erro de scraping simulado")
    
    def _simulate_processing(self, complexity: str = "medium") -> None:
        """Simula processamento de dados"""
        if complexity == "low":
            delay = random.uniform(0.01, 0.1)
        elif complexity == "medium":
            delay = random.uniform(0.1, 0.5)
        else:  # high
            delay = random.uniform(0.5, 2.0)
        
        time.sleep(delay)
        
        # Simular falha ocasional
        if random.random() < 0.02:  # 2% de chance de falha
            raise Exception("Erro de processamento simulado")
    
    def _simulate_posting(self, message_size: str = "medium") -> None:
        """Simula posting de mensagens"""
        if message_size == "small":
            delay = random.uniform(0.05, 0.2)
        elif message_size == "medium":
            delay = random.uniform(0.2, 0.8)
        else:  # large
            delay = random.uniform(0.8, 3.0)
        
        time.sleep(delay)
        
        # Simular falha ocasional
        if random.random() < 0.03:  # 3% de chance de falha
            raise Exception("Erro de posting simulado")
    
    def _simulate_validation(self, strict_mode: bool = False) -> None:
        """Simula validação de dados"""
        delay = random.uniform(0.01, 0.1)
        if strict_mode:
            delay *= 2  # Validação mais rigorosa leva mais tempo
        
        time.sleep(delay)
        
        # Simular falha ocasional
        if random.random() < 0.01:  # 1% de chance de falha
            raise Exception("Erro de validação simulado")
    
    def get_test_history(self) -> List[TestResult]:
        """Obtém histórico de testes"""
        return self.test_history.copy()
    
    def get_active_tests(self) -> Dict[str, TestResult]:
        """Obtém testes ativos"""
        return self.active_tests.copy()
    
    def clear_history(self) -> None:
        """Limpa histórico de testes"""
        self.test_history.clear()
        self.logger.info("Histórico de testes limpo")
    
    def generate_report(self, test_results: List[TestResult]) -> PerformanceReport:
        """Gera relatório de performance"""
        if not test_results:
            raise ValueError("Nenhum resultado de teste fornecido")
        
        # Calcular estatísticas gerais
        total_tests = len(test_results)
        successful_tests = len([t for t in test_results if t.status == TestStatus.COMPLETED])
        failed_tests = len([t for t in test_results if t.status == TestStatus.FAILED])
        
        avg_duration = statistics.mean([t.duration_ms for t in test_results if t.duration_ms]) if test_results else 0.0
        
        # Métricas de performance agregadas
        all_metrics = [t.metrics for t in test_results if t.metrics]
        if all_metrics:
            avg_throughput = statistics.mean([m.throughput_rps for m in all_metrics])
            avg_response_time = statistics.mean([m.avg_response_time_ms for m in all_metrics])
            avg_error_rate = statistics.mean([m.error_rate_percent for m in all_metrics])
        else:
            avg_throughput = avg_response_time = avg_error_rate = 0.0
        
        summary = {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "failed_tests": failed_tests,
            "success_rate": (successful_tests / total_tests * 100) if total_tests > 0 else 0.0,
            "avg_duration_ms": avg_duration,
            "avg_throughput_rps": avg_throughput,
            "avg_response_time_ms": avg_response_time,
            "avg_error_rate_percent": avg_error_rate
        }
        
        # Gerar recomendações
        recommendations = []
        
        if avg_error_rate > 5.0:
            recommendations.append("Taxa de erro alta detectada. Verificar logs e otimizar tratamento de erros.")
        
        if avg_response_time > 2000:
            recommendations.append("Tempo de resposta alto. Considerar otimizações de performance.")
        
        if avg_throughput < 10:
            recommendations.append("Throughput baixo. Verificar gargalos no sistema.")
        
        if failed_tests > 0:
            recommendations.append(f"{failed_tests} testes falharam. Revisar configurações e logs.")
        
        report = PerformanceReport(
            report_id=f"report_{int(time.time())}",
            timestamp=datetime.now(),
            test_results=test_results,
            summary=summary,
            recommendations=recommendations
        )
        
        return report
