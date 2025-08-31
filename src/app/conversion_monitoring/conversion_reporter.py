"""
Sistema de Relatórios de Conversão Geek vs Geral
Gera relatórios detalhados e exportáveis de métricas de conversão
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
import csv
from decimal import Decimal

from .conversion_tracker import ConversionTracker, ConversionMetrics
from .conversion_analyzer import ConversionAnalyzer, ConversionReport


@dataclass
class ReportConfig:
    """Configuração de relatório"""
    report_type: str  # "daily", "weekly", "monthly", "custom"
    period: str  # "day", "week", "month"
    include_insights: bool = True
    include_trends: bool = True
    include_recommendations: bool = True
    include_category_breakdown: bool = True
    export_format: str = "json"  # "json", "csv", "html"
    output_directory: str = "reports"


@dataclass
class ConversionReportData:
    """Dados completos de relatório de conversão"""
    report_info: Dict[str, Any]
    metrics_summary: Dict[str, Any]
    geek_vs_general: Dict[str, Any]
    category_analysis: Dict[str, Any]
    insights: List[Dict[str, Any]]
    trends: List[Dict[str, Any]]
    recommendations: List[str]
    performance_score: float
    raw_data: Dict[str, Any]


class ConversionReporter:
    """
    Sistema de geração de relatórios de conversão
    """
    
    def __init__(self, tracker: ConversionTracker, analyzer: ConversionAnalyzer):
        self.logger = logging.getLogger(__name__)
        self.tracker = tracker
        self.analyzer = analyzer
        
        # Configurações padrão
        self.default_config = ReportConfig(
            report_type="daily",
            period="day",
            include_insights=True,
            include_trends=True,
            include_recommendations=True,
            include_category_breakdown=True,
            export_format="json",
            output_directory="reports"
        )
        
        # Criar diretório de relatórios
        Path(self.default_config.output_directory).mkdir(exist_ok=True)
    
    async def generate_report(self, config: Optional[ReportConfig] = None) -> ConversionReportData:
        """
        Gera relatório completo de conversão
        """
        if config is None:
            config = self.default_config
        
        self.logger.info(f"Gerando relatório de conversão: {config.report_type}")
        
        try:
            # Obter métricas
            metrics = await self.tracker.calculate_conversion_metrics(config.period)
            
            # Gerar análise
            analysis = await self.analyzer.analyze_conversions(config.period)
            
            # Preparar dados do relatório
            report_data = ConversionReportData(
                report_info=self._create_report_info(config),
                metrics_summary=self._create_metrics_summary(metrics),
                geek_vs_general=self._create_geek_vs_general_comparison(metrics),
                category_analysis=self._create_category_analysis(metrics) if config.include_category_breakdown else {},
                insights=[asdict(insight) for insight in analysis.insights] if config.include_insights else [],
                trends=[asdict(trend) for trend in analysis.trends] if config.include_trends else [],
                recommendations=analysis.recommendations if config.include_recommendations else [],
                performance_score=analysis.performance_score,
                raw_data={
                    "metrics": asdict(metrics),
                    "analysis": asdict(analysis)
                }
            )
            
            self.logger.info(f"Relatório gerado com sucesso: {len(report_data.insights)} insights, {len(report_data.trends)} tendências")
            return report_data
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar relatório: {e}")
            return self._create_empty_report_data(config)
    
    def _create_report_info(self, config: ReportConfig) -> Dict[str, Any]:
        """Cria informações do relatório"""
        return {
            "generated_at": datetime.now().isoformat(),
            "report_type": config.report_type,
            "period": config.period,
            "config": asdict(config),
            "tracker_stats": {
                "total_events": len(self.tracker.conversion_events),
                "tracking_enabled": self.tracker.tracking_enabled,
                "data_file": self.tracker.data_file
            }
        }
    
    def _create_metrics_summary(self, metrics: ConversionMetrics) -> Dict[str, Any]:
        """Cria resumo das métricas"""
        return {
            "total_conversions": metrics.total_conversions,
            "total_revenue": float(metrics.total_revenue),
            "total_commission": float(metrics.total_commission),
            "average_order_value": float(metrics.average_order_value),
            "overall_conversion_rate": metrics.overall_conversion_rate,
            "geek_conversion_rate": metrics.geek_conversion_rate,
            "general_conversion_rate": metrics.general_conversion_rate,
            "period": metrics.period,
            "timestamp": metrics.timestamp
        }
    
    def _create_geek_vs_general_comparison(self, metrics: ConversionMetrics) -> Dict[str, Any]:
        """Cria comparação geek vs geral"""
        total_conversions = metrics.total_conversions
        
        if total_conversions > 0:
            geek_percentage = (metrics.geek_conversions / total_conversions) * 100
            general_percentage = (metrics.general_conversions / total_conversions) * 100
        else:
            geek_percentage = 0
            general_percentage = 0
        
        return {
            "geek": {
                "conversions": metrics.geek_conversions,
                "revenue": float(metrics.geek_revenue),
                "commission": float(metrics.geek_commission),
                "conversion_rate": metrics.geek_conversion_rate,
                "percentage_of_total": geek_percentage,
                "trend": metrics.geek_trend,
                "avg_order_value": float(metrics.geek_revenue / max(metrics.geek_conversions, 1))
            },
            "general": {
                "conversions": metrics.general_conversions,
                "revenue": float(metrics.general_revenue),
                "commission": float(metrics.general_commission),
                "conversion_rate": metrics.general_conversion_rate,
                "percentage_of_total": general_percentage,
                "trend": metrics.general_trend,
                "avg_order_value": float(metrics.general_revenue / max(metrics.general_conversions, 1))
            },
            "comparison": {
                "geek_vs_general_ratio": metrics.geek_conversions / max(metrics.general_conversions, 1),
                "geek_revenue_ratio": float(metrics.geek_revenue / max(metrics.general_revenue, 1)),
                "geek_conversion_rate_ratio": metrics.geek_conversion_rate / max(metrics.general_conversion_rate, 0.001)
            }
        }
    
    def _create_category_analysis(self, metrics: ConversionMetrics) -> Dict[str, Any]:
        """Cria análise por categoria"""
        if not metrics.category_performance:
            return {}
        
        # Ordenar categorias por receita
        sorted_categories = sorted(
            metrics.category_performance.items(),
            key=lambda x: x[1].get("revenue", 0),
            reverse=True
        )
        
        category_analysis = {
            "total_categories": len(metrics.category_performance),
            "top_performing": [],
            "worst_performing": [],
            "category_breakdown": {}
        }
        
        # Top 5 categorias
        for i, (category, stats) in enumerate(sorted_categories[:5]):
            category_analysis["top_performing"].append({
                "rank": i + 1,
                "category": category,
                "conversions": stats.get("conversions", 0),
                "revenue": float(stats.get("revenue", 0)),
                "commission": float(stats.get("commission", 0)),
                "geek_conversions": stats.get("geek_conversions", 0),
                "general_conversions": stats.get("general_conversions", 0)
            })
        
        # Piores 5 categorias
        for i, (category, stats) in enumerate(sorted_categories[-5:]):
            category_analysis["worst_performing"].append({
                "rank": len(sorted_categories) - i,
                "category": category,
                "conversions": stats.get("conversions", 0),
                "revenue": float(stats.get("revenue", 0)),
                "commission": float(stats.get("commission", 0)),
                "geek_conversions": stats.get("geek_conversions", 0),
                "general_conversions": stats.get("general_conversions", 0)
            })
        
        # Breakdown completo
        for category, stats in metrics.category_performance.items():
            category_analysis["category_breakdown"][category] = {
                "conversions": stats.get("conversions", 0),
                "revenue": float(stats.get("revenue", 0)),
                "commission": float(stats.get("commission", 0)),
                "geek_conversions": stats.get("geek_conversions", 0),
                "general_conversions": stats.get("general_conversions", 0),
                "geek_percentage": (stats.get("geek_conversions", 0) / max(stats.get("conversions", 1), 1)) * 100
            }
        
        return category_analysis
    
    def _create_empty_report_data(self, config: ReportConfig) -> ConversionReportData:
        """Cria relatório vazio"""
        return ConversionReportData(
            report_info=self._create_report_info(config),
            metrics_summary={},
            geek_vs_general={},
            category_analysis={},
            insights=[],
            trends=[],
            recommendations=["Dados insuficientes para análise"],
            performance_score=0.0,
            raw_data={}
        )
    
    async def export_report(self, report_data: ConversionReportData, 
                          config: Optional[ReportConfig] = None) -> str:
        """
        Exporta relatório para arquivo
        """
        if config is None:
            config = self.default_config
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if config.export_format == "json":
                return await self._export_json_report(report_data, config, timestamp)
            elif config.export_format == "csv":
                return await self._export_csv_report(report_data, config, timestamp)
            elif config.export_format == "html":
                return await self._export_html_report(report_data, config, timestamp)
            else:
                raise ValueError(f"Formato de exportação não suportado: {config.export_format}")
                
        except Exception as e:
            self.logger.error(f"Erro ao exportar relatório: {e}")
            return ""
    
    async def _export_json_report(self, report_data: ConversionReportData, 
                                config: ReportConfig, timestamp: str) -> str:
        """Exporta relatório em formato JSON"""
        filename = f"conversion_report_{config.report_type}_{timestamp}.json"
        filepath = Path(config.output_directory) / filename
        
        try:
            # Função auxiliar para converter Decimal para string
            def decimal_to_str(obj):
                if isinstance(obj, Decimal):
                    return str(obj)
                elif isinstance(obj, dict):
                    return {k: decimal_to_str(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [decimal_to_str(item) for item in obj]
                else:
                    return obj
            
            report_dict = decimal_to_str(asdict(report_data))
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(report_dict, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Relatório JSON exportado: {filepath}")
            return str(filepath)
            
        except Exception as e:
            self.logger.error(f"Erro ao exportar JSON: {e}")
            return ""
    
    async def _export_csv_report(self, report_data: ConversionReportData, 
                               config: ReportConfig, timestamp: str) -> str:
        """Exporta relatório em formato CSV"""
        filename = f"conversion_report_{config.report_type}_{timestamp}.csv"
        filepath = Path(config.output_directory) / filename
        
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Cabeçalho
                writer.writerow(["Relatório de Conversão Geek vs Geral"])
                writer.writerow([f"Gerado em: {report_data.report_info['generated_at']}"])
                writer.writerow([f"Período: {config.period}"])
                writer.writerow([])
                
                # Métricas resumidas
                writer.writerow(["MÉTRICAS RESUMIDAS"])
                writer.writerow(["Métrica", "Valor"])
                for key, value in report_data.metrics_summary.items():
                    writer.writerow([key, value])
                writer.writerow([])
                
                # Comparação geek vs geral
                writer.writerow(["COMPARAÇÃO GEEK VS GERAL"])
                writer.writerow(["Segmento", "Conversões", "Receita", "Taxa de Conversão", "Ticket Médio"])
                
                geek_data = report_data.geek_vs_general.get("geek", {})
                general_data = report_data.geek_vs_general.get("general", {})
                
                writer.writerow([
                    "Geek",
                    geek_data.get("conversions", 0),
                    f"R$ {geek_data.get('revenue', 0):.2f}",
                    f"{geek_data.get('conversion_rate', 0):.3%}",
                    f"R$ {geek_data.get('avg_order_value', 0):.2f}"
                ])
                
                writer.writerow([
                    "Geral",
                    general_data.get("conversions", 0),
                    f"R$ {general_data.get('revenue', 0):.2f}",
                    f"{general_data.get('conversion_rate', 0):.3%}",
                    f"R$ {general_data.get('avg_order_value', 0):.2f}"
                ])
                writer.writerow([])
                
                # Top categorias
                if report_data.category_analysis.get("top_performing"):
                    writer.writerow(["TOP 5 CATEGORIAS"])
                    writer.writerow(["Rank", "Categoria", "Conversões", "Receita", "Comissão"])
                    
                    for cat in report_data.category_analysis["top_performing"]:
                        writer.writerow([
                            cat["rank"],
                            cat["category"],
                            cat["conversions"],
                            f"R$ {cat['revenue']:.2f}",
                            f"R$ {cat['commission']:.2f}"
                        ])
                    writer.writerow([])
                
                # Insights
                if report_data.insights:
                    writer.writerow(["INSIGHTS"])
                    writer.writerow(["Tipo", "Título", "Descrição", "Severidade"])
                    
                    for insight in report_data.insights:
                        writer.writerow([
                            insight.get("insight_type", ""),
                            insight.get("title", ""),
                            insight.get("description", ""),
                            insight.get("severity", "")
                        ])
                    writer.writerow([])
                
                # Recomendações
                if report_data.recommendations:
                    writer.writerow(["RECOMENDAÇÕES"])
                    for rec in report_data.recommendations:
                        writer.writerow([rec])
            
            self.logger.info(f"Relatório CSV exportado: {filepath}")
            return str(filepath)
            
        except Exception as e:
            self.logger.error(f"Erro ao exportar CSV: {e}")
            return ""
    
    async def _export_html_report(self, report_data: ConversionReportData, 
                                config: ReportConfig, timestamp: str) -> str:
        """Exporta relatório em formato HTML"""
        filename = f"conversion_report_{config.report_type}_{timestamp}.html"
        filepath = Path(config.output_directory) / filename
        
        try:
            html_content = self._generate_html_content(report_data, config)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            self.logger.info(f"Relatório HTML exportado: {filepath}")
            return str(filepath)
            
        except Exception as e:
            self.logger.error(f"Erro ao exportar HTML: {e}")
            return ""
    
    def _generate_html_content(self, report_data: ConversionReportData, config: ReportConfig) -> str:
        """Gera conteúdo HTML do relatório"""
        html = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Relatório de Conversão Geek vs Geral</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ text-align: center; border-bottom: 2px solid #333; padding-bottom: 20px; margin-bottom: 30px; }}
        .section {{ margin-bottom: 30px; }}
        .section h2 {{ color: #333; border-left: 4px solid #007bff; padding-left: 10px; }}
        .metric-card {{ background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 10px 0; }}
        .metric-value {{ font-size: 24px; font-weight: bold; color: #007bff; }}
        .comparison-table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
        .comparison-table th, .comparison-table td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        .comparison-table th {{ background-color: #f2f2f2; }}
        .insight {{ background: #fff3cd; border: 1px solid #ffeaa7; padding: 10px; margin: 10px 0; border-radius: 5px; }}
        .insight.critical {{ background: #f8d7da; border-color: #f5c6cb; }}
        .insight.opportunity {{ background: #d1ecf1; border-color: #bee5eb; }}
        .recommendation {{ background: #d4edda; border: 1px solid #c3e6cb; padding: 10px; margin: 5px 0; border-radius: 5px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Relatório de Conversão Geek vs Geral</h1>
            <p>Gerado em: {report_data.report_info['generated_at']}</p>
            <p>Período: {config.period}</p>
        </div>
        
        <div class="section">
            <h2>📈 Métricas Resumidas</h2>
            <div class="metric-card">
                <div class="metric-value">{report_data.metrics_summary.get('total_conversions', 0)}</div>
                <div>Total de Conversões</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">R$ {report_data.metrics_summary.get('total_revenue', 0):.2f}</div>
                <div>Receita Total</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{report_data.performance_score:.1f}/100</div>
                <div>Score de Performance</div>
            </div>
        </div>
        
        <div class="section">
            <h2>🎯 Comparação Geek vs Geral</h2>
            <table class="comparison-table">
                <tr>
                    <th>Segmento</th>
                    <th>Conversões</th>
                    <th>Receita</th>
                    <th>Taxa de Conversão</th>
                    <th>Ticket Médio</th>
                </tr>
                <tr>
                    <td>🎮 Geek</td>
                    <td>{report_data.geek_vs_general.get('geek', {}).get('conversions', 0)}</td>
                    <td>R$ {report_data.geek_vs_general.get('geek', {}).get('revenue', 0):.2f}</td>
                    <td>{report_data.geek_vs_general.get('geek', {}).get('conversion_rate', 0):.3%}</td>
                    <td>R$ {report_data.geek_vs_general.get('geek', {}).get('avg_order_value', 0):.2f}</td>
                </tr>
                <tr>
                    <td>🌐 Geral</td>
                    <td>{report_data.geek_vs_general.get('general', {}).get('conversions', 0)}</td>
                    <td>R$ {report_data.geek_vs_general.get('general', {}).get('revenue', 0):.2f}</td>
                    <td>{report_data.geek_vs_general.get('general', {}).get('conversion_rate', 0):.3%}</td>
                    <td>R$ {report_data.geek_vs_general.get('general', {}).get('avg_order_value', 0):.2f}</td>
                </tr>
            </table>
        </div>
        """
        
        # Adicionar seção de insights
        if report_data.insights:
            html += """
        <div class="section">
            <h2>💡 Insights</h2>
            """
            for insight in report_data.insights:
                severity_class = insight.get('severity', '')
                html += f"""
            <div class="insight {severity_class}">
                <strong>{insight.get('title', '')}</strong><br>
                {insight.get('description', '')}
            </div>
                """
            html += """
        </div>
            """
        
        # Adicionar seção de recomendações
        if report_data.recommendations:
            html += """
        <div class="section">
            <h2>🚀 Recomendações</h2>
            """
            for rec in report_data.recommendations:
                html += f"""
            <div class="recommendation">
                • {rec}
            </div>
                """
            html += """
        </div>
            """
        
        html += """
    </div>
</body>
</html>
        """
        
        return html
    
    async def generate_daily_report(self) -> str:
        """Gera e exporta relatório diário"""
        config = ReportConfig(
            report_type="daily",
            period="day",
            export_format="json"
        )
        
        report_data = await self.generate_report(config)
        return await self.export_report(report_data, config)
    
    async def generate_weekly_report(self) -> str:
        """Gera e exporta relatório semanal"""
        config = ReportConfig(
            report_type="weekly",
            period="week",
            export_format="html"
        )
        
        report_data = await self.generate_report(config)
        return await self.export_report(report_data, config)
    
    async def generate_monthly_report(self) -> str:
        """Gera e exporta relatório mensal"""
        config = ReportConfig(
            report_type="monthly",
            period="month",
            export_format="csv"
        )
        
        report_data = await self.generate_report(config)
        return await self.export_report(report_data, config)
