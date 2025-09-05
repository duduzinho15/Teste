#!/usr/bin/env python3
"""
Demonstração do Sistema de Deep Learning - Garimpeiro Geek
==========================================================

Script para demonstrar o sistema de redes neurais avançadas para otimização
de priorização de produtos geek.
"""

import asyncio
import sys
import logging
import numpy as np
from datetime import datetime
from pathlib import Path

# Adicionar o diretório raiz ao Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.deep_learning import DeepLearningManager
from src.core.deep_learning_dashboard import DeepLearningDashboard

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DeepLearningDemo:
    """Demonstração do sistema de Deep Learning"""
    
    def __init__(self):
        self.manager = DeepLearningManager()
        self.dashboard = DeepLearningDashboard()
    
    async def run_quick_demo(self):
        """Executa demonstração rápida"""
        print("⚡ INICIANDO DEMONSTRAÇÃO RÁPIDA DE DEEP LEARNING")
        print("=" * 60)
        
        try:
            # Treinar modelos rapidamente
            print("\n🚀 TREINANDO MODELOS...")
            result = await self.manager.train_all_models()
            
            print(f"\n✅ TREINAMENTO CONCLUÍDO!")
            print(f"📊 Modelos treinados: {result['models_trained']}")
            print(f"⏱️  Tempo: {result['training_time']:.2f}s")
            
            # Fazer algumas predições de teste
            print("\n🔮 FAZENDO PREDIÇÕES DE TESTE...")
            
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
                }
            ]
            
            for product in test_products:
                # Adicionar features
                product_data = product['data'].copy()
                for i in range(44):
                    product_data[f'feature_{i}'] = float(np.random.random())
                
                result = await self.manager.predict_product_priority(product_data)
                print(f"  {product['name']}: Score {result.predicted_score:.3f} | {result.recommendation}")
            
            # Gerar insights
            print("\n💡 GERANDO INSIGHTS...")
            insights = await self.manager.generate_insights()
            
            print(f"📊 Total de predições: {insights['total_predictions']}")
            print(f"🎯 Confiança média: {insights['average_confidence']:.3f}")
            
            print("\n✅ DEMONSTRAÇÃO RÁPIDA FINALIZADA!")
            print("=" * 60)
            
        except Exception as e:
            print(f"\n❌ Erro na demonstração rápida: {e}")
            logger.error(f"Erro na demonstração rápida: {e}")
    
    async def run_full_demo(self):
        """Executa demonstração completa"""
        print("🚀 INICIANDO DEMONSTRAÇÃO COMPLETA DE DEEP LEARNING")
        print("=" * 60)
        
        try:
            # 1. Treinar modelos
            print("\n1️⃣ TREINANDO MODELOS DE DEEP LEARNING...")
            result = await self.manager.train_all_models()
            
            print(f"✅ Treinamento concluído!")
            print(f"📊 Modelos: {result['models_trained']}")
            print(f"⏱️  Tempo: {result['training_time']:.2f}s")
            
            # 2. Avaliar performance
            print("\n2️⃣ AVALIANDO PERFORMANCE...")
            performance = await self.manager.get_model_performance()
            
            for model_name, perf in performance.items():
                print(f"🤖 {model_name.upper()}:")
                print(f"  📈 Acurácia: {perf.accuracy:.3f}")
                print(f"  🎯 Precisão: {perf.precision:.3f}")
                print(f"  📊 R²: {perf.r2_score:.3f}")
                print(f"  ⏱️  Inferência: {perf.inference_time:.4f}s")
            
            # 3. Fazer predições em lote
            print("\n3️⃣ PREDIÇÕES EM LOTE...")
            
            batch_products = []
            for i in range(10):
                product = {
                    'product_id': f'BATCH_{i+1:03d}',
                    'category': ['gaming', 'anime', 'tech', 'collectibles'][i % 4],
                    'price': 100 + i * 50,
                    'rating': 3.5 + (i * 0.2),
                    'popularity': 0.5 + (i * 0.05),
                    'availability': 0.7 + (i * 0.02)
                }
                
                # Adicionar features
                for j in range(44):
                    product[f'feature_{j}'] = float(np.random.random())
                
                batch_products.append(product)
            
            batch_results = []
            for product in batch_products:
                result = await self.manager.predict_product_priority(product)
                batch_results.append(result)
            
            # Estatísticas das predições
            scores = [r.predicted_score for r in batch_results]
            confidences = [r.confidence for r in batch_results]
            
            print(f"📊 Score médio: {np.mean(scores):.3f}")
            print(f"📊 Score máximo: {np.max(scores):.3f}")
            print(f"📊 Score mínimo: {np.min(scores):.3f}")
            print(f"🎯 Confiança média: {np.mean(confidences):.3f}")
            
            # 4. Gerar insights completos
            print("\n4️⃣ INSIGHTS COMPLETOS...")
            insights = await self.manager.generate_insights()
            
            print("🤖 STATUS DOS MODELOS:")
            for model, status in insights['models_status'].items():
                print(f"  {model}: {status}")
            
            print(f"\n📊 ESTATÍSTICAS:")
            print(f"  🎯 Total de predições: {insights['total_predictions']}")
            print(f"  🎯 Confiança média: {insights['average_confidence']:.3f}")
            
            if insights['top_features']:
                print(f"\n🔍 TOP 3 FEATURES:")
                for feature, importance in insights['top_features'][:3]:
                    print(f"  {feature}: {importance:.3f}")
            
            # 5. Histórico de treinamento
            print("\n5️⃣ HISTÓRICO DE TREINAMENTO...")
            history = await self.manager.get_training_history()
            
            if history:
                print(f"📊 Total de épocas: {len(history)}")
                print(f"📉 Loss final: {history[-1].train_loss:.4f}")
                print(f"📈 Melhor loss: {min([h.train_loss for h in history]):.4f}")
            
            print("\n✅ DEMONSTRAÇÃO COMPLETA FINALIZADA!")
            print("=" * 60)
            
        except Exception as e:
            print(f"\n❌ Erro na demonstração completa: {e}")
            logger.error(f"Erro na demonstração completa: {e}")
    
    async def run_dashboard_demo(self):
        """Executa demonstração do dashboard interativo"""
        print("🎛️ INICIANDO DASHBOARD INTERATIVO DE DEEP LEARNING")
        print("=" * 60)
        
        try:
            # Treinar modelos primeiro
            print("🔄 Treinando modelos para o dashboard...")
            await self.manager.train_all_models()
            
            print("✅ Modelos treinados! Iniciando dashboard...")
            print("💡 Use o menu interativo para explorar o sistema!")
            
            # Executar dashboard
            await self.dashboard.run()
            
        except Exception as e:
            print(f"\n❌ Erro no dashboard: {e}")
            logger.error(f"Erro no dashboard: {e}")

async def main():
    """Função principal"""
    if len(sys.argv) != 2:
        print("Uso: python demo_deep_learning.py [quick|full|dashboard]")
        print("  quick     - Demonstração rápida")
        print("  full      - Demonstração completa")
        print("  dashboard - Dashboard interativo")
        return
    
    mode = sys.argv[1].lower()
    demo = DeepLearningDemo()
    
    if mode == "quick":
        await demo.run_quick_demo()
    elif mode == "full":
        await demo.run_full_demo()
    elif mode == "dashboard":
        await demo.run_dashboard_demo()
    else:
        print("❌ Modo inválido. Use: quick, full ou dashboard")

if __name__ == "__main__":
    asyncio.run(main())
