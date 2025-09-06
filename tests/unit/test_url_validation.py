"""Testes de validação de URLs."""

import pytest
from core.affiliate_validator import AffiliateValidator

@pytest.mark.asyncio
async def test_amazon_validation():
    """Testa validação da Amazon."""
    val = AffiliateValidator()
    valid = "https://www.amazon.com.br/dp/B07YFF3JCN/?tag=garimpeirogee-20"
    invalid = "https://www.amazon.com.br/dp/B07YFF3JCN/"
    assert (await val.validate(valid))[0] is True
    assert (await val.validate(invalid))[0] is False

@pytest.mark.asyncio
async def test_awin_validation():
    """Testa validação da Awin."""
    val = AffiliateValidator()
    valid = "https://www.awin1.com/cread.php?awinmid=23377&awinaffid=2370719"
    invalid = "https://www.awin1.com/cread.php?awinmid=99999&awinaffid=2370719"
    assert (await val.validate(valid))[0] is True
    assert (await val.validate(invalid))[0] is False
