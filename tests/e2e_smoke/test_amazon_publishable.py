from src.core.affiliate_validator import AffiliateValidator


def test_amazon_publishable_valid_asin():
    v = AffiliateValidator()
    url = "https://www.amazon.com.br/dp/B08N5WRWNW"
    ok, reason = v.is_publishable_affiliate_url(url)
    assert ok, f"esperava válido, motivo: {reason}"


def test_amazon_publishable_invalid_asin():
    v = AffiliateValidator()
    url = "https://www.amazon.com.br/dp/INVALID"
    ok, reason = v.is_publishable_affiliate_url(url)
    assert not ok and "asin" in reason.lower()

