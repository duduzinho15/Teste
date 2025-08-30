"""
Sistema de Gerenciamento de Postagem
Gerencia o processo completo de postagem de ofertas
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum

from ..core.models import Offer
from ..core.affiliate_validator import AffiliateValidator
from .message_formatter import message_formatter
from .scheduler import job_scheduler


class PostingStatus(Enum):
    """Status de uma postagem"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    POSTED = "posted"
    FAILED = "failed"


class PostingQuality(Enum):
    """Qualidade de uma postagem"""
    EXCELLENT = "excellent"
    GOOD = "good"
    AVERAGE = "average"
    POOR = "poor"
    REJECTED = "rejected"


@dataclass
class PostingRequest:
    """Requisição de postagem"""
    
    id: str
    offer: Offer
    status: PostingStatus = PostingStatus.PENDING
    quality_score: float = 0.0
    quality_level: PostingQuality = PostingQuality.AVERAGE
    created_at: datetime = None
    processed_at: Optional[datetime] = None
    posted_at: Optional[datetime] = None
    moderator_notes: Optional[str] = None
    auto_approved: bool = False
    flags: List[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.flags is None:
            self.flags = []
        if self.metadata is None:
            self.metadata = {}


class PostingManager:
    """Gerenciador de postagem de ofertas"""
    
    def __init__(self):
        self.logger = logging.getLogger("posting_manager")
        self.validator = AffiliateValidator()
        
        # Fila de postagem
        self.posting_queue: List[PostingRequest] = []
        self.posted_offers: List[PostingRequest] = []
        self.rejected_offers: List[PostingRequest] = []
        
        # Configurações
        self.auto_approval_threshold = 0.8  # Score mínimo para aprovação automática
        self.max_daily_posts = 50  # Máximo de postagens por dia
        self.quality_thresholds = {
            PostingQuality.EXCELLENT: 0.9,
            PostingQuality.GOOD: 0.7,
            PostingQuality.AVERAGE: 0.5,
            PostingQuality.POOR: 0.3
        }
        
        # Callbacks
        self.on_post_callback: Optional[Callable] = None
        self.on_reject_callback: Optional[Callable] = None
        
        # Estatísticas
        self.stats = {
            "total_requests": 0,
            "approved": 0,
            "rejected": 0,
            "posted": 0,
            "failed": 0,
            "auto_approved": 0,
            "manual_approved": 0
        }
    
    async def submit_offer(self, offer: Offer) -> str:
        """
        Submete uma oferta para postagem
        
        Args:
            offer: Oferta a ser postada
            
        Returns:
            ID da requisição de postagem
        """
        try:
            # Validar oferta
            validation_result = await self._validate_offer(offer)
            
            if not validation_result["is_valid"]:
                raise ValueError(f"Oferta inválida: {validation_result['errors']}")
            
            # Criar requisição de postagem
            request_id = f"post_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
            
            posting_request = PostingRequest(
                id=request_id,
                offer=offer,
                metadata={
                    "validation_score": validation_result["score"],
                    "validation_details": validation_result["details"]
                }
            )
            
            # Avaliar qualidade
            quality_result = await self._evaluate_quality(posting_request)
            posting_request.quality_score = quality_result["score"]
            posting_request.quality_level = quality_result["level"]
            
            # Verificar aprovação automática
            if posting_request.quality_score >= self.auto_approval_threshold:
                posting_request.auto_approved = True
                posting_request.status = PostingStatus.APPROVED
                self.stats["auto_approved"] += 1
                self.logger.info(f"Oferta aprovada automaticamente: {offer.title}")
            else:
                self.logger.info(f"Oferta requer moderação: {offer.title} (score: {posting_request.quality_score:.2f})")
            
            # Adicionar à fila
            self.posting_queue.append(posting_request)
            self.stats["total_requests"] += 1
            
            self.logger.info(f"Oferta submetida: {offer.title} (ID: {request_id})")
            return request_id
            
        except Exception as e:
            self.logger.error(f"Erro ao submeter oferta: {e}")
            raise
    
    async def _validate_offer(self, offer: Offer) -> Dict[str, Any]:
        """Valida uma oferta antes da postagem"""
        validation_result = {
            "is_valid": True,
            "score": 0.0,
            "errors": [],
            "warnings": [],
            "details": {}
        }
        
        try:
            # Validar campos obrigatórios
            if not offer.title or len(offer.title.strip()) < 5:
                validation_result["errors"].append("Título muito curto ou vazio")
                validation_result["is_valid"] = False
            
            if not offer.price or offer.price <= 0:
                validation_result["errors"].append("Preço inválido")
                validation_result["is_valid"] = False
            
            if not offer.url:
                validation_result["errors"].append("URL não fornecida")
                validation_result["is_valid"] = False
            
            # Validar URL de afiliado
            if offer.url:
                url_validation = self.validator.validate_url(offer.url)
                validation_result["details"]["url_validation"] = {
                    "status": url_validation.status.value,
                    "score": url_validation.score,
                    "message": url_validation.message
                }
                
                if url_validation.status.value == "invalid":
                    validation_result["errors"].append(f"URL inválida: {url_validation.message}")
                    validation_result["is_valid"] = False
            
            # Calcular score de validação
            if validation_result["is_valid"]:
                validation_result["score"] = 1.0
                if url_validation and hasattr(url_validation, 'score'):
                    validation_result["score"] = url_validation.score
            else:
                validation_result["score"] = 0.0
            
        except Exception as e:
            validation_result["errors"].append(f"Erro na validação: {str(e)}")
            validation_result["is_valid"] = False
            validation_result["score"] = 0.0
        
        return validation_result
    
    async def _evaluate_quality(self, posting_request: PostingRequest) -> Dict[str, Any]:
        """Avalia a qualidade de uma oferta para postagem"""
        quality_result = {
            "score": 0.0,
            "level": PostingQuality.AVERAGE,
            "factors": {},
            "recommendations": []
        }
        
        try:
            offer = posting_request.offer
            factors = {}
            
            # Avaliar título (0-25 pontos)
            title_score = self._evaluate_title(offer.title)
            factors["title"] = title_score
            quality_result["score"] += title_score * 0.25
            
            # Avaliar preço (0-25 pontos)
            price_score = self._evaluate_price(offer.price, getattr(offer, 'original_price', None))
            factors["price"] = price_score
            quality_result["score"] += price_score * 0.25
            
            # Avaliar desconto (0-20 pontos)
            discount_score = self._evaluate_discount(offer.price, getattr(offer, 'original_price', None))
            factors["discount"] = discount_score
            quality_result["score"] += discount_score * 0.20
            
            # Avaliar loja (0-15 pontos)
            store_score = self._evaluate_store(offer.store)
            factors["store"] = store_score
            quality_result["score"] += store_score * 0.15
            
            # Avaliar categoria (0-15 pontos)
            category_score = self._evaluate_category(offer.category)
            factors["category"] = category_score
            quality_result["score"] += category_score * 0.15
            
            quality_result["factors"] = factors
            
            # Determinar nível de qualidade
            if quality_result["score"] >= self.quality_thresholds[PostingQuality.EXCELLENT]:
                quality_result["level"] = PostingQuality.EXCELLENT
            elif quality_result["score"] >= self.quality_thresholds[PostingQuality.GOOD]:
                quality_result["level"] = PostingQuality.GOOD
            elif quality_result["score"] >= self.quality_thresholds[PostingQuality.AVERAGE]:
                quality_result["level"] = PostingQuality.AVERAGE
            elif quality_result["score"] >= self.quality_thresholds[PostingQuality.POOR]:
                quality_result["level"] = PostingQuality.POOR
            else:
                quality_result["level"] = PostingQuality.REJECTED
            
            # Gerar recomendações
            quality_result["recommendations"] = self._generate_quality_recommendations(factors)
            
        except Exception as e:
            self.logger.error(f"Erro na avaliação de qualidade: {e}")
            quality_result["score"] = 0.0
            quality_result["level"] = PostingQuality.REJECTED
        
        return quality_result
    
    def _evaluate_title(self, title: str) -> float:
        """Avalia qualidade do título"""
        if not title:
            return 0.0
        
        title = title.strip()
        score = 0.0
        
        # Comprimento
        if 10 <= len(title) <= 100:
            score += 0.4
        elif 5 <= len(title) < 10:
            score += 0.2
        
        # Palavras-chave
        keywords = ["smartphone", "notebook", "headphone", "monitor", "gaming", "wireless", "bluetooth"]
        if any(keyword.lower() in title.lower() for keyword in keywords):
            score += 0.3
        
        # Formatação
        if title[0].isupper() and not title.isupper():
            score += 0.3
        
        return min(score, 1.0)
    
    def _evaluate_price(self, price: float, original_price: Optional[float]) -> float:
        """Avalia qualidade do preço"""
        if not price or price <= 0:
            return 0.0
        
        score = 0.0
        
        # Faixa de preço
        if 50 <= price <= 5000:
            score += 0.5
        elif 10 <= price < 50 or 5000 < price <= 10000:
            score += 0.3
        else:
            score += 0.1
        
        # Comparação com preço original
        if original_price and original_price > price:
            score += 0.5
        
        return min(score, 1.0)
    
    def _evaluate_discount(self, price: float, original_price: Optional[float]) -> float:
        """Avalia qualidade do desconto"""
        if not original_price or original_price <= price:
            return 0.0
        
        discount_percentage = ((original_price - price) / original_price) * 100
        
        if discount_percentage >= 30:
            return 1.0
        elif discount_percentage >= 20:
            return 0.8
        elif discount_percentage >= 10:
            return 0.6
        elif discount_percentage >= 5:
            return 0.4
        else:
            return 0.2
    
    def _evaluate_store(self, store: str) -> float:
        """Avalia qualidade da loja"""
        if not store:
            return 0.0
        
        # Lojas conhecidas
        known_stores = ["amazon", "mercadolivre", "shopee", "magazine luiza", "aliexpress"]
        store_lower = store.lower()
        
        if any(known_store in store_lower for known_store in known_stores):
            return 1.0
        elif len(store) >= 3:
            return 0.5
        else:
            return 0.2
    
    def _evaluate_category(self, category: str) -> float:
        """Avalia qualidade da categoria"""
        if not category:
            return 0.0
        
        # Categorias válidas
        valid_categories = ["eletrônicos", "informática", "celulares", "computadores", "games", "casa"]
        category_lower = category.lower()
        
        if any(valid_cat in category_lower for valid_cat in valid_categories):
            return 1.0
        elif len(category) >= 3:
            return 0.5
        else:
            return 0.2
    
    def _generate_quality_recommendations(self, factors: Dict[str, float]) -> List[str]:
        """Gera recomendações baseadas nos fatores de qualidade"""
        recommendations = []
        
        if factors.get("title", 0) < 0.5:
            recommendations.append("Melhorar título - adicionar mais detalhes")
        
        if factors.get("price", 0) < 0.5:
            recommendations.append("Verificar preço - pode estar muito baixo ou alto")
        
        if factors.get("discount", 0) < 0.5:
            recommendations.append("Desconto baixo - considerar ofertas com maior desconto")
        
        if factors.get("store", 0) < 0.5:
            recommendations.append("Verificar credibilidade da loja")
        
        if factors.get("category", 0) < 0.5:
            recommendations.append("Categoria muito genérica - especificar melhor")
        
        return recommendations
    
    async def approve_offer(self, request_id: str, moderator_notes: Optional[str] = None) -> bool:
        """Aprova uma oferta para postagem"""
        try:
            request = self._find_request(request_id)
            if not request:
                return False
            
            request.status = PostingStatus.APPROVED
            request.processed_at = datetime.now()
            request.moderator_notes = moderator_notes
            request.auto_approved = False
            
            self.stats["approved"] += 1
            self.stats["manual_approved"] += 1
            
            self.logger.info(f"Oferta aprovada manualmente: {request.offer.title}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao aprovar oferta: {e}")
            return False
    
    async def reject_offer(self, request_id: str, reason: str) -> bool:
        """Rejeita uma oferta"""
        try:
            request = self._find_request(request_id)
            if not request:
                return False
            
            request.status = PostingStatus.REJECTED
            request.processed_at = datetime.now()
            request.moderator_notes = reason
            
            # Mover para lista de rejeitadas
            self.posting_queue.remove(request)
            self.rejected_offers.append(request)
            
            self.stats["rejected"] += 1
            
            # Executar callback se configurado
            if self.on_reject_callback:
                await self.on_reject_callback(request, reason)
            
            self.logger.info(f"Oferta rejeitada: {request.offer.title} - {reason}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao rejeitar oferta: {e}")
            return False
    
    async def post_approved_offers(self) -> int:
        """Posta todas as ofertas aprovadas"""
        try:
            approved_requests = [r for r in self.posting_queue if r.status == PostingStatus.APPROVED]
            
            if not approved_requests:
                self.logger.info("Nenhuma oferta aprovada para postar")
                return 0
            
            posted_count = 0
            
            for request in approved_requests:
                try:
                    # Formatar mensagem
                    message = message_formatter.format_offer_message(request.offer)
                    
                    # Validar mensagem
                    message_validation = message_formatter.validate_message(message)
                    
                    if not message_validation["is_valid"]:
                        self.logger.warning(f"Mensagem inválida para {request.offer.title}: {message_validation['errors']}")
                        continue
                    
                    # Simular postagem
                    await self._post_message(message, request.offer)
                    
                    # Atualizar status
                    request.status = PostingStatus.POSTED
                    request.posted_at = datetime.now()
                    
                    # Mover para lista de postadas
                    self.posting_queue.remove(request)
                    self.posted_offers.append(request)
                    
                    posted_count += 1
                    self.stats["posted"] += 1
                    
                    self.logger.info(f"Oferta postada: {request.offer.title}")
                    
                    # Executar callback se configurado
                    if self.on_post_callback:
                        await self.on_post_callback(request, message)
                    
                    # Aguardar entre postagens para evitar spam
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    self.logger.error(f"Erro ao postar oferta {request.offer.title}: {e}")
                    request.status = PostingStatus.FAILED
                    self.stats["failed"] += 1
            
            self.logger.info(f"Postagem concluída: {posted_count} ofertas postadas")
            return posted_count
            
        except Exception as e:
            self.logger.error(f"Erro na postagem em lote: {e}")
            return 0
    
    async def _post_message(self, message: str, offer: Offer):
        """Posta uma mensagem (simulado)"""
        # Simular postagem
        await asyncio.sleep(0.5)
        
        # Em produção, aqui seria feita a postagem real no Telegram
        self.logger.debug(f"📝 Mensagem postada:\n{message[:100]}...")
    
    def _find_request(self, request_id: str) -> Optional[PostingRequest]:
        """Encontra uma requisição pelo ID"""
        for request in self.posting_queue:
            if request.id == request_id:
                return request
        return None
    
    def get_queue_status(self) -> Dict[str, Any]:
        """Retorna status da fila de postagem"""
        return {
            "queue_size": len(self.posting_queue),
            "pending": len([r for r in self.posting_queue if r.status == PostingStatus.PENDING]),
            "approved": len([r for r in self.posting_queue if r.status == PostingStatus.APPROVED]),
            "posted_today": len([r for r in self.posted_offers if r.posted_at and r.posted_at.date() == datetime.now().date()]),
            "rejected_today": len([r for r in self.rejected_offers if r.processed_at and r.processed_at.date() == datetime.now().date()]),
            "max_daily_posts": self.max_daily_posts
        }
    
    def get_quality_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de qualidade"""
        quality_counts = {
            PostingQuality.EXCELLENT: 0,
            PostingQuality.GOOD: 0,
            PostingQuality.AVERAGE: 0,
            PostingQuality.POOR: 0,
            PostingQuality.REJECTED: 0
        }
        
        for request in self.posting_queue:
            quality_counts[request.quality_level] += 1
        
        return {
            "quality_distribution": {level.value: count for level, count in quality_counts.items()},
            "average_score": sum(r.quality_score for r in self.posting_queue) / len(self.posting_queue) if self.posting_queue else 0,
            "auto_approval_rate": self.stats["auto_approved"] / max(self.stats["total_requests"], 1)
        }
    
    def get_posting_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas gerais de postagem"""
        return {
            **self.stats,
            "queue_status": self.get_queue_status(),
            "quality_stats": self.get_quality_stats()
        }
    
    def set_post_callback(self, callback: Callable):
        """Define callback para quando uma oferta é postada"""
        self.on_post_callback = callback
    
    def set_reject_callback(self, callback: Callable):
        """Define callback para quando uma oferta é rejeitada"""
        self.on_reject_callback = callback


# Instância global para uso em outros módulos
posting_manager = PostingManager()
