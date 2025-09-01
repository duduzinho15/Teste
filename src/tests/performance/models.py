"""
Modelos de Dados para Testes de Performance
Sistema de Recomendações de Ofertas - Garimpeiro Geek
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
import json


class TestType(Enum):
    """Tipos de teste de performance"""
    STRESS = "stress"
    LOAD = "load"
    CONCURRENCY = "concurrency"
    MEMORY = "memory"
    NETWORK = "network"
    BENCHMARK = "benchmark"


class TestStatus(Enum):
    """Status dos testes"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


@dataclass
class PerformanceMetrics:
    """Métricas de performance"""
    test_name: str
    test_type: TestType
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_ms: Optional[float] = None
    requests_total: int = 0
    requests_successful: int = 0
    requests_failed: int = 0
    requests_timeout: int = 0
    avg_response_time_ms: float = 0.0
    min_response_time_ms: float = 0.0
    max_response_time_ms: float = 0.0
    p50_response_time_ms: float = 0.0
    p95_response_time_ms: float = 0.0
    p99_response_time_ms: float = 0.0
    throughput_rps: float = 0.0
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    error_rate_percent: float = 0.0
    concurrent_users: int = 1
    test_config: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            "test_name": self.test_name,
            "test_type": self.test_type.value,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_ms": self.duration_ms,
            "requests_total": self.requests_total,
            "requests_successful": self.requests_successful,
            "requests_failed": self.requests_failed,
            "requests_timeout": self.requests_timeout,
            "avg_response_time_ms": self.avg_response_time_ms,
            "min_response_time_ms": self.min_response_time_ms,
            "max_response_time_ms": self.max_response_time_ms,
            "p50_response_time_ms": self.p50_response_time_ms,
            "p95_response_time_ms": self.p95_response_time_ms,
            "p99_response_time_ms": self.p99_response_time_ms,
            "throughput_rps": self.throughput_rps,
            "memory_usage_mb": self.memory_usage_mb,
            "cpu_usage_percent": self.cpu_usage_percent,
            "error_rate_percent": self.error_rate_percent,
            "concurrent_users": self.concurrent_users,
            "test_config": self.test_config
        }


@dataclass
class StressTestConfig:
    """Configuração para testes de stress"""
    test_name: str
    duration_seconds: int = 300  # 5 minutos
    concurrent_users: int = 10
    ramp_up_seconds: int = 30
    ramp_down_seconds: int = 30
    target_rps: Optional[float] = None
    max_response_time_ms: int = 5000
    timeout_seconds: int = 30
    memory_limit_mb: Optional[float] = None
    cpu_limit_percent: Optional[float] = None
    error_threshold_percent: float = 5.0
    test_scenarios: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            "test_name": self.test_name,
            "duration_seconds": self.duration_seconds,
            "concurrent_users": self.concurrent_users,
            "ramp_up_seconds": self.ramp_up_seconds,
            "ramp_down_seconds": self.ramp_down_seconds,
            "target_rps": self.target_rps,
            "max_response_time_ms": self.max_response_time_ms,
            "timeout_seconds": self.timeout_seconds,
            "memory_limit_mb": self.memory_limit_mb,
            "cpu_limit_percent": self.cpu_limit_percent,
            "error_threshold_percent": self.error_threshold_percent,
            "test_scenarios": self.test_scenarios
        }


@dataclass
class LoadTestConfig:
    """Configuração para testes de carga"""
    test_name: str
    initial_users: int = 1
    max_users: int = 100
    step_users: int = 10
    step_duration_seconds: int = 60
    hold_duration_seconds: int = 300
    target_rps: Optional[float] = None
    max_response_time_ms: int = 2000
    timeout_seconds: int = 10
    error_threshold_percent: float = 2.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            "test_name": self.test_name,
            "initial_users": self.initial_users,
            "max_users": self.max_users,
            "step_users": self.step_users,
            "step_duration_seconds": self.step_duration_seconds,
            "hold_duration_seconds": self.hold_duration_seconds,
            "target_rps": self.target_rps,
            "max_response_time_ms": self.max_response_time_ms,
            "timeout_seconds": self.timeout_seconds,
            "error_threshold_percent": self.error_threshold_percent
        }


