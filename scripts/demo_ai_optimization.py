"""
Demonstração do Sistema de IA para Otimização Automática de Priorização
Garimpeiro Geek - Sistema Inteligente de Otimização de Scores
"""

import asyncio
import logging
from datetime import datetime
from decimal import Decimal
from typing import List

from src.core.models import Offer
from src.app.ai_optimization import (
    AIOptimizer, ModelConfig, DataCollector, ModelTrainer, 
    PredictionEngine, OptimizationDashboard
)


async def demo_ai_optimization_system():
    """Demonstração completa do sistema de IA de otimização"""
    print("🤖 SISTEMA DE IA PARA OTIMIZAÇÃO AUTOMÁTICA DE PRIORIZAÇÃO")
    print("=" * 70)
    print("Garimpeiro Geek - Otimização Inteligente de Scores Geek")
    print()
    
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        # 1. Inicializar componentes
        print("🔄 Inicializando componentes do sistema...")
        
        config = ModelConfig(
            auto_retrain=True,
            retrain_interval_days=7,
            min_data_points=500,
            confidence_threshold=0.7,
            batch_size=50
        )
        
        ai_optimizer = AIOptimizer(config)
        data_collector = DataCollector()
        model_trainer = ModelTrainer()
        prediction_engine = PredictionEngine(model_trainer)
        
        print("✅ Componentes inicializados!")
        
        # 2. Coletar dados históricos
        print("\n📊 Coletando dados históricos para treinamento...")
        historical_data = await data_collector.collect_historical_data(days_back=30)
        print(f"✅ Coletados {len(historical_data)} registros históricos")
        
        # 3. Gerar target scores
        print("\n🎯 Gerando target scores para treinamento...")
        target_scores = []
        for feature in historical_data:
            # Score baseado em performance simulada
            base_score = feature.geek_score
            performance_bonus = feature.conversion_rate * 0.3 + feature.engagement_rate * 0.2
            target_score = min(1.0, base_score + performance_bonus)
            target_scores.append(target_score)
        
        # 4. Salvar dados de treinamento
        print("\n💾 Salvando dados de treinamento...")
        success = await data_collector.save_training_data(historical_data, target_scores)
        if success:
            print("✅ Dados salvos com sucesso!")
        else:
            print("❌ Erro ao salvar dados")
            return
        
        # 5. Carregar dados para treinamento
        print("\n📈 Carregando dados para treinamento...")
        training_data = await data_collector.load_training_data()
        print(f"✅ Carregados {len(training_data.features)} registros para treinamento")
        
        # 6. Treinar modelos
        print("\n🤖 Treinando modelos de IA...")
        training_results = await model_trainer.train_all_models(training_data)
        
        if training_results:
            print(f"✅ {len(training_results)} modelos treinados com sucesso!")
            
            for result in training_results:
                print(f"\n   🤖 {result.model_name.upper()}:")
                print(f"      R² Score: {result.metrics.r2_score:.4f}")
                print(f"      MSE: {result.metrics.mse:.4f}")
                print(f"      MAE: {result.metrics.mae:.4f}")
                print(f"      Cross-Val Score: {result.metrics.cross_val_score:.4f}")
                print(f"      Tempo de Treinamento: {result.metrics.training_time:.2f}s")
        else:
            print("❌ Erro no treinamento dos modelos")
            return
        
        # 7. Inicializar sistema de IA
        print("\n🚀 Inicializando sistema de IA...")
        success = await ai_optimizer.initialize()
        if not success:
            print("❌ Falha na inicialização do sistema")
            return
        
        print("✅ Sistema de IA inicializado!")
        
        # 8. Criar ofertas de teste
        print("\n📦 Criando ofertas de teste...")
        test_offers = create_test_offers()
        
        # 9. Otimizar ofertas
        print("\n🎯 Otimizando ofertas de teste...")
        conversion_data = {
            'conversion_rate': 0.15,
            'click_rate': 0.10,
            'engagement_rate': 0.18
        }
        
        optimization_results = await ai_optimizer.optimize_batch(test_offers, conversion_data)
        
        if optimization_results:
            print(f"✅ {len(optimization_results)} ofertas otimizadas!")
            
            print("\n📊 RESULTADOS DA OTIMIZAÇÃO:")
            total_improvement = 0
            high_confidence = 0
            
            for i, result in enumerate(optimization_results, 1):
                improvement = result.predicted_score - result.original_score
                total_improvement += improvement
                
                if result.confidence.confidence > 0.8:
                    high_confidence += 1
                
                print(f"\n   {i}. {result.offer_id[:40]}...")
                print(f"      Original: {result.original_score:.4f} → Otimizado: {result.predicted_score:.4f}")
                print(f"      Melhoria: {improvement:+.4f} | Confiança: {result.confidence.confidence:.2%}")
                print(f"      Modelo: {result.model_used}")
            
            print(f"\n📈 RESUMO GERAL:")
            print(f"   Melhoria média: {total_improvement/len(optimization_results):+.4f}")
            print(f"   Alta confiança: {high_confidence}/{len(optimization_results)} ({high_confidence/len(optimization_results):.1%})")
        
        # 10. Mostrar insights detalhados
        print("\n💡 INSIGHTS DETALHADOS:")
        if optimization_results:
            insights = await ai_optimizer.get_optimization_insights(optimization_results[0])
            if insights:
                print(f"   Recomendação: {insights.get('recommendation', 'N/A')}")
                print(f"   Nível de Confiança: {insights.get('confidence_level', 'N/A')}")
                print(f"   Melhoria Percentual: {insights.get('improvement_percentage', 0):.1f}%")
                
                key_factors = insights.get('key_factors', [])
                if key_factors:
                    print(f"   Fatores-chave: {', '.join(key_factors[:3])}")
        
        # 11. Mostrar status do sistema
        print("\n📊 STATUS FINAL DO SISTEMA:")
        status = await ai_optimizer.get_system_status()
        print(f"   Inicializado: {'Sim' if status.get('is_initialized') else 'Não'}")
        print(f"   Modelo Ativo: {status.get('current_model', 'Nenhum')}")
        print(f"   Total de Otimizações: {status.get('total_optimizations', 0)}")
        print(f"   Última Atualização: {status.get('last_updated', 'N/A')}")
        
        # 12. Estatísticas dos dados
        print("\n📊 ESTATÍSTICAS DOS DADOS:")
        stats = await data_collector.get_feature_statistics()
        if stats:
            print(f"   Total de registros: {stats.get('total_records', 0)}")
            print(f"   Score geek médio: {stats.get('avg_geek_score', 0):.4f}")
            print(f"   Taxa de conversão média: {stats.get('avg_conversion_rate', 0):.2%}")
            print(f"   Preço médio: R$ {stats.get('avg_price', 0):.2f}")
        
        print("\n🎉 DEMONSTRAÇÃO CONCLUÍDA COM SUCESSO!")
        print("🤖 Sistema de IA para otimização automática está funcionando perfeitamente!")
        
    except Exception as e:
        print(f"❌ Erro na demonstração: {e}")
        logging.error(f"Erro na demonstração: {e}")


