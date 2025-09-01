"""
Dashboard Interativo para Sistema de Deep Learning
=================================================

Interface console para gerenciar e visualizar o sistema de deep learning
com redes neurais avançadas para otimização de priorização geek.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from src.core.deep_learning import DeepLearningManager, PredictionResult, ModelPerformance

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DeepLearningDashboard:
    """Dashboard interativo para sistema de Deep Learning"""
    
    def __init__(self):
        self.manager = DeepLearningManager()
        self.is_running = True
    
    async def run(self):
        """Executa o dashboard principal"""
        print("🤖 DASHBOARD DE DEEP LEARNING - GARIMPEIRO GEEK")
        print("=" * 60)
        print("Sistema de Redes Neurais Avançadas para Otimização de Priorização")
        print("=" * 60)
        
        while self.is_running:
            await self._show_main_menu()
            choice = input("\n🎯 Escolha uma opção: ").strip()
            await self._handle_main_choice(choice)
    
    async def _show_main_menu(self):
        """Exibe menu principal"""
        print("\n📋 MENU PRINCIPAL")
        print("-" * 40)
        print("1. 🚀 Treinar Modelos de Deep Learning")
        print("2. 🔮 Fazer Predições")
        print("3. 📊 Visualizar Performance dos Modelos")
        print("4. 📈 Histórico de Treinamento")
        print("5. 💡 Gerar Insights")
        print("6. 🎯 Teste Rápido de Produtos")
        print("7. 🔧 Configurações Avançadas")
        print("8. 📋 Relatório Completo")
        print("0. ❌ Sair")
    
    async def _handle_main_choice(self, choice: str):
        """Processa escolha do menu principal"""
        if choice == "1":
            await self._train_models()
        elif choice == "2":
            await self._make_predictions()
        elif choice == "3":
            await self._view_model_performance()
        elif choice == "4":
            await self._view_training_history()
        elif choice == "5":
            await self._generate_insights()
        elif choice == "6":
            await self._quick_product_test()
        elif choice == "7":
            await self._advanced_settings()
        elif choice == "8":
            await self._generate_complete_report()
        elif choice == "0":
            self.is_running = False
            print("\n👋 Saindo do Dashboard de Deep Learning...")
        else:
            print("\n❌ Opção inválida. Tente novamente.")
    
    async def _train_models(self):
        """Treina todos os modelos de deep learning"""
        print("\n🚀 TREINAMENTO DE MODELOS DE DEEP LEARNING")
        print("-" * 50)
        
        if self.manager.is_trained:
            print("⚠️  Modelos já foram treinados!")
            retrain = input("Deseja treinar novamente? (s/n): ").strip().lower()
            if retrain != 's':
                return
        
        print("🔄 Iniciando treinamento...")
        print("📊 Coletando dados...")
        print("🤖 Treinando redes neurais...")
        
        try:
            result = await self.manager.train_all_models()
            
            print("\n✅ TREINAMENTO CONCLUÍDO!")
            print("-" * 30)
            print(f"📊 Modelos treinados: {result['models_trained']}")
            print(f"⏱️  Tempo total: {result['training_time']:.2f} segundos")
            print(f"📈 Status: {result['status']}")
            
            # Mostrar performance
            if 'performance' in result:
                print("\n📊 PERFORMANCE DOS MODELOS:")
                for model_name, perf in result['performance'].items():
                    print(f"  {model_name.upper()}:")
                    print(f"    📈 Acurácia: {perf.accuracy:.3f}")
                    print(f"    🎯 Precisão: {perf.precision:.3f}")
                    print(f"    🔄 Recall: {perf.recall:.3f}")
                    print(f"    ⚡ F1-Score: {perf.f1_score:.3f}")
                    print(f"    📉 MSE: {perf.mse:.4f}")
                    print(f"    📊 R²: {perf.r2_score:.3f}")
                    print(f"    ⏱️  Tempo de inferência: {perf.inference_time:.4f}s")
            
        except Exception as e:
            print(f"\n❌ Erro durante treinamento: {e}")
            logger.error(f"Erro no treinamento: {e}")
    
    async def _make_predictions(self):
        """Faz predições de produtos"""
        print("\n🔮 PREDIÇÕES DE PRODUTOS")
        print("-" * 30)
        
        if not self.manager.is_trained:
            print("❌ Modelos não treinados. Treine os modelos primeiro.")
            return
        
        while True:
            print("\nEscolha uma opção:")
            print("1. 🎯 Predição Individual")
            print("2. 📦 Predição em Lote")
            print("3. 🎲 Produto Simulado")
            print("0. ⬅️  Voltar")
            
            choice = input("\nEscolha: ").strip()
            
            if choice == "1":
                await self._individual_prediction()
            elif choice == "2":
                await self._batch_prediction()
            elif choice == "3":
                await self._simulated_prediction()
            elif choice == "0":
                break
            else:
                print("❌ Opção inválida.")
    
    async def _individual_prediction(self):
        """Faz predição individual"""
        print("\n🎯 PREDIÇÃO INDIVIDUAL")
        print("-" * 25)
        
        # Coletar dados do produto
        product_data = {}
        
        print("📝 Insira os dados do produto:")
        product_data['product_id'] = input("ID do Produto: ").strip()
        product_data['category'] = input("Categoria (gaming/anime/tech/collectibles): ").strip()
        product_data['price'] = float(input("Preço (R$): ").strip() or "100.0")
        product_data['rating'] = float(input("Avaliação (1-5): ").strip() or "4.0")
        product_data['popularity'] = float(input("Popularidade (0-1): ").strip() or "0.7")
        product_data['availability'] = float(input("Disponibilidade (0-1): ").strip() or "0.8")
        
        # Adicionar features numéricas
        for i in range(44):  # Completar 50 features
            product_data[f'feature_{i}'] = float(np.random.random())
        
        try:
            result = await self.manager.predict_product_priority(product_data)
            
            print("\n🎯 RESULTADO DA PREDIÇÃO:")
            print("-" * 30)
            print(f"🆔 Produto: {result.product_id}")
            print(f"📊 Score: {result.predicted_score:.3f}")
            print(f"🎯 Confiança: {result.confidence:.3f}")
            print(f"💡 Recomendação: {result.recommendation}")
            print(f"⏰ Timestamp: {result.timestamp.strftime('%d/%m/%Y %H:%M:%S')}")
            
            # Mostrar features mais importantes
            if result.features_importance:
                print("\n🔍 FEATURES MAIS IMPORTANTES:")
                top_features = sorted(result.features_importance.items(), 
                                    key=lambda x: x[1], reverse=True)[:5]
                for feature, importance in top_features:
                    print(f"  {feature}: {importance:.3f}")
        
        except Exception as e:
            print(f"\n❌ Erro na predição: {e}")
    
    async def _batch_prediction(self):
        """Faz predições em lote"""
        print("\n📦 PREDIÇÕES EM LOTE")
        print("-" * 25)
        
        try:
            # Simular produtos em lote
            products = []
            for i in range(5):
                product = {
                    'product_id': f'PROD_{i+1:03d}',
                    'category': ['gaming', 'anime', 'tech', 'collectibles'][i % 4],
                    'price': 50 + i * 25,
                    'rating': 3.5 + (i * 0.3),
                    'popularity': 0.5 + (i * 0.1),
                    'availability': 0.7 + (i * 0.05)
                }
                
                # Adicionar features
                for j in range(44):
                    product[f'feature_{j}'] = float(np.random.random())
                
                products.append(product)
            
            print(f"🔄 Processando {len(products)} produtos...")
            
            results = []
            for product in products:
                result = await self.manager.predict_product_priority(product)
                results.append(result)
            
            print("\n📊 RESULTADOS EM LOTE:")
            print("-" * 30)
            
            for result in results:
                print(f"🆔 {result.product_id}: Score {result.predicted_score:.3f} "
                      f"| Confiança {result.confidence:.3f} | {result.recommendation}")
            
            # Estatísticas
            scores = [r.predicted_score for r in results]
            confidences = [r.confidence for r in results]
            
            print(f"\n📈 ESTATÍSTICAS:")
            print(f"  📊 Score médio: {np.mean(scores):.3f}")
            print(f"  📊 Score máximo: {np.max(scores):.3f}")
            print(f"  📊 Score mínimo: {np.min(scores):.3f}")
            print(f"  🎯 Confiança média: {np.mean(confidences):.3f}")
        
        except Exception as e:
            print(f"\n❌ Erro nas predições em lote: {e}")
    
    async def _simulated_prediction(self):
        """Faz predição com produto simulado"""
        print("\n🎲 PRODUTO SIMULADO")
        print("-" * 20)
        
        # Simular produto geek
        product_data = {
            'product_id': 'GEEK_SIM_001',
            'category': 'gaming',
            'price': 299.99,
            'rating': 4.8,
            'popularity': 0.95,
            'availability': 0.9
        }
        
        # Adicionar features
        for i in range(44):
            product_data[f'feature_{i}'] = float(np.random.random())
        
        try:
            result = await self.manager.predict_product_priority(product_data)
            
            print(f"\n🎮 PRODUTO SIMULADO: {product_data['product_id']}")
            print(f"📊 Categoria: {product_data['category']}")
            print(f"💰 Preço: R$ {product_data['price']:.2f}")
            print(f"⭐ Avaliação: {product_data['rating']}/5")
            
            print(f"\n🎯 RESULTADO:")
            print(f"📊 Score: {result.predicted_score:.3f}")
            print(f"🎯 Confiança: {result.confidence:.3f}")
            print(f"💡 Recomendação: {result.recommendation}")
        
        except Exception as e:
            print(f"\n❌ Erro na predição simulada: {e}")
    
    async def _view_model_performance(self):
        """Visualiza performance dos modelos"""
        print("\n📊 PERFORMANCE DOS MODELOS")
        print("-" * 35)
        
        if not self.manager.is_trained:
            print("❌ Modelos não treinados.")
            return
        
        try:
            performance = await self.manager.get_model_performance()
            
            if not performance:
                print("📊 Nenhuma métrica de performance disponível.")
                return
            
            for model_name, perf in performance.items():
                print(f"\n🤖 {model_name.upper()}:")
                print(f"  📈 Acurácia: {perf.accuracy:.3f}")
                print(f"  🎯 Precisão: {perf.precision:.3f}")
                print(f"  🔄 Recall: {perf.recall:.3f}")
                print(f"  ⚡ F1-Score: {perf.f1_score:.3f}")
                print(f"  📉 MSE: {perf.mse:.4f}")
                print(f"  📊 R²: {perf.r2_score:.3f}")
                print(f"  ⏱️  Tempo de inferência: {perf.inference_time:.4f}s")
                print(f"  📅 Última atualização: {perf.last_updated.strftime('%d/%m/%Y %H:%M')}")
        
        except Exception as e:
            print(f"\n❌ Erro ao obter performance: {e}")
    
    async def _view_training_history(self):
        """Visualiza histórico de treinamento"""
        print("\n📈 HISTÓRICO DE TREINAMENTO")
        print("-" * 35)
        
        if not self.manager.is_trained:
            print("❌ Modelos não treinados.")
            return
        
        try:
            history = await self.manager.get_training_history()
            
            if not history:
                print("📊 Nenhum histórico disponível.")
                return
            
            print(f"📊 Total de épocas: {len(history)}")
            
            # Mostrar últimas 10 épocas
            recent_history = history[-10:]
            
            print("\n📈 ÚLTIMAS 10 ÉPOCAS:")
            print("Época | Train Loss | Val Loss | LR")
            print("-" * 40)
            
            for metric in recent_history:
                print(f"{metric.epoch:5d} | {metric.train_loss:9.4f} | {metric.val_loss:8.4f} | {metric.learning_rate:.6f}")
            
            # Estatísticas
            train_losses = [m.train_loss for m in history]
            val_losses = [m.val_loss for m in history]
            
            print(f"\n📊 ESTATÍSTICAS:")
            print(f"  📉 Loss de treino final: {train_losses[-1]:.4f}")
            print(f"  📉 Loss de validação final: {val_losses[-1]:.4f}")
            print(f"  📈 Melhor loss de validação: {min(val_losses):.4f}")
            print(f"  📊 Época do melhor modelo: {val_losses.index(min(val_losses))}")
        
        except Exception as e:
            print(f"\n❌ Erro ao obter histórico: {e}")
    
    async def _generate_insights(self):
        """Gera insights sobre o sistema"""
        print("\n💡 INSIGHTS DO SISTEMA")
        print("-" * 25)
        
        if not self.manager.is_trained:
            print("❌ Modelos não treinados.")
            return
        
        try:
            insights = await self.manager.generate_insights()
            
            if 'error' in insights:
                print(f"❌ {insights['error']}")
                return
            
            print("🤖 STATUS DOS MODELOS:")
            for model, status in insights['models_status'].items():
                print(f"  {model}: {status}")
            
            print(f"\n📊 ESTATÍSTICAS GERAIS:")
            print(f"  🎯 Total de predições: {insights['total_predictions']}")
            print(f"  🎯 Confiança média: {insights['average_confidence']:.3f}")
            
            if insights['top_features']:
                print(f"\n🔍 TOP 5 FEATURES MAIS IMPORTANTES:")
                for feature, importance in insights['top_features'][:5]:
                    print(f"  {feature}: {importance:.3f}")
            
            if insights['recommendations']:
                print(f"\n💡 ÚLTIMAS RECOMENDAÇÕES:")
                for i, rec in enumerate(insights['recommendations'][-5:], 1):
                    print(f"  {i}. {rec}")
        
        except Exception as e:
            print(f"\n❌ Erro ao gerar insights: {e}")
    
    async def _quick_product_test(self):
        """Teste rápido de produtos"""
        print("\n🎯 TESTE RÁPIDO DE PRODUTOS")
        print("-" * 30)
        
        if not self.manager.is_trained:
            print("❌ Modelos não treinados.")
            return
        
        # Produtos de teste
        test_products = [
            {
                'name': '🎮 Console Gaming',
                'data': {'product_id': 'CONSOLE_001', 'category': 'gaming', 'price': 2500, 'rating': 4.9, 'popularity': 0.95, 'availability': 0.8}
            },
            {
                'name': '📱 Smartphone Gamer',
                'data': {'product_id': 'PHONE_001', 'category': 'tech', 'price': 1500, 'rating': 4.7, 'popularity': 0.88, 'availability': 0.9}
            },
            {
                'name': '🎨 Action Figure Anime',
                'data': {'product_id': 'FIGURE_001', 'category': 'anime', 'price': 150, 'rating': 4.5, 'popularity': 0.75, 'availability': 0.6}
            },
            {
                'name': '💻 Notebook Gamer',
                'data': {'product_id': 'NOTEBOOK_001', 'category': 'tech', 'price': 3500, 'rating': 4.8, 'popularity': 0.92, 'availability': 0.7}
            },
            {
                'name': '🎲 Board Game Geek',
                'data': {'product_id': 'BOARD_001', 'category': 'gaming', 'price': 200, 'rating': 4.6, 'popularity': 0.82, 'availability': 0.85}
            }
        ]
        
        print("🔄 Testando produtos geek...")
        
        results = []
        for product in test_products:
            # Adicionar features
            product_data = product['data'].copy()
            for i in range(44):
                product_data[f'feature_{i}'] = float(np.random.random())
            
            try:
                result = await self.manager.predict_product_priority(product_data)
                results.append((product['name'], result))
            except Exception as e:
                print(f"❌ Erro ao testar {product['name']}: {e}")
        
        print("\n📊 RESULTADOS DO TESTE:")
        print("-" * 30)
        
        for name, result in results:
            print(f"{name}:")
            print(f"  📊 Score: {result.predicted_score:.3f}")
            print(f"  🎯 Confiança: {result.confidence:.3f}")
            print(f"  💡 {result.recommendation}")
            print()
    
    async def _advanced_settings(self):
        """Configurações avançadas"""
        print("\n🔧 CONFIGURAÇÕES AVANÇADAS")
        print("-" * 30)
        
        print("⚙️  Configurações atuais:")
        config = self.manager.config
        print(f"  📊 Tamanho de entrada: {config.input_size}")
        print(f"  🧠 Camadas ocultas: {config.hidden_layers}")
        print(f"  📤 Tamanho de saída: {config.output_size}")
        print(f"  🎲 Dropout: {config.dropout_rate}")
        print(f"  📚 Learning rate: {config.learning_rate}")
        print(f"  📦 Batch size: {config.batch_size}")
        print(f"  🔄 Épocas: {config.epochs}")
        print(f"  🛑 Early stopping patience: {config.early_stopping_patience}")
        
        print("\n⚠️  Configurações avançadas em desenvolvimento...")
    
    async def _generate_complete_report(self):
        """Gera relatório completo"""
        print("\n📋 RELATÓRIO COMPLETO - DEEP LEARNING")
        print("=" * 50)
        
        print(f"📅 Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print(f"🤖 Status: {'✅ Treinado' if self.manager.is_trained else '❌ Não treinado'}")
        
        if self.manager.is_trained:
            try:
                # Performance dos modelos
                performance = await self.manager.get_model_performance()
                print(f"\n📊 MODELOS TREINADOS: {len(performance)}")
                
                for model_name, perf in performance.items():
                    print(f"\n🤖 {model_name.upper()}:")
                    print(f"  📈 Acurácia: {perf.accuracy:.3f}")
                    print(f"  🎯 Precisão: {perf.precision:.3f}")
                    print(f"  📊 R²: {perf.r2_score:.3f}")
                    print(f"  ⏱️  Tempo de inferência: {perf.inference_time:.4f}s")
                
                # Insights
                insights = await self.manager.generate_insights()
                print(f"\n💡 INSIGHTS:")
                print(f"  🎯 Total de predições: {insights['total_predictions']}")
                print(f"  🎯 Confiança média: {insights['average_confidence']:.3f}")
                
                # Histórico
                history = await self.manager.get_training_history()
                if history:
                    print(f"\n📈 HISTÓRICO:")
                    print(f"  🔄 Total de épocas: {len(history)}")
                    print(f"  📉 Loss final: {history[-1].train_loss:.4f}")
                
            except Exception as e:
                print(f"\n❌ Erro ao gerar relatório: {e}")
        else:
            print("\n📊 Nenhum modelo treinado para relatório.")
        
        print("\n" + "=" * 50)

# Import necessário para numpy
import numpy as np
