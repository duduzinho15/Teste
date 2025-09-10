from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Dict, Optional, Set
from decimal import Decimal
import logging

from src.core.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class DealScoreLevel(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


@dataclass
class PriceStats:
    """Historical price statistics for a product."""
    mean_90d: Optional[Decimal] = None
    p25_90d: Optional[Decimal] = None
    low_40d: Optional[Decimal] = None
    low_90d: Optional[Decimal] = None
    low_180d: Optional[Decimal] = None


@dataclass
class DealPolicy:
    """Scoring policy configuration."""
    min_discount_pct: Dict[str, float] = field(default_factory=dict)  # by category
    low_40d_bonus: float = 0.2
    low_90d_bonus: float = 0.25
    low_180d_bonus: float = 0.35
    trusted_sellers: Set[str] = field(default_factory=set)
    category_weights: Dict[str, float] = field(default_factory=dict)


@dataclass
class DealScore:
    """Scoring result for a deal."""
    score: float = 0.0
    reasons: List[str] = field(default_factory=list)
    level: DealScoreLevel = DealScoreLevel.LOW

    def __post_init__(self):
        # Ensure score is between 0 and 1
        self.score = max(0.0, min(1.0, self.score))
        
        # Set level based on score
        if self.score >= float(settings.DEAL_SCORE_CRITICAL):
            self.level = DealScoreLevel.CRITICAL
        elif self.score >= float(settings.DEAL_SCORE_HIGH):
            self.level = DealScoreLevel.HIGH
        elif self.score >= 0.5:  # Default threshold for MEDIUM
            self.level = DealScoreLevel.MEDIUM
        else:
            self.level = DealScoreLevel.LOW


def get_default_policy() -> DealPolicy:
    """Get default deal scoring policy from settings."""
    return DealPolicy(
        min_discount_pct={
            "electronics": float(settings.ELECTRONICS_MIN_DISC),
            "peripherals": float(settings.PERIPHERALS_MIN_DISC),
            "appliances": float(settings.APPLIANCES_MIN_DISC),
        },
        trusted_sellers=set(settings.TRUSTED_SELLERS.split(",") if settings.TRUSTED_SELLERS else []),
    )


def compute_deal_score(offer: dict, price_stats: PriceStats, policy: Optional[DealPolicy] = None) -> DealScore:
    """
    Compute a deal score based on offer details and price history.
    
    Args:
        offer: Dictionary containing offer details
        price_stats: Historical price statistics
        policy: Scoring policy (uses default if None)
        
    Returns:
        DealScore object with score, level, and reasons
    """
    if policy is None:
        policy = get_default_policy()
        
    score = 0.0
    reasons = []
    
    # Get offer details with defaults
    price = Decimal(str(offer.get('price', 0)))
    list_price = Decimal(str(offer.get('list_price', price)))
    category = (offer.get('category', '').lower() or 'other').split('/')[0]  # Use top-level category
    seller = (offer.get('seller') or '').strip()
    
    # Calculate discount if list price is available and valid
    discount_pct = 0.0
    if list_price and list_price > 0 and price < list_price:
        discount_pct = float((list_price - price) / list_price)
    
    # Apply category-specific scoring
    if category in ['electronics', 'eletronicos', 'informatica']:
        score += _score_electronics(price, discount_pct, price_stats, policy, reasons)
    elif category in ['peripherals', 'perifericos', 'acessorios']:
        score += _score_peripherals(price, discount_pct, price_stats, policy, reasons)
    elif category in ['appliances', 'eletrodomesticos']:
        score += _score_appliances(price, discount_pct, price_stats, policy, reasons)
    else:
        # Default scoring for other categories
        if discount_pct >= 0.15:  # 15% minimum discount for other categories
            score += 0.5 + min(0.3, (discount_pct - 0.15) * 2)
            reasons.append(f"Desconto de {discount_pct:.0%} na categoria {category}")
    
    # Seller trust bonus
    if seller and seller.lower() in {s.lower() for s in policy.trusted_sellers}:
        score += 0.1
        reasons.append(f"Vendedor confiável: {seller}")
    
    # Create and return the score object
    result = DealScore(score=score, reasons=reasons)
    logger.debug(
        f"Scored offer: {offer.get('id', 'unknown')} - "
        f"Score: {result.score:.2f} ({result.level}), "
        f"Reasons: {', '.join(reasons)[:100]}..."
    )
    return result


def _score_electronics(
    price: Decimal, 
    discount_pct: float, 
    price_stats: PriceStats, 
    policy: DealPolicy,
    reasons: List[str]
) -> float:
    """Score electronics deals."""
    score = 0.0
    min_discount = policy.min_discount_pct.get('electronics', 0.2)
    
    # Discount vs 90-day mean
    if price_stats.mean_90d and price < price_stats.mean_90d * Decimal('0.8'):  # 20% below mean
        score += 0.35
        reasons.append(f"Preço {((price_stats.mean_90d - price) / price_stats.mean_90d):.0%} abaixo da média de 90 dias")
    
    # Historical lows
    if price_stats.low_180d and price <= price_stats.low_180d:
        score += policy.low_180d_bonus
        reasons.append("Menor preço em 180 dias")
    elif price_stats.low_40d and price <= price_stats.low_40d:
        score += policy.low_40d_bonus
        reasons.append("Menor preço em 40 dias")
    
    # Percentile-based scoring
    if price_stats.p25_90d and price <= price_stats.p25_90d * Decimal('0.88'):  # 12% below 25th percentile
        score += 0.15
        reasons.append("Preço entre os 25% mais baixos dos últimos 90 dias")
    
    # Minimum discount threshold
    if discount_pct >= min_discount:
        score += 0.2
        reasons.append(f"Desconto de {discount_pct:.0%} (mínimo: {min_discount:.0%})")
    
    return min(1.0, score)


def _score_peripherals(
    price: Decimal, 
    discount_pct: float, 
    price_stats: PriceStats, 
    policy: DealPolicy,
    reasons: List[str]
) -> float:
    """Score peripherals deals."""
    score = 0.0
    min_discount = policy.min_discount_pct.get('peripherals', 0.25)
    
    # Discount-based scoring
    if discount_pct >= min_discount:
        score += 0.4
        reasons.append(f"Desconto de {discount_pct:.0%} (mínimo: {min_discount:.0%})")
    
    # Historical low bonus
    low_threshold = price_stats.low_90d or price_stats.low_40d
    if low_threshold and price <= low_threshold:
        score += policy.low_90d_bonus
        days = 90 if price_stats.low_90d else 40
        reasons.append(f"Menor preço em {days} dias")
    
    return min(1.0, score)


def _score_appliances(
    price: Decimal, 
    discount_pct: float, 
    price_stats: PriceStats, 
    policy: DealPolicy,
    reasons: List[str]
) -> float:
    """Score appliances deals."""
    score = 0.0
    min_discount = policy.min_discount_pct.get('appliances', 0.18)
    
    # Discount-based scoring
    if discount_pct >= min_discount:
        score += 0.3
        reasons.append(f"Desconto de {discount_pct:.0%} (mínimo: {min_discount:.0%})")
    
    # Historical low bonus (longer period for appliances)
    if price_stats.low_180d and price <= price_stats.low_180d:
        score += policy.low_180d_bonus
        reasons.append("Menor preço em 180 dias")
    
    return min(1.0, score)
