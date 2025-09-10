"""
Script para testar o sistema de pontuação de ofertas.

Exemplo de uso:
    python scripts/test_deal_scoring.py --category electronics --price 2000 --list_price 3000 --seller "Magazine Luiza"
"""

import argparse
import json
from decimal import Decimal
from pathlib import Path
import sys

# Adiciona o diretório raiz ao path para importar módulos
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.app.queue.deal_scoring import (
    compute_deal_score,
    PriceStats,
    DealPolicy
)

def create_sample_offer(args):
    """Cria um dicionário de oferta a partir dos argumentos."""
    return {
        'id': 'test_offer',
        'name': f'Produto de Teste {args.category}',
        'category': args.category,
        'price': float(args.price),
        'list_price': float(args.list_price) if args.list_price else float(args.price) * 1.25,
        'seller': args.seller,
        'platform': 'test',
    }

def create_sample_price_stats(args):
    """Cria estatísticas de preço para teste."""
    price = Decimal(str(args.price))
    list_price = Decimal(str(args.list_price)) if args.list_price else price * Decimal('1.25')
    
    return PriceStats(
        mean_90d=Decimal(str(args.mean_90d)) if args.mean_90d else list_price * Decimal('0.9'),
        p25_90d=Decimal(str(args.p25_90d)) if args.p25_90d else list_price * Decimal('0.85'),
        low_40d=Decimal(str(args.low_40d)) if args.low_40d else list_price * Decimal('0.82'),
        low_90d=Decimal(str(args.low_90d)) if args.low_90d else list_price * Decimal('0.8'),
        low_180d=Decimal(str(args.low_180d)) if args.low_180d else list_price * Decimal('0.78'),
    )

def main():
    parser = argparse.ArgumentParser(description='Testar sistema de pontuação de ofertas')
    
    # Parâmetros da oferta
    parser.add_argument('--category', type=str, default='electronics',
                       choices=['electronics', 'peripherals', 'appliances', 'other'],
                       help='Categoria do produto')
    parser.add_argument('--price', type=float, required=True,
                       help='Preço atual do produto')
    parser.add_argument('--list_price', type=float,
                       help='Preço de tabela (opcional, calculado se não informado)')
    parser.add_argument('--seller', type=str, default='Loja Genérica',
                       help='Nome do vendedor')
    
    # Estatísticas de preço
    parser.add_argument('--mean_90d', type=float,
                       help='Preço médio dos últimos 90 dias')
    parser.add_argument('--p25_90d', type=float,
                       help='25º percentil dos preços dos últimos 90 dias')
    parser.add_argument('--low_40d', type=float,
                       help='Menor preço dos últimos 40 dias')
    parser.add_argument('--low_90d', type=float,
                       help='Menor preço dos últimos 90 dias')
    parser.add_argument('--low_180d', type=float,
                       help='Menor preço dos últimos 180 dias')
    
    # Política personalizada
    parser.add_argument('--trusted_sellers', type=str,
                       help='Lista de vendedores confiáveis (separados por vírgula)')
    
    args = parser.parse_args()
    
    # Criar oferta e estatísticas de teste
    offer = create_sample_offer(args)
    price_stats = create_sample_price_stats(args)
    
    # Criar política personalizada se necessário
    policy_args = {}
    if args.trusted_sellers:
        policy_args['trusted_sellers'] = set(s.strip() for s in args.trusted_sellers.split(','))
    
    policy = DealPolicy(**policy_args)
    
    # Calcular pontuação
    score = compute_deal_score(offer, price_stats, policy)
    
    # Exibir resultados
    print("\n=== RESULTADO DA PONTUAÇÃO ===")
    print(f"Produto: {offer['name']}")
    print(f"Categoria: {offer['category']}")
    print(f"Vendedor: {offer['seller']}")
    print(f"Preço: R$ {offer['price']:.2f}")
    print(f"Preço de tabela: R$ {offer['list_price']:.2f}")
    print(f"Desconto: {(1 - offer['price'] / offer['list_price']):.1%}")
    print(f"\nEstatísticas de preço:")
    print(f"- Média 90d: R$ {price_stats.mean_90d:.2f}" if price_stats.mean_90d else "- Média 90d: N/A")
    print(f"- 25º percentil 90d: R$ {price_stats.p25_90d:.2f}" if price_stats.p25_90d else "- 25º percentil 90d: N/A")
    print(f"- Mínimo 40d: R$ {price_stats.low_40d:.2f}" if price_stats.low_40d else "- Mínimo 40d: N/A")
    print(f"- Mínimo 90d: R$ {price_stats.low_90d:.2f}" if price_stats.low_90d else "- Mínimo 90d: N/A")
    print(f"- Mínimo 180d: R$ {price_stats.low_180d:.2f}" if price_stats.low_180d else "- Mínimo 180d: N/A")
    
    print(f"\n=== PONTUAÇÃO: {score.score:.2f} ({score.level}) ===")
    print("Motivos:")
    for reason in score.reasons:
        print(f"- {reason}")
    
    # Interpretação da pontuação
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
    main()
