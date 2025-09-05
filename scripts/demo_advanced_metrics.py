"""
Demonstração do Sistema de Métricas Avançadas
============================================

Script para demonstrar todas as funcionalidades do sistema de métricas avançadas
"""

import asyncio
import json
import sys
from datetime import datetime, timedelta
from dataclasses import asdict
from pathlib import Path

# Adicionar o diretório raiz ao Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.advanced_metrics import (
    AdvancedMetricsManager,
    TimeSeriesAnalyzer,
    DemographicAnalyzer,
    SeasonalAnalyzer,
    EngagementAnalyzer,
    TimeSeriesData
)
from src.core.advanced_metrics_dashboard import AdvancedMetricsDashboard


class AdvancedMetricsDemo:
    """Demonstração do sistema de métricas avançadas"""
    
    def __init__(self):
        self.metrics_manager = AdvancedMetricsManager()
        self.dashboard = AdvancedMetricsDashboard()
    
    async def run_full_demo(self):
        """Executa demonstração completa"""
        print("🚀 INICIANDO DEMONSTRAÇÃO COMPLETA DE MÉTRICAS AVANÇADAS")
        print("="*70)
        
        # 1. Simulação de dados
        await self._simulate_data_collection()
        
        # 2. Análise de tendências
        await self._demo_trend_analysis()
        
        # 3. Análise demográfica
        await self._demo_demographic_analysis()
        
        # 4. Análise sazonal
        await self._demo_seasonal_analysis()
        
        # 5. Métricas de engajamento
        await self._demo_engagement_analysis()
        
        # 6. Relatório completo
        await self._demo_comprehensive_report()
        
        # 7. Insights preditivos
        await self._demo_predictive_insights()
        
        # 8. Relatórios personalizados
        await self._demo_custom_reports()
        
        print("\n✅ DEMONSTRAÇÃO COMPLETA FINALIZADA!")
        print("="*70)
    
    async def run_quick_demo(self):
        """Executa demonstração rápida"""
        print("⚡ INICIANDO DEMONSTRAÇÃO RÁPIDA DE MÉTRICAS AVANÇADAS")
        print("="*60)
        
        # Simulação rápida de dados
        await self._simulate_data_collection()
        
        # Relatório completo
        print("\n📊 GERANDO RELATÓRIO COMPLETO...")
        report = await self.metrics_manager.generate_comprehensive_report()
        
        print("\n📈 RESUMO EXECUTIVO")
        print("-" * 30)
        print(f"📅 Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        print(f"📊 Categorias: {len(report.demographic_segments)}")
        print(f"👥 Segmentos: {len(report.demographic_segments)}")
        print(f"📅 Padrões sazonais: {len(report.seasonal_patterns)}")
        
        # Tendências principais
        trend_analysis = report.trend_analysis
        print(f"\n📈 TENDÊNCIAS")
        print("-" * 20)
        print(f"🎯 Geral: {trend_analysis.get('overall_trend', 'N/A')}")
        print(f"🏆 Top: {trend_analysis.get('top_performing_category', 'N/A')}")
        print(f"📈 Crescimento: {trend_analysis.get('growth_rate', 0)*100:.1f}%")
        
        # Engajamento
        engagement = report.engagement_metrics
        print(f"\n🎯 ENGAJAMENTO")
        print("-" * 20)
        print(f"👥 Usuários: {engagement.unique_users:,}")
        print(f"⏱️  Sessão: {engagement.avg_session_duration:.1f} min")
        print(f"📉 Bounce: {engagement.bounce_rate*100:.1f}%")
        print(f"🔄 Retenção: {engagement.user_retention_rate*100:.1f}%")
        
        # Previsões
        insights = report.predictive_insights
        forecast = insights.get("next_month_forecast", {})
        print(f"\n🔮 PREVISÕES")
        print("-" * 20)
        for category, value in forecast.items():
            print(f"📊 {category.title()}: {value:,}")
        
        print("\n✅ DEMONSTRAÇÃO RÁPIDA FINALIZADA!")
        print("="*60)
    
    async def _simulate_data_collection(self):
        """Simula coleta de dados"""
        print("\n📊 SIMULANDO COLETA DE DADOS...")
        
        # Adiciona dados de série temporal
        categories = ["gaming", "anime", "tech", "collectibles"]
        for i in range(30):  # 30 dias de dados
            timestamp = datetime.now() - timedelta(days=i)
            for category in categories:
                # Simula valores com tendência e sazonalidade
                base_value = 100 + (i * 2) + (hash(category) % 50)
                seasonal_factor = 1.2 if timestamp.weekday() >= 5 else 1.0  # Fim de semana
                value = base_value * seasonal_factor
                
                data_point = TimeSeriesData(
                    timestamp=timestamp,
                    value=value,
                    category=category,
                    metric_type="conversion_rate",
                    metadata={"source": "simulated", "day": i}
                )
                
                await self.metrics_manager.time_analyzer.add_data_point(data_point)
        
        # Simula sessões de usuários
        for i in range(100):
            user_id = f"user_{i}"
            session_data = {
                "duration": 20 + (i % 30),  # 20-50 minutos
                "pages_visited": ["home", "products", "cart"],
                "interactions": 5 + (i % 10),
                "converted": i % 5 == 0  # 20% de conversão
            }
            await self.metrics_manager.engagement_analyzer.track_session(user_id, session_data)
            
            # Simula interações
            interaction_types = ["view_product", "add_to_cart", "share", "like"]
            for j in range(3):
                interaction_type = interaction_types[j % len(interaction_types)]
                metadata = {"product_id": f"prod_{i}_{j}", "category": categories[i % len(categories)]}
                await self.metrics_manager.engagement_analyzer.track_interaction(user_id, interaction_type, metadata)
        
        print("✅ Dados simulados coletados com sucesso!")
    
    async def _demo_trend_analysis(self):
        """Demonstra análise de tendências"""
        print("\n📈 DEMONSTRANDO ANÁLISE DE TENDÊNCIAS...")
        
        categories = ["gaming", "anime", "tech", "collectibles"]
        
        for category in categories:
            print(f"\n📊 Analisando {category.title()}...")
            trend = await self.metrics_manager.time_analyzer.get_trend_analysis(category)
            
            if "error" not in trend:
                print(f"   📈 Tendência: {trend.get('trend_direction', 'N/A')}")
                print(f"   💪 Força: {trend.get('trend_strength', 'N/A')}")
                print(f"   📊 Valor atual: {trend.get('current_value', 0):.2f}")
                print(f"   📈 Inclinação: {trend.get('trend_slope', 0):.4f}")
                print(f"   📊 Volatilidade: {trend.get('volatility', 0):.2f}")
                print(f"   🎯 R²: {trend.get('r_squared', 0):.3f}")
            else:
                print(f"   ❌ Erro: {trend['error']}")
        
        print("✅ Análise de tendências concluída!")
    
    async def _demo_demographic_analysis(self):
        """Demonstra análise demográfica"""
        print("\n👥 DEMONSTRANDO ANÁLISE DEMOGRÁFICA...")
        
        segments = self.metrics_manager.demographic_analyzer.segments
        
        for segment in segments:
            print(f"\n👥 {segment.name}")
            print(f"   📝 {segment.description}")
            print(f"   👥 Tamanho: {segment.size_estimate:,}")
            print(f"   📊 Conversão: {segment.conversion_rate*100:.1f}%")
            print(f"   💰 Valor médio: R$ {segment.avg_order_value:.2f}")
            print(f"   🎯 Preferências: {', '.join(segment.preferences)}")
        
        # Testa análise de usuário
        test_user = {
            "gaming_hours": "25",
            "platforms": ["PC", "Console"],
            "genres": ["FPS", "RPG"],
            "anime_hours": "5",
            "tech_interests": ["smartphones", "laptops"]
        }
        
        matched_segment = await self.metrics_manager.demographic_analyzer.analyze_user_segment(test_user)
        print(f"\n🎯 Usuário teste classificado como: {matched_segment.name}")
        
        print("✅ Análise demográfica concluída!")
    
    async def _demo_seasonal_analysis(self):
        """Demonstra análise sazonal"""
        print("\n📅 DEMONSTRANDO ANÁLISE SAZONAL...")
        
        patterns = self.metrics_manager.seasonal_analyzer.patterns
        
        for pattern in patterns:
            print(f"\n📅 {pattern.name}")
            print(f"   📝 {pattern.description}")
            print(f"   📊 Tipo: {pattern.season_type}")
            print(f"   📅 Período: {pattern.start_date.strftime('%d/%m')} - {pattern.end_date.strftime('%d/%m')}")
            print(f"   📈 Pico: {pattern.peak_value:.2f}x")
            print(f"   📉 Vale: {pattern.trough_value:.2f}x")
            print(f"   🎯 Confiança: {pattern.confidence*100:.1f}%")
            print(f"   📂 Categorias: {', '.join(pattern.affected_categories)}")
        
        # Testa multiplicador sazonal
        test_date = datetime.now()
        test_category = "gaming"
        multiplier = await self.metrics_manager.seasonal_analyzer.get_seasonal_multiplier(test_category, test_date)
        print(f"\n📊 Multiplicador sazonal para {test_category} em {test_date.strftime('%d/%m/%Y')}: {multiplier:.2f}x")
        
        print("✅ Análise sazonal concluída!")
    
    async def _demo_engagement_analysis(self):
        """Demonstra análise de engajamento"""
        print("\n🎯 DEMONSTRANDO ANÁLISE DE ENGAJAMENTO...")
        
        metrics = await self.metrics_manager.engagement_analyzer.calculate_engagement_metrics()
        
        print(f"\n📊 MÉTRICAS DE ENGAJAMENTO")
        print("-" * 30)
        print(f"👥 Usuários únicos: {metrics.unique_users:,}")
        print(f"🖱️  Total de interações: {metrics.total_interactions:,}")
        print(f"⏱️  Duração média da sessão: {metrics.avg_session_duration:.1f} min")
        print(f"📉 Taxa de bounce: {metrics.bounce_rate*100:.1f}%")
        print(f"🔄 Taxa de retenção: {metrics.user_retention_rate*100:.1f}%")
        print(f"📊 Coeficiente viral: {metrics.viral_coefficient*100:.1f}%")
        print(f"⭐ NPS: {metrics.net_promoter_score}/100")
        
        # Funil de conversão
        funnel = metrics.conversion_funnel
        print(f"\n🔄 FUNIL DE CONVERSÃO")
        print("-" * 25)
        print(f"📊 Sessões totais: {funnel.get('sessions', 0):,}")
        print(f"🎯 Sessões engajadas: {funnel.get('engaged', 0):,}")
        print(f"💰 Sessões convertidas: {funnel.get('converted', 0):,}")
        print(f"📈 Taxa de conversão: {funnel.get('conversion_rate', 0)*100:.2f}%")
        
        print("✅ Análise de engajamento concluída!")
    
    async def _demo_comprehensive_report(self):
        """Demonstra relatório completo"""
        print("\n📊 GERANDO RELATÓRIO COMPLETO...")
        
        report = await self.metrics_manager.generate_comprehensive_report()
        
        print(f"\n📈 RELATÓRIO COMPLETO")
        print("-" * 25)
        print(f"📅 Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        print(f"📊 Categorias analisadas: {len(report.demographic_segments)}")
        print(f"👥 Segmentos demográficos: {len(report.demographic_segments)}")
        print(f"📅 Padrões sazonais: {len(report.seasonal_patterns)}")
        print(f"📈 Pontos de dados temporais: {len(report.time_series_data)}")
        
        # Tendências
        trend_analysis = report.trend_analysis
        print(f"\n📈 TENDÊNCIAS PRINCIPAIS")
        print("-" * 25)
        print(f"🎯 Tendência geral: {trend_analysis.get('overall_trend', 'N/A')}")
        print(f"🏆 Categoria top: {trend_analysis.get('top_performing_category', 'N/A')}")
        print(f"📈 Taxa de crescimento: {trend_analysis.get('growth_rate', 0)*100:.1f}%")
        print(f"📅 Impacto sazonal: {trend_analysis.get('seasonal_impact', 0)*100:.1f}%")
        
        print("✅ Relatório completo gerado!")
    
    async def _demo_predictive_insights(self):
        """Demonstra insights preditivos"""
        print("\n🔮 GERANDO INSIGHTS PREDITIVOS...")
        
        report = await self.metrics_manager.generate_comprehensive_report()
        insights = report.predictive_insights
        
        print(f"\n🔮 INSIGHTS PREDITIVOS")
        print("-" * 25)
        
        # Previsões
        forecast = insights.get("next_month_forecast", {})
        print("📈 PREVISÕES PARA PRÓXIMO MÊS:")
        for category, value in forecast.items():
            print(f"   📊 {category.title()}: {value:,}")
        
        # Ações recomendadas
        recommendations = insights.get("recommended_actions", [])
        print(f"\n💡 AÇÕES RECOMENDADAS:")
        for i, action in enumerate(recommendations, 1):
            print(f"   {i}. {action}")
        
        # Fatores de risco
        risks = insights.get("risk_factors", [])
        print(f"\n⚠️  FATORES DE RISCO:")
        for i, risk in enumerate(risks, 1):
            print(f"   {i}. {risk}")
        
        print("✅ Insights preditivos gerados!")
    
    async def _demo_custom_reports(self):
        """Demonstra relatórios personalizados"""
        print("\n⚙️  DEMONSTRANDO RELATÓRIOS PERSONALIZADOS...")
        
        # Relatório de tendências
        trends_config = {
            "type": "trends",
            "filters": {
                "categories": ["gaming", "anime"],
                "days": 15
            }
        }
        
        trends_report = await self.metrics_manager.get_custom_report(trends_config)
        print(f"\n📈 RELATÓRIO DE TENDÊNCIAS (15 dias)")
        print(f"📂 Categorias: {', '.join(trends_config['filters']['categories'])}")
        print(f"📊 Dados: {len(trends_report.get('trends', {}))} categorias analisadas")
        
        # Relatório demográfico
        demo_config = {
            "type": "demographics",
            "filters": {
                "segments": ["hardcore_gamer", "anime_otaku"]
            }
        }
        
        demo_report = await self.metrics_manager.get_custom_report(demo_config)
        print(f"\n👥 RELATÓRIO DEMOGRÁFICO")
        print(f"👥 Segmentos: {', '.join(demo_config['filters']['segments'])}")
        print(f"📊 Insights: {len(demo_report.get('insights', {}))} segmentos analisados")
        
        # Relatório sazonal
        seasonal_config = {
            "type": "seasonal",
            "filters": {
                "categories": ["gaming", "tech"]
            }
        }
        
        seasonal_report = await self.metrics_manager.get_custom_report(seasonal_config)
        print(f"\n📅 RELATÓRIO SAZONAL")
        print(f"📂 Categorias: {', '.join(seasonal_config['filters']['categories'])}")
        print(f"📅 Padrões: {len(seasonal_report.get('patterns', []))} padrões identificados")
        
        # Relatório de engajamento
        engagement_config = {
            "type": "engagement",
            "filters": {}
        }
        
        engagement_report = await self.metrics_manager.get_custom_report(engagement_config)
        print(f"\n🎯 RELATÓRIO DE ENGAJAMENTO")
        print(f"📊 Métricas calculadas: {len(engagement_report.get('metrics', {}))} métricas")
        
        print("✅ Relatórios personalizados gerados!")
    
    async def run_dashboard_demo(self):
        """Executa demonstração do dashboard"""
        print("\n🎛️  INICIANDO DEMONSTRAÇÃO DO DASHBOARD...")
        print("="*50)
        
        # Simula dados primeiro
        await self._simulate_data_collection()
        
        print("\n🎯 Executando dashboard interativo...")
        print("💡 Use as opções do menu para explorar as funcionalidades")
        print("🚪 Digite '0' para sair do dashboard")
        
        # Executa o dashboard
        await self.dashboard.run_dashboard()
        
        print("\n✅ Demonstração do dashboard finalizada!")


async def main():
    """Função principal"""
    import sys
    
    demo = AdvancedMetricsDemo()
    
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        
        if mode == "full":
            await demo.run_full_demo()
        elif mode == "quick":
            await demo.run_quick_demo()
        elif mode == "dashboard":
            await demo.run_dashboard_demo()
        else:
            print("❌ Modo inválido. Use: full, quick ou dashboard")
            print("💡 Exemplo: python demo_advanced_metrics.py quick")
    else:
        print("🎯 DEMONSTRAÇÃO DE MÉTRICAS AVANÇADAS")
        print("="*50)
        print("Modos disponíveis:")
        print("  • full: Demonstração completa")
        print("  • quick: Demonstração rápida")
        print("  • dashboard: Dashboard interativo")
        print("\n💡 Exemplo: python demo_advanced_metrics.py quick")


if __name__ == "__main__":
    asyncio.run(main())