def create_test_offers() -> List[Offer]:
    """Cria ofertas de teste para demonstração"""
    offers = [
        Offer(
            title="Action Figure Dragon Ball Z Goku Super Saiyan",
            price=Decimal("89.90"),
            category="Action Figures",
            url="https://exemplo.com/goku-ssj-action-figure",
            store="Amazon",
            store_data={"rating": 4.5, "reviews": 1200},
            scraped_at=datetime.now()
        ),
        Offer(
            title="Manga One Piece Vol. 1 - Edição Especial",
            price=Decimal("29.90"),
            category="Manga",
            url="https://exemplo.com/one-piece-vol1-special",
            store="Magalu",
            store_data={"rating": 4.8, "reviews": 850},
            scraped_at=datetime.now()
        ),
        Offer(
            title="Video Game PS5 God of War Ragnarök",
            price=Decimal("299.90"),
            category="Video Games",
            url="https://exemplo.com/god-of-war-ragnarok-ps5",
            store="Americanas",
            store_data={"rating": 4.9, "reviews": 2100},
            scraped_at=datetime.now()
        ),
        Offer(
            title="Cosplay Naruto Completo com Acessórios",
            price=Decimal("159.90"),
            category="Cosplay",
            url="https://exemplo.com/cosplay-naruto-completo",
            store="Submarino",
            store_data={"rating": 4.2, "reviews": 320},
            scraped_at=datetime.now()
        ),
        Offer(
            title="Board Game Catan - Edição Geek",
            price=Decimal("129.90"),
            category="Board Games",
            url="https://exemplo.com/catan-geek-edition",
            store="Casas Bahia",
            store_data={"rating": 4.6, "reviews": 650},
            scraped_at=datetime.now()
        ),
        Offer(
            title="Tech Gadget Smart Watch Gamer",
            price=Decimal("199.90"),
            category="Tech Gadgets",
            url="https://exemplo.com/smartwatch-gamer",
            store="Amazon",
            store_data={"rating": 4.3, "reviews": 890},
            scraped_at=datetime.now()
        ),
        Offer(
            title="Comic Book Batman - Edição Limitada",
            price=Decimal("45.90"),
            category="Comic Books",
            url="https://exemplo.com/batman-limited-edition",
            store="Magalu",
            store_data={"rating": 4.7, "reviews": 420},
            scraped_at=datetime.now()
        ),
        Offer(
            title="Gaming Accessories Headset Pro Gamer",
            price=Decimal("179.90"),
            category="Gaming Accessories",
            url="https://exemplo.com/headset-pro-gamer",
            store="Americanas",
            store_data={"rating": 4.4, "reviews": 1100},
            scraped_at=datetime.now()
        )
    ]
    
    return offers


