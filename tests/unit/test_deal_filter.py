from decimal import Decimal
from src.core.models import Offer
from src.core.deal_filter import is_hot_deal


def make_offer(price: float, discount: float = 0.0) -> Offer:
    return Offer(
        title="Produto Teste",
        price=Decimal(str(price)),
        url="https://example.com/produto",
        store="loja",
        original_price=Decimal(str(price)) / (Decimal('1') - Decimal(discount) / Decimal('100')) if discount else None,
        discount_percentage=discount,
    )


def test_is_hot_deal_discount_boundary():
    offer = make_offer(100, discount=30)
    assert is_hot_deal(offer, {})


def test_is_hot_deal_price_history_boundary():
    offer = make_offer(80, discount=10)
    price_history = {"price_90d": Decimal("100")}
    assert is_hot_deal(offer, price_history)


def test_is_not_hot_deal_when_below_thresholds():
    offer = make_offer(81, discount=29)
    price_history = {"price_90d": Decimal("100")}
    assert not is_hot_deal(offer, price_history)
