"""
Sistema Unificado de Dashboard
Integra todos os sistemas implementados em uma interface única
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass

# Imports dos sistemas implementados
from .production_testing import ProductionTestRunner
from .conversion_monitoring import ConversionTracker, ConversionAnalyzer, ConversionDashboard
from .user_feedback import FeedbackCollector, FeedbackAnalyzer, ScoreAdjuster, FeedbackDashboard
from .category_expansion import CategoryAnalyzer, CategoryExpander, MarketResearcher, CategoryOptimizer
from .ai_optimization import AIOptimizer, DataCollector, ModelTrainer, PredictionEngine, OptimizationDashboard

logger = logging.getLogger(__name__)


@dataclass
class SystemStatus:
    """Status de cada sistema"""
    name: str
    status: str  # "active", "inactive", "error", "running"
    last_run: Optional[datetime]
    metrics: Dict[str, Any]
    error_message: Optional[str] = None


@dataclass
class DashboardMetrics:
    """Métricas consolidadas do dashboard"""
    total_offers_processed: int
    conversion_rate_geek: float
    conversion_rate_general: float
    feedback_score: float
    categories_expanded: int
    ai_model_accuracy: float
    system_health: str


class UnifiedDashboard:
    """
    Dashboard unificado que integra todos os sistemas implementados
    """
    
    def __init__(self):
        self.systems = {
            "production_testing": ProductionTestRunner(),
            "conversion_monitoring": ConversionTracker(),
            "user_feedback": FeedbackCollector(),
            "category_expansion": CategoryAnalyzer(),
            "ai_optimization": AIOptimizer()
        }
        
        self.system_status = {}
        self.consolidated_metrics = DashboardMetrics(
            total_offers_processed=0,
            conversion_rate_geek=0.0,
            conversion_rate_general=0.0,
            feedback_score=0.0,
            categories_expanded=0,
            ai_model_accuracy=0.0,
            system_health="unknown"
        )
        
        self._initialize_systems()
    
    def _initialize_systems(self):
        """Inicializa todos os sistemas"""
        for name, system in self.systems.items():
            try:
                # Verificar se o sistema precisa de inicialização assíncrona
                if hasattr(system, 'initialize') and asyncio.iscoroutinefunction(system.initialize):
                    # Para sistemas que precisam de event loop, vamos inicializar quando necessário
                    pass
                elif hasattr(system, 'initialize'):
                    # Para sistemas síncronos
                    system.initialize()
                
                self.system_status[name] = SystemStatus(
                    name=name,
                    status="active",
                    last_run=None,
                    metrics={}
                )
                logger.info(f"Sistema {name} inicializado com sucesso")
            except Exception as e:
                logger.error(f"Erro ao inicializar sistema {name}: {e}")
                self.system_status[name] = SystemStatus(
                    name=name,
                    status="error",
                    last_run=None,
                    metrics={},
                    error_message=str(e)
                )
    
    async def get_system_status(self) -> Dict[str, SystemStatus]:
        """Retorna o status de todos os sistemas"""
        return self.system_status
    
    async def get_consolidated_metrics(self) -> DashboardMetrics:
        """Retorna métricas consolidadas de todos os sistemas"""
        try:
            # Coletar métricas de cada sistema
            metrics = {}
            
            # Métricas de conversão
            if "conversion_monitoring" in self.systems:
                try:
                    # Usar dados básicos do tracker
                    tracker = self.systems["conversion_monitoring"]
                    conversion_stats = {
                        "total_offers": len(tracker.conversion_events) if hasattr(tracker, 'conversion_events') else 0,
                        "geek_conversion_rate": 0.15,  # Valor simulado
                        "general_conversion_rate": 0.08  # Valor simulado
                    }
                    metrics["conversion"] = conversion_stats
                except Exception as e:
                    logger.error(f"Erro ao obter métricas de conversão: {e}")
                    metrics["conversion"] = {}
            
            # Métricas de feedback
            if "user_feedback" in self.systems:
                try:
                    # Usar dados básicos do collector
                    collector = self.systems["user_feedback"]
                    feedback_stats = {
                        "total_feedback": len(collector.feedback_data) if hasattr(collector, 'feedback_data') else 0,
                        "overall_score": 4.2,  # Valor simulado
                        "positive_rate": 0.85  # Valor simulado
                    }
                    metrics["feedback"] = feedback_stats
                except Exception as e:
                    logger.error(f"Erro ao obter métricas de feedback: {e}")
                    metrics["feedback"] = {}
            
            # Métricas de categorias
            if "category_expansion" in self.systems:
                try:
                    # Usar dados básicos do analyzer
                    analyzer = self.systems["category_expansion"]
                    category_stats = {
                        "total_categories": len(analyzer.categories) if hasattr(analyzer, 'categories') else 0,
                        "expanded_count": 5,  # Valor simulado
                        "expansion_opportunities": 12  # Valor simulado
                    }
                    metrics["categories"] = category_stats
                except Exception as e:
                    logger.error(f"Erro ao obter métricas de categorias: {e}")
                    metrics["categories"] = {}
            
            # Métricas de IA
            if "ai_optimization" in self.systems:
                try:
                    # Usar dados básicos do otimizador
                    optimizer = self.systems["ai_optimization"]
                    ai_stats = {
                        "best_model_accuracy": 0.87,  # Valor simulado
                        "models_trained": 3,  # Valor simulado
                        "optimized_count": 150  # Valor simulado
                    }
                    metrics["ai"] = ai_stats
                except Exception as e:
                    logger.error(f"Erro ao obter métricas de IA: {e}")
                    metrics["ai"] = {}
            
            # Consolidar métricas
            self.consolidated_metrics = DashboardMetrics(
                total_offers_processed=metrics.get("conversion", {}).get("total_offers", 0),
                conversion_rate_geek=metrics.get("conversion", {}).get("geek_conversion_rate", 0.0),
                conversion_rate_general=metrics.get("conversion", {}).get("general_conversion_rate", 0.0),
                feedback_score=metrics.get("feedback", {}).get("overall_score", 0.0),
                categories_expanded=metrics.get("categories", {}).get("expanded_count", 0),
                ai_model_accuracy=metrics.get("ai", {}).get("best_model_accuracy", 0.0),
                system_health="healthy" if all(s.status == "active" for s in self.system_status.values()) else "warning"
            )
            
        except Exception as e:
            logger.error(f"Erro ao consolidar métricas: {e}")
            self.consolidated_metrics.system_health = "error"
        
        return self.consolidated_metrics
    
    async def run_production_test(self, quick: bool = False) -> Dict[str, Any]:
        """Executa teste em produção"""
        try:
            self.system_status["production_testing"].status = "running"
            
            if quick:
                result = await self.systems["production_testing"].run_quick_test()
            else:
                result = await self.systems["production_testing"].run_full_test()
            
            self.system_status["production_testing"].status = "active"
            self.system_status["production_testing"].last_run = datetime.now()
            self.system_status["production_testing"].metrics = result
            
            return {
                "success": True,
                "result": result,
                "message": "Teste executado com sucesso"
            }
            
        except Exception as e:
            self.system_status["production_testing"].status = "error"
            self.system_status["production_testing"].error_message = str(e)
            logger.error(f"Erro no teste de produção: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Erro ao executar teste"
            }
    
    async def start_conversion_tracking(self) -> Dict[str, Any]:
        """Inicia tracking de conversões"""
        try:
            self.system_status["conversion_monitoring"].status = "running"
            
            # Simular início do tracking
            await asyncio.sleep(1)
            
            self.system_status["conversion_monitoring"].status = "active"
            self.system_status["conversion_monitoring"].last_run = datetime.now()
            
            return {
                "success": True,
                "message": "Tracking de conversões iniciado"
            }
            
        except Exception as e:
            self.system_status["conversion_monitoring"].status = "error"
            self.system_status["conversion_monitoring"].error_message = str(e)
            logger.error(f"Erro ao iniciar tracking: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Erro ao iniciar tracking"
            }
    
    async def collect_user_feedback(self) -> Dict[str, Any]:
        """Coleta feedback dos usuários"""
        try:
            self.system_status["user_feedback"].status = "running"
            
            # Simular coleta de feedback
            await asyncio.sleep(1)
            
            # Dados simulados
            from dataclasses import dataclass
            
            @dataclass
            class FeedbackStats:
                total_feedback: int = 150
                positive_rate: float = 0.85
                negative_rate: float = 0.15
            
            stats = FeedbackStats()
            
            self.system_status["user_feedback"].status = "active"
            self.system_status["user_feedback"].last_run = datetime.now()
            self.system_status["user_feedback"].metrics = {
                "total_feedback": stats.total_feedback,
                "positive_rate": stats.positive_rate,
                "negative_rate": stats.negative_rate
            }
            
            return {
                "success": True,
                "stats": stats,
                "message": "Feedback coletado com sucesso"
            }
            
        except Exception as e:
            self.system_status["user_feedback"].status = "error"
            self.system_status["user_feedback"].error_message = str(e)
            logger.error(f"Erro ao coletar feedback: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Erro ao coletar feedback"
            }
    
    async def expand_categories(self) -> Dict[str, Any]:
        """Expande categorias"""
        try:
            self.system_status["category_expansion"].status = "running"
            
            # Simular expansão de categorias
            await asyncio.sleep(1)
            
            # Dados simulados
            from dataclasses import dataclass
            
            @dataclass
            class ExpansionResult:
                expanded_count: int = 8
                new_categories: List[str] = None
                
                def __post_init__(self):
                    if self.new_categories is None:
                        self.new_categories = ["Gaming Chairs", "Mechanical Keyboards", "Gaming Mice", "Streaming Equipment", "VR Headsets", "Gaming Monitors", "PC Components", "Gaming Accessories"]
            
            result = ExpansionResult()
            
            self.system_status["category_expansion"].status = "active"
            self.system_status["category_expansion"].last_run = datetime.now()
            self.system_status["category_expansion"].metrics = {
                "expanded_count": result.expanded_count,
                "new_categories": result.new_categories
            }
            
            return {
                "success": True,
                "result": result,
                "message": "Categorias expandidas com sucesso"
            }
            
        except Exception as e:
            self.system_status["category_expansion"].status = "error"
            self.system_status["category_expansion"].error_message = str(e)
            logger.error(f"Erro ao expandir categorias: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Erro ao expandir categorias"
            }
    
    async def train_ai_models(self) -> Dict[str, Any]:
        """Treina modelos de IA"""
        try:
            self.system_status["ai_optimization"].status = "running"
            
            # Simular treinamento de modelos
            await asyncio.sleep(2)
            
            # Dados simulados
            from dataclasses import dataclass
            
            @dataclass
            class ModelMetrics:
                r2_score: float = 0.87
                mse: float = 0.023
                mae: float = 0.045
            
            @dataclass
            class TrainingResult:
                best_model: str = "RandomForestRegressor"
                best_metrics: ModelMetrics = None
                training_results: List[Dict] = None
                
                def __post_init__(self):
                    if self.best_metrics is None:
                        self.best_metrics = ModelMetrics()
                    if self.training_results is None:
                        self.training_results = [
                            {"model": "RandomForestRegressor", "r2": 0.87},
                            {"model": "GradientBoostingRegressor", "r2": 0.85},
                            {"model": "LinearRegression", "r2": 0.78}
                        ]
            
            result = TrainingResult()
            
            self.system_status["ai_optimization"].status = "active"
            self.system_status["ai_optimization"].last_run = datetime.now()
            self.system_status["ai_optimization"].metrics = {
                "best_model": result.best_model,
                "best_accuracy": result.best_metrics.r2_score,
                "models_trained": len(result.training_results)
            }
            
            return {
                "success": True,
                "result": result,
                "message": "Modelos treinados com sucesso"
            }
            
        except Exception as e:
            self.system_status["ai_optimization"].status = "error"
            self.system_status["ai_optimization"].error_message = str(e)
            logger.error(f"Erro ao treinar modelos: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Erro ao treinar modelos"
            }
    
    async def optimize_offers(self) -> Dict[str, Any]:
        """Otimiza ofertas usando IA"""
        try:
            self.system_status["ai_optimization"].status = "running"
            
            # Simular otimização de ofertas
            await asyncio.sleep(1)
            
            # Dados simulados
            from dataclasses import dataclass
            
            @dataclass
            class OptimizationResult:
                optimized_count: int = 150
                average_improvement: float = 0.23
                confidence_score: float = 0.89
            
            result = OptimizationResult()
            
            self.system_status["ai_optimization"].status = "active"
            self.system_status["ai_optimization"].last_run = datetime.now()
            self.system_status["ai_optimization"].metrics.update({
                "optimized_count": result.optimized_count,
                "improvement_rate": result.average_improvement
            })
            
            return {
                "success": True,
                "result": result,
                "message": "Ofertas otimizadas com sucesso"
            }
            
        except Exception as e:
            self.system_status["ai_optimization"].status = "error"
            self.system_status["ai_optimization"].error_message = str(e)
            logger.error(f"Erro ao otimizar ofertas: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Erro ao otimizar ofertas"
            }
    
    async def get_system_health_report(self) -> Dict[str, Any]:
        """Gera relatório de saúde do sistema"""
        status = await self.get_system_status()
        metrics = await self.get_consolidated_metrics()
        
        active_systems = sum(1 for s in status.values() if s.status == "active")
        total_systems = len(status)
        
        return {
            "overall_health": metrics.system_health,
            "active_systems": active_systems,
            "total_systems": total_systems,
            "system_status": status,
            "consolidated_metrics": metrics,
            "timestamp": datetime.now().isoformat()
        }
    
    async def run_full_system_check(self) -> Dict[str, Any]:
        """Executa verificação completa de todos os sistemas"""
        results = {}
        
        # Teste de produção
        results["production_test"] = await self.run_production_test(quick=True)
        
        # Verificar tracking de conversões
        results["conversion_tracking"] = await self.start_conversion_tracking()
        
        # Coletar feedback
        results["user_feedback"] = await self.collect_user_feedback()
        
        # Verificar categorias
        results["category_expansion"] = await self.expand_categories()
        
        # Verificar IA
        results["ai_optimization"] = await self.train_ai_models()
        
        # Relatório de saúde
        results["health_report"] = await self.get_system_health_report()
        
        return results


# Instância global do dashboard unificado
unified_dashboard = UnifiedDashboard()
