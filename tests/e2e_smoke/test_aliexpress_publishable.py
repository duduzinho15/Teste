from src.core.affiliate_validator import AffiliateValidator


def test_aliexpress_publishable_valid():
    v = AffiliateValidator()
    url = "https://s.click.aliexpress.com/e/abc123?tracking_id=telegram"
    ok, reason = v.is_publishable_affiliate_url(url)
    assert ok, f"esperava válido, motivo: {reason}"


def test_aliexpress_publishable_missing_tracking():
    v = AffiliateValidator()
    url = "https://s.click.aliexpress.com/e/abc123"
    ok, reason = v.is_publishable_affiliate_url(url)
    assert not ok and "tracking_id=telegram" in reason.lower()

