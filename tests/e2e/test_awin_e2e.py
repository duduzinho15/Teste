"""
Testes E2E para validação completa do fluxo da Awin.
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
VALID_AWIN_URL = "https://www.awin1.com/cread.php?awinmid=23377&awinaffid=2370719&ued=https://www.lojadoimportador.com.br"
INVALID_MID_URL = "https://www.awin1.com/cread.php?awinmid=99999&awinaffid=2370719&ued=https://www.lojadoimportador.com.br"
INVALID_AFFID_URL = "https://www.awin1.com/cread.php?awinmid=23377&awinaffid=9999999&ued=https://www.lojadoimportador.com.br"
MISSING_PARAMS_URL = "https://www.awin1.com/cread.php?awinmid=23377"

class TestAwinE2E:
    """Testes E2E para o fluxo da Awin."""
    
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
    async def test_valid_awin_url(self):
        """Testa uma URL da Awin válida com MID e AFFID corretos."""
        # Converter URL
        converted = await self.converter.convert(VALID_AWIN_URL)
        
        # Validar URL convertida
        validation = await self.validator.validate(converted)
        
        # Verificar se é postável
        offer = Offer(
            url=converted,
            title="Produto de Teste",
            price=99.90,
            original_price=199.90,
            discount=50,
            store="Loja do Importador"
        )
        
        can_post, reason = await self.posting_manager.can_post_offer(offer)
        
        assert can_post is True
        assert reason == ""
    
    @pytest.mark.asyncio
    async def test_awin_url_with_invalid_mid(self):
        """Testa uma URL da Awin com MID inválido."""
        # Converter URL
        converted = await self.converter.convert(INVALID_MID_URL)
        
        # Validar URL convertida
        validation = await self.validator.validate(converted)
        
        # Verificar se é postável
        offer = Offer(
            url=converted,
            title="Produto de Teste",
            price=99.90,
            original_price=199.90,
            discount=50,
            store="Loja do Importador"
        )
        
        can_post, reason = await self.posting_manager.can_post_offer(offer)
        
        assert can_post is False
        assert "mid inválido" in reason.lower()
    
    @pytest.mark.asyncio
    async def test_awin_url_with_invalid_affid(self):
        """Testa uma URL da Awin com AFFID inválido."""
        # Converter URL
        converted = await self.converter.convert(INVALID_AFFID_URL)
        
        # Validar URL convertida
        validation = await self.validator.validate(converted)
        
        # Verificar se é postável
        offer = Offer(
            url=converted,
            title="Produto de Teste",
            price=99.90,
            original_price=199.90,
            discount=50,
            store="Loja do Importador"
        )
        
        can_post, reason = await self.posting_manager.can_post_offer(offer)
        
        assert can_post is False
        assert "affid inválido" in reason.lower()
    
    @pytest.mark.asyncio
    async def test_awin_url_missing_params(self):
        """Testa uma URL da Awin com parâmetros ausentes."""
        # Converter URL
        converted = await self.converter.convert(MISSING_PARAMS_URL)
        
        # Validar URL convertida
        validation = await self.validator.validate(converted)
        
        # Verificar se é postável
        offer = Offer(
            url=converted,
            title="Produto de Teste",
            price=99.90,
            original_price=199.90,
            discount=50,
            store="Loja do Importador"
        )
        
        can_post, reason = await self.posting_manager.can_post_offer(offer)
        
        assert can_post is False
        assert "parâmetros obrigatórios ausentes" in reason.lower()

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
