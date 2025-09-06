"""
Testes de deduplicação de ofertas.
"""

import pytest
import asyncio
from core.posting_manager import PostingManager
from core.models import Offer

class TestDeduplication:
    """Testes de deduplicação."""
    
    @pytest.mark.asyncio
    async def test_duplicate_offer_detection(self):
        """Testa a detecção de ofertas duplicadas."""
        posting_manager = PostingManager()
        
        # Primeira oferta
        offer1 = Offer(
            url="https://www.amazon.com.br/dp/B07YFF3JCN/?tag=garimpeirogee-20",
            title="Produto de Teste",
            price=99.90,
            store="Amazon"
        )
        
        # Oferta idêntica
        offer2 = Offer(
            url="https://www.amazon.com.br/dp/B07YFF3JCN/?tag=garimpeirogee-20",
            title="Produto de Teste",
            price=99.90,
            store="Amazon"
        )
        
        # Primeira oferta deve ser postada
        can_post1, _ = await posting_manager.can_post_offer(offer1)
        assert can_post1 is True
        
        # Segunda oferta idêntica não deve ser postada
        can_post2, reason = await posting_manager.can_post_offer(offer2)
        assert can_post2 is False
        assert "já foi publicada" in reason.lower()
    
    @pytest.mark.asyncio
    async def test_similar_offer_detection(self):
        """Testa a detecção de ofertas similares."""
        posting_manager = PostingManager()
        
        # Primeira oferta
        offer1 = Offer(
            url="https://www.amazon.com.br/dp/B07YFF3JCN/?tag=garimpeirogee-20",
            title="Produto de Teste",
            price=99.90,
            store="Amazon"
        )
        
        # Oferta similar (mesmo produto, preço diferente)
        offer2 = Offer(
            url="https://www.amazon.com.br/dp/B07YFF3JCN/?tag=garimpeirogee-20",
            title="Produto de Teste",
            price=89.90,  # Preço diferente
            store="Amazon"
        )
        
        # Primeira oferta deve ser postada
        can_post1, _ = await posting_manager.can_post_offer(offer1)
        assert can_post1 is True
        
        # Segunda oferta similar não deve ser bloqueada
        can_post2, _ = await posting_manager.can_post_offer(offer2)
        assert can_post2 is True

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
