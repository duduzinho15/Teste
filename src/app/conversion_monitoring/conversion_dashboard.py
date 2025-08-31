"""
Dashboard de Conversões Geek vs Geral
Interface em tempo real para monitoramento de métricas de conversão
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import json
from pathlib import Path

from .conversion_tracker import ConversionTracker
from .conversion_analyzer import ConversionAnalyzer, ConversionReport


class ConversionDashboard:
    """
    Dashboard de conversões em tempo real
    """
    
    def __init__(self, tracker: ConversionTracker, analyzer: ConversionAnalyzer):
        self.logger = logging.getLogger(__name__)
        self.tracker = tracker
        self.analyzer = analyzer
        
        # Configurações do dashboard
        self.update_interval = 30  # 30 segundos
        self.dashboard_enabled = True
        self.auto_refresh = True
        
        # Estado do dashboard
        self.current_data = {}
        self.last_update = None
        self.dashboard_stats = {
            "total_updates": 0,
            "last_refresh": None,
            "uptime_seconds": 0
        }
    
    async def start_dashboard(self):
        """Inicia o dashboard em modo contínuo"""
        self.logger.info("Iniciando dashboard de conversões...")
        start_time = datetime.now()
        
        try:
            while self.dashboard_enabled:
                # Atualizar dados
                await self._update_dashboard_data()
                
                # Exibir dashboard
                self._display_dashboard()
                
                # Aguardar próximo update
                if self.auto_refresh:
                    await asyncio.sleep(self.update_interval)
                
                # Atualizar estatísticas
                self.dashboard_stats["uptime_seconds"] = (datetime.now() - start_time).total_seconds()
                
        except KeyboardInterrupt:
            self.logger.info("Dashboard interrompido pelo usuário")
        except Exception as e:
            self.logger.error(f"Erro no dashboard: {e}")
    
    async def _update_dashboard_data(self):
        """Atualiza dados do dashboard"""
        try:
            # Obter métricas em tempo real
            real_time_metrics = self.tracker.get_real_time_metrics()
            
            # Calcular métricas do dia
            daily_metrics = await self.tracker.calculate_conversion_metrics("day")
            
            # Gerar análise
            analysis_report = await self.analyzer.analyze_conversions("day")
            
            # Atualizar dados atuais
            self.current_data = {
                "real_time": real_time_metrics,
                "daily_metrics": daily_metrics,
                "analysis": analysis_report,
                "last_update": datetime.now().isoformat()
            }
            
            self.last_update = datetime.now()
            self.dashboard_stats["total_updates"] += 1
            self.dashboard_stats["last_refresh"] = datetime.now().isoformat()
            
        except Exception as e:
            self.logger.error(f"Erro ao atualizar dados do dashboard: {e}")
    
    def _display_dashboard(self):
        """Exibe o dashboard no console"""
        if not self.current_data:
            print("🔄 Carregando dashboard...")
            return
        
        # Limpar console (simulado)
        print("\n" + "="*80)
        print("📊 DASHBOARD DE CONVERSÕES GEEK VS GERAL")
        print("="*80)
        
        # Informações básicas
        real_time = self.current_data.get("real_time", {})
        current_metrics = real_time.get("current_metrics", {})
        
        print(f"🕐 Última atualização: {self._format_timestamp(self.current_data.get('last_update'))}")
        print(f"📈 Total de conversões hoje: {current_metrics.get('total_conversions_today', 0)}")
        print(f"💰 Receita total hoje: R$ {current_metrics.get('total_revenue_today', '0.00')}")
        
        # Métricas geek vs geral
        print("\n🎯 MÉTRICAS GEEK VS GERAL:")
        print("-" * 40)
        
        geek_conversions = current_metrics.get('geek_conversions_today', 0)
        general_conversions = current_metrics.get('general_conversions_today', 0)
        total_conversions = current_metrics.get('total_conversions_today', 0)
        
        if total_conversions > 0:
            geek_percentage = (geek_conversions / total_conversions) * 100
            general_percentage = (general_conversions / total_conversions) * 100
        else:
            geek_percentage = 0
            general_percentage = 0
        
        print(f"🎮 Geek: {geek_conversions} conversões ({geek_percentage:.1f}%) - R$ {current_metrics.get('geek_revenue_today', '0.00')}")
        print(f"🌐 Geral: {general_conversions} conversões ({general_percentage:.1f}%) - R$ {current_metrics.get('general_revenue_today', '0.00')}")
        
        # Análise e insights
        analysis = self.current_data.get("analysis")
        if analysis:
            print(f"\n📊 ANÁLISE E INSIGHTS:")
            print("-" * 40)
            print(f"📋 {analysis.summary}")
            print(f"🎯 Score de Performance: {analysis.performance_score:.1f}/100")
            
            # Mostrar insights críticos
            critical_insights = [i for i in analysis.insights if i.severity in ["high", "critical"]]
            if critical_insights:
                print(f"\n⚠️ INSIGHTS CRÍTICOS ({len(critical_insights)}):")
                for insight in critical_insights[:3]:  # Mostrar apenas 3
                    print(f"   • {insight.title}: {insight.description}")
            
            # Mostrar tendências
            if analysis.trends:
                print(f"\n📈 TENDÊNCIAS:")
                for trend in analysis.trends[:3]:  # Mostrar apenas 3
                    emoji = "📈" if trend.trend_direction == "up" else "📉" if trend.trend_direction == "down" else "➡️"
                    print(f"   {emoji} {trend.description}")
        
        # Performance por categoria
        daily_metrics = self.current_data.get("daily_metrics")
        if daily_metrics and daily_metrics.category_performance:
            print(f"\n🏷️ PERFORMANCE POR CATEGORIA:")
            print("-" * 40)
            
            # Ordenar por receita
            sorted_categories = sorted(
                daily_metrics.category_performance.items(),
                key=lambda x: x[1].get("revenue", 0),
                reverse=True
            )
            
            for category, stats in sorted_categories[:5]:  # Top 5
                revenue = stats.get("revenue", 0)
                conversions = stats.get("conversions", 0)
                print(f"   • {category}: {conversions} conversões - R$ {revenue:.2f}")
        
        # Estatísticas do dashboard
        print(f"\n🔧 ESTATÍSTICAS DO DASHBOARD:")
        print("-" * 40)
        print(f"   • Total de atualizações: {self.dashboard_stats['total_updates']}")
        print(f"   • Tempo ativo: {self._format_duration(self.dashboard_stats['uptime_seconds'])}")
        print(f"   • Rastreamento: {'✅ Ativo' if real_time.get('tracking_enabled', False) else '❌ Inativo'}")
        
        # Recomendações
        if analysis and analysis.recommendations:
            print(f"\n💡 RECOMENDAÇÕES:")
            print("-" * 40)
            for rec in analysis.recommendations[:5]:  # Mostrar apenas 5
                print(f"   • {rec}")
        
        print("\n" + "="*80)
    
    def _format_timestamp(self, timestamp_str: str) -> str:
        """Formata timestamp para exibição"""
        try:
            dt = datetime.fromisoformat(timestamp_str)
            return dt.strftime("%d/%m/%Y %H:%M:%S")
        except:
            return "N/A"
    
    def _format_duration(self, seconds: float) -> str:
        """Formata duração em segundos para exibição"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m {secs}s"
        elif minutes > 0:
            return f"{minutes}m {secs}s"
        else:
            return f"{secs}s"
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Retorna dados atuais do dashboard"""
        return {
            "dashboard_data": self.current_data,
            "dashboard_stats": self.dashboard_stats,
            "last_update": self.last_update.isoformat() if self.last_update else None
        }
    
    def export_dashboard_report(self, output_file: str = None) -> str:
        """Exporta relatório do dashboard"""
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"conversion_dashboard_report_{timestamp}.json"
        
        try:
            report_data = {
                "report_info": {
                    "generated_at": datetime.now().isoformat(),
                    "dashboard_uptime": self.dashboard_stats["uptime_seconds"],
                    "total_updates": self.dashboard_stats["total_updates"]
                },
                "dashboard_data": self.current_data,
                "dashboard_stats": self.dashboard_stats
            }
            
            # Salvar arquivo
            output_path = Path(output_file)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Relatório do dashboard exportado para: {output_path}")
            return str(output_path)
            
        except Exception as e:
            self.logger.error(f"Erro ao exportar relatório do dashboard: {e}")
            return ""
    
    def enable_auto_refresh(self):
        """Habilita atualização automática"""
        self.auto_refresh = True
        self.logger.info("Atualização automática habilitada")
    
    def disable_auto_refresh(self):
        """Desabilita atualização automática"""
        self.auto_refresh = False
        self.logger.info("Atualização automática desabilitada")
    
    def set_update_interval(self, seconds: int):
        """Define intervalo de atualização"""
        self.update_interval = max(5, seconds)  # Mínimo 5 segundos
        self.logger.info(f"Intervalo de atualização definido para {self.update_interval} segundos")
    
    def stop_dashboard(self):
        """Para o dashboard"""
        self.dashboard_enabled = False
        self.logger.info("Dashboard parado")
    
    async def get_quick_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas rápidas"""
        try:
            real_time = self.tracker.get_real_time_metrics()
            current_metrics = real_time.get("current_metrics", {})
            
            return {
                "total_conversions_today": current_metrics.get("total_conversions_today", 0),
                "geek_conversions_today": current_metrics.get("geek_conversions_today", 0),
                "general_conversions_today": current_metrics.get("general_conversions_today", 0),
                "total_revenue_today": str(current_metrics.get("total_revenue_today", "0")),
                "geek_revenue_today": str(current_metrics.get("geek_revenue_today", "0")),
                "general_revenue_today": str(current_metrics.get("general_revenue_today", "0")),
                "tracking_enabled": real_time.get("tracking_enabled", False),
                "last_update": real_time.get("last_update"),
                "dashboard_uptime": self.dashboard_stats["uptime_seconds"]
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao obter estatísticas rápidas: {e}")
            return {}
    
    async def generate_summary_report(self) -> Dict[str, Any]:
        """Gera relatório resumido"""
        try:
            # Obter dados atuais
            real_time = self.tracker.get_real_time_metrics()
            daily_metrics = await self.tracker.calculate_conversion_metrics("day")
            analysis = await self.analyzer.analyze_conversions("day")
            
            # Calcular métricas resumidas
            current_metrics = real_time.get("current_metrics", {})
            total_conversions = current_metrics.get("total_conversions_today", 0)
            
            if total_conversions > 0:
                geek_percentage = (current_metrics.get("geek_conversions_today", 0) / total_conversions) * 100
            else:
                geek_percentage = 0
            
            summary = {
                "timestamp": datetime.now().isoformat(),
                "period": "today",
                "key_metrics": {
                    "total_conversions": total_conversions,
                    "geek_conversions": current_metrics.get("geek_conversions_today", 0),
                    "general_conversions": current_metrics.get("general_conversions_today", 0),
                    "geek_percentage": geek_percentage,
                    "total_revenue": str(current_metrics.get("total_revenue_today", "0")),
                    "geek_revenue": str(current_metrics.get("geek_revenue_today", "0")),
                    "general_revenue": str(current_metrics.get("general_revenue_today", "0"))
                },
                "performance_score": analysis.performance_score,
                "critical_insights_count": len([i for i in analysis.insights if i.severity in ["high", "critical"]]),
                "trends_count": len(analysis.trends),
                "recommendations_count": len(analysis.recommendations),
                "dashboard_uptime": self.dashboard_stats["uptime_seconds"],
                "tracking_status": real_time.get("tracking_enabled", False)
            }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar relatório resumido: {e}")
            return {"error": str(e)}
