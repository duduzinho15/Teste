#!/usr/bin/env python3
"""
Demonstração do Sistema de Priorização Geek/Gamer
Garimpeiro Geek - Foco em Cultura Geek, Otaku, Nerd, Gamer e Tech
"""

import asyncio
import sys
from pathlib import Path
from decimal import Decimal

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

async def demo_geek_prioritization():
    """Demonstra o sistema de priorização geek"""
    
    try:
        from src.core.geek_prioritizer import GeekPrioritizer
        from src.core.models import Offer
        
        print("🎮 SISTEMA DE PRIORIZAÇÃO GEEK/GAMER - GARIMPEIRO GEEK")
        print("=" * 70)
        
        # Inicializar prioritizador
        prioritizer = GeekPrioritizer()
        
        # Mostrar configurações
        print("\n📋 CONFIGURAÇÕES GEEK CARREGADAS:")
        stats = prioritizer.get_geek_stats()
        for key, value in stats.items():
            print(f"   - {key}: {value}")
        
        # Criar ofertas de exemplo para demonstração
        sample_offers = [
            # 🎮 Categorias PRIMÁRIAS (Alta Prioridade)
            Offer(
                title="PlayStation 5 Console Digital Edition 825GB SSD",
                price=Decimal("3999.99"),
                discount_percentage=15,
                category="consoles_gaming",
                store="Sony Store",
                url="https://example.com/ps5"
            ),
            Offer(
                title="Notebook Gamer ASUS ROG Strix G15 RTX 4060 16GB RAM",
                price=Decimal("5999.99"),
                discount_percentage=20,
                category="notebooks_gamer",
                store="ASUS Store",
                url="https://example.com/notebook-gamer"
            ),
            Offer(
                title="Placa de Vídeo NVIDIA RTX 4070 Ti Gaming X Trio",
                price=Decimal("3999.99"),
                discount_percentage=10,
                category="placas_video",
                store="MSI Store",
                url="https://example.com/rtx4070ti"
            ),
            Offer(
                title="Figura Action Figure Anime Dragon Ball Z Goku Ultra Instinct",
                price=Decimal("299.99"),
                discount_percentage=25,
                category="figuras_action",
                store="Anime Store",
                url="https://example.com/goku-figure"
            ),
            
            # ⚡ Categorias SECUNDÁRIAS (Média Prioridade)
            Offer(
                title="Smartphone Samsung Galaxy S24 Ultra 256GB",
                price=Decimal("6999.99"),
                discount_percentage=18,
                category="smartphones_premium",
                store="Samsung Store",
                url="https://example.com/s24-ultra"
            ),
            Offer(
                title="Smart TV LG OLED 65\" 4K HDR",
                price=Decimal("4999.99"),
                discount_percentage=22,
                category="smart_tvs",
                store="LG Store",
                url="https://example.com/lg-oled"
            ),
            
            # 📱 Categorias GERAIS (Baixa Prioridade)
            Offer(
                title="Fone de Ouvido Bluetooth Genérico",
                price=Decimal("89.99"),
                discount_percentage=30,
                category="audio",
                store="Loja Genérica",
                url="https://example.com/fone-generico"
            ),
            Offer(
                title="Cabo USB-C 2m",
                price=Decimal("19.99"),
                discount_percentage=40,
                category="acessorios",
                store="Loja de Cabos",
                url="https://example.com/cabo-usb"
            )
        ]
        
        print(f"\n🎯 DEMONSTRAÇÃO COM {len(sample_offers)} OFERTAS DE EXEMPLO:")
        print("-" * 70)
        
        # Mostrar ofertas originais
        print("📦 OFERTAS ORIGINAIS:")
        for i, offer in enumerate(sample_offers, 1):
            print(f"   {i}. {offer.title[:60]}...")
            print(f"      💰 R$ {offer.price} | 🏪 {offer.store} | 📂 {offer.category}")
        
        # Priorizar ofertas por score geek
        print(f"\n🚀 PRIORIZANDO OFERTAS POR SCORE GEEK...")
        prioritized_offers = prioritizer.prioritize_offers(sample_offers)
        
        # Mostrar resultados da priorização
        print("\n🏆 OFERTAS PRIORIZADAS POR SCORE GEEK:")
        print("-" * 70)
        
        for i, (offer, geek_score) in enumerate(prioritized_offers, 1):
            emoji = "🎮" if geek_score.geek_level == "primary" else "⚡" if geek_score.geek_level == "secondary" else "📱"
            level_name = {
                "primary": "PRIMÁRIA",
                "secondary": "SECUNDÁRIA", 
                "general": "GERAL"
            }[geek_score.geek_level]
            
            print(f"\n{emoji} {i}. {level_name} - Score: {geek_score.overall_score:.2f}")
            print(f"   📝 {offer.title[:60]}...")
            print(f"   💰 R$ {offer.price} | 🏪 {offer.store}")
            print(f"   📊 Scores: Categoria={geek_score.category_score:.2f}, Keywords={geek_score.keyword_score:.2f}, Tipo={geek_score.product_type_score:.2f}")
            print(f"   🔗 Multiplicador: {geek_score.priority_multiplier:.2f}x")
            
            if geek_score.matched_categories:
                print(f"   🏷️ Categorias: {', '.join(geek_score.matched_categories)}")
            
            if geek_score.matched_keywords:
                print(f"   🔍 Keywords: {', '.join(geek_score.matched_keywords)}")
            
            if geek_score.recommendations:
                print(f"   💡 Recomendações: {'; '.join(geek_score.recommendations)}")
        
        # Estatísticas da priorização
        print("\n📊 ESTATÍSTICAS DA PRIORIZAÇÃO:")
        print("-" * 70)
        
        primary_count = sum(1 for _, score in prioritized_offers if score.geek_level == "primary")
        secondary_count = sum(1 for _, score in prioritized_offers if score.geek_level == "secondary")
        general_count = sum(1 for _, score in prioritized_offers if score.geek_level == "general")
        
        print(f"   🎮 Categorias Primárias (Geek): {primary_count}")
        print(f"   ⚡ Categorias Secundárias (Tech): {secondary_count}")
        print(f"   📱 Categorias Gerais: {general_count}")
        
        avg_score = sum(score.overall_score for _, score in prioritized_offers) / len(prioritized_offers)
        print(f"   📈 Score Médio: {avg_score:.2f}")
        
        best_score = prioritized_offers[0][1].overall_score
        worst_score = prioritized_offers[-1][1].overall_score
        print(f"   🏆 Melhor Score: {best_score:.2f}")
        print(f"   📉 Pior Score: {worst_score:.2f}")
        
        # Explicar como funciona
        print("\n💡 COMO FUNCIONA A PRIORIZAÇÃO GEEK:")
        print("-" * 70)
        print("   1. 🎮 CATEGORIAS PRIMÁRIAS: Gaming, PC Gaming, Tech Geek, Anime/Otaku, Collectibles")
        print("   2. ⚡ CATEGORIAS SECUNDÁRIAS: Home Tech, Fitness Tech, Eletrônicos Gerais")
        print("   3. 📱 CATEGORIAS GERAIS: Outros produtos (não prioritários)")
        print("   4. 🔍 PALAVRAS-CHAVE: Detecta termos como 'gaming', 'gamer', 'tech', 'geek', 'nerd', 'otaku'")
        print("   5. 🏷️ PRODUTOS PRIORITÁRIOS: PlayStation, Xbox, RTX, Ryzen, etc. sempre recebem boost")
        print("   6. 📊 SCORE FINAL: Combina categoria, keywords e tipo de produto com pesos configuráveis")
        
        print("\n🎯 OBJETIVO DO GARIMPEIRO GEEK:")
        print("   Focar em produtos que interessam ao público geek/gamer/otaku/nerd")
        print("   Priorizar ofertas de alta tecnologia e cultura geek")
        print("   Manter qualidade geral enquanto destaca produtos relevantes")
        print("   Não excluir outras categorias, mas dar preferência ao nicho principal")
        
        print("\n🎉 DEMONSTRAÇÃO CONCLUÍDA COM SUCESSO!")
        return True
        
    except ImportError as e:
        print(f"❌ Erro ao importar módulo: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro durante a demonstração: {e}")
        return False

async def main():
    """Função principal"""
    
    print("🚀 Iniciando demonstração do sistema de priorização geek...")
    
    success = await demo_geek_prioritization()
    
    if success:
        print("\n🎯 PRÓXIMOS PASSOS RECOMENDADOS:")
        print("1. Integrar o GeekPrioritizer nos pipelines existentes")
        print("2. Configurar alertas específicos para produtos geek de alta prioridade")
        print("3. Ajustar pesos e categorias conforme feedback dos usuários")
        print("4. Implementar dashboard específico para métricas geek")
        print("5. Treinar equipe no novo sistema de priorização")
    
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
