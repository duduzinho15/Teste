"""
Dashboard de Otimização de IA
Interface para monitorar e controlar o sistema de IA para otimização
"""

import asyncio
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging
from pathlib import Path
from decimal import Decimal

from src.core.models import Offer
from .ai_optimizer import AIOptimizer, ModelConfig
from .data_collector import DataCollector


class OptimizationDashboard:
    """Dashboard de otimização de IA"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.ai_optimizer = AIOptimizer()
        self.data_collector = DataCollector()
        
    async def start_dashboard(self):
        """Inicia o dashboard interativo"""
        try:
            print("🤖 DASHBOARD DE OTIMIZAÇÃO DE IA - GARIMPEIRO GEEK")
            print("=" * 60)
            
            while True:
                await self._show_main_menu()
                choice = input("\nEscolha uma opção: ").strip()
                
                if choice == "1":
                    await self._show_system_status()
                elif choice == "2":
                    await self._optimize_single_offer()
                elif choice == "3":
                    await self._optimize_batch_offers()
                elif choice == "4":
                    await self._show_optimization_history()
                elif choice == "5":
                    await self._show_model_performance()
                elif choice == "6":
                    await self._retrain_models()
                elif choice == "7":
                    await self._show_configuration()
                elif choice == "8":
                    await self._show_data_statistics()
                elif choice == "9":
                    await self._compare_models()
                elif choice == "0":
                    print("👋 Saindo do dashboard...")
                    break
                else:
                    print("❌ Opção inválida!")
                
                input("\nPressione ENTER para continuar...")
                os.system('cls' if os.name == 'nt' else 'clear')
                
        except KeyboardInterrupt:
            print("\n👋 Dashboard interrompido pelo usuário")
        except Exception as e:
            self.logger.error(f"Erro no dashboard: {e}")
            print(f"❌ Erro: {e}")
    
    async def _show_main_menu(self):
        """Mostra menu principal"""
        print("\n📋 MENU PRINCIPAL")
        print("1. 📊 Status do Sistema")
        print("2. 🎯 Otimizar Oferta Única")
        print("3. 📦 Otimizar Lote de Ofertas")
        print("4. 📈 Histórico de Otimizações")
        print("5. 🏆 Performance dos Modelos")
        print("6. 🔄 Retreinar Modelos")
        print("7. ⚙️  Configurações")
        print("8. 📊 Estatísticas dos Dados")
        print("9. 🔍 Comparar Modelos")
        print("0. 🚪 Sair")
    
    async def _show_system_status(self):
        """Mostra status do sistema"""
        try:
            print("\n📊 STATUS DO SISTEMA DE IA")
            print("-" * 40)
            
            status = await self.ai_optimizer.get_system_status()
            
            print(f"✅ Inicializado: {'Sim' if status.get('is_initialized') else 'Não'}")
            print(f"🤖 Modelo Atual: {status.get('current_model', 'Nenhum')}")
            print(f"🕒 Último Treinamento: {status.get('last_training', 'Nunca')}")
            print(f"📈 Total de Otimizações: {status.get('total_optimizations', 0)}")
            print(f"🔄 Última Atualização: {status.get('last_updated', 'N/A')}")
            
            if 'config' in status:
                config = status['config']
                print(f"\n⚙️  CONFIGURAÇÕES:")
                print(f"   Auto-retreinamento: {'Sim' if config.get('auto_retrain') else 'Não'}")
                print(f"   Intervalo de retreinamento: {config.get('retrain_interval_days')} dias")
                print(f"   Mínimo de dados: {config.get('min_data_points')} registros")
                print(f"   Limite de confiança: {config.get('confidence_threshold')}")
                print(f"   Tamanho do lote: {config.get('batch_size')}")
            
        except Exception as e:
            print(f"❌ Erro ao obter status: {e}")
    
    async def _optimize_single_offer(self):
        """Otimiza uma oferta única"""
        try:
            print("\n🎯 OTIMIZAR OFERTA ÚNICA")
            print("-" * 40)
            
            # Criar oferta de exemplo
            offer = Offer(
                title="Action Figure Dragon Ball Z Goku",
                price=Decimal("89.90"),
                category="Action Figures",
                url="https://exemplo.com/goku-action-figure",
                store="Amazon",
                store_data={"rating": 4.5, "reviews": 1200},
                scraped_at=datetime.now()
            )
            
            print(f"📦 Oferta: {offer.title}")
            print(f"💰 Preço: R$ {offer.price}")
            print(f"🏷️  Categoria: {offer.category}")
            print(f"🏪 Loja: {offer.store}")
            
            # Dados de conversão simulados
            conversion_data = {
                'conversion_rate': 0.12,
                'click_rate': 0.08,
                'engagement_rate': 0.15
            }
            
            print("\n🔄 Otimizando...")
            prediction = await self.ai_optimizer.optimize_offer(offer, conversion_data)
            
            print(f"\n✅ RESULTADO DA OTIMIZAÇÃO:")
            print(f"   Score Original: {prediction.original_score:.4f}")
            print(f"   Score Otimizado: {prediction.predicted_score:.4f}")
            print(f"   Melhoria: {prediction.predicted_score - prediction.original_score:+.4f}")
            print(f"   Confiança: {prediction.confidence.confidence:.2%}")
            print(f"   Modelo: {prediction.model_used}")
            
            # Insights
            insights = await self.ai_optimizer.get_optimization_insights(prediction)
            if insights:
                print(f"\n💡 INSIGHTS:")
                print(f"   Recomendação: {insights.get('recommendation', 'N/A')}")
                print(f"   Nível de Confiança: {insights.get('confidence_level', 'N/A')}")
                
                key_factors = insights.get('key_factors', [])
                if key_factors:
                    print(f"   Fatores-chave: {', '.join(key_factors[:3])}")
            
        except Exception as e:
            print(f"❌ Erro ao otimizar oferta: {e}")
    
    async def _optimize_batch_offers(self):
        """Otimiza lote de ofertas"""
        try:
            print("\n📦 OTIMIZAR LOTE DE OFERTAS")
            print("-" * 40)
            
            # Criar ofertas de exemplo
            offers = [
                Offer(
                    title="Manga One Piece Vol. 1",
                    price=Decimal("29.90"),
                    category="Manga",
                    url="https://exemplo.com/one-piece-vol1",
                    store="Magalu",
                    store_data={"rating": 4.8, "reviews": 850},
                    scraped_at=datetime.now()
                ),
                Offer(
                    title="Video Game PS5 God of War",
                    price=Decimal("299.90"),
                    category="Video Games",
                    url="https://exemplo.com/god-of-war-ps5",
                    store="Americanas",
                    store_data={"rating": 4.9, "reviews": 2100},
                    scraped_at=datetime.now()
                ),
                Offer(
                    title="Cosplay Naruto Completo",
                    price=Decimal("159.90"),
                    category="Cosplay",
                    url="https://exemplo.com/cosplay-naruto",
                    store="Submarino",
                    store_data={"rating": 4.2, "reviews": 320},
                    scraped_at=datetime.now()
                )
            ]
            
            print(f"📦 Otimizando {len(offers)} ofertas...")
            
            # Dados de conversão simulados
            conversion_data = {
                'conversion_rate': 0.15,
                'click_rate': 0.10,
                'engagement_rate': 0.18
            }
            
            results = await self.ai_optimizer.optimize_batch(offers, conversion_data)
            
            print(f"\n✅ RESULTADOS DA OTIMIZAÇÃO:")
            print(f"   Total processado: {len(results)} ofertas")
            
            total_improvement = 0
            high_confidence = 0
            
            for i, result in enumerate(results, 1):
                improvement = result.predicted_score - result.original_score
                total_improvement += improvement
                
                if result.confidence.confidence > 0.8:
                    high_confidence += 1
                
                print(f"\n   {i}. {result.offer_id[:30]}...")
                print(f"      Original: {result.original_score:.4f} → Otimizado: {result.predicted_score:.4f}")
                print(f"      Melhoria: {improvement:+.4f} | Confiança: {result.confidence.confidence:.2%}")
            
            print(f"\n📊 RESUMO:")
            print(f"   Melhoria média: {total_improvement/len(results):+.4f}")
            print(f"   Alta confiança: {high_confidence}/{len(results)} ({high_confidence/len(results):.1%})")
            
        except Exception as e:
            print(f"❌ Erro ao otimizar lote: {e}")
    
    async def _show_optimization_history(self):
        """Mostra histórico de otimizações"""
        try:
            print("\n📈 HISTÓRICO DE OTIMIZAÇÕES")
            print("-" * 40)
            
            history = await self.ai_optimizer.get_optimization_history(limit=10)
            
            if not history:
                print("📭 Nenhuma otimização encontrada")
                return
            
            print(f"📊 Últimas {len(history)} otimizações:")
            
            for i, record in enumerate(history, 1):
                improvement = record['optimized_score'] - record['original_score']
                print(f"\n   {i}. {record['offer_id'][:30]}...")
                print(f"      {record['original_score']:.4f} → {record['optimized_score']:.4f} ({improvement:+.4f})")
                print(f"      Confiança: {record['confidence']:.2%} | Modelo: {record['model_used']}")
                print(f"      Data: {record['optimization_date']}")
            
        except Exception as e:
            print(f"❌ Erro ao obter histórico: {e}")
    
    async def _show_model_performance(self):
        """Mostra performance dos modelos"""
        try:
            print("\n🏆 PERFORMANCE DOS MODELOS")
            print("-" * 40)
            
            model_names = ['random_forest', 'gradient_boosting', 'linear_regression']
            
            for model_name in model_names:
                print(f"\n🤖 Modelo: {model_name.upper()}")
                
                metrics = await self.ai_optimizer.model_trainer.get_model_metrics(model_name)
                if metrics:
                    latest = metrics[0]
                    print(f"   R² Score: {latest.r2_score:.4f}")
                    print(f"   MSE: {latest.mse:.4f}")
                    print(f"   MAE: {latest.mae:.4f}")
                    print(f"   Cross-Val Score: {latest.cross_val_score:.4f}")
                    print(f"   Tempo de Treinamento: {latest.training_time:.2f}s")
                    
                    # Feature importance
                    importance = await self.ai_optimizer.model_trainer.get_feature_importance(model_name)
                    if importance:
                        top_features = sorted(importance.items(), key=lambda x: x[1], reverse=True)[:3]
                        print(f"   Top Features: {', '.join([f'{f}:{i:.3f}' for f, i in top_features])}")
                else:
                    print("   ❌ Nenhuma métrica disponível")
            
        except Exception as e:
            print(f"❌ Erro ao obter performance: {e}")
    
    async def _retrain_models(self):
        """Retreina modelos"""
        try:
            print("\n🔄 RETREINAMENTO DE MODELOS")
            print("-" * 40)
            
            print("🔄 Iniciando retreinamento...")
            
            # Verificar dados
            training_data = await self.data_collector.load_training_data()
            print(f"📊 Dados disponíveis: {len(training_data.features)} registros")
            
            if len(training_data.features) < 100:
                print("⚠️  Poucos dados para treinamento. Coletando mais dados...")
                await self.ai_optimizer._collect_initial_data()
                training_data = await self.data_collector.load_training_data()
                print(f"📊 Dados atualizados: {len(training_data.features)} registros")
            
            # Treinar modelos
            results = await self.ai_optimizer.model_trainer.train_all_models(training_data)
            
            if results:
                print(f"✅ {len(results)} modelos treinados com sucesso!")
                
                for result in results:
                    print(f"\n   🤖 {result.model_name.upper()}:")
                    print(f"      R² Score: {result.metrics.r2_score:.4f}")
                    print(f"      MSE: {result.metrics.mse:.4f}")
                    print(f"      Tempo: {result.metrics.training_time:.2f}s")
                
                # Atualizar sistema
                await self.ai_optimizer.prediction_engine.load_best_model()
                print(f"\n✅ Melhor modelo carregado: {self.ai_optimizer.prediction_engine.current_model_name}")
            else:
                print("❌ Erro no treinamento dos modelos")
            
        except Exception as e:
            print(f"❌ Erro no retreinamento: {e}")
    
    async def _show_configuration(self):
        """Mostra e permite editar configurações"""
        try:
            print("\n⚙️  CONFIGURAÇÕES DO SISTEMA")
            print("-" * 40)
            
            config = self.ai_optimizer.config
            print(f"🔄 Auto-retreinamento: {'Sim' if config.auto_retrain else 'Não'}")
            print(f"📅 Intervalo de retreinamento: {config.retrain_interval_days} dias")
            print(f"📊 Mínimo de dados: {config.min_data_points} registros")
            print(f"🎯 Limite de confiança: {config.confidence_threshold}")
            print(f"📦 Tamanho do lote: {config.batch_size}")
            
            print("\n💡 Para alterar configurações, edite o código do dashboard")
            
        except Exception as e:
            print(f"❌ Erro ao obter configurações: {e}")
    
    async def _show_data_statistics(self):
        """Mostra estatísticas dos dados"""
        try:
            print("\n📊 ESTATÍSTICAS DOS DADOS")
            print("-" * 40)
            
            stats = await self.data_collector.get_feature_statistics()
            
            if stats:
                print(f"📈 Total de registros: {stats.get('total_records', 0)}")
                print(f"🎯 Score geek médio: {stats.get('avg_geek_score', 0):.4f}")
                print(f"🔄 Taxa de conversão média: {stats.get('avg_conversion_rate', 0):.2%}")
                print(f"👆 Taxa de clique média: {stats.get('avg_click_rate', 0):.2%}")
                print(f"💬 Taxa de engajamento média: {stats.get('avg_engagement_rate', 0):.2%}")
                print(f"💰 Preço médio: R$ {stats.get('avg_price', 0):.2f}")
            else:
                print("📭 Nenhuma estatística disponível")
            
        except Exception as e:
            print(f"❌ Erro ao obter estatísticas: {e}")
    
    async def _compare_models(self):
        """Compara diferentes modelos"""
        try:
            print("\n🔍 COMPARAÇÃO DE MODELOS")
            print("-" * 40)
            
            # Criar feature set de exemplo
            from .data_collector import FeatureSet
            feature_set = FeatureSet(
                offer_id="test_comparison",
                title="Produto de Teste",
                category="Video Games",
                price=150.0,
                store="Amazon",
                geek_score=0.85,
                conversion_rate=0.15,
                click_rate=0.10,
                engagement_rate=0.18,
                time_of_day=14,
                day_of_week=2,
                season="Verão",
                price_range="Médio",
                category_popularity=0.8,
                store_reputation=0.9,
                title_length=25,
                has_discount=True,
                discount_percentage=15.0,
                created_at=datetime.now()
            )
            
            print("🔄 Comparando predições dos modelos...")
            
            predictions = await self.ai_optimizer.prediction_engine.compare_models(feature_set)
            
            if predictions:
                print(f"\n📊 PREDIÇÕES PARA: {feature_set.title}")
                print(f"   Score Original: {feature_set.geek_score:.4f}")
                
                for model_name, predicted_score in predictions.items():
                    improvement = predicted_score - feature_set.geek_score
                    print(f"\n   🤖 {model_name.upper()}:")
                    print(f"      Predição: {predicted_score:.4f}")
                    print(f"      Diferença: {improvement:+.4f}")
            else:
                print("❌ Erro na comparação dos modelos")
            
        except Exception as e:
            print(f"❌ Erro na comparação: {e}")
    
    async def quick_test(self):
        """Teste rápido do sistema"""
        try:
            print("🚀 TESTE RÁPIDO DO SISTEMA DE IA")
            print("=" * 50)
            
            # Inicializar sistema
            print("🔄 Inicializando sistema...")
            success = await self.ai_optimizer.initialize()
            
            if not success:
                print("❌ Falha na inicialização")
                return
            
            print("✅ Sistema inicializado!")
            
            # Status
            status = await self.ai_optimizer.get_system_status()
            print(f"🤖 Modelo ativo: {status.get('current_model', 'Nenhum')}")
            print(f"📈 Otimizações: {status.get('total_optimizations', 0)}")
            
            # Teste de otimização
            print("\n🎯 Testando otimização...")
            offer = Offer(
                title="Teste IA - Action Figure",
                price=Decimal("99.90"),
                category="Action Figures",
                url="https://teste.com/action-figure",
                store="Teste Store",
                store_data={},
                scraped_at=datetime.now()
            )
            
            prediction = await self.ai_optimizer.optimize_offer(offer)
            print(f"✅ Score original: {prediction.original_score:.4f}")
            print(f"✅ Score otimizado: {prediction.predicted_score:.4f}")
            print(f"✅ Confiança: {prediction.confidence.confidence:.2%}")
            
            print("\n🎉 TESTE CONCLUÍDO COM SUCESSO!")
            
        except Exception as e:
            print(f"❌ Erro no teste: {e}")


async def main():
    """Função principal para executar o dashboard"""
    dashboard = OptimizationDashboard()
    
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "quick":
        await dashboard.quick_test()
    else:
        await dashboard.start_dashboard()


if __name__ == "__main__":
    asyncio.run(main())
