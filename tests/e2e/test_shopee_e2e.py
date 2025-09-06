"""
Testes E2E para validação completa do fluxo da Shopee.
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
VALID_SHOPEE_URL = "https://s.shopee.com.br/example-product"
INVALID_SHOPEE_URL = "https://shopee.com.br/example-product"  # Não é shortlink
COLLECTION_URL = "https://s.shopee.com.br/collection/123"
STORE_URL = "https://s.shopee.com.br/store/123"

class TestShopeeE2E:
    """Testes E2E para o fluxo da Shopee."""
    
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
    async def test_valid_shopee_shortlink(self):
        """Testa um shortlink válido da Shopee."""
        # Converter URL
        converted = await self.converter.convert(VALID_SHOPEE_URL)
        
        # Validar URL convertida
        validation = await self.validator.validate(converted)
        
        # Verificar se é postável
        offer = Offer(
            url=converted,
            title="Produto de Teste",
            price=99.90,
            original_price=199.90,
            discount=50,
            store="Shopee"
        )
        
        can_post, reason = await self.posting_manager.can_post_offer(offer)
        
        assert can_post is True
        assert reason == ""
    
    @pytest.mark.asyncio
    async def test_invalid_shopee_url(self):
        """Testa uma URL da Shopee que não é shortlink."""
        # Converter URL
        converted = await self.converter.convert(INVALID_SHOPEE_URL)
        
        # Validar URL convertida
        validation = await self.validator.validate(converted)
        
        # Verificar se é postável
        offer = Offer(
            url=converted,
            title="Produto de Teste",
            price=99.90,
            original_price=199.90,
            discount=50,
            store="Shopee"
        )
        
        can_post, reason = await self.posting_manager.can_post_offer(offer)
        
        assert can_post is False
        assert "não é um shortlink válido" in reason.lower()
    
    @pytest.mark.asyncio
    async def test_shopee_collection_url(self):
        """Testa uma URL de coleção da Shopee."""
        # Converter URL
        converted = await self.converter.convert(COLLECTION_URL)
        
        # Validar URL convertida
        validation = await self.validator.validate(converted)
        
        # Verificar se é postável
        offer = Offer(
            url=converted,
            title="Coleção de Teste",
            price=0,  # Coleções não têm preço
            store="Shopee"
        )
        
        can_post, reason = await self.posting_manager.can_post_offer(offer)
        
        assert can_post is False
        assert "coleção não é permitida" in reason.lower()
    
    @pytest.mark.asyncio
    async def test_shopee_store_url(self):
        """Testa uma URL de loja da Shopee."""
        # Converter URL
        converted = await self.converter.convert(STORE_URL)
        
        # Validar URL convertida
        validation = await self.validator.validate(converted)
        
        # Verificar se é postável
        offer = Offer(
            url=converted,
            title="Loja de Teste",
            price=0,  # Lojas não têm preço
            store="Shopee"
        )
        
        can_post, reason = await self.posting_manager.can_post_offer(offer)
        
        assert can_post is False
        assert "loja não é permitida" in reason.lower()

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
