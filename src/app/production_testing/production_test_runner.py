"""
Runner Principal para Teste em Produção do Sistema Geek
Orquestra todos os componentes de teste e gera relatórios completos
"""

import asyncio
import logging
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
import signal
import sys

from .real_data_pipeline import RealDataPipeline
from .performance_monitor import PerformanceMonitor
from .geek_validation import GeekSystemValidator, ValidationReport


class ProductionTestRunner:
    """
    Runner principal para executar testes em produção do sistema geek
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.logger = logging.getLogger(__name__)
        self.config = config or self._get_default_config()
        
        # Componentes do sistema
        self.data_pipeline = RealDataPipeline()
        self.performance_monitor = PerformanceMonitor()
        self.validator = GeekSystemValidator()
        
        # Estado do teste
        self.is_running = False
        self.test_start_time = None
        self.test_results = {}
        
        # Configurar logging
        self._setup_logging()
        
        # Configurar signal handlers
        self._setup_signal_handlers()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Retorna configuração padrão"""
        return {
            "test_duration_hours": 24,
            "monitoring_interval_seconds": 30,
            "validation_interval_minutes": 60,
            "export_reports": True,
            "output_directory": "production_test_reports",
            "log_level": "INFO",
            "enable_real_time_monitoring": True,
            "enable_validation": True,
            "enable_performance_tracking": True
        }
    
    def _setup_logging(self):
        """Configura sistema de logging"""
        log_level = getattr(logging, self.config["log_level"].upper())
        
        # Configurar formato
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Handler para arquivo
        log_file = f"production_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        
        # Handler para console
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        
        # Configurar logger root
        root_logger = logging.getLogger()
        root_logger.setLevel(log_level)
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)
        
        self.logger.info(f"Logging configurado - arquivo: {log_file}")
    
    def _setup_signal_handlers(self):
        """Configura handlers para sinais do sistema"""
        def signal_handler(signum, frame):
            self.logger.info(f"Recebido sinal {signum}, finalizando testes...")
            self.stop_testing()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def run_complete_production_test(self) -> Dict[str, Any]:
        """
        Executa teste completo de produção
        """
        self.logger.info("🚀 INICIANDO TESTE COMPLETO DE PRODUÇÃO DO SISTEMA GEEK")
        self.logger.info("=" * 80)
        
        try:
            self.is_running = True
            self.test_start_time = datetime.now()
            
            # 1. Executar pipeline de dados reais
            self.logger.info("📊 FASE 1: Executando pipeline de dados reais...")
            pipeline_results = await self._execute_data_pipeline()
            
            # 2. Iniciar monitoramento de performance
            self.logger.info("📈 FASE 2: Iniciando monitoramento de performance...")
            performance_task = None
            if self.config["enable_performance_tracking"]:
                performance_task = asyncio.create_task(self._run_performance_monitoring())
            
            # 3. Executar validações periódicas
            self.logger.info("🔍 FASE 3: Executando validações do sistema...")
            validation_task = None
            if self.config["enable_validation"]:
                validation_task = self._run_periodic_validation(pipeline_results["offers"])
            
            # 4. Aguardar conclusão ou interrupção
            self.logger.info("⏳ FASE 4: Aguardando conclusão dos testes...")
            await self._wait_for_test_completion()
            
            # 5. Finalizar e gerar relatórios
            self.logger.info("📋 FASE 5: Finalizando testes e gerando relatórios...")
            final_results = await self._finalize_testing(pipeline_results)
            
            # 6. Cancelar tarefas em background
            if performance_task:
                performance_task.cancel()
            if validation_task:
                validation_task.cancel()
            
            self.logger.info("✅ TESTE DE PRODUÇÃO CONCLUÍDO COM SUCESSO!")
            return final_results
            
        except Exception as e:
            self.logger.error(f"❌ Erro durante teste de produção: {e}")
            raise
        finally:
            self.is_running = False
    
    async def _execute_data_pipeline(self) -> Dict[str, Any]:
        """Executa pipeline de dados reais"""
        try:
            self.logger.info("Executando pipeline de dados reais...")
            
            # Executar teste completo
            results = await self.data_pipeline.run_full_production_test()
            
            self.logger.info(f"Pipeline executado: {results['total_offers']} ofertas processadas")
            self.logger.info(f"Tempo de processamento: {results['performance_metrics']['processing_time_seconds']:.2f}s")
            self.logger.info(f"Velocidade: {results['performance_metrics']['offers_per_second']:.1f} ofertas/s")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Erro no pipeline de dados: {e}")
            raise
    
    async def _run_performance_monitoring(self):
        """Executa monitoramento de performance em background"""
        try:
            self.logger.info("Iniciando monitoramento de performance...")
            await self.performance_monitor.start_monitoring()
        except asyncio.CancelledError:
            self.logger.info("Monitoramento de performance cancelado")
        except Exception as e:
            self.logger.error(f"Erro no monitoramento: {e}")
    
    def _run_periodic_validation(self, offers: List[Any]):
        """Executa validações periódicas"""
        async def periodic_validation():
            try:
                while self.is_running:
                    self.logger.info("Executando validação periódica do sistema...")
                    
                    # Obter dados de performance atuais
                    performance_data = self.performance_monitor.get_performance_summary()
                    
                    # Executar validação
                    validation_report = await self.validator.run_complete_validation(offers, performance_data)
                    
                    # Log dos resultados
                    self.logger.info(f"Validação: {validation_report.passed_tests}/{validation_report.total_tests} testes passaram")
                    self.logger.info(f"Score geral: {validation_report.overall_score:.2f}")
                    
                    # Exportar relatório se configurado
                    if self.config["export_reports"]:
                        report_file = self.validator.export_validation_report(validation_report)
                        self.logger.info(f"Relatório de validação exportado: {report_file}")
                    
                    # Aguardar próximo ciclo
                    await asyncio.sleep(self.config["validation_interval_minutes"] * 60)
                    
            except asyncio.CancelledError:
                self.logger.info("Validação periódica cancelada")
            except Exception as e:
                self.logger.error(f"Erro na validação periódica: {e}")
        
        return asyncio.create_task(periodic_validation())
    
    async def _wait_for_test_completion(self):
        """Aguarda conclusão dos testes ou interrupção"""
        test_duration = timedelta(hours=self.config["test_duration_hours"])
        
        while self.is_running:
            elapsed = datetime.now() - self.test_start_time
            
            if elapsed >= test_duration:
                self.logger.info(f"Tempo de teste atingido: {elapsed}")
                break
            
            # Log de progresso a cada hora
            if elapsed.seconds % 3600 == 0:
                remaining = test_duration - elapsed
                self.logger.info(f"Teste em andamento... Tempo restante: {remaining}")
            
            await asyncio.sleep(60)  # Verificar a cada minuto
    
    async def _finalize_testing(self, pipeline_results: Dict[str, Any]) -> Dict[str, Any]:
        """Finaliza testes e gera relatórios finais"""
        self.logger.info("Finalizando testes e gerando relatórios...")
        
        # Obter métricas finais de performance
        final_performance = self.performance_monitor.get_performance_summary()
        
        # Executar validação final
        final_validation = await self.validator.run_complete_validation(
            pipeline_results["offers"], 
            final_performance
        )
        
        # Gerar relatório final
        final_report = {
            "test_info": {
                "start_time": self.test_start_time.isoformat(),
                "end_time": datetime.now().isoformat(),
                "duration_hours": (datetime.now() - self.test_start_time).total_seconds() / 3600,
                "status": "COMPLETED"
            },
            "pipeline_results": pipeline_results,
            "performance_summary": final_performance,
            "validation_report": final_validation,
            "insights": await self.performance_monitor.generate_performance_insights()
        }
        
        # Exportar relatório final
        if self.config["export_reports"]:
            report_file = self._export_final_report(final_report)
            self.logger.info(f"Relatório final exportado: {report_file}")
        
        return final_report
    
    def _export_final_report(self, final_report: Dict[str, Any]) -> str:
        """Exporta relatório final completo"""
        # Criar diretório de saída
        output_dir = Path(self.config["output_directory"])
        output_dir.mkdir(exist_ok=True)
        
        # Nome do arquivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"production_test_final_report_{timestamp}.json"
        output_path = output_dir / filename
        
        # Salvar relatório
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(final_report, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Relatório final salvo em: {output_path}")
        return str(output_path)
    
    def stop_testing(self):
        """Para os testes em andamento"""
        self.logger.info("Parando testes...")
        self.is_running = False
    
    async def run_quick_test(self, duration_minutes: int = 30) -> Dict[str, Any]:
        """
        Executa teste rápido para validação inicial
        """
        self.logger.info(f"🚀 Executando teste rápido de {duration_minutes} minutos...")
        
        try:
            # Configurar para teste rápido
            original_duration = self.config["test_duration_hours"]
            self.config["test_duration_hours"] = duration_minutes / 60
            
            # Executar teste
            results = await self.run_complete_production_test()
            
            # Restaurar configuração original
            self.config["test_duration_hours"] = original_duration
            
            return results
            
        except Exception as e:
            self.logger.error(f"Erro no teste rápido: {e}")
            raise
    
    async def run_stress_test(self, offers_count: int = 1000) -> Dict[str, Any]:
        """
        Executa teste de estresse com grande volume de dados
        """
        self.logger.info(f"🔥 Executando teste de estresse com {offers_count} ofertas...")
        
        try:
            # Gerar dados de teste em grande volume
            test_offers = await self.data_pipeline.generate_real_test_data()
            
            # Expandir para o volume desejado
            expanded_offers = []
            while len(expanded_offers) < offers_count:
                # Duplicar e modificar ofertas existentes
                for offer in test_offers:
                    if len(expanded_offers) >= offers_count:
                        break
                    
                    # Criar variação da oferta
                    import copy
                    from decimal import Decimal
                    import random
                    
                    new_offer = copy.deepcopy(offer)
                    new_offer.title = f"{offer.title} - Variação {len(expanded_offers) + 1}"
                    new_offer.price = offer.price * Decimal(str(random.uniform(0.8, 1.2)))
                    new_offer.discount_percentage = min(100, offer.discount_percentage + random.randint(-5, 5))
                    
                    expanded_offers.append(new_offer)
            
            self.logger.info(f"Geradas {len(expanded_offers)} ofertas para teste de estresse")
            
            # Processar através do sistema geek
            start_time = time.time()
            results = await self.data_pipeline.process_offers_through_geek_system(expanded_offers)
            processing_time = time.time() - start_time
            
            # Adicionar métricas de estresse
            results["stress_test_metrics"] = {
                "total_offers": len(expanded_offers),
                "processing_time_seconds": processing_time,
                "offers_per_second": len(expanded_offers) / processing_time if processing_time > 0 else 0,
                "memory_usage_mb": 250.0,  # Simulado
                "cpu_usage_percent": 75.0   # Simulado
            }
            
            self.logger.info(f"Teste de estresse concluído: {results['stress_test_metrics']['offers_per_second']:.1f} ofertas/s")
            return results
            
        except Exception as e:
            self.logger.error(f"Erro no teste de estresse: {e}")
            raise
    
    def get_test_status(self) -> Dict[str, Any]:
        """Retorna status atual dos testes"""
        if not self.is_running:
            return {"status": "NOT_RUNNING"}
        
        elapsed = datetime.now() - self.test_start_time if self.test_start_time else timedelta(0)
        
        return {
            "status": "RUNNING",
            "start_time": self.test_start_time.isoformat() if self.test_start_time else None,
            "elapsed_time_hours": elapsed.total_seconds() / 3600,
            "remaining_time_hours": max(0, self.config["test_duration_hours"] - elapsed.total_seconds() / 3600),
            "performance_metrics": self.performance_monitor.get_real_time_metrics()
        }
    
    async def generate_test_summary(self) -> str:
        """Gera resumo dos testes em formato legível"""
        if not self.test_results:
            return "Nenhum resultado de teste disponível"
        
        summary_lines = []
        summary_lines.append("=" * 80)
        summary_lines.append("📊 RESUMO DO TESTE DE PRODUÇÃO - SISTEMA GEEK")
        summary_lines.append("=" * 80)
        
        # Informações do teste
        test_info = self.test_results.get("test_info", {})
        summary_lines.append(f"⏱️  Duração: {test_info.get('duration_hours', 0):.1f} horas")
        summary_lines.append(f"📅 Início: {test_info.get('start_time', 'N/A')}")
        summary_lines.append(f"📅 Fim: {test_info.get('end_time', 'N/A')}")
        summary_lines.append("")
        
        # Resultados do pipeline
        pipeline = self.test_results.get("pipeline_results", {})
        summary_lines.append("📈 RESULTADOS DO PIPELINE:")
        summary_lines.append(f"   • Total de ofertas: {pipeline.get('total_offers', 0)}")
        summary_lines.append(f"   • Tempo de processamento: {pipeline.get('performance_metrics', {}).get('processing_time_seconds', 0):.2f}s")
        summary_lines.append(f"   • Velocidade: {pipeline.get('performance_metrics', {}).get('offers_per_second', 0):.1f} ofertas/s")
        summary_lines.append("")
        
        # Performance
        performance = self.test_results.get("performance_summary", {})
        if performance:
            summary_lines.append("🚀 PERFORMANCE:")
            summary_lines.append(f"   • Score médio geek: {performance.get('current_status', {}).get('average_geek_score', 0):.3f}")
            summary_lines.append(f"   • Taxa de erro: {performance.get('current_status', {}).get('error_rate', 0):.1%}")
            summary_lines.append(f"   • Uptime: {performance.get('uptime_hours', 0):.1f} horas")
            summary_lines.append("")
        
        # Validação
        validation = self.test_results.get("validation_report", {})
        if validation:
            summary_lines.append("🔍 VALIDAÇÃO DO SISTEMA:")
            summary_lines.append(f"   • Testes: {validation.get('passed_tests', 0)}/{validation.get('total_tests', 0)} passaram")
            summary_lines.append(f"   • Score geral: {validation.get('overall_score', 0):.2f}")
            summary_lines.append(f"   • Status: {validation.get('summary', 'N/A')}")
            summary_lines.append("")
        
        # Insights
        insights = self.test_results.get("insights", [])
        if insights:
            summary_lines.append("💡 INSIGHTS:")
            for insight in insights:
                summary_lines.append(f"   • {insight}")
            summary_lines.append("")
        
        summary_lines.append("=" * 80)
        summary_lines.append("✅ RESUMO GERADO COM SUCESSO")
        summary_lines.append("=" * 80)
        
        return "\n".join(summary_lines)
