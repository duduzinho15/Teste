"""
Dashboard de Métricas Avançadas para Garimpeiro Geek
===================================================

Interface interativa para visualização e análise de métricas avançadas
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any
from dataclasses import asdict

from .advanced_metrics import (
    AdvancedMetricsManager,
    TimeSeriesAnalyzer,
    DemographicAnalyzer,
    SeasonalAnalyzer,
    EngagementAnalyzer
)


class AdvancedMetricsDashboard:
    """Dashboard interativo para métricas avançadas"""
    
    def __init__(self):
        self.metrics_manager = AdvancedMetricsManager()
        self.categories = ["gaming", "anime", "tech", "collectibles", "smartphones", "laptops"]
        self.report_types = ["comprehensive", "trends", "demographics", "seasonal", "engagement"]
    
    async def run_dashboard(self):
        """Executa o dashboard principal"""
        while True:
            self._show_main_menu()
            choice = input("\n🎯 Escolha uma opção: ").strip()
            
            if choice == "1":
                await self._show_comprehensive_report()
            elif choice == "2":
                await self._show_trends_analysis()
            elif choice == "3":
                await self._show_demographics_analysis()
            elif choice == "4":
                await self._show_seasonal_analysis()
            elif choice == "5":
                await self._show_engagement_analysis()
            elif choice == "6":
                await self._show_custom_report()
            elif choice == "7":
                await self._show_predictive_insights()
            elif choice == "8":
                await self._export_data()
            elif choice == "0":
                print("\n👋 Saindo do Dashboard de Métricas Avançadas...")
                break
            else:
                print("\n❌ Opção inválida. Tente novamente.")
            
            if choice != "0":
                input("\n⏸️  Pressione Enter para continuar...")
    
    def _show_main_menu(self):
        """Exibe menu principal"""
        print("\n" + "="*60)
        print("📊 DASHBOARD DE MÉTRICAS AVANÇADAS - GARIMPEIRO GEEK")
        print("="*60)
        print("1. 📈 Relatório Completo")
        print("2. 📊 Análise de Tendências")
        print("3. 👥 Análise Demográfica")
        print("4. 📅 Análise Sazonal")
        print("5. 🎯 Métricas de Engajamento")
        print("6. ⚙️  Relatório Personalizado")
        print("7. 🔮 Insights Preditivos")
        print("8. 💾 Exportar Dados")
        print("0. 🚪 Sair")
        print("-"*60)
    
    async def _show_comprehensive_report(self):
        """Exibe relatório completo"""
        print("\n📈 GERANDO RELATÓRIO COMPLETO...")
        print("⏳ Coletando dados...")
        
        report = await self.metrics_manager.generate_comprehensive_report()
        
        print("\n" + "="*60)
        print("📊 RELATÓRIO COMPLETO DE MÉTRICAS AVANÇADAS")
        print("="*60)
        
        # Resumo executivo
        print("\n🎯 RESUMO EXECUTIVO")
        print("-"*30)
        print(f"📅 Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        print(f"📊 Categorias analisadas: {len(self.categories)}")
        print(f"👥 Segmentos demográficos: {len(report.demographic_segments)}")
        print(f"📅 Padrões sazonais: {len(report.seasonal_patterns)}")
        
        # Tendências principais
        print("\n📈 TENDÊNCIAS PRINCIPAIS")
        print("-"*30)
        trend_analysis = report.trend_analysis
        print(f"🎯 Tendência geral: {trend_analysis.get('overall_trend', 'N/A')}")
        print(f"🏆 Categoria top: {trend_analysis.get('top_performing_category', 'N/A')}")
        print(f"📈 Taxa de crescimento: {trend_analysis.get('growth_rate', 0)*100:.1f}%")
        print(f"📅 Impacto sazonal: {trend_analysis.get('seasonal_impact', 0)*100:.1f}%")
        
        # Métricas de engajamento
        print("\n🎯 MÉTRICAS DE ENGAJAMENTO")
        print("-"*30)
        engagement = report.engagement_metrics
        print(f"👥 Usuários únicos: {engagement.unique_users:,}")
        print(f"⏱️  Duração média da sessão: {engagement.avg_session_duration:.1f} min")
        print(f"📉 Taxa de bounce: {engagement.bounce_rate*100:.1f}%")
        print(f"🔄 Taxa de retenção: {engagement.user_retention_rate*100:.1f}%")
        print(f"📊 NPS: {engagement.net_promoter_score}/100")
        
        # Insights preditivos
        print("\n🔮 INSIGHTS PREDITIVOS")
        print("-"*30)
        insights = report.predictive_insights
        forecast = insights.get("next_month_forecast", {})
        print("📈 Previsão para próximo mês:")
        for category, value in forecast.items():
            print(f"   • {category.title()}: {value:,}")
        
        print("\n💡 Ações recomendadas:")
        for action in insights.get("recommended_actions", []):
            print(f"   • {action}")
        
        print("\n⚠️  Fatores de risco:")
        for risk in insights.get("risk_factors", []):
            print(f"   • {risk}")
    
    async def _show_trends_analysis(self):
        """Exibe análise de tendências"""
        print("\n📊 ANÁLISE DE TENDÊNCIAS")
        print("="*40)
        
        # Seleção de categorias
        print("\n📂 Categorias disponíveis:")
        for i, category in enumerate(self.categories, 1):
            print(f"{i}. {category.title()}")
        
        try:
            choice = input("\n🎯 Escolha categorias (separadas por vírgula) ou 'all': ").strip()
            if choice.lower() == "all":
                selected_categories = self.categories
            else:
                indices = [int(x.strip()) - 1 for x in choice.split(",")]
                selected_categories = [self.categories[i] for i in indices if 0 <= i < len(self.categories)]
        except (ValueError, IndexError):
            print("❌ Seleção inválida. Usando todas as categorias.")
            selected_categories = self.categories
        
        # Período
        try:
            days = int(input("\n📅 Período em dias (padrão: 30): ").strip() or "30")
        except ValueError:
            days = 30
        
        print(f"\n⏳ Analisando tendências para {len(selected_categories)} categorias...")
        
        report_config = {
            "type": "trends",
            "filters": {
                "categories": selected_categories,
                "days": days
            }
        }
        
        report = await self.metrics_manager.get_custom_report(report_config)
        
        print("\n" + "="*60)
        print("📈 RELATÓRIO DE TENDÊNCIAS")
        print("="*60)
        print(f"📅 Período: {days} dias")
        print(f"📂 Categorias: {', '.join(selected_categories)}")
        
        # Análise por categoria
        for category in selected_categories:
            trend_data = report.get("trends", {}).get(category, {})
            if "error" in trend_data:
                print(f"\n❌ {category.title()}: {trend_data['error']}")
                continue
            
            print(f"\n📊 {category.upper()}")
            print("-" * 30)
            print(f"📈 Tendência: {trend_data.get('trend_direction', 'N/A')}")
            print(f"💪 Força: {trend_data.get('trend_strength', 'N/A')}")
            print(f"📊 Valor atual: {trend_data.get('current_value', 0):.2f}")
            print(f"📈 Inclinação: {trend_data.get('trend_slope', 0):.4f}")
            print(f"📊 Volatilidade: {trend_data.get('volatility', 0):.2f}")
            print(f"🎯 R²: {trend_data.get('r_squared', 0):.3f}")
            print(f"🔮 Previsão próxima: {trend_data.get('prediction_next_period', 0):.2f}")
        
        # Resumo
        summary = report.get("summary", {})
        print(f"\n🏆 RESUMO")
        print("-" * 20)
        print(f"🏆 Melhor performance: {summary.get('best_performing', 'N/A')}")
        print(f"📈 Crescimento mais rápido: {summary.get('fastest_growing', 'N/A')}")
        print(f"📊 Mais volátil: {summary.get('most_volatile', 'N/A')}")
    
    async def _show_demographics_analysis(self):
        """Exibe análise demográfica"""
        print("\n👥 ANÁLISE DEMOGRÁFICA")
        print("="*40)
        
        # Seleção de segmentos
        segments = self.metrics_manager.demographic_analyzer.segments
        print("\n👥 Segmentos disponíveis:")
        for i, segment in enumerate(segments, 1):
            print(f"{i}. {segment.name} ({segment.segment_id})")
        
        try:
            choice = input("\n🎯 Escolha segmentos (separados por vírgula) ou 'all': ").strip()
            if choice.lower() == "all":
                selected_segments = [s.segment_id for s in segments]
            else:
                indices = [int(x.strip()) - 1 for x in choice.split(",")]
                selected_segments = [segments[i].segment_id for i in indices if 0 <= i < len(segments)]
        except (ValueError, IndexError):
            print("❌ Seleção inválida. Usando todos os segmentos.")
            selected_segments = [s.segment_id for s in segments]
        
        print(f"\n⏳ Analisando {len(selected_segments)} segmentos demográficos...")
        
        report_config = {
            "type": "demographics",
            "filters": {
                "segments": selected_segments
            }
        }
        
        report = await self.metrics_manager.get_custom_report(report_config)
        
        print("\n" + "="*60)
        print("👥 RELATÓRIO DEMOGRÁFICO")
        print("="*60)
        
        # Análise por segmento
        insights = report.get("insights", {})
        for segment_id in selected_segments:
            segment_data = insights.get(segment_id, {})
            if "error" in segment_data:
                print(f"\n❌ {segment_id}: {segment_data['error']}")
                continue
            
            segment_info = segment_data.get("segment", {})
            engagement = segment_data.get("engagement", {})
            
            print(f"\n👥 {segment_info.get('name', segment_id).upper()}")
            print("-" * 40)
            print(f"📝 Descrição: {segment_info.get('description', 'N/A')}")
            print(f"👥 Tamanho estimado: {segment_info.get('size_estimate', 0):,}")
            print(f"📊 Taxa de conversão: {segment_info.get('conversion_rate', 0)*100:.1f}%")
            print(f"💰 Valor médio do pedido: R$ {segment_info.get('avg_order_value', 0):.2f}")
            print(f"⏱️  Duração média da sessão: {engagement.get('avg_session', 0)} min")
            print(f"📉 Taxa de bounce: {engagement.get('bounce_rate', 0)*100:.1f}%")
            print(f"🔄 Taxa de retenção: {engagement.get('retention', 0)*100:.1f}%")
            
            print(f"\n🎯 Preferências:")
            for pref in segment_info.get("preferences", []):
                print(f"   • {pref}")
            
            print(f"\n💡 Recomendações:")
            for rec in segment_data.get("recommendations", []):
                print(f"   • {rec}")
        
        # Resumo
        summary = report.get("summary", {})
        print(f"\n🏆 RESUMO")
        print("-" * 20)
        print(f"👥 Audiência total: {summary.get('total_audience', 0):,}")
        print(f"📊 Taxa de conversão média: {summary.get('avg_conversion_rate', 0)*100:.1f}%")
        print(f"💰 Valor médio do pedido: R$ {summary.get('avg_order_value', 0):.2f}")
    
    async def _show_seasonal_analysis(self):
        """Exibe análise sazonal"""
        print("\n📅 ANÁLISE SAZONAL")
        print("="*40)
        
        # Seleção de categorias
        print("\n📂 Categorias disponíveis:")
        for i, category in enumerate(self.categories, 1):
            print(f"{i}. {category.title()}")
        
        try:
            choice = input("\n🎯 Escolha categorias (separadas por vírgula) ou 'all': ").strip()
            if choice.lower() == "all":
                selected_categories = self.categories
            else:
                indices = [int(x.strip()) - 1 for x in choice.split(",")]
                selected_categories = [self.categories[i] for i in indices if 0 <= i < len(self.categories)]
        except (ValueError, IndexError):
            print("❌ Seleção inválida. Usando todas as categorias.")
            selected_categories = self.categories
        
        print(f"\n⏳ Analisando padrões sazonais...")
        
        report_config = {
            "type": "seasonal",
            "filters": {
                "categories": selected_categories
            }
        }
        
        report = await self.metrics_manager.get_custom_report(report_config)
        
        print("\n" + "="*60)
        print("📅 RELATÓRIO SAZONAL")
        print("="*60)
        
        # Padrões sazonais
        patterns = report.get("patterns", [])
        print(f"\n📅 PADRÕES SAZONAIS IDENTIFICADOS ({len(patterns)})")
        print("-" * 50)
        
        for pattern in patterns:
            print(f"\n📅 {pattern.get('name', 'N/A').upper()}")
            print("-" * 30)
            print(f"📝 Descrição: {pattern.get('description', 'N/A')}")
            print(f"📊 Tipo: {pattern.get('season_type', 'N/A')}")
            print(f"📅 Início: {pattern.get('start_date', 'N/A')}")
            print(f"📅 Fim: {pattern.get('end_date', 'N/A')}")
            print(f"📈 Pico: {pattern.get('peak_value', 0):.2f}x")
            print(f"📉 Vale: {pattern.get('trough_value', 0):.2f}x")
            print(f"🎯 Confiança: {pattern.get('confidence', 0)*100:.1f}%")
            
            affected = pattern.get('affected_categories', [])
            if affected:
                print(f"📂 Categorias afetadas: {', '.join(affected)}")
        
        # Impacto por categoria
        category_impact = report.get("category_impact", {})
        print(f"\n📊 IMPACTO POR CATEGORIA")
        print("-" * 30)
        
        for category in selected_categories:
            impacts = category_impact.get(category, {})
            if impacts:
                print(f"\n📂 {category.upper()}")
                for pattern_name, impact in impacts.items():
                    print(f"   📅 {pattern_name}:")
                    print(f"      📈 Pico: {impact.get('peak_multiplier', 0):.2f}x")
                    print(f"      📉 Vale: {impact.get('trough_multiplier', 0):.2f}x")
                    print(f"      🎯 Confiança: {impact.get('confidence', 0)*100:.1f}%")
        
        # Resumo
        summary = report.get("summary", {})
        print(f"\n🏆 RESUMO")
        print("-" * 20)
        print(f"📅 Padrões ativos: {summary.get('active_patterns', 0)}")
        print(f"📈 Maior impacto: {summary.get('highest_impact', 'N/A')}")
        print(f"🎯 Mais confiável: {summary.get('most_confident', 'N/A')}")
    
    async def _show_engagement_analysis(self):
        """Exibe análise de engajamento"""
        print("\n🎯 ANÁLISE DE ENGAJAMENTO")
        print("="*40)
        
        print("\n⏳ Calculando métricas de engajamento...")
        
        report_config = {
            "type": "engagement",
            "filters": {}
        }
        
        report = await self.metrics_manager.get_custom_report(report_config)
        
        print("\n" + "="*60)
        print("🎯 RELATÓRIO DE ENGAJAMENTO")
        print("="*60)
        
        metrics = report.get("metrics", {})
        summary = report.get("summary", {})
        
        print(f"\n📊 MÉTRICAS BÁSICAS")
        print("-" * 25)
        print(f"👥 Usuários únicos: {metrics.get('unique_users', 0):,}")
        print(f"🖱️  Total de interações: {metrics.get('total_interactions', 0):,}")
        print(f"⏱️  Duração média da sessão: {metrics.get('avg_session_duration', 0):.1f} min")
        print(f"📉 Taxa de bounce: {metrics.get('bounce_rate', 0)*100:.1f}%")
        print(f"🔄 Taxa de retenção: {metrics.get('user_retention_rate', 0)*100:.1f}%")
        print(f"📊 Coeficiente viral: {metrics.get('viral_coefficient', 0)*100:.1f}%")
        print(f"⭐ NPS: {metrics.get('net_promoter_score', 0)}/100")
        
        # Funil de conversão
        funnel = metrics.get("conversion_funnel", {})
        print(f"\n🔄 FUNIL DE CONVERSÃO")
        print("-" * 25)
        print(f"📊 Sessões totais: {funnel.get('sessions', 0):,}")
        print(f"🎯 Sessões engajadas: {funnel.get('engaged', 0):,}")
        print(f"💰 Sessões convertidas: {funnel.get('converted', 0):,}")
        print(f"📈 Taxa de conversão: {funnel.get('conversion_rate', 0)*100:.2f}%")
        
        # Scores
        print(f"\n🏆 SCORES")
        print("-" * 15)
        print(f"🎯 Score de engajamento: {summary.get('engagement_score', 0):.1f}/100")
        print(f"💰 Eficiência de conversão: {summary.get('conversion_efficiency', 0):.1f}%")
        print(f"📈 Potencial viral: {summary.get('viral_potential', 0):.1f}%")
    
    async def _show_custom_report(self):
        """Exibe relatório personalizado"""
        print("\n⚙️  RELATÓRIO PERSONALIZADO")
        print("="*40)
        
        print("\n📊 Tipos de relatório disponíveis:")
        for i, report_type in enumerate(self.report_types, 1):
            print(f"{i}. {report_type.title()}")
        
        try:
            choice = int(input("\n🎯 Escolha o tipo de relatório: ").strip())
            if 1 <= choice <= len(self.report_types):
                selected_type = self.report_types[choice - 1]
            else:
                print("❌ Opção inválida. Usando relatório completo.")
                selected_type = "comprehensive"
        except ValueError:
            print("❌ Opção inválida. Usando relatório completo.")
            selected_type = "comprehensive"
        
        # Configurações específicas
        filters = {}
        
        if selected_type == "trends":
            try:
                days = int(input("\n📅 Período em dias (padrão: 30): ").strip() or "30")
                filters["days"] = days
            except ValueError:
                filters["days"] = 30
            
            print("\n📂 Categorias disponíveis:")
            for i, category in enumerate(self.categories, 1):
                print(f"{i}. {category.title()}")
            
            try:
                choice = input("\n🎯 Escolha categorias (separadas por vírgula) ou 'all': ").strip()
                if choice.lower() == "all":
                    filters["categories"] = self.categories
                else:
                    indices = [int(x.strip()) - 1 for x in choice.split(",")]
                    filters["categories"] = [self.categories[i] for i in indices if 0 <= i < len(self.categories)]
            except (ValueError, IndexError):
                filters["categories"] = self.categories
        
        elif selected_type == "demographics":
            segments = [s.segment_id for s in self.metrics_manager.demographic_analyzer.segments]
            print("\n👥 Segmentos disponíveis:")
            for i, segment_id in enumerate(segments, 1):
                print(f"{i}. {segment_id}")
            
            try:
                choice = input("\n🎯 Escolha segmentos (separados por vírgula) ou 'all': ").strip()
                if choice.lower() == "all":
                    filters["segments"] = segments
                else:
                    indices = [int(x.strip()) - 1 for x in choice.split(",")]
                    filters["segments"] = [segments[i] for i in indices if 0 <= i < len(segments)]
            except (ValueError, IndexError):
                filters["segments"] = segments
        
        print(f"\n⏳ Gerando relatório personalizado...")
        
        report_config = {
            "type": selected_type,
            "filters": filters
        }
        
        report = await self.metrics_manager.get_custom_report(report_config)
        
        print(f"\n📊 RELATÓRIO PERSONALIZADO - {selected_type.upper()}")
        print("="*60)
        
        # Exibe relatório baseado no tipo
        if selected_type == "comprehensive":
            await self._show_comprehensive_report()
        elif selected_type == "trends":
            await self._show_trends_analysis()
        elif selected_type == "demographics":
            await self._show_demographics_analysis()
        elif selected_type == "seasonal":
            await self._show_seasonal_analysis()
        elif selected_type == "engagement":
            await self._show_engagement_analysis()
    
    async def _show_predictive_insights(self):
        """Exibe insights preditivos"""
        print("\n🔮 INSIGHTS PREDITIVOS")
        print("="*40)
        
        print("\n⏳ Gerando insights preditivos...")
        
        report = await self.metrics_manager.generate_comprehensive_report()
        insights = report.predictive_insights
        
        print("\n" + "="*60)
        print("🔮 INSIGHTS PREDITIVOS")
        print("="*60)
        
        # Previsões
        forecast = insights.get("next_month_forecast", {})
        print(f"\n📈 PREVISÕES PARA PRÓXIMO MÊS")
        print("-" * 35)
        for category, value in forecast.items():
            print(f"📊 {category.title()}: {value:,}")
        
        # Ações recomendadas
        recommendations = insights.get("recommended_actions", [])
        print(f"\n💡 AÇÕES RECOMENDADAS")
        print("-" * 25)
        for i, action in enumerate(recommendations, 1):
            print(f"{i}. {action}")
        
        # Fatores de risco
        risks = insights.get("risk_factors", [])
        print(f"\n⚠️  FATORES DE RISCO")
        print("-" * 20)
        for i, risk in enumerate(risks, 1):
            print(f"{i}. {risk}")
        
        # Oportunidades
        print(f"\n🎯 OPORTUNIDADES IDENTIFICADAS")
        print("-" * 30)
        print("• Aumentar estoque de produtos gaming durante Black Friday")
        print("• Lançar campanha específica para anime otaku")
        print("• Otimizar preços para tech enthusiasts")
        print("• Criar conteúdo exclusivo para colecionadores")
    
    async def _export_data(self):
        """Exporta dados para arquivo"""
        print("\n💾 EXPORTAR DADOS")
        print("="*30)
        
        print("\n📊 Tipos de exportação:")
        print("1. Relatório completo (JSON)")
        print("2. Dados de tendências (CSV)")
        print("3. Análise demográfica (JSON)")
        print("4. Padrões sazonais (JSON)")
        print("5. Métricas de engajamento (JSON)")
        
        try:
            choice = int(input("\n🎯 Escolha o tipo de exportação: ").strip())
        except ValueError:
            print("❌ Opção inválida.")
            return
        
        filename = input("\n📁 Nome do arquivo (sem extensão): ").strip()
        if not filename:
            filename = f"metrics_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        print(f"\n⏳ Exportando dados...")
        
        try:
            if choice == 1:
                report = await self.metrics_manager.generate_comprehensive_report()
                data = asdict(report)
                filename += ".json"
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, default=str)
                
                print(f"✅ Dados exportados para: {filename}")
            
            elif choice == 2:
                # Exporta dados de tendências
                trends_data = []
                for category in self.categories:
                    trend = await self.metrics_manager.time_analyzer.get_trend_analysis(category)
                    trends_data.append(trend)
                
                filename += ".json"
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(trends_data, f, indent=2, default=str)
                
                print(f"✅ Dados de tendências exportados para: {filename}")
            
            elif choice == 3:
                segments = [asdict(s) for s in self.metrics_manager.demographic_analyzer.segments]
                filename += ".json"
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(segments, f, indent=2, default=str)
                
                print(f"✅ Análise demográfica exportada para: {filename}")
            
            elif choice == 4:
                patterns = [asdict(p) for p in self.metrics_manager.seasonal_analyzer.patterns]
                filename += ".json"
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(patterns, f, indent=2, default=str)
                
                print(f"✅ Padrões sazonais exportados para: {filename}")
            
            elif choice == 5:
                metrics = await self.metrics_manager.engagement_analyzer.calculate_engagement_metrics()
                data = asdict(metrics)
                filename += ".json"
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, default=str)
                
                print(f"✅ Métricas de engajamento exportadas para: {filename}")
            
            else:
                print("❌ Opção inválida.")
        
        except Exception as e:
            print(f"❌ Erro ao exportar dados: {e}")


async def main():
    """Função principal para executar o dashboard"""
    dashboard = AdvancedMetricsDashboard()
    await dashboard.run_dashboard()


if __name__ == "__main__":
    asyncio.run(main())
