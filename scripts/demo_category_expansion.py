"""
Demonstração do Sistema de Expansão de Categorias
Mostra como o sistema analisa, expande e otimiza categorias automaticamente
"""

import asyncio
import json
from datetime import datetime
from decimal import Decimal
from typing import Dict, List

from src.app.category_expansion import (
    CategoryAnalyzer, CategoryExpander, MarketResearcher, CategoryOptimizer,
    CategoryTrend, CategoryInsight, ExpansionSuggestion, MarketTrend, 
    ProductCategory, OptimizationResult, CategoryScore
)
from src.core.models import Offer


class CategoryExpansionDemo:
    """Demonstração do sistema de expansão de categorias"""
    
    def __init__(self):
        self.category_analyzer = CategoryAnalyzer()
        self.category_expander = CategoryExpander()
        self.market_researcher = MarketResearcher()
        self.category_optimizer = CategoryOptimizer()
        
        # Dados simulados
        self.categories = [
            "gaming", "anime", "tech", "nerd", "otaku", "cosplay",
            "board_games", "collectibles", "electronics", "smart_home"
        ]
    
    async def run_full_demo(self):
        """Executa demonstração completa do sistema"""
        print("🚀 INICIANDO DEMONSTRAÇÃO DO SISTEMA DE EXPANSÃO DE CATEGORIAS")
        print("=" * 80)
        
        try:
            # 1. Análise de Categorias
            print("\n📊 ETAPA 1: ANÁLISE DE CATEGORIAS")
            print("-" * 50)
            await self._demo_category_analysis()
            
            # 2. Pesquisa de Mercado
            print("\n🔍 ETAPA 2: PESQUISA DE MERCADO")
            print("-" * 50)
            await self._demo_market_research()
            
            # 3. Geração de Sugestões de Expansão
            print("\n💡 ETAPA 3: GERAÇÃO DE SUGESTÕES DE EXPANSÃO")
            print("-" * 50)
            await self._demo_expansion_suggestions()
            
            # 4. Implementação de Expansões
            print("\n✅ ETAPA 4: IMPLEMENTAÇÃO DE EXPANSÕES")
            print("-" * 50)
            await self._demo_expansion_implementation()
            
            # 5. Otimização de Categorias
            print("\n⚡ ETAPA 5: OTIMIZAÇÃO DE CATEGORIAS")
            print("-" * 50)
            await self._demo_category_optimization()
            
            # 6. Resumo Final
            print("\n📋 RESUMO FINAL")
            print("-" * 50)
            await self._demo_final_summary()
            
            print("\n🎉 DEMONSTRAÇÃO CONCLUÍDA COM SUCESSO!")
            
        except Exception as e:
            print(f"❌ Erro na demonstração: {e}")
    
    async def _demo_category_analysis(self):
        """Demonstra análise de categorias"""
        try:
            # Analisar tendências
            print("🔍 Analisando tendências de categorias...")
            trends = await self.category_analyzer.analyze_category_trends(days_back=30)
            
            # Mostrar top tendências
            print("\n📈 TOP 5 TENDÊNCIAS DE CATEGORIAS:")
            sorted_trends = sorted(trends, key=lambda x: x.trend_score, reverse=True)[:5]
            for i, trend in enumerate(sorted_trends, 1):
                print(f"  {i}. {trend.category}: Score {trend.trend_score:.2f} "
                      f"({trend.trend_direction}, +{trend.growth_rate:.1%})")
            
            # Gerar insights
            print("\n💡 Gerando insights de categoria...")
            insights = await self.category_analyzer.generate_category_insights(trends)
            
            print(f"\n📊 INSIGHTS GERADOS: {len(insights)}")
            for insight in insights[:3]:  # Mostrar apenas 3
                print(f"  • {insight.category}: {insight.description}")
            
            # Simular feedback de usuários
            print("\n👥 Analisando preferências dos usuários...")
            user_feedback = self._generate_simulated_user_feedback()
            user_preferences = await self.category_analyzer.analyze_user_preferences(user_feedback)
            
            print(f"\n📈 PREFERÊNCIAS DOS USUÁRIOS:")
            for category, score in sorted(user_preferences.items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"  • {category}: {score:.2f}/5.0")
            
            # Identificar oportunidades
            print("\n🎯 Identificando oportunidades de expansão...")
            opportunities = await self.category_analyzer.identify_expansion_opportunities(
                trends, insights, user_preferences
            )
            
            print(f"\n🎯 OPORTUNIDADES IDENTIFICADAS: {len(opportunities)}")
            for opportunity in opportunities:
                print(f"  • {opportunity}")
            
            # Salvar dados para próximas etapas
            self.trends = trends
            self.insights = insights
            self.user_preferences = user_preferences
            self.opportunities = opportunities
            
        except Exception as e:
            print(f"❌ Erro na análise de categorias: {e}")
    
    async def _demo_market_research(self):
        """Demonstra pesquisa de mercado"""
        try:
            # Analisar tendências de mercado
            print("📈 Analisando tendências de mercado...")
            market_trends = await self.market_researcher.analyze_market_trends(self.categories)
            
            print(f"\n📊 TENDÊNCIAS DE MERCADO ANALISADAS: {len(market_trends)}")
            
            # Pesquisar categorias de produto
            print("\n🔍 Pesquisando categorias de produto...")
            product_categories = await self.market_researcher.research_product_categories(self.categories)
            
            print(f"\n📦 CATEGORIAS DE PRODUTO PESQUISADAS: {len(product_categories)}")
            for category in product_categories[:5]:  # Mostrar apenas 5
                print(f"  • {category.name}: Volume {category.market_volume:,}, "
                      f"Preço médio R$ {category.average_price:.2f}, "
                      f"Crescimento {category.growth_rate:.1%}")
            
            # Analisar competidores
            print("\n🏢 Analisando competidores...")
            competitor_analysis = await self.market_researcher.analyze_competitors(self.categories[:5])
            
            print(f"\n🏢 ANÁLISE DE COMPETIDORES:")
            for category, competitors in competitor_analysis.items():
                print(f"  • {category}: {len(competitors)} competidores identificados")
            
            # Identificar oportunidades de mercado
            print("\n🎯 Identificando oportunidades de mercado...")
            market_opportunities = await self.market_researcher.identify_market_opportunities(
                market_trends, product_categories
            )
            
            print(f"\n🎯 OPORTUNIDADES DE MERCADO: {len(market_opportunities)}")
            for opportunity in market_opportunities[:3]:  # Mostrar apenas 3
                print(f"  • {opportunity['category']}: {opportunity['trend_name']} "
                      f"(Score: {opportunity['opportunity_score']:.2f})")
            
            # Gerar insights sazonais
            print("\n📅 Gerando insights sazonais...")
            seasonal_insights = await self.market_researcher.generate_seasonal_insights(self.categories[:5])
            
            print(f"\n📅 INSIGHTS SAZONAIS:")
            for category, insights in seasonal_insights.items():
                print(f"  • {category}: {len(insights)} padrões sazonais")
            
            # Salvar dados para próximas etapas
            self.market_trends = market_trends
            self.product_categories = product_categories
            self.market_opportunities = market_opportunities
            
        except Exception as e:
            print(f"❌ Erro na pesquisa de mercado: {e}")
    
    async def _demo_expansion_suggestions(self):
        """Demonstra geração de sugestões de expansão"""
        try:
            # Converter tendências para formato esperado
            trends_data = [{"category": t.category, "trend_score": t.trend_score} for t in self.trends]
            
            # Gerar sugestões de expansão
            print("💡 Gerando sugestões de expansão...")
            suggestions = await self.category_expander.generate_expansion_suggestions(
                self.opportunities, trends_data, self.user_preferences
            )
            
            print(f"\n💡 SUGESTÕES DE EXPANSÃO GERADAS: {len(suggestions)}")
            
            # Agrupar por tipo de expansão
            by_type = {}
            for suggestion in suggestions:
                exp_type = suggestion.expansion_type.value
                if exp_type not in by_type:
                    by_type[exp_type] = []
                by_type[exp_type].append(suggestion)
            
            for exp_type, type_suggestions in by_type.items():
                print(f"\n📋 {exp_type.upper()}: {len(type_suggestions)} sugestões")
                for suggestion in type_suggestions[:3]:  # Mostrar apenas 3 por tipo
                    print(f"  • {suggestion.original_category} → {suggestion.new_category} "
                          f"(Confiança: {suggestion.confidence_score:.2f}, "
                          f"Impacto: {suggestion.expected_impact})")
            
            # Expandir palavras-chave
            print("\n🔍 Expandindo palavras-chave...")
            for category in self.categories[:3]:  # Apenas 3 categorias
                keywords = await self.category_expander.expand_category_keywords(category)
                print(f"  • {category}: {len(keywords)} palavras-chave expandidas")
            
            # Criar mapeamentos de categoria
            print("\n🗺️ Criando mapeamentos de categoria...")
            mapping = await self.category_expander.create_category_mapping(
                "gaming", "esports",
                ["esports", "competitive", "tournament"],
                ["competitivo", "torneio", "profissional"]
            )
            if mapping:
                print(f"  ✅ Mapeamento criado: {mapping.source_category} → {mapping.target_category}")
            
            # Salvar sugestões para próxima etapa
            self.expansion_suggestions = suggestions
            
        except Exception as e:
            print(f"❌ Erro na geração de sugestões: {e}")
    
    async def _demo_expansion_implementation(self):
        """Demonstra implementação de expansões"""
        try:
            # Implementar sugestões de expansão
            print("✅ Implementando sugestões de expansão...")
            implemented_categories = await self.category_expander.implement_expansion_suggestions(
                self.expansion_suggestions, max_implementations=5
            )
            
            print(f"\n✅ CATEGORIAS IMPLEMENTADAS: {len(implemented_categories)}")
            for category in implemented_categories:
                print(f"  • {category}")
            
            # Mostrar resumo das expansões
            print("\n📋 Resumo das expansões...")
            expansion_summary = await self.category_expander.get_expansion_summary()
            
            print(f"\n📊 RESUMO DAS EXPANSÕES:")
            print(f"  • Total de sugestões: {expansion_summary.get('total_suggestions', 0)}")
            print(f"  • Sugestões implementadas: {expansion_summary.get('implemented_suggestions', 0)}")
            print(f"  • Categorias expandidas ativas: {expansion_summary.get('active_expanded_categories', 0)}")
            
            # Mostrar top sugestões
            print(f"\n🏆 TOP SUGESTÕES:")
            for suggestion in expansion_summary.get('top_suggestions', [])[:3]:
                print(f"  • {suggestion['from']} → {suggestion['to']} "
                      f"(Confiança: {suggestion['confidence']:.2f})")
            
        except Exception as e:
            print(f"❌ Erro na implementação de expansões: {e}")
    
    async def _demo_category_optimization(self):
        """Demonstra otimização de categorias"""
        try:
            # Gerar dados de performance simulados
            print("📊 Gerando dados de performance...")
            performance_data = self._generate_simulated_performance_data()
            
            # Calcular scores de categoria
            print("\n📈 Calculando scores de categoria...")
            category_scores = await self.category_optimizer.calculate_category_scores(
                self.categories, performance_data, self.user_preferences
            )
            
            print(f"\n📊 SCORES DE CATEGORIA CALCULADOS: {len(category_scores)}")
            for score in sorted(category_scores, key=lambda x: x.overall_score, reverse=True)[:5]:
                print(f"  • {score.category}: {score.overall_score:.2f} "
                      f"(Geek: {score.geek_relevance:.2f}, "
                      f"Performance: {score.performance_score:.2f})")
            
            # Identificar categorias com baixo desempenho
            print("\n⚠️ Identificando categorias com baixo desempenho...")
            underperforming = await self.category_optimizer.identify_underperforming_categories(
                category_scores, threshold=0.6
            )
            
            print(f"\n⚠️ CATEGORIAS COM BAIXO DESEMPENHO: {len(underperforming)}")
            for category in underperforming:
                print(f"  • {category}")
            
            # Sugerir melhorias
            print("\n💡 Sugerindo melhorias...")
            improvements = await self.category_optimizer.suggest_category_improvements(category_scores)
            
            print(f"\n💡 SUGESTÕES DE MELHORIA:")
            for category, suggestions in improvements.items():
                print(f"  • {category}:")
                for suggestion in suggestions[:2]:  # Apenas 2 sugestões por categoria
                    print(f"    - {suggestion}")
            
            # Otimização automática
            print("\n🤖 Aplicando otimização automática...")
            optimization_results = await self.category_optimizer.auto_optimize_categories(
                self.categories, performance_data, self.user_preferences, max_optimizations=5
            )
            
            print(f"\n⚡ OTIMIZAÇÕES APLICADAS: {len(optimization_results)}")
            for result in optimization_results[:3]:  # Mostrar apenas 3
                print(f"  • {result.category}: {result.improvement_percentage:.1f}% de melhoria "
                      f"({result.optimization_type.value})")
            
            # Mostrar resumo das otimizações
            print("\n📋 Resumo das otimizações...")
            optimization_summary = await self.category_optimizer.get_optimization_summary()
            
            print(f"\n📊 RESUMO DAS OTIMIZAÇÕES:")
            print(f"  • Total de otimizações: {optimization_summary.get('total_optimizations', 0)}")
            print(f"  • Melhoria média: {optimization_summary.get('average_improvement', 0):.1f}%")
            print(f"  • Scores de categoria: {optimization_summary.get('total_category_scores', 0)}")
            
        except Exception as e:
            print(f"❌ Erro na otimização de categorias: {e}")
    
    async def _demo_final_summary(self):
        """Demonstra resumo final"""
        try:
            print("📋 GERANDO RESUMO FINAL...")
            
            # Resumo da análise
            analysis_summary = await self.category_analyzer.get_analysis_summary()
            print(f"\n📊 ANÁLISE DE CATEGORIAS:")
            print(f"  • Tendências analisadas: {analysis_summary.get('total_trends', 0)}")
            print(f"  • Insights gerados: {analysis_summary.get('total_insights', 0)}")
            
            # Resumo da pesquisa de mercado
            market_summary = await self.market_researcher.get_market_research_summary()
            print(f"\n🔍 PESQUISA DE MERCADO:")
            print(f"  • Tendências de mercado: {market_summary.get('total_trends', 0)}")
            print(f"  • Categorias pesquisadas: {market_summary.get('total_categories', 0)}")
            print(f"  • Análises de competidores: {market_summary.get('total_competitor_analyses', 0)}")
            
            # Resumo das expansões
            expansion_summary = await self.category_expander.get_expansion_summary()
            print(f"\n💡 EXPANSÕES DE CATEGORIAS:")
            print(f"  • Sugestões geradas: {expansion_summary.get('total_suggestions', 0)}")
            print(f"  • Implementadas: {expansion_summary.get('implemented_suggestions', 0)}")
            print(f"  • Categorias ativas: {expansion_summary.get('active_expanded_categories', 0)}")
            
            # Resumo das otimizações
            optimization_summary = await self.category_optimizer.get_optimization_summary()
            print(f"\n⚡ OTIMIZAÇÕES:")
            print(f"  • Otimizações aplicadas: {optimization_summary.get('total_optimizations', 0)}")
            print(f"  • Melhoria média: {optimization_summary.get('average_improvement', 0):.1f}%")
            
            print(f"\n🎯 RESULTADO FINAL:")
            print(f"  • Sistema de expansão de categorias implementado com sucesso!")
            print(f"  • {len(self.opportunities)} oportunidades identificadas")
            print(f"  • {len(self.expansion_suggestions)} sugestões geradas")
            print(f"  • {len(optimization_summary.get('top_optimizations', []))} otimizações aplicadas")
            
        except Exception as e:
            print(f"❌ Erro no resumo final: {e}")
    
    def _generate_simulated_user_feedback(self) -> List[Dict]:
        """Gera feedback de usuários simulado"""
        feedback = []
        
        for category in self.categories:
            # Simular múltiplas avaliações por categoria
            for i in range(5):  # 5 avaliações por categoria
                rating = 3.5 + (hash(f"{category}_{i}") % 15) / 10  # Rating entre 3.5 e 5.0
                feedback.append({
                    "category": category,
                    "rating": rating,
                    "user_id": f"user_{i}",
                    "timestamp": datetime.now().isoformat()
                })
        
        return feedback
    
    def _generate_simulated_performance_data(self) -> Dict[str, Dict]:
        """Gera dados de performance simulados"""
        performance_data = {}
        
        for category in self.categories:
            # Simular dados de performance baseados no hash da categoria
            category_hash = hash(category) % 1000
            performance_data[category] = {
                "performance_score": 0.6 + (category_hash % 40) / 100,  # 0.6 a 1.0
                "conversion_rate": 0.02 + (category_hash % 8) / 100,   # 0.02 a 0.10
                "click_rate": 0.05 + (category_hash % 15) / 100,       # 0.05 a 0.20
                "revenue": 500 + (category_hash % 5000)                # 500 a 5500
            }
        
        return performance_data


