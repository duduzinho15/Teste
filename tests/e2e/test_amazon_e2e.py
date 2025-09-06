"""
Testes E2E para validação completa do fluxo da Amazon.
Valida fluxo completo: URL → conversor → validador → PostingManager
"""

import pytest
import pytest_asyncio
from unittest.mock import patch, MagicMock
from pathlib import Path
import sys

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from core.affiliate_validator import AffiliateValidator
from core.affiliate_converter import AffiliateConverter
from core.posting_manager import PostingManager
from core.models import Offer

# URLs de teste
VALID_AMAZON_URL = "https://www.amazon.com.br/dp/B07YFF3JCN/?tag=garimpeirogee-20"
INVALID_AMAZON_URL = "https://www.amazon.com.br/dp/INVALID_ASIN"
MISSING_TAG_URL = "https://www.amazon.com.br/dp/B07YFF3JCN"

class TestAmazonE2E:
    """Testes E2E para o fluxo da Amazon."""
    
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self):
        """Setup para os testes."""
        self.validator = AffiliateValidator()
        self.converter = AffiliateConverter()
        self.posting_manager = PostingManager()
        
        # Mock do logger para evitar poluição nos logs durante os testes
        self.logger_patch = patch('core.affiliate_validator.logger')
        self.mock_logger = self.logger_patch.start()
        
        yield
        
        # Cleanup
        self.logger_patch.stop()
    
    @pytest.mark.asyncio
    async def test_valid_amazon_url_with_asin_and_tag(self):
        """Testa uma URL da Amazon válida com ASIN e tag corretos."""
        # Converter URL
        converted = await self.converter.convert(VALID_AMAZON_URL)
        
        # Validar URL convertida
        validation = await self.validator.validate(converted)
        
        # Verificar se é postável
        offer = Offer(
            url=converted,
            title="Produto de Teste",
            price=99.90,
            original_price=199.90,
            discount=50,
            store="Amazon"
        )
        
        can_post, reason = await self.posting_manager.can_post_offer(offer)
        
        assert can_post is True
        assert reason == ""
    
    @pytest.mark.asyncio
    async def test_amazon_url_without_tag(self):
        """Testa uma URL da Amazon sem tag de afiliado."""
        # Converter URL
        converted = await self.converter.convert(MISSING_TAG_URL)
        
        # Validar URL convertida
        validation = await self.validator.validate(converted)
        
        # Verificar se é postável
        offer = Offer(
            url=converted,
            title="Produto de Teste",
            price=99.90,
            original_price=199.90,
            discount=50,
            store="Amazon"
        )
        
        can_post, reason = await self.posting_manager.can_post_offer(offer)
        
        assert can_post is False
        assert "tag de afiliado ausente" in reason.lower()
    
    @pytest.mark.asyncio
    async def test_invalid_asin(self):
        """Testa uma URL da Amazon com ASIN inválido."""
        # Converter URL
        converted = await self.converter.convert(INVALID_AMAZON_URL)
        
        # Validar URL convertida
        validation = await self.validator.validate(converted)
        
        # Verificar se é postável
        offer = Offer(
            url=converted,
            title="Produto de Teste",
            price=99.90,
            original_price=199.90,
            discount=50,
            store="Amazon"
        )
        
        can_post, reason = await self.posting_manager.can_post_offer(offer)
        
        assert can_post is False
        assert "asin inválido" in reason.lower()

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
