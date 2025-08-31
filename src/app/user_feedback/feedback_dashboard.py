"""
Dashboard de Feedback dos Usuários
Interface para visualização e gerenciamento do sistema de feedback
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any
import os
import sys

from .feedback_collector import FeedbackCollector, FeedbackType
from .feedback_analyzer import FeedbackAnalyzer
from .score_adjuster import ScoreAdjuster, AdjustmentConfig
from src.core.models import Offer


@dataclass
class DashboardStats:
    """Estatísticas do dashboard"""
    total_feedback: int
    unique_users: int
    feedback_by_type: Dict[str, int]
    top_categories: List[Dict[str, Any]]
    recent_adjustments: List[Dict[str, Any]]
    system_health: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return asdict(self)


class FeedbackDashboard:
    """Dashboard para visualização e gerenciamento do sistema de feedback"""
    
    def __init__(
        self,
        feedback_collector: FeedbackCollector,
        feedback_analyzer: FeedbackAnalyzer,
        score_adjuster: ScoreAdjuster
    ):
        self.feedback_collector = feedback_collector
        self.feedback_analyzer = feedback_analyzer
        self.score_adjuster = score_adjuster
        self.logger = logging.getLogger(__name__)
    
    async def start_dashboard(self) -> None:
        """Inicia o dashboard interativo"""
        try:
            print("\n" + "="*80)
            print("🎯 DASHBOARD DE FEEDBACK DOS USUÁRIOS - GARIMPEIRO GEEK")
            print("="*80)
            
            while True:
                await self._display_main_menu()
                choice = input("\nEscolha uma opção: ").strip()
                
                if choice == "1":
                    await self._show_feedback_overview()
                elif choice == "2":
                    await self._show_user_preferences()
                elif choice == "3":
                    await self._show_category_performance()
                elif choice == "4":
                    await self._show_score_adjustments()
                elif choice == "5":
                    await self._manage_adjustments()
                elif choice == "6":
                    await self._show_insights()
                elif choice == "7":
                    await self._simulate_feedback()
                elif choice == "0":
                    print("\n👋 Saindo do dashboard...")
                    break
                else:
                    print("\n❌ Opção inválida. Tente novamente.")
                
                input("\nPressione ENTER para continuar...")
                
        except KeyboardInterrupt:
            print("\n\n👋 Dashboard interrompido pelo usuário.")
        except Exception as e:
            self.logger.error(f"Erro no dashboard: {e}")
            print(f"\n❌ Erro no dashboard: {e}")
    
    async def _display_main_menu(self) -> None:
        """Exibe o menu principal"""
        print("\n" + "-"*60)
        print("📊 MENU PRINCIPAL")
        print("-"*60)
        print("1. 📈 Visão Geral do Feedback")
        print("2. 👤 Preferências dos Usuários")
        print("3. 🏷️  Performance das Categorias")
        print("4. ⚖️  Ajustes de Score")
        print("5. 🔧 Gerenciar Ajustes")
        print("6. 💡 Insights e Recomendações")
        print("7. 🧪 Simular Feedback")
        print("0. 🚪 Sair")
        print("-"*60)
    
    async def _show_feedback_overview(self) -> None:
        """Exibe visão geral do feedback"""
        try:
            print("\n" + "="*60)
            print("📈 VISÃO GERAL DO FEEDBACK")
            print("="*60)
            
            # Obter estatísticas
            summary = await self.feedback_collector.get_feedback_summary(days=7)
            
            if not summary:
                print("❌ Nenhum dado de feedback disponível.")
                return
            
            print(f"\n📊 Período: Últimos {summary['period_days']} dias")
            print(f"👥 Usuários únicos: {summary['unique_users']}")
            print(f"💬 Total de feedback: {summary['total_feedback']}")
            
            print("\n📋 Feedback por tipo:")
            for feedback_type, count in summary['feedback_by_type'].items():
                print(f"   • {feedback_type}: {count}")
            
            # Estatísticas de ajustes
            adjustment_summary = await self.score_adjuster.get_adjustment_summary(days=7)
            if adjustment_summary:
                print(f"\n⚖️  Ajustes aplicados: {adjustment_summary['total_adjustments']}")
                print(f"🎯 Confiança média: {adjustment_summary['average_confidence']:.2f}")
            
        except Exception as e:
            self.logger.error(f"Erro ao mostrar visão geral: {e}")
            print(f"❌ Erro: {e}")
    
    async def _show_user_preferences(self) -> None:
        """Exibe preferências dos usuários"""
        try:
            print("\n" + "="*60)
            print("👤 PREFERÊNCIAS DOS USUÁRIOS")
            print("="*60)
            
            user_id = input("Digite o ID do usuário (ou ENTER para ver todos): ").strip()
            
            if user_id:
                # Preferências de um usuário específico
                preferences = await self.feedback_analyzer.analyze_user_preferences(user_id)
                
                if not preferences:
                    print(f"❌ Nenhuma preferência encontrada para o usuário {user_id}")
                    return
                
                print(f"\n🎯 Preferências do usuário {user_id}:")
                for i, pref in enumerate(preferences[:10], 1):
                    print(f"{i:2d}. {pref.category:15s} | Score: {pref.preference_score:.2f} | Confiança: {pref.confidence:.2f} | Amostra: {pref.sample_size}")
            else:
                # Mostrar usuários mais ativos
                print("\n📊 Usuários mais ativos (simulado):")
                active_users = [
                    {"user_id": "user_001", "feedback_count": 45, "top_category": "games"},
                    {"user_id": "user_002", "feedback_count": 32, "top_category": "tech"},
                    {"user_id": "user_003", "feedback_count": 28, "top_category": "anime"},
                    {"user_id": "user_004", "feedback_count": 22, "top_category": "electronics"},
                    {"user_id": "user_005", "feedback_count": 18, "top_category": "geek"}
                ]
                
                for i, user in enumerate(active_users, 1):
                    print(f"{i:2d}. {user['user_id']:10s} | Feedback: {user['feedback_count']:3d} | Top: {user['top_category']}")
            
        except Exception as e:
            self.logger.error(f"Erro ao mostrar preferências: {e}")
            print(f"❌ Erro: {e}")
    
    async def _show_category_performance(self) -> None:
        """Exibe performance das categorias"""
        try:
            print("\n" + "="*60)
            print("🏷️  PERFORMANCE DAS CATEGORIAS")
            print("="*60)
            
            days = input("Período em dias (padrão: 30): ").strip()
            days = int(days) if days.isdigit() else 30
            
            performances = await self.feedback_analyzer.analyze_category_performance(days)
            
            if not performances:
                print("❌ Nenhuma performance de categoria disponível.")
                return
            
            print(f"\n📊 Performance das categorias (últimos {days} dias):")
            print("-" * 80)
            print(f"{'Categoria':<15} {'Feedback':<8} {'Positivo':<8} {'Rating':<6} {'Conversão':<10} {'Score':<6}")
            print("-" * 80)
            
            for perf in performances[:15]:
                print(f"{perf.category:<15} {perf.total_feedback:<8} {perf.positive_feedback:<8} "
                      f"{perf.average_rating:<6.1f} {perf.conversion_rate:<10.1%} {perf.performance_score:<6.2f}")
            
        except Exception as e:
            self.logger.error(f"Erro ao mostrar performance: {e}")
            print(f"❌ Erro: {e}")
    
    async def _show_score_adjustments(self) -> None:
        """Exibe ajustes de score"""
        try:
            print("\n" + "="*60)
            print("⚖️  AJUSTES DE SCORE")
            print("="*60)
            
            # Sugerir ajustes
            suggestions = await self.score_adjuster.analyze_and_suggest_adjustments()
            
            if not suggestions:
                print("✅ Nenhum ajuste de score sugerido no momento.")
                return
            
            print(f"\n🎯 Sugestões de ajuste ({len(suggestions)} encontradas):")
            print("-" * 90)
            print(f"{'Categoria':<15} {'Atual':<6} {'Sugerido':<8} {'Fator':<6} {'Confiança':<9} {'Motivo'}")
            print("-" * 90)
            
            for suggestion in suggestions[:10]:
                print(f"{suggestion.category:<15} {suggestion.current_score:<6.2f} "
                      f"{suggestion.suggested_score:<8.2f} {suggestion.adjustment_factor:<6.2f} "
                      f"{suggestion.confidence:<9.2f} {suggestion.reasoning[:30]}...")
            
            # Histórico de ajustes
            print(f"\n📜 Histórico de ajustes aplicados:")
            history = await self.score_adjuster.get_adjustment_history(days=30)
            
            if history:
                print("-" * 80)
                print(f"{'Categoria':<15} {'Antes':<6} {'Depois':<6} {'Data':<12} {'Motivo'}")
                print("-" * 80)
                
                for adj in history[:10]:
                    date_str = adj.applied_at.strftime("%d/%m %H:%M")
                    print(f"{adj.category:<15} {adj.old_score:<6.2f} {adj.new_score:<6.2f} "
                          f"{date_str:<12} {adj.reasoning[:25]}...")
            else:
                print("   Nenhum ajuste aplicado nos últimos 30 dias.")
            
        except Exception as e:
            self.logger.error(f"Erro ao mostrar ajustes: {e}")
            print(f"❌ Erro: {e}")
    
    async def _manage_adjustments(self) -> None:
        """Gerencia ajustes de score"""
        try:
            print("\n" + "="*60)
            print("🔧 GERENCIAR AJUSTES")
            print("="*60)
            
            print("1. 🔄 Aplicar ajustes automáticos")
            print("2. ⚖️  Aplicar ajuste específico")
            print("3. ↩️  Fazer rollback")
            print("4. ⚙️  Configurar ajustes")
            print("0. 🔙 Voltar")
            
            choice = input("\nEscolha uma opção: ").strip()
            
            if choice == "1":
                await self._apply_automatic_adjustments()
            elif choice == "2":
                await self._apply_specific_adjustment()
            elif choice == "3":
                await self._rollback_adjustment()
            elif choice == "4":
                await self._configure_adjustments()
            elif choice == "0":
                return
            else:
                print("❌ Opção inválida.")
                
        except Exception as e:
            self.logger.error(f"Erro ao gerenciar ajustes: {e}")
            print(f"❌ Erro: {e}")
    
    async def _show_insights(self) -> None:
        """Exibe insights e recomendações"""
        try:
            print("\n" + "="*60)
            print("💡 INSIGHTS E RECOMENDAÇÕES")
            print("="*60)
            
            days = input("Período em dias (padrão: 30): ").strip()
            days = int(days) if days.isdigit() else 30
            
            insights = await self.feedback_analyzer.generate_feedback_insights(days)
            
            if not insights:
                print("❌ Nenhum insight disponível no momento.")
                return
            
            print(f"\n🎯 Insights gerados ({len(insights)} encontrados):")
            
            for i, insight in enumerate(insights, 1):
                print(f"\n{i}. {insight.title}")
                print(f"   📝 {insight.description}")
                print(f"   🎯 Confiança: {insight.confidence:.2f}")
                print(f"   💡 Recomendações:")
                for rec in insight.recommendations:
                    print(f"      • {rec}")
                print("-" * 50)
            
        except Exception as e:
            self.logger.error(f"Erro ao mostrar insights: {e}")
            print(f"❌ Erro: {e}")
    
    async def _simulate_feedback(self) -> None:
        """Simula feedback para teste"""
        try:
            print("\n" + "="*60)
            print("🧪 SIMULAR FEEDBACK")
            print("="*60)
            
            print("Tipos de feedback disponíveis:")
            print("1. Clique em oferta")
            print("2. Avaliação (1-5)")
            print("3. Like/Dislike")
            print("4. Compra")
            print("5. Preferência de categoria")
            
            choice = input("\nEscolha o tipo de feedback: ").strip()
            
            # Criar oferta de teste
            test_offer = Offer(
                title="Produto de Teste",
                price=Decimal("99.99"),
                url="https://exemplo.com/produto",
                store="Loja Teste",
                category="test",
                scraped_at=datetime.now()
            )
            
            user_id = input("ID do usuário (padrão: test_user): ").strip() or "test_user"
            
            if choice == "1":
                await self.feedback_collector.collect_click_feedback(user_id, test_offer)
                print("✅ Clique simulado com sucesso!")
                
            elif choice == "2":
                rating = input("Avaliação (1-5): ").strip()
                if rating.isdigit() and 1 <= int(rating) <= 5:
                    await self.feedback_collector.collect_rating_feedback(user_id, test_offer, int(rating))
                    print(f"✅ Avaliação {rating} simulada com sucesso!")
                else:
                    print("❌ Avaliação inválida.")
                    
            elif choice == "3":
                like_dislike = input("Like (l) ou Dislike (d): ").strip().lower()
                if like_dislike == "l":
                    await self.feedback_collector.collect_feedback(
                        user_id, test_offer, FeedbackType.LIKE, 1
                    )
                    print("✅ Like simulado com sucesso!")
                elif like_dislike == "d":
                    await self.feedback_collector.collect_feedback(
                        user_id, test_offer, FeedbackType.DISLIKE, 1
                    )
                    print("✅ Dislike simulado com sucesso!")
                else:
                    print("❌ Opção inválida.")
                    
            elif choice == "4":
                value = input("Valor da compra: ").strip()
                try:
                    from decimal import Decimal
                    purchase_value = Decimal(value)
                    await self.feedback_collector.collect_purchase_feedback(user_id, test_offer, purchase_value)
                    print(f"✅ Compra de R$ {value} simulada com sucesso!")
                except:
                    print("❌ Valor inválido.")
                    
            elif choice == "5":
                category = input("Categoria: ").strip()
                score = input("Score de preferência (0-1): ").strip()
                try:
                    preference_score = float(score)
                    if 0 <= preference_score <= 1:
                        await self.feedback_collector.collect_category_preference(user_id, category, preference_score)
                        print(f"✅ Preferência por {category} simulada com sucesso!")
                    else:
                        print("❌ Score deve estar entre 0 e 1.")
                except:
                    print("❌ Score inválido.")
            else:
                print("❌ Opção inválida.")
                
        except Exception as e:
            self.logger.error(f"Erro ao simular feedback: {e}")
            print(f"❌ Erro: {e}")
    
    async def _apply_automatic_adjustments(self) -> None:
        """Aplica ajustes automáticos"""
        try:
            print("\n🔄 Aplicando ajustes automáticos...")
            
            applied = await self.score_adjuster.apply_automatic_adjustments()
            
            if applied:
                print(f"✅ {len(applied)} ajustes aplicados automaticamente!")
                for adj in applied:
                    print(f"   • {adj.category}: {adj.current_score:.2f} → {adj.suggested_score:.2f}")
            else:
                print("ℹ️  Nenhum ajuste foi aplicado automaticamente.")
                
        except Exception as e:
            self.logger.error(f"Erro ao aplicar ajustes automáticos: {e}")
            print(f"❌ Erro: {e}")
    
    async def _apply_specific_adjustment(self) -> None:
        """Aplica ajuste específico"""
        try:
            suggestions = await self.score_adjuster.analyze_and_suggest_adjustments()
            
            if not suggestions:
                print("❌ Nenhuma sugestão de ajuste disponível.")
                return
            
            print("\n🎯 Sugestões disponíveis:")
            for i, suggestion in enumerate(suggestions[:10], 1):
                print(f"{i}. {suggestion.category}: {suggestion.current_score:.2f} → {suggestion.suggested_score:.2f}")
            
            choice = input("\nEscolha o ajuste (número): ").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(suggestions):
                suggestion = suggestions[int(choice) - 1]
                
                confirm = input(f"Confirmar ajuste para {suggestion.category}? (s/n): ").strip().lower()
                if confirm == "s":
                    success = await self.score_adjuster.apply_score_adjustment(suggestion)
                    if success:
                        print("✅ Ajuste aplicado com sucesso!")
                    else:
                        print("❌ Falha ao aplicar ajuste.")
                else:
                    print("❌ Ajuste cancelado.")
            else:
                print("❌ Opção inválida.")
                
        except Exception as e:
            self.logger.error(f"Erro ao aplicar ajuste específico: {e}")
            print(f"❌ Erro: {e}")
    
    async def _rollback_adjustment(self) -> None:
        """Faz rollback de ajuste"""
        try:
            category = input("Categoria para rollback: ").strip()
            
            if not category:
                print("❌ Categoria é obrigatória.")
                return
            
            confirm = input(f"Confirmar rollback para {category}? (s/n): ").strip().lower()
            if confirm == "s":
                success = await self.score_adjuster.rollback_last_adjustment(category)
                if success:
                    print("✅ Rollback aplicado com sucesso!")
                else:
                    print("❌ Falha ao aplicar rollback.")
            else:
                print("❌ Rollback cancelado.")
                
        except Exception as e:
            self.logger.error(f"Erro ao fazer rollback: {e}")
            print(f"❌ Erro: {e}")
    
    async def _configure_adjustments(self) -> None:
        """Configura ajustes"""
        try:
            print("\n⚙️  Configurações atuais:")
            config = self.score_adjuster.config
            print(f"   • Confiança mínima: {config.min_confidence}")
            print(f"   • Fator máximo de ajuste: {config.max_adjustment_factor}")
            print(f"   • Amostra mínima: {config.min_feedback_sample}")
            print(f"   • Aplicação automática: {'Sim' if config.auto_apply else 'Não'}")
            print(f"   • Cooldown (dias): {config.adjustment_cooldown_days}")
            
            print("\n1. Alterar confiança mínima")
            print("2. Alterar fator máximo")
            print("3. Alterar amostra mínima")
            print("4. Ativar/desativar aplicação automática")
            print("5. Alterar cooldown")
            print("0. Voltar")
            
            choice = input("\nEscolha uma opção: ").strip()
            
            if choice == "1":
                value = input("Nova confiança mínima (0-1): ").strip()
                try:
                    config.min_confidence = float(value)
                    print("✅ Confiança mínima atualizada!")
                except:
                    print("❌ Valor inválido.")
                    
            elif choice == "2":
                value = input("Novo fator máximo: ").strip()
                try:
                    config.max_adjustment_factor = float(value)
                    print("✅ Fator máximo atualizado!")
                except:
                    print("❌ Valor inválido.")
                    
            elif choice == "3":
                value = input("Nova amostra mínima: ").strip()
                try:
                    config.min_feedback_sample = int(value)
                    print("✅ Amostra mínima atualizada!")
                except:
                    print("❌ Valor inválido.")
                    
            elif choice == "4":
                config.auto_apply = not config.auto_apply
                status = "ativada" if config.auto_apply else "desativada"
                print(f"✅ Aplicação automática {status}!")
                
            elif choice == "5":
                value = input("Novo cooldown (dias): ").strip()
                try:
                    config.adjustment_cooldown_days = int(value)
                    print("✅ Cooldown atualizado!")
                except:
                    print("❌ Valor inválido.")
                    
            elif choice == "0":
                return
            else:
                print("❌ Opção inválida.")
                
        except Exception as e:
            self.logger.error(f"Erro ao configurar ajustes: {e}")
            print(f"❌ Erro: {e}")
    
    async def get_dashboard_stats(self) -> DashboardStats:
        """Obtém estatísticas do dashboard"""
        try:
            # Estatísticas de feedback
            feedback_summary = await self.feedback_collector.get_feedback_summary(days=7)
            
            # Performance das categorias
            performances = await self.feedback_analyzer.analyze_category_performance(days=7)
            top_categories = [p.to_dict() for p in performances[:5]]
            
            # Ajustes recentes
            adjustment_history = await self.score_adjuster.get_adjustment_history(days=7)
            recent_adjustments = [adj.to_dict() for adj in adjustment_history[:5]]
            
            # Verificar saúde do sistema
            system_health = "✅ Saudável"
            if not feedback_summary.get('total_feedback', 0):
                system_health = "⚠️  Sem feedback"
            elif feedback_summary.get('total_feedback', 0) < 10:
                system_health = "⚠️  Pouco feedback"
            
            return DashboardStats(
                total_feedback=feedback_summary.get('total_feedback', 0),
                unique_users=feedback_summary.get('unique_users', 0),
                feedback_by_type=feedback_summary.get('feedback_by_type', {}),
                top_categories=top_categories,
                recent_adjustments=recent_adjustments,
                system_health=system_health
            )
            
        except Exception as e:
            self.logger.error(f"Erro ao obter estatísticas: {e}")
            return DashboardStats(
                total_feedback=0,
                unique_users=0,
                feedback_by_type={},
                top_categories=[],
                recent_adjustments=[],
                system_health="❌ Erro"
            )