async def quick_test():
    """Teste rápido do sistema"""
    print("🚀 TESTE RÁPIDO - SISTEMA DE IA DE OTIMIZAÇÃO")
    print("=" * 50)
    
    try:
        # Inicializar otimizador
        ai_optimizer = AIOptimizer()
        
        # Inicializar sistema
        print("🔄 Inicializando sistema...")
        success = await ai_optimizer.initialize()
        
        if not success:
            print("❌ Falha na inicialização")
            return
        
        print("✅ Sistema inicializado!")
        
        # Criar oferta de teste
        offer = Offer(
            title="Teste IA - Action Figure Dragon Ball",
            price=Decimal("99.90"),
            category="Action Figures",
            url="https://teste.com/action-figure-db",
            store="Teste Store",
            store_data={},
            scraped_at=datetime.now()
        )
        
        # Otimizar oferta
        print("🎯 Otimizando oferta de teste...")
        prediction = await ai_optimizer.optimize_offer(offer)
        
        print(f"✅ Score original: {prediction.original_score:.4f}")
        print(f"✅ Score otimizado: {prediction.predicted_score:.4f}")
        print(f"✅ Melhoria: {prediction.predicted_score - prediction.original_score:+.4f}")
        print(f"✅ Confiança: {prediction.confidence.confidence:.2%}")
        print(f"✅ Modelo: {prediction.model_used}")
        
        # Status do sistema
        status = await ai_optimizer.get_system_status()
        print(f"✅ Total de otimizações: {status.get('total_optimizations', 0)}")
        
        print("\n🎉 TESTE CONCLUÍDO COM SUCESSO!")
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")


async def main():
    """Função principal"""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "quick":
        await quick_test()
    else:
        await demo_ai_optimization_system()


if __name__ == "__main__":
    asyncio.run(main())
