"""
Simple test script for the deal scoring system.
"""
import sys
from decimal import Decimal
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from src.app.queue.deal_scoring import compute_deal_score, PriceStats, DealPolicy

def test_scoring():
    """Test the deal scoring with sample data."""
    # Sample offer data
    offer = {
        'id': 'test_offer_1',
        'name': 'Smartphone XYZ',
        'category': 'electronics',
        'price': 2000.00,
        'list_price': 3000.00,
        'seller': 'Magazine Luiza',
        'platform': 'test'
    }
    
    # Sample price statistics
    price_stats = PriceStats(
        mean_90d=Decimal('2800.00'),
        p25_90d=Decimal('2600.00'),
        low_40d=Decimal('2100.00'),
        low_90d=Decimal('2050.00'),
        low_180d=Decimal('2000.00')
    )
    
    # Create a policy with trusted sellers
    policy = DealPolicy(trusted_sellers={"Magazine Luiza", "Kabum"})
    
    # Calculate the score
    score = compute_deal_score(offer, price_stats, policy)
    
    # Print results
    print("\n=== TESTE DE PONTUAÇÃO DE OFERTA ===")
    print(f"Produto: {offer['name']}")
    print(f"Categoria: {offer['category']}")
    print(f"Vendedor: {offer['seller']}")
    print(f"Preço: R$ {offer['price']:.2f}")
    print(f"Preço de tabela: R$ {offer['list_price']:.2f}")
    print(f"Desconto: {(1 - offer['price'] / offer['list_price']):.1%}")
    
    print("\nHistórico de preços:")
    print(f"- Média 90d: R$ {price_stats.mean_90d:.2f}")
    print(f"- 25º percentil 90d: R$ {price_stats.p25_90d:.2f}")
    print(f"- Mínimo 40d: R$ {price_stats.low_40d:.2f}")
    print(f"- Mínimo 90d: R$ {price_stats.low_90d:.2f}")
    print(f"- Mínimo 180d: R$ {price_stats.low_180d:.2f}")
    
    print(f"\n=== PONTUAÇÃO: {score.score:.2f} ({score.level}) ===")
    print("Motivos:")
    for reason in score.reasons:
        print(f"- {reason}")
    
    print("\nINTERPRETAÇÃO:")
    if score.level == "CRITICAL":
        print("🔥 OFERTA EXCELENTE! Postar imediatamente.")
    elif score.level == "HIGH":
        print("👍 Boa oferta. Postar na próxima janela disponível.")
    elif score.level == "MEDIUM":
        print("🤔 Oferta razoável. Postar se houver espaço na programação.")
    else:
        print("⏭  Oferta abaixo do limiar. Não postar.")

if __name__ == "__main__":
    test_scoring()
