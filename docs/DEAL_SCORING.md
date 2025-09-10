# Sistema de Pontuação de Ofertas

## Visão Geral

O sistema de pontuação de ofertas classifica automaticamente as ofertas com base em diversos fatores como desconto, histórico de preços e confiabilidade do vendedor. Cada oferta recebe uma pontuação de 0 a 1 e é classificada em um dos seguintes níveis:

- **CRÍTICO (≥ 0.85)**: Ofertas excelentes que devem ser publicadas imediatamente
- **ALTA (0.75 - 0.84)**: Boas ofertas para publicar na próxima janela disponível
- **MÉDIA (0.50 - 0.74)**: Ofertas razoáveis, publicar se houver espaço
- **BAIXA (< 0.50)**: Ofertas abaixo do limiar, não publicar

## Fatores de Pontuação

### 1. Categoria do Produto

Cada categoria tem regras específicas de pontuação:

#### Eletrônicos (eletrônicos, informática, smartphones, etc.)
- +0.35 se preço ≤ 80% da média de 90 dias
- +0.35 se for o menor preço em 180 dias (ou +0.20 se for em 40 dias)
- +0.15 se preço ≤ 88% do 25º percentil dos últimos 90 dias
- +0.20 se desconto ≥ 20% (configurável)

#### Periféricos (headphones, mouses, teclados, etc.)
- +0.40 se desconto ≥ 25% (configurável)
- +0.25 se for o menor preço em 90 dias

#### Eletrodomésticos (geladeiras, fogões, etc.)
- +0.30 se desconto ≥ 18% (configurável)
- +0.30 se for o menor preço em 180 dias

### 2. Vendedor Confiável
- +0.10 se o vendedor estiver na lista de confiáveis

## Como Funciona

1. **Coleta**: As ofertas são coletadas das fontes configuradas
2. **Enriquecimento**: Dados adicionais são coletados (histórico de preços, etc.)
3. **Pontuação**: Cada oferta é pontuada com base nos critérios acima
4. **Classificação**: As ofertas são classificadas em níveis (CRÍTICO, ALTA, etc.)
5. **Publicação**: O sistema agenda a publicação com base na classificação

## Testando o Sistema

Você pode testar o sistema de pontuação com o script `test_deal_scoring.py`:

```bash
# Exemplo: Testar uma oferta de smartphone
python scripts/test_deal_scoring.py --category electronics --price 2000 --list_price 3000 --seller "Magazine Luiza"

# Com histórico de preços
python scripts/test_deal_scoring.py --category electronics --price 1800 --list_price 2500 --mean_90d 2200 --low_40d 1850 --seller "Kabum"
```

## Configuração

As configurações podem ser ajustadas no arquivo `.env`:

```ini
# Limiares de pontuação
DEAL_SCORE_CRITICAL=0.85
DEAL_SCORE_HIGH=0.75

# Descontos mínimos por categoria
ELECTRONICS_MIN_DISC=0.20
PERIPHERALS_MIN_DISC=0.25
APPLIANCES_MIN_DISC=0.18

# Vendedores confiáveis (separados por vírgula)
TRUSTED_SELLERS=Magazine Luiza,Kabum,Pichau

# Intervalos de publicação (em segundos)
TG_MIN_INTERVAL_CRITICAL=20
TG_MIN_INTERVAL_HIGH=120
TG_MAX_PER_HOUR=20
```

## Integração com o Sistema

O sistema de pontuação é automaticamente integrado ao pipeline de processamento de ofertas. Para usá-lo no código:

```python
from src.app.queue.deal_scoring import compute_deal_score, PriceStats

# Exemplo de uso
offer = {
    'name': 'Smartphone XYZ',
    'category': 'electronics/smartphones',
    'price': 2000.00,
    'list_price': 3000.00,
    'seller': 'Magazine Luiza',
    'platform': 'magazineluiza'
}

price_stats = PriceStats(
    mean_90d=Decimal('2800.00'),
    p25_90d=Decimal('2600.00'),
    low_40d=Decimal('2100.00'),
    low_180d=Decimal('2050.00')
)

score = compute_deal_score(offer, price_stats)
print(f"Pontuação: {score.score:.2f} ({score.level})")
print("Motivos:", score.reasons)
```

## Personalização

Você pode personalizar as regras de pontuação criando uma política personalizada:

```python
from src.app.queue.deal_scoring import DealPolicy

# Criar política personalizada
custom_policy = DealPolicy(
    min_discount_pct={
        'electronics': 0.25,  # Aumentar desconto mínimo para eletrônicos
        'peripherals': 0.25,
        'appliances': 0.20
    },
    trusted_sellers={"Magazine Luiza", "Kabum"},
    low_40d_bonus=0.25,  # Aumentar peso do menor preço em 40 dias
    low_180d_bonus=0.40  # Aumentar peso do menor preço em 180 dias
)

# Usar a política personalizada
score = compute_deal_score(offer, price_stats, custom_policy)
```
