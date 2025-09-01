"""
Monitor de Performance
Sistema de Recomendações de Ofertas - Garimpeiro Geek
"""

import asyncio
import time
import psutil
import threading
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import deque
import logging

from .models import PerformanceMetrics, TestType


@dataclass
class SystemMetrics:
    """Métricas do sistema"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    memory_available_mb: float
    disk_usage_percent: float
    network_sent_mb: float
    network_recv_mb: float
    active_threads: int
    active_processes: int


@dataclass
class ResponseTime:
    """Tempo de resposta"""
    timestamp: datetime
    duration_ms: float
    success: bool
    error_message: Optional[str] = None


class PerformanceMonitor:
    """Monitor de performance em tempo real"""
    
    def __init__(self, max_history_size: int = 1000):
        self.max_history_size = max_history_size
        self.system_metrics: deque = deque(maxlen=max_history_size)
        self.response_times: deque = deque(maxlen=max_history_size)
        self.monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.logger = logging.getLogger(__name__)
        
        # Callbacks para eventos
        self.on_high_cpu: Optional[Callable[[float], None]] = None
        self.on_high_memory: Optional[Callable[[float], None]] = None
        self.on_slow_response: Optional[Callable[[float], None]] = None
        self.on_error_rate_high: Optional[Callable[[float], None]] = None
        
        # Thresholds
        self.cpu_threshold = 80.0
        self.memory_threshold = 80.0
        self.response_time_threshold = 5000.0  # 5 segundos
        self.error_rate_threshold = 5.0  # 5%
    
    def start_monitoring(self, interval_seconds: float = 1.0) -> None:
        """Inicia o monitoramento"""
        if self.monitoring:
            self.logger.warning("Monitoramento já está ativo")
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            args=(interval_seconds,),
            daemon=True
        )
        self.monitor_thread.start()
        self.logger.info(f"Monitoramento iniciado com intervalo de {interval_seconds}s")
    
    def stop_monitoring(self) -> None:
        """Para o monitoramento"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5.0)
        self.logger.info("Monitoramento parado")
    
    def _monitor_loop(self, interval_seconds: float) -> None:
        """Loop principal de monitoramento"""
        while self.monitoring:
            try:
                metrics = self._collect_system_metrics()
                self.system_metrics.append(metrics)
                
                # Verificar thresholds
                self._check_thresholds(metrics)
                
                time.sleep(interval_seconds)
            except Exception as e:
                self.logger.error(f"Erro no monitoramento: {e}")
                time.sleep(interval_seconds)
    
    def _collect_system_metrics(self) -> SystemMetrics:
        """Coleta métricas do sistema"""
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=0.1)
            
            # Memória
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_used_mb = memory.used / (1024 * 1024)
            memory_available_mb = memory.available / (1024 * 1024)
            
            # Disco
            disk = psutil.disk_usage('/')
            disk_usage_percent = disk.percent
            
            # Rede
            network = psutil.net_io_counters()
            network_sent_mb = network.bytes_sent / (1024 * 1024)
            network_recv_mb = network.bytes_recv / (1024 * 1024)
            
            # Threads e processos
            active_threads = threading.active_count()
            active_processes = len(psutil.pids())
            
            return SystemMetrics(
                timestamp=datetime.now(),
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                memory_used_mb=memory_used_mb,
                memory_available_mb=memory_available_mb,
                disk_usage_percent=disk_usage_percent,
                network_sent_mb=network_sent_mb,
                network_recv_mb=network_recv_mb,
                active_threads=active_threads,
                active_processes=active_processes
            )
        except Exception as e:
            self.logger.error(f"Erro ao coletar métricas do sistema: {e}")
            # Retornar métricas vazias em caso de erro
            return SystemMetrics(
                timestamp=datetime.now(),
                cpu_percent=0.0,
                memory_percent=0.0,
                memory_used_mb=0.0,
                memory_available_mb=0.0,
                disk_usage_percent=0.0,
                network_sent_mb=0.0,
                network_recv_mb=0.0,
                active_threads=0,
                active_processes=0
            )
    
    def _check_thresholds(self, metrics: SystemMetrics) -> None:
        """Verifica thresholds e dispara callbacks"""
        # CPU alto
        if metrics.cpu_percent > self.cpu_threshold and self.on_high_cpu:
            self.on_high_cpu(metrics.cpu_percent)
        
        # Memória alta
        if metrics.memory_percent > self.memory_threshold and self.on_high_memory:
            self.on_high_memory(metrics.memory_percent)
        
        # Verificar tempos de resposta lentos
        recent_responses = self._get_recent_response_times(60)  # Últimos 60 segundos
        if recent_responses:
            slow_responses = [r for r in recent_responses if r.duration_ms > self.response_time_threshold]
            if slow_responses and self.on_slow_response:
                avg_slow_time = sum(r.duration_ms for r in slow_responses) / len(slow_responses)
                self.on_slow_response(avg_slow_time)
        
        # Verificar taxa de erro alta
        if recent_responses:
            error_count = len([r for r in recent_responses if not r.success])
            error_rate = (error_count / len(recent_responses)) * 100
            if error_rate > self.error_rate_threshold and self.on_error_rate_high:
                self.on_error_rate_high(error_rate)
    
    def record_response_time(self, duration_ms: float, success: bool = True, error_message: Optional[str] = None) -> None:
        """Registra tempo de resposta"""
        response_time = ResponseTime(
            timestamp=datetime.now(),
            duration_ms=duration_ms,
            success=success,
            error_message=error_message
        )
        self.response_times.append(response_time)
    
    def _get_recent_response_times(self, seconds: int) -> List[ResponseTime]:
        """Obtém tempos de resposta recentes"""
        cutoff_time = datetime.now() - timedelta(seconds=seconds)
        return [r for r in self.response_times if r.timestamp >= cutoff_time]
    
    def get_current_metrics(self) -> SystemMetrics:
        """Obtém métricas atuais do sistema"""
        return self._collect_system_metrics()
    
    def get_metrics_history(self, minutes: int = 10) -> List[SystemMetrics]:
        """Obtém histórico de métricas"""
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        return [m for m in self.system_metrics if m.timestamp >= cutoff_time]
    
    def get_response_time_stats(self, minutes: int = 10) -> Dict[str, float]:
        """Obtém estatísticas de tempo de resposta"""
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        recent_responses = [r for r in self.response_times if r.timestamp >= cutoff_time]
        
        if not recent_responses:
            return {
                "count": 0,
                "avg_ms": 0.0,
                "min_ms": 0.0,
                "max_ms": 0.0,
                "p50_ms": 0.0,
                "p95_ms": 0.0,
                "p99_ms": 0.0,
                "error_rate_percent": 0.0
            }
        
        durations = [r.duration_ms for r in recent_responses]
        durations.sort()
        
        error_count = len([r for r in recent_responses if not r.success])
        error_rate = (error_count / len(recent_responses)) * 100
        
        return {
            "count": len(recent_responses),
            "avg_ms": sum(durations) / len(durations),
            "min_ms": min(durations),
            "max_ms": max(durations),
            "p50_ms": durations[len(durations) // 2],
            "p95_ms": durations[int(len(durations) * 0.95)],
            "p99_ms": durations[int(len(durations) * 0.99)],
            "error_rate_percent": error_rate
        }
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Obtém resumo de performance"""
        current_metrics = self.get_current_metrics()
        response_stats = self.get_response_time_stats()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "system": {
                "cpu_percent": current_metrics.cpu_percent,
                "memory_percent": current_metrics.memory_percent,
                "memory_used_mb": current_metrics.memory_used_mb,
                "disk_usage_percent": current_metrics.disk_usage_percent,
                "active_threads": current_metrics.active_threads,
                "active_processes": current_metrics.active_processes
            },
            "response_times": response_stats,
            "alerts": {
                "high_cpu": current_metrics.cpu_percent > self.cpu_threshold,
                "high_memory": current_metrics.memory_percent > self.memory_threshold,
                "slow_responses": response_stats["avg_ms"] > self.response_time_threshold,
                "high_error_rate": response_stats["error_rate_percent"] > self.error_rate_threshold
            }
        }
    
    def set_thresholds(self, cpu: Optional[float] = None, memory: Optional[float] = None,
                      response_time: Optional[float] = None, error_rate: Optional[float] = None) -> None:
        """Define thresholds de alerta"""
        if cpu is not None:
            self.cpu_threshold = cpu
        if memory is not None:
            self.memory_threshold = memory
        if response_time is not None:
            self.response_time_threshold = response_time
        if error_rate is not None:
            self.error_rate_threshold = error_rate
        
        self.logger.info(f"Thresholds atualizados: CPU={self.cpu_threshold}%, "
                        f"Memory={self.memory_threshold}%, "
                        f"ResponseTime={self.response_time_threshold}ms, "
                        f"ErrorRate={self.error_rate_threshold}%")
    
    def set_callbacks(self, on_high_cpu: Optional[Callable[[float], None]] = None,
                     on_high_memory: Optional[Callable[[float], None]] = None,
                     on_slow_response: Optional[Callable[[float], None]] = None,
                     on_error_rate_high: Optional[Callable[[float], None]] = None) -> None:
        """Define callbacks para eventos"""
        self.on_high_cpu = on_high_cpu
        self.on_high_memory = on_high_memory
        self.on_slow_response = on_slow_response
        self.on_error_rate_high = on_error_rate_high
    
    def clear_history(self) -> None:
        """Limpa histórico de métricas"""
        self.system_metrics.clear()
        self.response_times.clear()
        self.logger.info("Histórico de métricas limpo")
    
    def export_metrics(self, filepath: str) -> None:
        """Exporta métricas para arquivo"""
        import json
        
        data = {
            "export_timestamp": datetime.now().isoformat(),
            "system_metrics": [
                {
                    "timestamp": m.timestamp.isoformat(),
                    "cpu_percent": m.cpu_percent,
                    "memory_percent": m.memory_percent,
                    "memory_used_mb": m.memory_used_mb,
                    "disk_usage_percent": m.disk_usage_percent,
                    "active_threads": m.active_threads
                }
                for m in self.system_metrics
            ],
            "response_times": [
                {
                    "timestamp": r.timestamp.isoformat(),
                    "duration_ms": r.duration_ms,
                    "success": r.success,
                    "error_message": r.error_message
                }
                for r in self.response_times
            ]
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        self.logger.info(f"Métricas exportadas para {filepath}")


# Instância global do monitor
performance_monitor = PerformanceMonitor()
