from src.core.affiliate_validator import AffiliateValidator


def test_ml_publishable_sec():
    v = AffiliateValidator()
    url = "https://www.mercadolivre.com.br/sec/abc123"
    ok, reason = v.is_publishable_affiliate_url(url)
    assert ok, f"esperava válido, motivo: {reason}"


def test_ml_publishable_social_with_matt_word():
    v = AffiliateValidator()
    url = "https://www.mercadolivre.com.br/social/garimpeirogeek?matt_word=garimpeirogeek"
    ok, reason = v.is_publishable_affiliate_url(url)
    assert ok, f"esperava válido, motivo: {reason}"


def test_ml_publishable_invalid_product():
    v = AffiliateValidator()
    url = "https://produto.mercadolivre.com.br/MLB-123456"
    ok, reason = v.is_publishable_affiliate_url(url)
    assert not ok and "somente" in reason.lower()

