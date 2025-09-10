from src.core.affiliate_validator import AffiliateValidator


def test_shopee_publishable_valid():
    v = AffiliateValidator()
    url = "https://s.shopee.com.br/AbC123"
    ok, reason = v.is_publishable_affiliate_url(url)
    assert ok, f"esperava válido, motivo: {reason}"


def test_shopee_publishable_invalid_product_url():
    v = AffiliateValidator()
    url = "https://shopee.com.br/product/123/456"
    ok, reason = v.is_publishable_affiliate_url(url)
    assert not ok and "shortlinks" in reason.lower()

