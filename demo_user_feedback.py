#!/usr/bin/env python3
"""
Demonstração do Sistema de Feedback dos Usuários
Testa todas as funcionalidades do sistema de ajuste de scores baseado no feedback
"""

import asyncio
import logging
import random
from datetime import datetime, timedelta
from decimal import Decimal

from src.app.user_feedback import (
    FeedbackCollector,
    FeedbackAnalyzer,
    ScoreAdjuster,
    FeedbackDashboard,
    AdjustmentConfig,
    FeedbackType
)
from src.core.models import Offer
from src.core.geek_prioritizer import GeekPrioritizer


# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class UserFeedbackDemo:
    """Demonstração completa do sistema de feedback dos usuários"""
    
    def __init__(self):
        self.feedback_collector = FeedbackCollector()
        self.feedback_analyzer = FeedbackAnalyzer(self.feedback_collector)
        
        # Configuração para demonstração
        config = AdjustmentConfig(
            min_confidence=0.3,  # Mais permissivo para demo
            max_adjustment_factor=3.0,
            min_feedback_sample=5,  # Menor para demo
            auto_apply=False,  # Manual para demo
            adjustment_cooldown_days=1,
            backup_before_adjustment=True
        )
        
        self.score_adjuster = ScoreAdjuster(
            self.feedback_collector,
            self.feedback_analyzer,
            config
        )
        
        self.dashboard = FeedbackDashboard(
            self.feedback_collector,
            self.feedback_analyzer,
            self.score_adjuster
        )
        
        self.geek_prioritizer = GeekPrioritizer()
        
        # Dados de teste
        self.test_categories = [
            'games', 'anime', 'tech', 'geek', 'electronics',
            'smartphones', 'notebooks', 'consoles', 'action_figures', 'cosplay'
        ]
        
        self.test_users = [
            'user_001', 'user_002', 'user_003', 'user_004', 'user_005',
            'user_006', 'user_007', 'user_008', 'user_009', 'user_010'
        ]
    
    async def run_demo(self):
        """Executa a demonstração completa"""
        try:
            print("\n" + "="*80)
            print("🎯 DEMONSTRAÇÃO DO SISTEMA DE FEEDBACK DOS USUÁRIOS")
            print("="*80)
            
            # Etapa 1: Coletar feedback simulado
            print("\n📊 ETAPA 1: Coletando feedback simulado...")
            await self._simulate_feedback_collection()
            
            # Etapa 2: Analisar feedback
            print("\n📈 ETAPA 2: Analisando feedback...")
            await self._analyze_feedback()
            
            # Etapa 3: Sugerir ajustes
            print("\n⚖️  ETAPA 3: Sugerindo ajustes de score...")
            await self._suggest_adjustments()
            
            # Etapa 4: Aplicar ajustes
            print("\n🔧 ETAPA 4: Aplicando ajustes...")
            await self._apply_adjustments()
            
            # Etapa 5: Gerar insights
            print("\n💡 ETAPA 5: Gerando insights...")
            await self._generate_insights()
            
            # Etapa 6: Dashboard interativo
            print("\n🎛️  ETAPA 6: Iniciando dashboard interativo...")
            await self._start_dashboard()
            
            print("\n✅ Demonstração concluída com sucesso!")
            
        except Exception as e:
            logger.error(f"Erro na demonstração: {e}")
            print(f"❌ Erro na demonstração: {e}")
    
    async def _simulate_feedback_collection(self):
        """Simula coleta de feedback"""
        try:
            print("   Coletando feedback de diferentes usuários e categorias...")
            
            # Gerar ofertas de teste
            test_offers = self._generate_test_offers()
            
            # Simular feedback para cada categoria
            for category in self.test_categories:
                print(f"   📝 Simulando feedback para categoria: {category}")
                
                # Selecionar ofertas da categoria
                category_offers = [offer for offer in test_offers if category in offer.url.lower()]
                
                if not category_offers:
                    continue
                
                # Simular feedback de múltiplos usuários
                for user_id in random.sample(self.test_users, random.randint(3, 6)):
                    # Simular diferentes tipos de feedback
                    await self._simulate_user_feedback(user_id, category_offers, category)
            
            # Mostrar resumo
            summary = await self.feedback_collector.get_feedback_summary(days=1)
            print(f"   ✅ Feedback coletado: {summary.get('total_feedback', 0)} registros")
            print(f"   👥 Usuários únicos: {summary.get('unique_users', 0)}")
            
        except Exception as e:
            logger.error(f"Erro ao simular coleta de feedback: {e}")
            raise
    
    async def _simulate_user_feedback(self, user_id: str, offers: list, category: str):
        """Simula feedback de um usuário específico"""
        try:
            # Selecionar ofertas aleatórias
            selected_offers = random.sample(offers, min(len(offers), random.randint(1, 3)))
            
            for offer in selected_offers:
                # Simular diferentes tipos de feedback com pesos
                feedback_types = [
                    (FeedbackType.CLICK, 0.4),      # 40% de cliques
                    (FeedbackType.LIKE, 0.2),       # 20% de likes
                    (FeedbackType.RATING, 0.2),     # 20% de avaliações
                    (FeedbackType.PURCHASE, 0.1),   # 10% de compras
                    (FeedbackType.DISLIKE, 0.1)     # 10% de dislikes
                ]
                
                feedback_type, weight = random.choices(feedback_types, weights=[w for _, w in feedback_types])[0]
                
                if feedback_type == FeedbackType.CLICK:
                    await self.feedback_collector.collect_click_feedback(user_id, offer)
                
                elif feedback_type == FeedbackType.LIKE:
                    await self.feedback_collector.collect_feedback(
                        user_id, offer, FeedbackType.LIKE, 1,
                        metadata={"category": category}
                    )
                
                elif feedback_type == FeedbackType.RATING:
                    rating = random.randint(1, 5)
                    await self.feedback_collector.collect_rating_feedback(user_id, offer, rating)
                
                elif feedback_type == FeedbackType.PURCHASE:
                    purchase_value = Decimal(str(random.randint(50, 500)))
                    await self.feedback_collector.collect_purchase_feedback(user_id, offer, purchase_value)
                
                elif feedback_type == FeedbackType.DISLIKE:
                    await self.feedback_collector.collect_feedback(
                        user_id, offer, FeedbackType.DISLIKE, 1,
                        metadata={"category": category}
                    )
                
                # Pequena pausa entre feedbacks
                await asyncio.sleep(0.01)
                
        except Exception as e:
            logger.error(f"Erro ao simular feedback do usuário {user_id}: {e}")
    
    def _generate_test_offers(self) -> list:
        """Gera ofertas de teste para diferentes categorias"""
        offers = []
        
        for category in self.test_categories:
            # Gerar múltiplas ofertas por categoria
            for i in range(random.randint(2, 5)):
                offer = Offer(
                    title=f"Produto {category.title()} {i}",
                    price=Decimal(str(random.randint(50, 500))),
                    url=f"https://exemplo.com/{category}/produto_{i}",
                    store=f"Loja {category.title()}",
                    category=category,
                    scraped_at=datetime.now() - timedelta(hours=random.randint(1, 24))
                )
                offers.append(offer)
        
        return offers
    
    async def _analyze_feedback(self):
        """Analisa o feedback coletado"""
        try:
            print("   Analisando preferências dos usuários...")
            
            # Analisar preferências de alguns usuários
            for user_id in self.test_users[:3]:
                preferences = await self.feedback_analyzer.analyze_user_preferences(user_id, days=1)
                if preferences:
                    print(f"   👤 {user_id}: {len(preferences)} preferências detectadas")
                    top_pref = preferences[0] if preferences else None
                    if top_pref:
                        print(f"      🎯 Top: {top_pref.category} (score: {top_pref.preference_score:.2f})")
            
            print("   Analisando performance das categorias...")
            performances = await self.feedback_analyzer.analyze_category_performance(days=1)
            
            if performances:
                print(f"   📊 {len(performances)} categorias analisadas")
                top_perf = performances[0] if performances else None
                if top_perf:
                    print(f"      🏆 Melhor performance: {top_perf.category} (score: {top_perf.performance_score:.2f})")
            
        except Exception as e:
            logger.error(f"Erro ao analisar feedback: {e}")
            raise
    
    async def _suggest_adjustments(self):
        """Sugere ajustes de score"""
        try:
            print("   Gerando sugestões de ajuste...")
            
            suggestions = await self.score_adjuster.analyze_and_suggest_adjustments(days=1)
            
            if suggestions:
                print(f"   🎯 {len(suggestions)} sugestões de ajuste geradas:")
                for i, suggestion in enumerate(suggestions[:5], 1):
                    print(f"      {i}. {suggestion.category}: {suggestion.current_score:.2f} → {suggestion.suggested_score:.2f} "
                          f"(fator: {suggestion.adjustment_factor:.2f}, confiança: {suggestion.confidence:.2f})")
            else:
                print("   ℹ️  Nenhuma sugestão de ajuste no momento")
            
        except Exception as e:
            logger.error(f"Erro ao sugerir ajustes: {e}")
            raise
    
    async def _apply_adjustments(self):
        """Aplica ajustes de score"""
        try:
            print("   Aplicando ajustes de score...")
            
            # Obter sugestões
            suggestions = await self.score_adjuster.analyze_and_suggest_adjustments(days=1)
            
            if not suggestions:
                print("   ℹ️  Nenhum ajuste para aplicar")
                return
            
            # Aplicar alguns ajustes (limitado para demo)
            applied_count = 0
            for suggestion in suggestions[:3]:  # Aplicar no máximo 3 ajustes
                success = await self.score_adjuster.apply_score_adjustment(suggestion, force=True)
                if success:
                    applied_count += 1
                    print(f"   ✅ Ajuste aplicado: {suggestion.category} ({suggestion.current_score:.2f} → {suggestion.suggested_score:.2f})")
                else:
                    print(f"   ❌ Falha ao aplicar ajuste: {suggestion.category}")
            
            print(f"   📊 Total de ajustes aplicados: {applied_count}")
            
        except Exception as e:
            logger.error(f"Erro ao aplicar ajustes: {e}")
            raise
    
    async def _generate_insights(self):
        """Gera insights e recomendações"""
        try:
            print("   Gerando insights...")
            
            insights = await self.feedback_analyzer.generate_feedback_insights(days=1)
            
            if insights:
                print(f"   💡 {len(insights)} insights gerados:")
                for i, insight in enumerate(insights, 1):
                    print(f"      {i}. {insight.title}")
                    print(f"         📝 {insight.description}")
                    print(f"         🎯 Confiança: {insight.confidence:.2f}")
                    if insight.recommendations:
                        print(f"         💡 Recomendação: {insight.recommendations[0]}")
            else:
                print("   ℹ️  Nenhum insight disponível no momento")
            
        except Exception as e:
            logger.error(f"Erro ao gerar insights: {e}")
            raise
    
    async def _start_dashboard(self):
        """Inicia o dashboard interativo"""
        try:
            print("   Iniciando dashboard interativo...")
            print("   💡 Dica: Use a opção 7 para simular mais feedback")
            print("   💡 Dica: Use a opção 5 para gerenciar ajustes")
            
            # Iniciar dashboard
            await self.dashboard.start_dashboard()
            
        except Exception as e:
            logger.error(f"Erro no dashboard: {e}")
            raise
    
    async def demo_quick_test(self):
        """Teste rápido do sistema"""
        try:
            print("\n🚀 TESTE RÁPIDO DO SISTEMA DE FEEDBACK")
            print("="*50)
            
            # 1. Coletar feedback básico
            test_offer = Offer(
                title="Console de Games",
                price=Decimal("299.99"),
                url="https://exemplo.com/games/console",
                store="Loja Games",
                category="games",
                scraped_at=datetime.now()
            )
            
            await self.feedback_collector.collect_click_feedback("test_user", test_offer)
            await self.feedback_collector.collect_rating_feedback("test_user", test_offer, 5)
            await self.feedback_collector.collect_category_preference("test_user", "games", 0.8)
            
            # 2. Analisar
            preferences = await self.feedback_analyzer.analyze_user_preferences("test_user", days=1)
            performances = await self.feedback_analyzer.analyze_category_performance(days=1)
            
            # 3. Sugerir ajustes
            suggestions = await self.score_adjuster.analyze_and_suggest_adjustments(days=1)
            
            # 4. Mostrar resultados
            print(f"✅ Feedback coletado: {len(preferences)} preferências detectadas")
            print(f"✅ Performance analisada: {len(performances)} categorias")
            print(f"✅ Sugestões geradas: {len(suggestions)} ajustes")
            
            if suggestions:
                print(f"🎯 Exemplo de sugestão: {suggestions[0].category} "
                      f"({suggestions[0].current_score:.2f} → {suggestions[0].suggested_score:.2f})")
            
            print("\n✅ Teste rápido concluído!")
            
        except Exception as e:
            logger.error(f"Erro no teste rápido: {e}")
            print(f"❌ Erro no teste rápido: {e}")


async def main():
    """Função principal"""
    try:
        demo = UserFeedbackDemo()
        
        # Perguntar tipo de demonstração
        print("\n🎯 SISTEMA DE FEEDBACK DOS USUÁRIOS - GARIMPEIRO GEEK")
        print("="*60)
        print("1. 🚀 Teste Rápido")
        print("2. 📊 Demonstração Completa")
        print("3. 🎛️  Dashboard Interativo")
        print("0. 🚪 Sair")
        
        choice = input("\nEscolha uma opção: ").strip()
        
        if choice == "1":
            await demo.demo_quick_test()
        elif choice == "2":
            await demo.run_demo()
        elif choice == "3":
            await demo.dashboard.start_dashboard()
        elif choice == "0":
            print("👋 Saindo...")
        else:
            print("❌ Opção inválida. Executando teste rápido...")
            await demo.demo_quick_test()
            
    except KeyboardInterrupt:
        print("\n\n👋 Demonstração interrompida pelo usuário.")
    except Exception as e:
        logger.error(f"Erro na demonstração: {e}")
        print(f"❌ Erro na demonstração: {e}")


if __name__ == "__main__":
    asyncio.run(main())
