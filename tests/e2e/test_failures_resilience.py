"""
Testes de falha e resiliência para o sistema de afiliados.
"""

import pytest
import asyncio
from unittest.mock import patch, AsyncMock
from core.posting_manager import PostingManager
from core.models import Offer

class TestFailuresAndResilience:
    """Testes de falha e resiliência."""
    
    @pytest.mark.asyncio
    async def test_api_timeout_handling(self):
        """Testa o tratamento de timeout da API."""
        # Mock para simular timeout
        async def mock_validate_timeout(*args, **kwargs):
            await asyncio.sleep(2)  # Simula atraso
            return True, ""
            
        with patch('core.affiliate_validator.AffiliateValidator.validate', 
                 new=mock_validate_timeout):
            offer = Offer(
                url="https://www.amazon.com.br/dp/B07YFF3JCN/?tag=garimpeirogee-20",
                title="Teste",
                price=99.90,
                store="Amazon"
            )
            
            with patch('core.posting_manager.VALIDATION_TIMEOUT', 0.1):
                can_post, reason = await PostingManager().can_post_offer(offer)
                assert can_post is False
                assert "timeout" in reason.lower()
    
    @pytest.mark.asyncio
    async def test_rate_limit_handling(self):
        """Testa o tratamento de rate limiting."""
        # Mock para simular rate limit
        async def mock_validate_rate_limit(*args, **kwargs):
            return False, "rate limit exceeded"
            
        with patch('core.affiliate_validator.AffiliateValidator.validate', 
                 new=mock_validate_rate_limit):
            offer = Offer(
                url="https://s.click.aliexpress.com/e/_example?tracking_id=telegram",
                title="Teste",
                price=50.00,
                store="AliExpress"
            )
            
            can_post, reason = await PostingManager().can_post_offer(offer)
            assert can_post is False
            assert "rate limit" in reason.lower()
    
    @pytest.mark.asyncio
    async def test_invalid_response_handling(self):
        """Testa tratamento de respostas inválidas."""
        # Mock para simular resposta inválida
        async def mock_validate_invalid(*args, **kwargs):
            return False, "invalid response format"
            
        with patch('core.affiliate_validator.AffiliateValidator.validate', 
                 new=mock_validate_invalid):
            offer = Offer(
                url="https://www.mercadolivre.com.br/sec/example",
                title="Teste",
                price=150.00,
                store="Mercado Livre"
            )
            
            can_post, reason = await PostingManager().can_post_offer(offer)
            assert can_post is False
            assert "inválido" in reason.lower()

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