@dataclass
class ConcurrencyTestConfig:
    """Configuração para testes de concorrência"""
    test_name: str
    concurrent_tasks: int = 10
    task_duration_seconds: int = 60
    max_concurrent_tasks: int = 100
    task_types: List[str] = field(default_factory=lambda: ["scraping", "processing", "posting"])
    timeout_seconds: int = 30
    memory_limit_mb: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            "test_name": self.test_name,
            "concurrent_tasks": self.concurrent_tasks,
            "task_duration_seconds": self.task_duration_seconds,
            "max_concurrent_tasks": self.max_concurrent_tasks,
            "task_types": self.task_types,
            "timeout_seconds": self.timeout_seconds,
            "memory_limit_mb": self.memory_limit_mb
        }


@dataclass
class MemoryTestConfig:
    """Configuração para testes de memória"""
    test_name: str
    duration_seconds: int = 300
    check_interval_seconds: int = 5
    memory_threshold_mb: float = 500.0
    gc_enabled: bool = True
    memory_profiling: bool = True
    leak_detection: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            "test_name": self.test_name,
            "duration_seconds": self.duration_seconds,
            "check_interval_seconds": self.check_interval_seconds,
            "memory_threshold_mb": self.memory_threshold_mb,
            "gc_enabled": self.gc_enabled,
            "memory_profiling": self.memory_profiling,
            "leak_detection": self.leak_detection
        }


@dataclass
class NetworkTestConfig:
    """Configuração para testes de rede"""
    test_name: str
    duration_seconds: int = 300
    latency_ms: int = 100
    jitter_ms: int = 50
    packet_loss_percent: float = 1.0
    bandwidth_mbps: Optional[float] = None
    connection_drops: bool = False
    drop_interval_seconds: int = 30
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            "test_name": self.test_name,
            "duration_seconds": self.duration_seconds,
            "latency_ms": self.latency_ms,
            "jitter_ms": self.jitter_ms,
            "packet_loss_percent": self.packet_loss_percent,
            "bandwidth_mbps": self.bandwidth_mbps,
            "connection_drops": self.connection_drops,
            "drop_interval_seconds": self.drop_interval_seconds
        }


@dataclass
class BenchmarkConfig:
    """Configuração para benchmarks"""
    test_name: str
    iterations: int = 1000
    warmup_iterations: int = 100
    timeout_seconds: int = 300
    memory_profiling: bool = True
    cpu_profiling: bool = True
    detailed_reporting: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            "test_name": self.test_name,
            "iterations": self.iterations,
            "warmup_iterations": self.warmup_iterations,
            "timeout_seconds": self.timeout_seconds,
            "memory_profiling": self.memory_profiling,
            "cpu_profiling": self.cpu_profiling,
            "detailed_reporting": self.detailed_reporting
        }


@dataclass
class TestResult:
    """Resultado de um teste"""
    test_id: str
    test_name: str
    test_type: TestType
    status: TestStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_ms: Optional[float] = None
    metrics: Optional[PerformanceMetrics] = None
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    config: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            "test_id": self.test_id,
            "test_name": self.test_name,
            "test_type": self.test_type.value,
            "status": self.status.value,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_ms": self.duration_ms,
            "metrics": self.metrics.to_dict() if self.metrics else None,
            "errors": self.errors,
            "warnings": self.warnings,
            "config": self.config
        }
    
    def to_json(self) -> str:
        """Converte para JSON"""
        return json.dumps(self.to_dict(), indent=2, default=str)


@dataclass
class PerformanceReport:
    """Relatório de performance"""
    report_id: str
    timestamp: datetime
    test_results: List[TestResult]
    summary: Dict[str, Any]
    recommendations: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            "report_id": self.report_id,
            "timestamp": self.timestamp.isoformat(),
            "test_results": [result.to_dict() for result in self.test_results],
            "summary": self.summary,
            "recommendations": self.recommendations
        }
    
    def to_json(self) -> str:
        """Converte para JSON"""
        return json.dumps(self.to_dict(), indent=2, default=str)
    
    def save_to_file(self, filepath: str) -> None:
        """Salva o relatório em arquivo"""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(self.to_json())
