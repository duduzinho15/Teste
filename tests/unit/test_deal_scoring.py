import pytest
from decimal import Decimal
from unittest.mock import patch, MagicMock

from src.app.queue.deal_scoring import (
    compute_deal_score, DealScore, DealScoreLevel, PriceStats, DealPolicy
)

# Test fixtures
@pytest.fixture
def mock_settings():
    with patch('src.app.queue.deal_scoring.settings') as mock_settings:
        mock_settings.DEAL_SCORE_CRITICAL = 0.85
        mock_settings.DEAL_SCORE_HIGH = 0.75
        mock_settings.ELECTRONICS_MIN_DISC = 0.20
        mock_settings.PERIPHERALS_MIN_DISC = 0.25
        mock_settings.APPLIANCES_MIN_DISC = 0.18
        mock_settings.TRUSTED_SELLERS = "Magazine Luiza,Kabum,Pichau"
        yield mock_settings

@pytest.fixture
def default_policy():
    return DealPolicy(
        min_discount_pct={
            'electronics': 0.20,
            'peripherals': 0.25,
            'appliances': 0.18,
        },
        trusted_sellers={"magazine luiza", "kabum", "pichau"},
        low_40d_bonus=0.2,
        low_90d_bonus=0.25,
        low_180d_bonus=0.35
    )

def test_compute_deal_score_electronics_critical(mock_settings, default_policy):
    """Test critical electronics deal (lowest price in 180 days + good discount)."""
    offer = {
        'id': 'test1',
        'name': 'Smartphone XYZ',
        'category': 'electronics/smartphones',
        'price': 2000.00,
        'list_price': 3000.00,  # 33% discount
        'seller': 'Magazine Luiza',
        'platform': 'magazineluiza'
    }
    
    price_stats = PriceStats(
        mean_90d=Decimal('2800.00'),
        p25_90d=Decimal('2600.00'),
        low_40d=Decimal('2100.00'),
        low_180d=Decimal('2050.00')
    )
    
    result = compute_deal_score(offer, price_stats, default_policy)
    
    assert result.score >= 0.85
    assert result.level == DealScoreLevel.CRITICAL
    assert "Menor preço em 180 dias" in result.reasons
    assert "Vendedor confiável" in result.reasons[0]
    assert "33% abaixo da média" in "".join(result.reasons)

def test_compute_deal_score_peripherals_high(mock_settings, default_policy):
    """Test high score peripherals deal (good discount but not historical low)."""
    offer = {
        'id': 'test2',
        'name': 'Headphone Gamer',
        'category': 'peripherals/headphones',
        'price': 350.00,
        'list_price': 500.00,  # 30% discount
        'seller': 'Kabum',
        'platform': 'kabum'
    }
    
    price_stats = PriceStats(
        mean_90d=Decimal('450.00'),
        low_40d=Decimal('340.00'),
        low_90d=Decimal('330.00')
    )
    
    result = compute_deal_score(offer, price_stats, default_policy)
    
    assert 0.75 <= result.score < 0.85
    assert result.level == DealScoreLevel.HIGH
    assert "30%" in "".join(result.reasons)
    assert "Vendedor confiável" in result.reasons[0]

def test_compute_deal_score_appliances_medium(mock_settings, default_policy):
    """Test medium score appliances deal (meets minimum discount only)."""
    offer = {
        'id': 'test3',
        'name': 'Geladeira Frost Free',
        'category': 'appliances/refrigerators',
        'price': 2800.00,
        'list_price': 3200.00,  # 12.5% discount
        'seller': 'Loja Genérica',
        'platform': 'generic'
    }
    
    price_stats = PriceStats(
        mean_90d=Decimal('3100.00'),
        low_180d=Decimal('2700.00')
    )
    
    result = compute_deal_score(offer, price_stats, default_policy)
    
    assert 0.5 <= result.score < 0.75
    assert result.level == DealScoreLevel.MEDIUM
    assert "12%" in "".join(result.reasons) or "13%" in "".join(result.reasons)

def test_compute_deal_score_default_category(mock_settings, default_policy):
    """Test scoring for uncategorized items."""
    offer = {
        'id': 'test4',
        'name': 'Produto Genérico',
        'category': 'other/uncategorized',
        'price': 100.00,
        'list_price': 200.00,  # 50% discount
        'seller': 'Loja Genérica',
        'platform': 'generic'
    }
    
    result = compute_deal_score(offer, PriceStats(), default_policy)
    
    assert result.score >= 0.5
    assert result.level in [DealScoreLevel.HIGH, DealScoreLevel.MEDIUM]
    assert "50%" in "".join(result.reasons)

def test_deal_score_levels(mock_settings):
    """Test score level thresholds."""
    assert DealScore(score=0.9).level == DealScoreLevel.CRITICAL
    assert DealScore(score=0.8).level == DealScoreLevel.HIGH
    assert DealScore(score=0.6).level == DealScoreLevel.MEDIUM
    assert DealScore(score=0.3).level == DealScoreLevel.LOW
    
    # Test clamping
    assert DealScore(score=-1.0).score == 0.0
    assert DealScore(score=1.5).score == 1.0

def test_price_stats_handling(mock_settings, default_policy):
    """Test handling of missing price stats."""
    offer = {
        'id': 'test5',
        'name': 'Produto sem histórico',
        'category': 'electronics/other',
        'price': 100.00,
        'list_price': 200.00,  # 50% discount
        'seller': 'Kabum',
        'platform': 'kabum'
    }
    
    # No price stats at all
    result1 = compute_deal_score(offer, PriceStats(), default_policy)
    assert result1.score > 0  # Should still score based on discount and seller
    
    # Partial price stats
    price_stats = PriceStats(mean_90d=Decimal('180.00'))
    result2 = compute_deal_score(offer, price_stats, default_policy)
    assert result2.score > result1.score  # Should score higher with some history
