#!/usr/bin/env python3
"""
Script de Demonstração do Sistema de Monitoramento de Conversão Geek vs Geral
Mostra como usar o sistema completo de rastreamento e análise de conversões
"""

import asyncio
import sys
from pathlib import Path
import json
from decimal import Decimal
from datetime import datetime

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.app.conversion_monitoring import (
    ConversionTracker, 
    ConversionAnalyzer, 
    ConversionDashboard, 
    ConversionReporter
)
from src.core.models import Offer


async def demo_conversion_tracking():
    """Demonstra rastreamento de conversões"""
    print("🎯 DEMONSTRAÇÃO: Rastreamento de Conversões")
    print("=" * 60)
    
    try:
        # Inicializar tracker
        tracker = ConversionTracker()
        
        # Criar ofertas de teste
        test_offers = [
            Offer(
                title="PlayStation 5 Console Digital Edition",
                price=Decimal("3499.99"),
                url="https://exemplo.com/ps5",
                store="Loja Geek",
                original_price=Decimal("3999.99"),
                discount_percentage=12.5,
                category="gaming_consoles",
                stock_quantity=5,
                image_url="https://exemplo.com/ps5.jpg",
                description="Console PlayStation 5 Digital Edition",
                scraped_at=datetime.now()
            ),
            Offer(
                title="Smart TV Samsung 55\" 4K",
                price=Decimal("2999.99"),
                url="https://exemplo.com/smarttv",
                store="Loja Tech",
                original_price=Decimal("3499.99"),
                discount_percentage=14.3,
                category="smart_home_tech",
                stock_quantity=8,
                image_url="https://exemplo.com/smarttv.jpg",
                description="Smart TV Samsung 55 polegadas 4K",
                scraped_at=datetime.now()
            ),
            Offer(
                title="Microondas Panasonic 30L",
                price=Decimal("599.99"),
                url="https://exemplo.com/microondas",
                store="Loja Casa",
                original_price=Decimal("799.99"),
                discount_percentage=25.0,
                category="home_appliances",
                stock_quantity=15,
                image_url="https://exemplo.com/microondas.jpg",
                description="Microondas Panasonic 30L",
                scraped_at=datetime.now()
            )
        ]
        
        # Simular conversões
        print("Simulando conversões...")
        
        # Conversão geek (PS5)
        await tracker.track_conversion(
            test_offers[0], 
            "purchase", 
            "geek",
            revenue=Decimal("3499.99"),
            commission=Decimal("349.99")
        )
        
        # Conversão geek (Smart TV)
        await tracker.track_conversion(
            test_offers[1], 
            "purchase", 
            "geek",
            revenue=Decimal("2999.99"),
            commission=Decimal("299.99")
        )
        
        # Conversão geral (Microondas)
        await tracker.track_conversion(
            test_offers[2], 
            "purchase", 
            "general",
            revenue=Decimal("599.99"),
            commission=Decimal("59.99")
        )
        
        # Mais algumas conversões para simular dados
        for i in range(5):
            await tracker.track_conversion(
                test_offers[i % len(test_offers)], 
                "click", 
                "geek" if i % 2 == 0 else "general"
            )
        
        print(f"✅ {len(tracker.conversion_events)} conversões rastreadas")
        
        # Mostrar métricas em tempo real
        real_time_metrics = tracker.get_real_time_metrics()
        current_metrics = real_time_metrics.get("current_metrics", {})
        
        print(f"\n📊 Métricas em Tempo Real:")
        print(f"   • Conversões hoje: {current_metrics.get('total_conversions_today', 0)}")
        print(f"   • Conversões geek: {current_metrics.get('geek_conversions_today', 0)}")
        print(f"   • Conversões gerais: {current_metrics.get('general_conversions_today', 0)}")
        print(f"   • Receita total: R$ {current_metrics.get('total_revenue_today', '0.00')}")
        
        return tracker
        
    except Exception as e:
        print(f"❌ Erro no rastreamento: {e}")
        return None


