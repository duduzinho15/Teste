"""
Sistema de Validação do Sistema Geek para Teste em Produção
Valida se o sistema geek está funcionando corretamente com dados reais
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import statistics

from src.core.models import Offer
from src.core.geek_prioritizer import GeekPrioritizer
from src.core.geek_alerts import GeekAlertManager
from src.app.queue.quality_controller import QualityController
from config.garimpeiro_geek_config import GEEK_CATEGORIES_CONFIG


@dataclass
class ValidationResult:
    """Resultado de uma validação específica"""
    test_name: str
    status: str  # "PASS", "FAIL", "WARNING"
    score: float  # 0.0 a 1.0
    details: str
    recommendations: List[str]
    timestamp: str


@dataclass
class ValidationReport:
    """Relatório completo de validação"""
    timestamp: str
    total_tests: int
    passed_tests: int
    failed_tests: int
    warning_tests: int
    overall_score: float
    test_results: List[ValidationResult]
    summary: str
    critical_issues: List[str]
    improvement_suggestions: List[str]


class GeekSystemValidator:
    """
    Validador do sistema geek para testes em produção
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.geek_prioritizer = GeekPrioritizer()
        self.geek_alert_manager = GeekAlertManager()
        self.quality_controller = QualityController()
        
        # Critérios de validação
        self.validation_criteria = {
            "geek_score_distribution": {
                "min_primary_ratio": 0.3,  # 30% das ofertas devem ser primárias
                "min_secondary_ratio": 0.2,  # 20% devem ser secundárias
                "max_general_ratio": 0.5   # Máximo 50% gerais
            },
            "category_prioritization": {
                "gaming_consoles": {"min_score": 0.8, "expected_priority": "primary"},
                "pc_gaming": {"min_score": 0.7, "expected_priority": "primary"},
                "smart_home_tech": {"min_score": 0.7, "expected_priority": "primary"},
                "audio_tech": {"min_score": 0.6, "expected_priority": "primary"},
                "gaming_accessories": {"min_score": 0.6, "expected_priority": "secondary"},
                "anime_collectibles": {"min_score": 0.5, "expected_priority": "secondary"},
                "mobile_tech": {"min_score": 0.5, "expected_priority": "secondary"},
                "home_appliances": {"min_score": 0.3, "expected_priority": "general"}
            },
            "performance_thresholds": {
                "min_processing_speed": 5.0,  # 5 ofertas/segundo
                "max_error_rate": 0.05,       # 5% de erro
                "max_response_time": 2.0      # 2 segundos
            }
        }
    
    async def run_complete_validation(self, test_offers: List[Offer], 
                                    performance_data: Dict[str, Any]) -> ValidationReport:
        """
        Executa validação completa do sistema geek
        """
        self.logger.info("Iniciando validação completa do sistema geek...")
        
        validation_results = []
        
        # 1. Validar distribuição de scores geek
        score_distribution_result = await self._validate_geek_score_distribution(test_offers)
        validation_results.append(score_distribution_result)
        
        # 2. Validar priorização por categoria
        category_prioritization_result = await self._validate_category_prioritization(test_offers)
        validation_results.append(category_prioritization_result)
        
        # 3. Validar sistema de alertas
        alert_system_result = await self._validate_alert_system(test_offers)
        validation_results.append(alert_system_result)
        
        # 4. Validar integração com quality controller
        quality_integration_result = await self._validate_quality_integration(test_offers)
        validation_results.append(quality_integration_result)
        
        # 5. Validar performance geral
        performance_result = await self._validate_performance(performance_data)
        validation_results.append(performance_result)
        
        # 6. Validar consistência de dados
        data_consistency_result = await self._validate_data_consistency(test_offers)
        validation_results.append(data_consistency_result)
        
        # 7. Validar priorização de ofertas
        prioritization_result = await self._validate_offer_prioritization(test_offers)
        validation_results.append(prioritization_result)
        
        # Gerar relatório final
        report = self._generate_validation_report(validation_results)
        
        self.logger.info(f"Validação concluída: {report.passed_tests}/{report.total_tests} testes passaram")
        return report
    
    async def _validate_geek_score_distribution(self, offers: List[Offer]) -> ValidationResult:
        """Valida distribuição dos scores geek"""
        self.logger.info("Validando distribuição de scores geek...")
        
        if not offers:
            return ValidationResult(
                test_name="Distribuição de Scores Geek",
                status="FAIL",
                score=0.0,
                details="Nenhuma oferta disponível para validação",
                recommendations=["Verificar pipeline de dados"],
                timestamp=datetime.now().isoformat()
            )
        
        # Calcular scores para todas as ofertas
        geek_scores = []
        for offer in offers:
            score = self.geek_prioritizer.calculate_geek_score(offer)
            geek_scores.append(score)
        
        # Contar distribuição por nível
        primary_count = len([s for s in geek_scores if s.geek_level == "primary"])
        secondary_count = len([s for s in geek_scores if s.geek_level == "secondary"])
        general_count = len([s for s in geek_scores if s.geek_level == "general"])
        
        total_offers = len(offers)
        primary_ratio = primary_count / total_offers
        secondary_ratio = secondary_count / total_offers
        general_ratio = general_count / total_offers
        
        # Verificar critérios
        criteria = self.validation_criteria["geek_score_distribution"]
        issues = []
        recommendations = []
        
        if primary_ratio < criteria["min_primary_ratio"]:
            issues.append(f"Ratio de ofertas primárias muito baixo: {primary_ratio:.1%} < {criteria['min_primary_ratio']:.1%}")
            recommendations.append("Ajustar pesos de categorias primárias no config")
        
        if secondary_ratio < criteria["min_secondary_ratio"]:
            issues.append(f"Ratio de ofertas secundárias muito baixo: {secondary_ratio:.1%} < {criteria['min_secondary_ratio']:.1%}")
            recommendations.append("Revisar categorias secundárias")
        
        if general_ratio > criteria["max_general_ratio"]:
            issues.append(f"Ratio de ofertas gerais muito alto: {general_ratio:.1%} > {criteria['max_general_ratio']:.1%}")
            recommendations.append("Verificar se categorias estão sendo classificadas corretamente")
        
        # Calcular score de validação
        score = 1.0
        if issues:
            score = 0.5 if len(issues) <= 2 else 0.0
            status = "WARNING" if len(issues) <= 2 else "FAIL"
        else:
            status = "PASS"
        
        details = f"Primárias: {primary_ratio:.1%}, Secundárias: {secondary_ratio:.1%}, Gerais: {general_ratio:.1%}"
        if issues:
            details += f" | Problemas: {'; '.join(issues)}"
        
        return ValidationResult(
            test_name="Distribuição de Scores Geek",
            status=status,
            score=score,
            details=details,
            recommendations=recommendations,
            timestamp=datetime.now().isoformat()
        )
    
    async def _validate_category_prioritization(self, offers: List[Offer]) -> ValidationResult:
        """Valida priorização por categoria específica"""
        self.logger.info("Validando priorização por categoria...")
        
        if not offers:
            return ValidationResult(
                test_name="Priorização por Categoria",
                status="FAIL",
                score=0.0,
                details="Nenhuma oferta disponível",
                recommendations=["Verificar pipeline de dados"],
                timestamp=datetime.now().isoformat()
            )
        
        category_results = {}
        total_score = 0.0
        total_categories = 0
        
        for category_name, criteria in self.validation_criteria["category_prioritization"].items():
            # Filtrar ofertas da categoria
            category_offers = [o for o in offers if criteria["expected_priority"] in o.category or category_name in o.category]
            
            if not category_offers:
                continue
            
            # Calcular scores médios para a categoria
            category_scores = []
            for offer in category_offers:
                geek_score = self.geek_prioritizer.calculate_geek_score(offer)
                category_scores.append(geek_score.overall_score)
            
            avg_score = statistics.mean(category_scores) if category_scores else 0.0
            
            # Verificar se atende ao critério
            if avg_score >= criteria["min_score"]:
                category_results[category_name] = "PASS"
                total_score += 1.0
            else:
                category_results[category_name] = "FAIL"
                total_score += 0.0
            
            total_categories += 1
        
        # Calcular score geral
        overall_score = total_score / total_categories if total_categories > 0 else 0.0
        
        # Determinar status
        if overall_score >= 0.8:
            status = "PASS"
        elif overall_score >= 0.6:
            status = "WARNING"
        else:
            status = "FAIL"
        
        details = f"Score geral: {overall_score:.2f} | Categorias: {category_results}"
        
        recommendations = []
        if overall_score < 0.8:
            recommendations.append("Revisar pesos de categorias no config")
            recommendations.append("Verificar se produtos estão sendo classificados corretamente")
        
        return ValidationResult(
            test_name="Priorização por Categoria",
            status=status,
            score=overall_score,
            details=details,
            recommendations=recommendations,
            timestamp=datetime.now().isoformat()
        )
    
    async def _validate_alert_system(self, offers: List[Offer]) -> ValidationResult:
        """Valida sistema de alertas geek"""
        self.logger.info("Validando sistema de alertas...")
        
        if not offers:
            return ValidationResult(
                test_name="Sistema de Alertas",
                status="FAIL",
                score=0.0,
                details="Nenhuma oferta para testar alertas",
                recommendations=["Verificar pipeline de dados"],
                timestamp=datetime.now().isoformat()
            )
        
        # Testar sistema de alertas com algumas ofertas
        test_offers = offers[:10]  # Primeiras 10 ofertas
        alerts_generated = 0
        total_tested = 0
        
        for offer in test_offers:
            try:
                geek_score = self.geek_prioritizer.calculate_geek_score(offer)
                alert = await self.geek_alert_manager.check_offer_for_alerts(offer, geek_score)
                if alert:
                    alerts_generated += 1
                total_tested += 1
            except Exception as e:
                title = getattr(offer, 'title', 'Sem título')
                self.logger.error(f"Erro ao testar alerta para {title}: {e}")
        
        # Calcular métricas
        alert_rate = alerts_generated / total_tested if total_tested > 0 else 0.0
        
        # Critérios de validação
        if alert_rate >= 0.1:  # Pelo menos 10% das ofertas devem gerar alertas
            status = "PASS"
            score = 1.0
        elif alert_rate >= 0.05:
            status = "WARNING"
            score = 0.7
        else:
            status = "FAIL"
            score = 0.3
        
        details = f"Taxa de alertas: {alert_rate:.1%} ({alerts_generated}/{total_tested})"
        
        recommendations = []
        if alert_rate < 0.1:
            recommendations.append("Verificar thresholds de alertas")
            recommendations.append("Revisar critérios de prioridade")
        
        return ValidationResult(
            test_name="Sistema de Alertas",
            status=status,
            score=score,
            details=details,
            recommendations=recommendations,
            timestamp=datetime.now().isoformat()
        )
    
    async def _validate_quality_integration(self, offers: List[Offer]) -> ValidationResult:
        """Valida integração com quality controller"""
        self.logger.info("Validando integração com quality controller...")
        
        if not offers:
            return ValidationResult(
                test_name="Integração Quality Controller",
                status="FAIL",
                score=0.0,
                details="Nenhuma oferta para testar",
                recommendations=["Verificar pipeline de dados"],
                timestamp=datetime.now().isoformat()
            )
        
        # Testar integração
        test_offers = offers[:10]
        integration_working = 0
        total_tested = 0
        
        for offer in test_offers:
            try:
                # Verificar se quality controller aplica boost geek
                quality_result = self.quality_controller.evaluate_offer(offer)
                
                # Verificar se há detalhes de análise geek
                if "category_analysis" in quality_result.get("analysis_details", {}):
                    integration_working += 1
                
                total_tested += 1
            except Exception as e:
                title = getattr(offer, 'title', 'Sem título')
                self.logger.error(f"Erro ao testar integração para {title}: {e}")
        
        integration_rate = integration_working / total_tested if total_tested > 0 else 0.0
        
        if integration_rate >= 0.8:
            status = "PASS"
            score = 1.0
        elif integration_rate >= 0.6:
            status = "WARNING"
            score = 0.7
        else:
            status = "FAIL"
            score = 0.3
        
        details = f"Taxa de integração: {integration_rate:.1%} ({integration_working}/{total_tested})"
        
        recommendations = []
        if integration_rate < 0.8:
            recommendations.append("Verificar configuração do quality controller")
            recommendations.append("Revisar critérios geek_categories")
        
        return ValidationResult(
            test_name="Integração Quality Controller",
            status=status,
            score=score,
            details=details,
            recommendations=recommendations,
            timestamp=datetime.now().isoformat()
        )
    
    async def _validate_performance(self, performance_data: Dict[str, Any]) -> ValidationResult:
        """Valida performance geral do sistema"""
        self.logger.info("Validando performance do sistema...")
        
        if not performance_data:
            return ValidationResult(
                test_name="Performance do Sistema",
                status="FAIL",
                score=0.0,
                details="Dados de performance não disponíveis",
                recommendations=["Verificar monitor de performance"],
                timestamp=datetime.now().isoformat()
            )
        
        criteria = self.validation_criteria["performance_thresholds"]
        issues = []
        score = 1.0
        
        # Verificar velocidade de processamento
        offers_per_second = performance_data.get("offers_per_second", 0)
        if offers_per_second < criteria["min_processing_speed"]:
            issues.append(f"Velocidade baixa: {offers_per_second:.1f}/s < {criteria['min_processing_speed']}/s")
            score -= 0.3
        
        # Verificar taxa de erro
        error_rate = performance_data.get("error_rate", 0)
        if error_rate > criteria["max_error_rate"]:
            issues.append(f"Taxa de erro alta: {error_rate:.1%} > {criteria['max_error_rate']:.1%}")
            score -= 0.4
        
        # Verificar tempo de resposta
        processing_time = performance_data.get("average_processing_time", 0)
        if processing_time > criteria["max_response_time"]:
            issues.append(f"Tempo de resposta alto: {processing_time:.2f}s > {criteria['max_response_time']}s")
            score -= 0.3
        
        score = max(0.0, score)
        
        if score >= 0.8:
            status = "PASS"
        elif score >= 0.6:
            status = "WARNING"
        else:
            status = "FAIL"
        
        details = f"Score: {score:.2f} | Velocidade: {offers_per_second:.1f}/s | Erro: {error_rate:.1%} | Tempo: {processing_time:.2f}s"
        if issues:
            details += f" | Problemas: {'; '.join(issues)}"
        
        recommendations = []
        if issues:
            recommendations.append("Otimizar algoritmos de processamento")
            recommendations.append("Investigar causas de erros")
            recommendations.append("Revisar configurações de performance")
        
        return ValidationResult(
            test_name="Performance do Sistema",
            status=status,
            score=score,
            details=details,
            recommendations=recommendations,
            timestamp=datetime.now().isoformat()
        )
    
    async def _validate_data_consistency(self, offers: List[Offer]) -> ValidationResult:
        """Valida consistência dos dados"""
        self.logger.info("Validando consistência dos dados...")
        
        if not offers:
            return ValidationResult(
                test_name="Consistência de Dados",
                status="FAIL",
                score=0.0,
                details="Nenhuma oferta para validar",
                recommendations=["Verificar pipeline de dados"],
                timestamp=datetime.now().isoformat()
            )
        
        issues = []
        total_issues = 0
        
        for offer in offers:
            # Verificar campos obrigatórios
            title = getattr(offer, 'title', '')
            if not title or len(title.strip()) < 3:
                total_issues += 1
                issues.append(f"Título inválido: {title}")
            
            price = getattr(offer, 'price', 0)
            if not price or price <= 0:
                total_issues += 1
                issues.append(f"Preço inválido: {price}")
            
            category = getattr(offer, 'category', '')
            if not category:
                total_issues += 1
                issues.append(f"Categoria vazia para: {title}")
            
            url = getattr(offer, 'url', '')
            if not url or not url.startswith("http"):
                total_issues += 1
                issues.append(f"URL inválida para: {title}")
        
        # Calcular score
        total_offers = len(offers)
        error_rate = total_issues / total_offers if total_offers > 0 else 1.0
        
        if error_rate < 0.05:  # Menos de 5% de erros
            status = "PASS"
            score = 1.0
        elif error_rate < 0.1:  # Menos de 10% de erros
            status = "WARNING"
            score = 0.7
        else:
            status = "FAIL"
            score = 0.3
        
        details = f"Taxa de erro: {error_rate:.1%} ({total_issues}/{total_offers})"
        if issues:
            details += f" | Exemplos: {'; '.join(issues[:3])}"
        
        recommendations = []
        if error_rate > 0.05:
            recommendations.append("Implementar validação de dados mais rigorosa")
            recommendations.append("Revisar pipeline de ingestão")
        
        return ValidationResult(
            test_name="Consistência de Dados",
            status=status,
            score=score,
            details=details,
            recommendations=recommendations,
            timestamp=datetime.now().isoformat()
        )
    
    async def _validate_offer_prioritization(self, offers: List[Offer]) -> ValidationResult:
        """Valida priorização geral de ofertas"""
        self.logger.info("Validando priorização de ofertas...")
        
        if not offers:
            return ValidationResult(
                test_name="Priorização de Ofertas",
                status="FAIL",
                score=0.0,
                details="Nenhuma oferta para priorizar",
                recommendations=["Verificar pipeline de dados"],
                timestamp=datetime.now().isoformat()
            )
        
        try:
            # Testar priorização
            prioritized_offers = self.geek_prioritizer.prioritize_offers(offers)
            
            if not prioritized_offers:
                return ValidationResult(
                    test_name="Priorização de Ofertas",
                    status="FAIL",
                    score=0.0,
                    details="Falha na priorização - lista vazia",
                    recommendations=["Verificar lógica de priorização"],
                    timestamp=datetime.now().isoformat()
                )
            
            # Verificar se ofertas com scores altos estão no topo
            top_offers = prioritized_offers[:5]  # Top 5
            
            # Calcular scores dos top offers
            top_scores = []
            for offer in top_offers:
                geek_score = self.geek_prioritizer.calculate_geek_score(offer)
                top_scores.append(geek_score.overall_score)
            
            avg_top_score = statistics.mean(top_scores) if top_scores else 0.0
            
            # Verificar se scores altos estão sendo priorizados
            if avg_top_score >= 0.6:
                status = "PASS"
                score = 1.0
            elif avg_top_score >= 0.4:
                status = "WARNING"
                score = 0.7
            else:
                status = "FAIL"
                score = 0.3
            
            details = f"Score médio dos top 5: {avg_top_score:.3f} | Total priorizado: {len(prioritized_offers)}"
            
            recommendations = []
            if avg_top_score < 0.6:
                recommendations.append("Revisar algoritmo de priorização")
                recommendations.append("Verificar pesos de categorias")
            
            return ValidationResult(
                test_name="Priorização de Ofertas",
                status=status,
                score=score,
                details=details,
                recommendations=recommendations,
                timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            return ValidationResult(
                test_name="Priorização de Ofertas",
                status="FAIL",
                score=0.0,
                details=f"Erro na priorização: {str(e)}",
                recommendations=["Investigar erro de priorização"],
                timestamp=datetime.now().isoformat()
            )
    
    def _generate_validation_report(self, results: List[ValidationResult]) -> ValidationReport:
        """Gera relatório final de validação"""
        total_tests = len(results)
        passed_tests = len([r for r in results if r.status == "PASS"])
        failed_tests = len([r for r in results if r.status == "FAIL"])
        warning_tests = len([r for r in results if r.status == "WARNING"])
        
        overall_score = sum(r.score for r in results) / total_tests if total_tests > 0 else 0.0
        
        # Gerar resumo
        if overall_score >= 0.8:
            summary = "✅ Sistema geek funcionando adequadamente"
        elif overall_score >= 0.6:
            summary = "⚠️ Sistema geek com algumas questões menores"
        else:
            summary = "❌ Sistema geek com problemas significativos"
        
        # Identificar problemas críticos
        critical_issues = []
        for result in results:
            if result.status == "FAIL":
                critical_issues.append(f"{result.test_name}: {result.details}")
        
        # Sugestões de melhoria
        improvement_suggestions = []
        for result in results:
            improvement_suggestions.extend(result.recommendations)
        
        # Remover duplicatas
        improvement_suggestions = list(set(improvement_suggestions))
        
        return ValidationReport(
            timestamp=datetime.now().isoformat(),
            total_tests=total_tests,
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            warning_tests=warning_tests,
            overall_score=overall_score,
            test_results=results,
            summary=summary,
            critical_issues=critical_issues,
            improvement_suggestions=improvement_suggestions
        )
    
    def export_validation_report(self, report: ValidationReport, output_file: str = None) -> str:
        """Exporta relatório de validação para arquivo"""
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"geek_validation_report_{timestamp}.json"
        
        # Converter para dict para serialização
        report_dict = asdict(report)
        
        # Salvar arquivo
        output_path = Path(output_file)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report_dict, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Relatório de validação exportado para: {output_path}")
        return str(output_path)
