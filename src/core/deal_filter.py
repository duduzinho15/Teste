"""Filtro de ofertas para identificar hot deals"""

from typing import Any, Dict, Optional

from src.core.models import Offer


def is_hot_deal(offer: Offer, price_history: Optional[Dict[str, Any]]) -> bool:
    """Verifica se uma oferta se qualifica como *hot deal*.

    Args:
        offer: Oferta a ser avaliada.
        price_history: Dicionário com informações de preço histórico. Deve
            conter opcionalmente a chave ``price_90d`` representando o preço de
            referência dos últimos 90 dias.

    Returns:
        ``True`` se a oferta atender a qualquer uma das regras de hot deal.
    """
    discount = offer.discount_percentage or 0
    if discount >= 30:
        return True

    price_90d = None
    if price_history:
        if isinstance(price_history, dict):
            price_90d = price_history.get("price_90d")
        else:
            price_90d = getattr(price_history, "price_90d", None)

    if price_90d is not None:
        try:
            if float(offer.price) <= 0.8 * float(price_90d):
                return True
        except (TypeError, ValueError):
            pass

    return False