async def demo_conversion_analysis(tracker: ConversionTracker):
    """Demonstra análise de conversões"""
    print("\n📈 DEMONSTRAÇÃO: Análise de Conversões")
    print("=" * 60)
    
    try:
        # Inicializar analyzer
        analyzer = ConversionAnalyzer(tracker)
        
        # Gerar análise
        print("Gerando análise de conversões...")
        analysis_report = await analyzer.analyze_conversions("day")
        
        print(f"✅ Análise concluída!")
        print(f"📋 {analysis_report.summary}")
        print(f"🎯 Score de Performance: {analysis_report.performance_score:.1f}/100")
        
        # Mostrar insights
        if analysis_report.insights:
            print(f"\n💡 INSIGHTS ({len(analysis_report.insights)}):")
            for insight in analysis_report.insights[:3]:  # Mostrar apenas 3
                emoji = "⚠️" if insight.severity in ["high", "critical"] else "💡" if insight.insight_type == "opportunity" else "📊"
                print(f"   {emoji} {insight.title}: {insight.description}")
        
        # Mostrar tendências
        if analysis_report.trends:
            print(f"\n📈 TENDÊNCIAS ({len(analysis_report.trends)}):")
            for trend in analysis_report.trends[:3]:  # Mostrar apenas 3
                emoji = "📈" if trend.trend_direction == "up" else "📉" if trend.trend_direction == "down" else "➡️"
                print(f"   {emoji} {trend.description}")
        
        # Mostrar recomendações
        if analysis_report.recommendations:
            print(f"\n🚀 RECOMENDAÇÕES ({len(analysis_report.recommendations)}):")
            for rec in analysis_report.recommendations[:5]:  # Mostrar apenas 5
                print(f"   • {rec}")
        
        return analyzer
        
    except Exception as e:
        print(f"❌ Erro na análise: {e}")
        return None


async def demo_conversion_dashboard(tracker: ConversionTracker, analyzer: ConversionAnalyzer):
    """Demonstra dashboard de conversões"""
    print("\n📊 DEMONSTRAÇÃO: Dashboard de Conversões")
    print("=" * 60)
    
    try:
        # Inicializar dashboard
        dashboard = ConversionDashboard(tracker, analyzer)
        
        # Configurar dashboard para atualização rápida
        dashboard.set_update_interval(5)  # 5 segundos
        
        print("Iniciando dashboard (5 segundos)...")
        
        # Simular algumas conversões durante o dashboard
        for i in range(3):
            # Aguardar 2 segundos
            await asyncio.sleep(2)
            
            # Simular conversão
            from src.core.models import Offer
            test_offer = Offer(
                title=f"Produto Teste {i+1}",
                price=Decimal("99.99"),
                url=f"https://exemplo.com/produto{i}",
                store="Loja Teste",
                original_price=Decimal("129.99"),
                discount_percentage=23.1,
                category="gaming_accessories" if i % 2 == 0 else "home_appliances",
                stock_quantity=10,
                image_url=f"https://exemplo.com/img{i}.jpg",
                description=f"Produto de teste {i+1}",
                scraped_at=datetime.now()
            )
            
            await tracker.track_conversion(
                test_offer,
                "purchase",
                "geek" if i % 2 == 0 else "general",
                revenue=Decimal("99.99"),
                commission=Decimal("9.99")
            )
        
        # Obter estatísticas rápidas
        quick_stats = await dashboard.get_quick_stats()
        
        print(f"\n📊 Estatísticas Rápidas:")
        print(f"   • Conversões hoje: {quick_stats.get('total_conversions_today', 0)}")
        print(f"   • Conversões geek: {quick_stats.get('geek_conversions_today', 0)}")
        print(f"   • Conversões gerais: {quick_stats.get('general_conversions_today', 0)}")
        print(f"   • Receita total: R$ {quick_stats.get('total_revenue_today', '0.00')}")
        print(f"   • Rastreamento: {'✅ Ativo' if quick_stats.get('tracking_enabled', False) else '❌ Inativo'}")
        
        # Gerar relatório resumido
        summary_report = await dashboard.generate_summary_report()
        
        print(f"\n📋 Relatório Resumido:")
        print(f"   • Score de Performance: {summary_report.get('performance_score', 0):.1f}/100")
        print(f"   • Insights críticos: {summary_report.get('critical_insights_count', 0)}")
        print(f"   • Tendências: {summary_report.get('trends_count', 0)}")
        print(f"   • Recomendações: {summary_report.get('recommendations_count', 0)}")
        
        return dashboard
        
    except Exception as e:
        print(f"❌ Erro no dashboard: {e}")
        return None


