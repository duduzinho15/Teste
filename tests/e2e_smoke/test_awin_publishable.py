from src.core.affiliate_validator import AffiliateValidator


def test_awin_publishable_valid():
    v = AffiliateValidator()
    url = (
        "https://www.awin1.com/cread.php?awinmid=23377&awinaffid=2370719"
        "&ued=https%3A%2F%2Fwww.comfy.com.br%2Fcadeira%2Fp%2F123"
    )
    ok, reason = v.is_publishable_affiliate_url(url)
    assert ok, f"esperava válido, motivo: {reason}"


def test_awin_publishable_missing_param():
    v = AffiliateValidator()
    url = (
        "https://www.awin1.com/cread.php?awinmid=23377"
        "&ued=https%3A%2F%2Fwww.comfy.com.br%2Fcadeira%2Fp%2F123"
    )
    ok, reason = v.is_publishable_affiliate_url(url)
    assert not ok and "obrigatório" in reason.lower()