async def demo_quick_test():
    """Teste rápido do sistema"""
    print("🚀 TESTE RÁPIDO DO SISTEMA DE EXPANSÃO DE CATEGORIAS")
    print("=" * 60)
    
    try:
        demo = CategoryExpansionDemo()
        
        # Teste básico de análise
        print("\n📊 Testando análise de categorias...")
        trends = await demo.category_analyzer.analyze_category_trends(days_back=7)
        print(f"✅ {len(trends)} tendências analisadas")
        
        # Teste básico de expansão
        print("\n💡 Testando expansão de categorias...")
        keywords = await demo.category_expander.expand_category_keywords("gaming")
        print(f"✅ {len(keywords)} palavras-chave expandidas para gaming")
        
        # Teste básico de otimização
        print("\n⚡ Testando otimização de categorias...")
        performance_data = demo._generate_simulated_performance_data()
        user_feedback = demo._generate_simulated_user_feedback()
        user_preferences = await demo.category_analyzer.analyze_user_preferences(user_feedback)
        
        category_scores = await demo.category_optimizer.calculate_category_scores(
            ["gaming", "anime", "tech"], performance_data, user_preferences
        )
        print(f"✅ {len(category_scores)} scores calculados")
        
        print("\n🎉 TESTE RÁPIDO CONCLUÍDO COM SUCESSO!")
        
    except Exception as e:
        print(f"❌ Erro no teste rápido: {e}")


async def main():
    """Função principal"""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "quick":
        await demo_quick_test()
    else:
        demo = CategoryExpansionDemo()
        await demo.run_full_demo()


if __name__ == "__main__":
    asyncio.run(main())