async def demo_conversion_reports(tracker: ConversionTracker, analyzer: ConversionAnalyzer):
    """Demonstra geração de relatórios"""
    print("\n📄 DEMONSTRAÇÃO: Relatórios de Conversão")
    print("=" * 60)
    
    try:
        # Inicializar reporter
        reporter = ConversionReporter(tracker, analyzer)
        
        # Gerar relatório diário (JSON)
        print("Gerando relatório diário (JSON)...")
        daily_report_path = await reporter.generate_daily_report()
        print(f"✅ Relatório diário: {daily_report_path}")
        
        # Gerar relatório semanal (HTML)
        print("Gerando relatório semanal (HTML)...")
        weekly_report_path = await reporter.generate_weekly_report()
        print(f"✅ Relatório semanal: {weekly_report_path}")
        
        # Gerar relatório mensal (CSV)
        print("Gerando relatório mensal (CSV)...")
        monthly_report_path = await reporter.generate_monthly_report()
        print(f"✅ Relatório mensal: {monthly_report_path}")
        
        # Gerar relatório customizado
        print("Gerando relatório customizado...")
        from src.app.conversion_monitoring.conversion_reporter import ReportConfig
        
        custom_config = ReportConfig(
            report_type="custom",
            period="day",
            include_insights=True,
            include_trends=True,
            include_recommendations=True,
            include_category_breakdown=True,
            export_format="json",
            output_directory="reports"
        )
        
        custom_report_data = await reporter.generate_report(custom_config)
        custom_report_path = await reporter.export_report(custom_report_data, custom_config)
        print(f"✅ Relatório customizado: {custom_report_path}")
        
        return reporter
        
    except Exception as e:
        print(f"❌ Erro nos relatórios: {e}")
        return None


async def demo_complete_workflow():
    """Demonstra workflow completo"""
    print("\n🔄 DEMONSTRAÇÃO: Workflow Completo")
    print("=" * 60)
    
    try:
        # 1. Rastreamento
        tracker = await demo_conversion_tracking()
        if not tracker:
            return
        
        # 2. Análise
        analyzer = await demo_conversion_analysis(tracker)
        if not analyzer:
            return
        
        # 3. Dashboard
        dashboard = await demo_conversion_dashboard(tracker, analyzer)
        if not dashboard:
            return
        
        # 4. Relatórios
        reporter = await demo_conversion_reports(tracker, analyzer)
        if not reporter:
            return
        
        # Salvar dados
        await tracker.save_data()
        
        print(f"\n🎉 WORKFLOW COMPLETO CONCLUÍDO!")
        print("=" * 60)
        print("✅ Todos os componentes funcionando:")
        print("   • Rastreamento de conversões")
        print("   • Análise e insights")
        print("   • Dashboard em tempo real")
        print("   • Geração de relatórios")
        print("\n📁 Relatórios salvos em: reports/")
        print("💾 Dados salvos em: conversion_data.json")
        
        return {
            "tracker": tracker,
            "analyzer": analyzer,
            "dashboard": dashboard,
            "reporter": reporter
        }
        
    except Exception as e:
        print(f"❌ Erro no workflow: {e}")
        import traceback
        traceback.print_exc()
        return None


async def main():
    """Função principal da demonstração"""
    print("🎯 DEMONSTRAÇÃO COMPLETA DO SISTEMA DE MONITORAMENTO DE CONVERSÃO")
    print("=" * 80)
    print("Este script demonstra o sistema completo de monitoramento de conversões")
    print("geek vs geral do Garimpeiro Geek.")
    print("=" * 80)
    
    try:
        # Executar workflow completo
        results = await demo_complete_workflow()
        
        if results:
            # Salvar resultados da demonstração
            demo_file = "conversion_monitoring_demo_results.json"
            demo_data = {
                "demo_info": {
                    "timestamp": datetime.now().isoformat(),
                    "components_tested": ["tracker", "analyzer", "dashboard", "reporter"],
                    "status": "success"
                },
                "tracker_stats": {
                    "total_events": len(results["tracker"].conversion_events),
                    "tracking_enabled": results["tracker"].tracking_enabled
                },
                "dashboard_stats": results["dashboard"].dashboard_stats
            }
            
            with open(demo_file, 'w', encoding='utf-8') as f:
                json.dump(demo_data, f, indent=2, ensure_ascii=False, default=str)
            
            print(f"\n💾 Resultados da demonstração salvos em: {demo_file}")
            print("🚀 Sistema de monitoramento de conversão pronto para uso!")
            
            return 0
        else:
            print("\n❌ Demonstração falhou")
            return 1
            
    except Exception as e:
        print(f"\n❌ Erro durante demonstração: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⚠️ Demonstração interrompida pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro fatal: {e}")
        sys.exit(1)
