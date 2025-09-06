"""
Testes E2E para validação completa do fluxo do Mercado Livre.
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
VALID_ML_URL = "https://www.mercadolivre.com.br/sec/example"
SOCIAL_ML_URL = "https://www.mercadolivre.com.br/social/garimpeirogeek/123"
INVALID_ML_URL = "https://produto.mercadolivre.com.br/123"

class TestMercadoLivreE2E:
    """Testes E2E para o fluxo do Mercado Livre."""
    
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
    async def test_valid_ml_shortlink(self):
        """Testa um shortlink válido do Mercado Livre."""
        # Converter URL
        converted = await self.converter.convert(VALID_ML_URL)
        
        # Validar URL convertida
        validation = await self.validator.validate(converted)
        
        # Verificar se é postável
        offer = Offer(
            url=converted,
            title="Produto de Teste",
            price=99.90,
            original_price=199.90,
            discount=50,
            store="Mercado Livre"
        )
        
        can_post, reason = await self.posting_manager.can_post_offer(offer)
        
        assert can_post is True
        assert reason == ""
    
    @pytest.mark.asyncio
    async def test_valid_ml_social_url(self):
        """Testa uma URL social do Mercado Livre."""
        # Converter URL
        converted = await self.converter.convert(SOCIAL_ML_URL)
        
        # Validar URL convertida
        validation = await self.validator.validate(converted)
        
        # Verificar se é postável
        offer = Offer(
            url=converted,
            title="Produto de Teste",
            price=99.90,
            original_price=199.90,
            discount=50,
            store="Mercado Livre"
        )
        
        can_post, reason = await self.posting_manager.can_post_offer(offer)
        
        assert can_post is True
        assert reason == ""
    
    @pytest.mark.asyncio
    async def test_invalid_ml_url(self):
        """Testa uma URL de produto direto do Mercado Livre."""
        # Converter URL
        converted = await self.converter.convert(INVALID_ML_URL)
        
        # Validar URL convertida
        validation = await self.validator.validate(converted)
        
        # Verificar se é postável
        offer = Offer(
            url=converted,
            title="Produto de Teste",
            price=99.90,
            original_price=199.90,
            discount=50,
            store="Mercado Livre"
        )
        
        can_post, reason = await self.posting_manager.can_post_offer(offer)
        
        assert can_post is False
        assert "url de produto direto não é permitida" in reason.lower()

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
