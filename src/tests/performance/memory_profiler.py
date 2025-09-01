"""
Profiler de Memória
Sistema de Recomendações de Ofertas - Garimpeiro Geek
"""

import gc
import psutil
import time
import threading
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
import logging
import tracemalloc
from collections import deque

from .models import (
    TestType, TestStatus, PerformanceMetrics, MemoryTestConfig, 
    TestResult
)
from .performance_monitor import performance_monitor


@dataclass
class MemorySnapshot:
    """Snapshot de memória"""
    timestamp: datetime
    memory_used_mb: float
    memory_available_mb: float
    memory_percent: float
    gc_objects: int
    gc_collections: Dict[str, int]
    tracemalloc_stats: Optional[Dict[str, Any]] = None


@dataclass
class MemoryLeak:
    """Detecção de vazamento de memória"""
    start_time: datetime
    end_time: datetime
    memory_increase_mb: float
    increase_rate_mb_per_min: float
    severity: str  # low, medium, high, critical


class MemoryProfiler:
    """Profiler de memória para o sistema"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.active_tests: Dict[str, TestResult] = {}
        self.test_history: List[TestResult] = []
        self.memory_snapshots: deque = deque(maxlen=10000)
        self.memory_leaks: List[MemoryLeak] = []
        
        # Configurações
        self.monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.tracemalloc_enabled = False
        
        # Thresholds para detecção de vazamentos
        self.leak_thresholds = {
            "low": 10.0,      # 10MB por minuto
            "medium": 50.0,   # 50MB por minuto
            "high": 100.0,    # 100MB por minuto
            "critical": 200.0 # 200MB por minuto
        }
    
    def start_memory_monitoring(self, interval_seconds: float = 1.0) -> None:
        """Inicia monitoramento de memória"""
        if self.monitoring:
            self.logger.warning("Monitoramento de memória já está ativo")
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._memory_monitor_loop,
            args=(interval_seconds,),
            daemon=True
        )
        self.monitor_thread.start()
        self.logger.info(f"Monitoramento de memória iniciado com intervalo de {interval_seconds}s")
    
    def stop_memory_monitoring(self) -> None:
        """Para monitoramento de memória"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5.0)
        self.logger.info("Monitoramento de memória parado")
    
    def _memory_monitor_loop(self, interval_seconds: float) -> None:
        """Loop principal de monitoramento de memória"""
        while self.monitoring:
            try:
                snapshot = self._take_memory_snapshot()
                self.memory_snapshots.append(snapshot)
                
                # Verificar vazamentos
                self._check_memory_leaks()
                
                time.sleep(interval_seconds)
            except Exception as e:
                self.logger.error(f"Erro no monitoramento de memória: {e}")
                time.sleep(interval_seconds)
    
    def _take_memory_snapshot(self) -> MemorySnapshot:
        """Tira um snapshot da memória"""
        try:
            # Informações do sistema
            memory = psutil.virtual_memory()
            memory_used_mb = memory.used / (1024 * 1024)
            memory_available_mb = memory.available / (1024 * 1024)
            memory_percent = memory.percent
            
            # Informações do garbage collector
            gc_objects = len(gc.get_objects())
            gc_collections = {}
            for gen in range(3):
                gc_collections[f"gen{gen}"] = gc.get_count()[gen]
            
            # Informações do tracemalloc (se habilitado)
            tracemalloc_stats = None
            if self.tracemalloc_enabled and tracemalloc.is_tracing():
                current, peak = tracemalloc.get_traced_memory()
                tracemalloc_stats = {
                    "current_mb": current / (1024 * 1024),
                    "peak_mb": peak / (1024 * 1024),
                    "top_stats": self._get_top_tracemalloc_stats()
                }
            
            return MemorySnapshot(
                timestamp=datetime.now(),
                memory_used_mb=memory_used_mb,
                memory_available_mb=memory_available_mb,
                memory_percent=memory_percent,
                gc_objects=gc_objects,
                gc_collections=gc_collections,
                tracemalloc_stats=tracemalloc_stats
            )
        except Exception as e:
            self.logger.error(f"Erro ao tirar snapshot de memória: {e}")
            # Retornar snapshot vazio em caso de erro
            return MemorySnapshot(
                timestamp=datetime.now(),
                memory_used_mb=0.0,
                memory_available_mb=0.0,
                memory_percent=0.0,
                gc_objects=0,
                gc_collections={}
            )
    
    def _get_top_tracemalloc_stats(self) -> List[Dict[str, Any]]:
        """Obtém estatísticas top do tracemalloc"""
        try:
            if tracemalloc.is_tracing():
                top_stats = tracemalloc.get_traced_memory()
                return [
                    {
                        "filename": "memory_allocation",
                        "size_mb": 0.0,
                        "count": 0
                    }
                    for _ in range(min(10, len(top_stats)))  # Top 10
                ]
        except Exception as e:
            self.logger.error(f"Erro ao obter estatísticas do tracemalloc: {e}")
        
        return []
    
    def _check_memory_leaks(self) -> None:
        """Verifica vazamentos de memória"""
        if len(self.memory_snapshots) < 2:
            return
        
        # Comparar snapshots recentes
        recent_snapshots = list(self.memory_snapshots)[-60:]  # Últimos 60 snapshots (1 minuto)
        if len(recent_snapshots) < 2:
            return
        
        first_snapshot = recent_snapshots[0]
        last_snapshot = recent_snapshots[-1]
        
        # Calcular aumento de memória
        memory_increase = last_snapshot.memory_used_mb - first_snapshot.memory_used_mb
        time_diff_minutes = (last_snapshot.timestamp - first_snapshot.timestamp).total_seconds() / 60
        
        if time_diff_minutes > 0:
            increase_rate = memory_increase / time_diff_minutes
            
            # Determinar severidade
            severity = "low"
            for level, threshold in self.leak_thresholds.items():
                if increase_rate >= threshold:
                    severity = level
            
            # Registrar vazamento se significativo
            if increase_rate > self.leak_thresholds["low"]:
                leak = MemoryLeak(
                    start_time=first_snapshot.timestamp,
                    end_time=last_snapshot.timestamp,
                    memory_increase_mb=memory_increase,
                    increase_rate_mb_per_min=increase_rate,
                    severity=severity
                )
                self.memory_leaks.append(leak)
                
                self.logger.warning(
                    f"Vazamento de memória detectado: {increase_rate:.2f}MB/min "
                    f"({severity} severity)"
                )
    
    def run_memory_test(self, config: MemoryTestConfig) -> TestResult:
        """Executa um teste de memória"""
        test_id = f"memory_{int(time.time())}"
        test_result = TestResult(
            test_id=test_id,
            test_name=config.test_name,
            test_type=TestType.MEMORY,
            status=TestStatus.RUNNING,
            start_time=datetime.now(),
            config=config.to_dict()
        )
        
        self.active_tests[test_id] = test_result
        self.logger.info(f"Iniciando teste de memória: {config.test_name}")
        
        try:
            # Configurar tracemalloc se habilitado
            if config.memory_profiling:
                self._enable_tracemalloc()
            
            # Iniciar monitoramento
            self.start_memory_monitoring(config.check_interval_seconds)
            
            # Executar teste
            metrics = self._execute_memory_test(config)
            
            # Finalizar teste
            test_result.end_time = datetime.now()
            test_result.duration_ms = (test_result.end_time - test_result.start_time).total_seconds() * 1000
            test_result.metrics = metrics
            test_result.status = TestStatus.COMPLETED
            
            # Parar monitoramento
            self.stop_memory_monitoring()
            
            # Desabilitar tracemalloc
            if config.memory_profiling:
                self._disable_tracemalloc()
            
            self.logger.info(f"Teste de memória concluído: {config.test_name}")
            
        except Exception as e:
            test_result.status = TestStatus.FAILED
            test_result.errors.append(str(e))
            test_result.end_time = datetime.now()
            self.stop_memory_monitoring()
            if config.memory_profiling:
                self._disable_tracemalloc()
            self.logger.error(f"Erro no teste de memória: {e}")
        
        # Adicionar ao histórico
        self.test_history.append(test_result)
        del self.active_tests[test_id]
        
        return test_result
    
    def _enable_tracemalloc(self) -> None:
        """Habilita tracemalloc"""
        if not tracemalloc.is_tracing():
            tracemalloc.start()
            self.tracemalloc_enabled = True
            self.logger.info("Tracemalloc habilitado")
    
    def _disable_tracemalloc(self) -> None:
        """Desabilita tracemalloc"""
        if tracemalloc.is_tracing():
            tracemalloc.stop()
            self.tracemalloc_enabled = False
            self.logger.info("Tracemalloc desabilitado")
    
    def _execute_memory_test(self, config: MemoryTestConfig) -> PerformanceMetrics:
        """Executa o teste de memória"""
        start_time = datetime.now()
        
        # Aguardar duração do teste
        time.sleep(config.duration_seconds)
        
        end_time = datetime.now()
        duration_ms = (end_time - start_time).total_seconds() * 1000
        
        # Obter métricas finais
        final_snapshot = self._take_memory_snapshot()
        
        # Calcular estatísticas de memória
        memory_snapshots = list(self.memory_snapshots)
        if memory_snapshots:
            memory_used_values = [s.memory_used_mb for s in memory_snapshots]
            memory_percent_values = [s.memory_percent for s in memory_snapshots]
            
            avg_memory_used = sum(memory_used_values) / len(memory_used_values)
            max_memory_used = max(memory_used_values)
            min_memory_used = min(memory_used_values)
            
            avg_memory_percent = sum(memory_percent_values) / len(memory_percent_values)
        else:
            avg_memory_used = max_memory_used = min_memory_used = 0.0
            avg_memory_percent = 0.0
        
        # Verificar vazamentos detectados
        leaks_during_test = [
            leak for leak in self.memory_leaks
            if leak.start_time >= start_time and leak.end_time <= end_time
        ]
        
        # Calcular métricas de vazamento
        total_leak_mb = sum(leak.memory_increase_mb for leak in leaks_during_test)
        avg_leak_rate = sum(leak.increase_rate_mb_per_min for leak in leaks_during_test) / len(leaks_during_test) if leaks_during_test else 0.0
        
        # Obter métricas do sistema
        system_metrics = performance_monitor.get_current_metrics()
        
        return PerformanceMetrics(
            test_name=config.test_name,
            test_type=TestType.MEMORY,
            start_time=start_time,
            end_time=end_time,
            duration_ms=duration_ms,
            memory_usage_mb=final_snapshot.memory_used_mb,
            cpu_usage_percent=system_metrics.cpu_percent,
            concurrent_users=1,  # Não aplicável para teste de memória
            test_config={
                **config.to_dict(),
                "avg_memory_used_mb": avg_memory_used,
                "max_memory_used_mb": max_memory_used,
                "min_memory_used_mb": min_memory_used,
                "avg_memory_percent": avg_memory_percent,
                "memory_leaks_detected": len(leaks_during_test),
                "total_leak_mb": total_leak_mb,
                "avg_leak_rate_mb_per_min": avg_leak_rate,
                "gc_objects_final": final_snapshot.gc_objects
            }
        )
    
    def get_memory_statistics(self, minutes: int = 10) -> Dict[str, Any]:
        """Obtém estatísticas de memória"""
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        recent_snapshots = [s for s in self.memory_snapshots if s.timestamp >= cutoff_time]
        
        if not recent_snapshots:
            return {
                "snapshots_count": 0,
                "avg_memory_used_mb": 0.0,
                "max_memory_used_mb": 0.0,
                "min_memory_used_mb": 0.0,
                "avg_memory_percent": 0.0,
                "memory_leaks": []
            }
        
        # Estatísticas básicas
        memory_used_values = [s.memory_used_mb for s in recent_snapshots]
        memory_percent_values = [s.memory_percent for s in recent_snapshots]
        
        avg_memory_used = sum(memory_used_values) / len(memory_used_values)
        max_memory_used = max(memory_used_values)
        min_memory_used = min(memory_used_values)
        avg_memory_percent = sum(memory_percent_values) / len(memory_percent_values)
        
        # Vazamentos recentes
        recent_leaks = [leak for leak in self.memory_leaks if leak.end_time >= cutoff_time]
        
        return {
            "snapshots_count": len(recent_snapshots),
            "avg_memory_used_mb": avg_memory_used,
            "max_memory_used_mb": max_memory_used,
            "min_memory_used_mb": min_memory_used,
            "avg_memory_percent": avg_memory_percent,
            "memory_leaks": [
                {
                    "start_time": leak.start_time.isoformat(),
                    "end_time": leak.end_time.isoformat(),
                    "memory_increase_mb": leak.memory_increase_mb,
                    "increase_rate_mb_per_min": leak.increase_rate_mb_per_min,
                    "severity": leak.severity
                }
                for leak in recent_leaks
            ]
        }
    
    def force_garbage_collection(self) -> Dict[str, Any]:
        """Força coleta de lixo e retorna estatísticas"""
        try:
            # Contar objetos antes
            objects_before = len(gc.get_objects())
            memory_before = psutil.virtual_memory().used / (1024 * 1024)
            
            # Executar coleta
            collected = gc.collect()
            
            # Contar objetos depois
            objects_after = len(gc.get_objects())
            memory_after = psutil.virtual_memory().used / (1024 * 1024)
            
            return {
                "objects_collected": collected,
                "objects_before": objects_before,
                "objects_after": objects_after,
                "objects_freed": objects_before - objects_after,
                "memory_before_mb": memory_before,
                "memory_after_mb": memory_after,
                "memory_freed_mb": memory_before - memory_after
            }
        except Exception as e:
            self.logger.error(f"Erro na coleta de lixo: {e}")
            return {
                "error": str(e)
            }
    
    def get_memory_leaks(self) -> List[Dict[str, Any]]:
        """Obtém lista de vazamentos de memória detectados"""
        return [
            {
                "start_time": leak.start_time.isoformat(),
                "end_time": leak.end_time.isoformat(),
                "memory_increase_mb": leak.memory_increase_mb,
                "increase_rate_mb_per_min": leak.increase_rate_mb_per_min,
                "severity": leak.severity
            }
            for leak in self.memory_leaks
        ]
    
    def get_test_history(self) -> List[TestResult]:
        """Obtém histórico de testes"""
        return self.test_history.copy()
    
    def get_active_tests(self) -> Dict[str, TestResult]:
        """Obtém testes ativos"""
        return self.active_tests.copy()
    
    def clear_history(self) -> None:
        """Limpa histórico de testes e snapshots"""
        self.test_history.clear()
        self.memory_snapshots.clear()
        self.memory_leaks.clear()
        self.logger.info("Histórico de testes e snapshots de memória limpo")
    
    def set_leak_thresholds(self, thresholds: Dict[str, float]) -> None:
        """Define thresholds para detecção de vazamentos"""
        self.leak_thresholds.update(thresholds)
        self.logger.info(f"Thresholds de vazamento atualizados: {thresholds}")
    
    def export_memory_data(self, filepath: str) -> None:
        """Exporta dados de memória para arquivo"""
        import json
        
        data = {
            "export_timestamp": datetime.now().isoformat(),
            "memory_snapshots": [
                {
                    "timestamp": s.timestamp.isoformat(),
                    "memory_used_mb": s.memory_used_mb,
                    "memory_available_mb": s.memory_available_mb,
                    "memory_percent": s.memory_percent,
                    "gc_objects": s.gc_objects,
                    "gc_collections": s.gc_collections
                }
                for s in self.memory_snapshots
            ],
            "memory_leaks": self.get_memory_leaks()
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        self.logger.info(f"Dados de memória exportados para {filepath}")
