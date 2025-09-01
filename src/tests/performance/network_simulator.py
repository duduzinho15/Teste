"""
Simulador de Rede
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
import socket
import select

from .models import (
    TestType, TestStatus, PerformanceMetrics, NetworkTestConfig, 
    TestResult
)
from .performance_monitor import performance_monitor


@dataclass
class NetworkCondition:
    """Condição de rede simulada"""
    latency_ms: int
    jitter_ms: int
    packet_loss_percent: float
    bandwidth_mbps: Optional[float]
    connection_drops: bool
    drop_interval_seconds: int


class NetworkSimulator:
    """Simulador de condições de rede para testes"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.active_tests: Dict[str, TestResult] = {}
        self.test_history: List[TestResult] = []
        self.network_conditions: List[NetworkCondition] = []
        
        # Configurações atuais
        self.current_condition: Optional[NetworkCondition] = None
        self.simulation_active = False
        self.simulation_thread: Optional[threading.Thread] = None
        
        # Callbacks para interceptação de rede
        self.original_socket_connect = socket.socket.connect
        self.original_socket_send = socket.socket.send
        self.original_socket_recv = socket.socket.recv
        
        # Estatísticas
        self.packets_sent = 0
        self.packets_received = 0
        self.packets_dropped = 0
        self.connections_dropped = 0
    
    def start_network_simulation(self, config: NetworkTestConfig) -> None:
        """Inicia simulação de rede"""
        if self.simulation_active:
            self.logger.warning("Simulação de rede já está ativa")
            return
        
        # Criar condição de rede
        condition = NetworkCondition(
            latency_ms=config.latency_ms,
            jitter_ms=config.jitter_ms,
            packet_loss_percent=config.packet_loss_percent,
            bandwidth_mbps=config.bandwidth_mbps,
            connection_drops=config.connection_drops,
            drop_interval_seconds=config.drop_interval_seconds
        )
        
        self.current_condition = condition
        self.simulation_active = True
        
        # Iniciar thread de simulação
        self.simulation_thread = threading.Thread(
            target=self._simulation_loop,
            args=(config.duration_seconds,),
            daemon=True
        )
        self.simulation_thread.start()
        
        # Interceptar chamadas de socket
        self._install_socket_interceptors()
        
        self.logger.info(f"Simulação de rede iniciada: {config.latency_ms}ms latência, "
                        f"{config.packet_loss_percent}% perda de pacotes")
    
    def stop_network_simulation(self) -> None:
        """Para simulação de rede"""
        self.simulation_active = False
        if self.simulation_thread:
            self.simulation_thread.join(timeout=5.0)
        
        # Remover interceptadores
        self._remove_socket_interceptors()
        
        self.current_condition = None
        self.logger.info("Simulação de rede parada")
    
    def _simulation_loop(self, duration_seconds: int) -> None:
        """Loop principal de simulação"""
        start_time = time.time()
        
        while self.simulation_active and (time.time() - start_time) < duration_seconds:
            try:
                # Simular quedas de conexão
                if self.current_condition and self.current_condition.connection_drops:
                    if random.random() < 0.1:  # 10% de chance a cada iteração
                        self._simulate_connection_drop()
                
                time.sleep(1.0)
            except Exception as e:
                self.logger.error(f"Erro na simulação de rede: {e}")
                time.sleep(1.0)
    
    def _install_socket_interceptors(self) -> None:
        """Instala interceptadores de socket"""
        def intercepted_connect(self_socket, address):
            # Simular latência na conexão
            if self.current_condition:
                latency = self.current_condition.latency_ms + random.randint(-self.current_condition.jitter_ms, self.current_condition.jitter_ms)
                time.sleep(latency / 1000.0)
            
            return self.original_socket_connect(self_socket, address)
        
        def intercepted_send(self_socket, data):
            # Simular perda de pacotes
            if self.current_condition and random.random() < (self.current_condition.packet_loss_percent / 100.0):
                self.packets_dropped += 1
                raise ConnectionError("Simulated packet loss")
            
            self.packets_sent += 1
            
            # Simular latência no envio
            if self.current_condition:
                latency = self.current_condition.latency_ms + random.randint(-self.current_condition.jitter_ms, self.current_condition.jitter_ms)
                time.sleep(latency / 1000.0)
            
            return self.original_socket_send(self_socket, data)
        
        def intercepted_recv(self_socket, bufsize):
            # Simular perda de pacotes
            if self.current_condition and random.random() < (self.current_condition.packet_loss_percent / 100.0):
                self.packets_dropped += 1
                raise ConnectionError("Simulated packet loss")
            
            self.packets_received += 1
            
            # Simular latência na recepção
            if self.current_condition:
                latency = self.current_condition.latency_ms + random.randint(-self.current_condition.jitter_ms, self.current_condition.jitter_ms)
                time.sleep(latency / 1000.0)
            
            return self.original_socket_recv(self_socket, bufsize)
        
        # Substituir métodos
        socket.socket.connect = intercepted_connect
        socket.socket.send = intercepted_send
        socket.socket.recv = intercepted_recv
    
    def _remove_socket_interceptors(self) -> None:
        """Remove interceptadores de socket"""
        socket.socket.connect = self.original_socket_connect
        socket.socket.send = self.original_socket_send
        socket.socket.recv = self.original_socket_recv
    
    def _simulate_connection_drop(self) -> None:
        """Simula queda de conexão"""
        self.connections_dropped += 1
        self.logger.warning("Simulação de queda de conexão")
    
    def run_network_test(self, config: NetworkTestConfig) -> TestResult:
        """Executa um teste de rede"""
        test_id = f"network_{int(time.time())}"
        test_result = TestResult(
            test_id=test_id,
            test_name=config.test_name,
            test_type=TestType.NETWORK,
            status=TestStatus.RUNNING,
            start_time=datetime.now(),
            config=config.to_dict()
        )
        
        self.active_tests[test_id] = test_result
        self.logger.info(f"Iniciando teste de rede: {config.test_name}")
        
        try:
            # Iniciar monitoramento
            performance_monitor.start_monitoring(interval_seconds=0.5)
            
            # Iniciar simulação de rede
            self.start_network_simulation(config)
            
            # Executar teste
            metrics = self._execute_network_test(config)
            
            # Finalizar teste
            test_result.end_time = datetime.now()
            test_result.duration_ms = (test_result.end_time - test_result.start_time).total_seconds() * 1000
            test_result.metrics = metrics
            test_result.status = TestStatus.COMPLETED
            
            # Parar simulação e monitoramento
            self.stop_network_simulation()
            performance_monitor.stop_monitoring()
            
            self.logger.info(f"Teste de rede concluído: {config.test_name}")
            
        except Exception as e:
            test_result.status = TestStatus.FAILED
            test_result.errors.append(str(e))
            test_result.end_time = datetime.now()
            self.stop_network_simulation()
            performance_monitor.stop_monitoring()
            self.logger.error(f"Erro no teste de rede: {e}")
        
        # Adicionar ao histórico
        self.test_history.append(test_result)
        del self.active_tests[test_id]
        
        return test_result
    
    async def run_network_test_async(self, config: NetworkTestConfig) -> TestResult:
        """Executa um teste de rede assíncrono"""
        test_id = f"network_async_{int(time.time())}"
        test_result = TestResult(
            test_id=test_id,
            test_name=config.test_name,
            test_type=TestType.NETWORK,
            status=TestStatus.RUNNING,
            start_time=datetime.now(),
            config=config.to_dict()
        )
        
        self.active_tests[test_id] = test_result
        self.logger.info(f"Iniciando teste de rede assíncrono: {config.test_name}")
        
        try:
            # Iniciar monitoramento
            performance_monitor.start_monitoring(interval_seconds=0.5)
            
            # Iniciar simulação de rede
            self.start_network_simulation(config)
            
            # Executar teste assíncrono
            metrics = await self._execute_network_test_async(config)
            
            # Finalizar teste
            test_result.end_time = datetime.now()
            test_result.duration_ms = (test_result.end_time - test_result.start_time).total_seconds() * 1000
            test_result.metrics = metrics
            test_result.status = TestStatus.COMPLETED
            
            # Parar simulação e monitoramento
            self.stop_network_simulation()
            performance_monitor.stop_monitoring()
            
            self.logger.info(f"Teste de rede assíncrono concluído: {config.test_name}")
            
        except Exception as e:
            test_result.status = TestStatus.FAILED
            test_result.errors.append(str(e))
            test_result.end_time = datetime.now()
            self.stop_network_simulation()
            performance_monitor.stop_monitoring()
            self.logger.error(f"Erro no teste de rede assíncrono: {e}")
        
        # Adicionar ao histórico
        self.test_history.append(test_result)
        del self.active_tests[test_id]
        
        return test_result
    
    def _execute_network_test(self, config: NetworkTestConfig) -> PerformanceMetrics:
        """Executa o teste de rede"""
        start_time = datetime.now()
        response_times = []
        successful_requests = 0
        failed_requests = 0
        
        # Simular requisições de rede
        while (datetime.now() - start_time).total_seconds() < config.duration_seconds:
            try:
                # Simular requisição HTTP
                request_start = time.time()
                self._simulate_http_request()
                request_duration = (time.time() - request_start) * 1000
                
                response_times.append(request_duration)
                successful_requests += 1
                
                # Registrar no monitor de performance
                performance_monitor.record_response_time(request_duration, success=True)
                
            except Exception as e:
                request_duration = (time.time() - request_start) * 1000
                response_times.append(request_duration)
                failed_requests += 1
                
                # Registrar no monitor de performance
                performance_monitor.record_response_time(request_duration, success=False, error_message=str(e))
        
        # Calcular métricas
        end_time = datetime.now()
        duration_ms = (end_time - start_time).total_seconds() * 1000
        
        if response_times:
            response_times.sort()
            avg_response_time = sum(response_times) / len(response_times)
            min_response_time = min(response_times)
            max_response_time = max(response_times)
            p50_response_time = response_times[len(response_times) // 2]
            p95_response_time = response_times[int(len(response_times) * 0.95)]
            p99_response_time = response_times[int(len(response_times) * 0.99)]
        else:
            avg_response_time = min_response_time = max_response_time = 0.0
            p50_response_time = p95_response_time = p99_response_time = 0.0
        
        total_requests = successful_requests + failed_requests
        throughput_rps = total_requests / (duration_ms / 1000) if duration_ms > 0 else 0.0
        error_rate = (failed_requests / total_requests * 100) if total_requests > 0 else 0.0
        
        # Obter métricas do sistema
        system_metrics = performance_monitor.get_current_metrics()
        
        return PerformanceMetrics(
            test_name=config.test_name,
            test_type=TestType.NETWORK,
            start_time=start_time,
            end_time=end_time,
            duration_ms=duration_ms,
            requests_total=total_requests,
            requests_successful=successful_requests,
            requests_failed=failed_requests,
            requests_timeout=0,  # Não aplicável para rede
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
            concurrent_users=1,  # Não aplicável para rede
            test_config={
                **config.to_dict(),
                "packets_sent": self.packets_sent,
                "packets_received": self.packets_received,
                "packets_dropped": self.packets_dropped,
                "connections_dropped": self.connections_dropped
            }
        )
    
    async def _execute_network_test_async(self, config: NetworkTestConfig) -> PerformanceMetrics:
        """Executa o teste de rede assíncrono"""
        start_time = datetime.now()
        response_times = []
        successful_requests = 0
        failed_requests = 0
        
        # Simular requisições de rede assíncronas
        while (datetime.now() - start_time).total_seconds() < config.duration_seconds:
            try:
                # Simular requisição HTTP assíncrona
                request_start = time.time()
                await self._simulate_http_request_async()
                request_duration = (time.time() - request_start) * 1000
                
                response_times.append(request_duration)
                successful_requests += 1
                
                # Registrar no monitor de performance
                performance_monitor.record_response_time(request_duration, success=True)
                
            except Exception as e:
                request_duration = (time.time() - request_start) * 1000
                response_times.append(request_duration)
                failed_requests += 1
                
                # Registrar no monitor de performance
                performance_monitor.record_response_time(request_duration, success=False, error_message=str(e))
        
        # Calcular métricas (mesmo código do método síncrono)
        end_time = datetime.now()
        duration_ms = (end_time - start_time).total_seconds() * 1000
        
        if response_times:
            response_times.sort()
            avg_response_time = sum(response_times) / len(response_times)
            min_response_time = min(response_times)
            max_response_time = max(response_times)
            p50_response_time = response_times[len(response_times) // 2]
            p95_response_time = response_times[int(len(response_times) * 0.95)]
            p99_response_time = response_times[int(len(response_times) * 0.99)]
        else:
            avg_response_time = min_response_time = max_response_time = 0.0
            p50_response_time = p95_response_time = p99_response_time = 0.0
        
        total_requests = successful_requests + failed_requests
        throughput_rps = total_requests / (duration_ms / 1000) if duration_ms > 0 else 0.0
        error_rate = (failed_requests / total_requests * 100) if total_requests > 0 else 0.0
        
        # Obter métricas do sistema
        system_metrics = performance_monitor.get_current_metrics()
        
        return PerformanceMetrics(
            test_name=config.test_name,
            test_type=TestType.NETWORK,
            start_time=start_time,
            end_time=end_time,
            duration_ms=duration_ms,
            requests_total=total_requests,
            requests_successful=successful_requests,
            requests_failed=failed_requests,
            requests_timeout=0,  # Não aplicável para rede
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
            concurrent_users=1,  # Não aplicável para rede
            test_config={
                **config.to_dict(),
                "packets_sent": self.packets_sent,
                "packets_received": self.packets_received,
                "packets_dropped": self.packets_dropped,
                "connections_dropped": self.connections_dropped
            }
        )
    
    def _simulate_http_request(self) -> None:
        """Simula uma requisição HTTP"""
        # Simular latência de rede
        if self.current_condition:
            latency = self.current_condition.latency_ms + random.randint(-self.current_condition.jitter_ms, self.current_condition.jitter_ms)
            time.sleep(latency / 1000.0)
        
        # Simular falha ocasional
        if random.random() < 0.1:  # 10% de chance de falha
            raise ConnectionError("Simulated network error")
    
    async def _simulate_http_request_async(self) -> None:
        """Simula uma requisição HTTP assíncrona"""
        # Simular latência de rede
        if self.current_condition:
            latency = self.current_condition.latency_ms + random.randint(-self.current_condition.jitter_ms, self.current_condition.jitter_ms)
            await asyncio.sleep(latency / 1000.0)
        
        # Simular falha ocasional
        if random.random() < 0.1:  # 10% de chance de falha
            raise ConnectionError("Simulated network error")
    
    def get_network_statistics(self) -> Dict[str, Any]:
        """Obtém estatísticas de rede"""
        return {
            "simulation_active": self.simulation_active,
            "current_condition": {
                "latency_ms": self.current_condition.latency_ms if self.current_condition else 0,
                "jitter_ms": self.current_condition.jitter_ms if self.current_condition else 0,
                "packet_loss_percent": self.current_condition.packet_loss_percent if self.current_condition else 0.0,
                "bandwidth_mbps": self.current_condition.bandwidth_mbps if self.current_condition else None,
                "connection_drops": self.current_condition.connection_drops if self.current_condition else False
            },
            "packets_sent": self.packets_sent,
            "packets_received": self.packets_received,
            "packets_dropped": self.packets_dropped,
            "connections_dropped": self.connections_dropped,
            "packet_loss_rate": (self.packets_dropped / (self.packets_sent + self.packets_received) * 100) if (self.packets_sent + self.packets_received) > 0 else 0.0
        }
    
    def get_test_history(self) -> List[TestResult]:
        """Obtém histórico de testes"""
        return self.test_history.copy()
    
    def get_active_tests(self) -> Dict[str, TestResult]:
        """Obtém testes ativos"""
        return self.active_tests.copy()
    
    def clear_history(self) -> None:
        """Limpa histórico de testes"""
        self.test_history.clear()
        self.packets_sent = 0
        self.packets_received = 0
        self.packets_dropped = 0
        self.connections_dropped = 0
        self.logger.info("Histórico de testes de rede limpo")
    
    def set_network_condition(self, condition: NetworkCondition) -> None:
        """Define condição de rede"""
        self.current_condition = condition
        self.logger.info(f"Condição de rede atualizada: {condition.latency_ms}ms latência, "
                        f"{condition.packet_loss_percent}% perda de pacotes")
