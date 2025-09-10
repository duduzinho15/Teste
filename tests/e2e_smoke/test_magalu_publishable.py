from src.core.affiliate_validator import AffiliateValidator


def test_magalu_publishable_valid_vitrine():
    v = AffiliateValidator()
    url = (
        "https://www.magazinevoce.com.br/magazinegarimpeirogeek/iphone-14/p/237184100/te/ip14/"
    )
    ok, reason = v.is_publishable_affiliate_url(url)
    assert ok, f"esperava válido, motivo: {reason}"


def test_magalu_publishable_invalid_domain():
    v = AffiliateValidator()
    url = "https://www.magazineluiza.com.br/produto/237184100"
    ok, reason = v.is_publishable_affiliate_url(url)
    assert not ok and "magazinevoce" in reason.lower()

