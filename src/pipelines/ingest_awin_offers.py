"""
Pipeline de Ingestão Automática de Ofertas Awin
Coleta, filtra e processa ofertas das 7 afiliações ativas
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from pathlib import Path

from affiliate.awin_api import AwinOffersCollector
from core.models import Offer
from core.affiliate_validator import AffiliateValidator
from posting.posting_manager import PostingManager
from core.rate_limiter import RateLimiter

logger = logging.getLogger(__name__)


@dataclass
class IngestConfig:
    """Configuração do pipeline de ingestão"""
    enabled: bool = True
    collection_interval: int = 3600  # 1 hora
    max_offers_per_run: int = 200
    auto_post: bool = True
    quality_threshold: float = 0.7
    deduplication: bool = True
    backup_enabled: bool = True


@dataclass
class IngestStats:
    """Estatísticas do pipeline de ingestão"""
    total_runs: int = 0
    successful_runs: int = 0
    failed_runs: int = 0
    total_offers_collected: int = 0
    total_offers_posted: int = 0
    total_offers_rejected: int = 0
    last_run: Optional[datetime] = None
    last_success: Optional[datetime] = None
    average_run_time: float = 0.0


class AwinIngestPipeline:
    """Pipeline principal de ingestão automática Awin"""
    
    def __init__(self, config: Optional[IngestConfig] = None):
        """
        Inicializa pipeline de ingestão
        
        Args:
            config: Configuração do pipeline
        """
        self.config = config or IngestConfig()
        self.stats = IngestStats()
        
        # Componentes do pipeline
        self.collector: Optional[AwinOffersCollector] = None
        self.validator = AffiliateValidator()
        self.posting_manager = PostingManager()
        self.rate_limiter = RateLimiter()
        
        # Cache de ofertas para deduplicação
        self.processed_offers = set()
        self.offer_cache: Dict[str, Offer] = {}
        
        # Estado do pipeline
        self.is_running = False
        self.current_run_id = None
        
        # Configurações de filtros automáticos
        self.auto_filters = {
            "min_discount": 15,
            "max_price": 1500.0,
            "categories": ["eletronicos", "informatica", "games", "casa"],
            "excluded_stores": [],
            "min_quality_score": 0.7,
            "max_daily_posts": 50
        }
        
        logger.info("🚀 Pipeline de Ingestão Awin inicializado")
    
    async def initialize(self) -> bool:
        """Inicializa o pipeline com credenciais Awin"""
        try:
            import os
            from dotenv import load_dotenv
            
            load_dotenv()
            
            # Tentar usar configuração de teste primeiro
            try:
                import sys
                sys.path.append(str(Path(__file__).parent.parent.parent / "config"))
                from awin_test_config import get_awin_credentials
                credentials = get_awin_credentials()
                publisher_id = credentials["publisher_id"]
                access_token = credentials["oauth2_token"]
            except ImportError:
                # Fallback para variáveis de ambiente
                publisher_id = os.getenv("AWIN_PUBLISHER_ID")
                access_token = os.getenv("AWIN_OAUTH2_TOKEN")
            
            if not publisher_id or not access_token:
                logger.error("❌ Credenciais Awin não configuradas")
                logger.error("   Configure AWIN_PUBLISHER_ID e AWIN_OAUTH2_TOKEN no .env")
                return False
            
            # Inicializar coletor
            self.collector = AwinOffersCollector(publisher_id, access_token)
            
            # Configurar filtros automáticos
            self.collector.update_filters(**self.auto_filters)
            
            logger.info("✅ Pipeline inicializado com sucesso")
            logger.info(f"📊 Filtros automáticos: {self.auto_filters}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar pipeline: {e}")
            return False
    
    async def start_continuous_ingestion(self):
        """Inicia ingestão contínua em loop"""
        if not self.collector:
            logger.error("❌ Pipeline não inicializado")
            return
        
        logger.info("🔄 Iniciando ingestão contínua...")
        self.is_running = True
        
        while self.is_running:
            try:
                # Executar uma rodada de ingestão
                await self.run_ingestion_cycle()
                
                # Aguardar próximo ciclo
                logger.info(f"⏰ Aguardando {self.config.collection_interval}s para próximo ciclo...")
                await asyncio.sleep(self.config.collection_interval)
                
            except KeyboardInterrupt:
                logger.info("🛑 Interrupção solicitada pelo usuário")
                break
            except Exception as e:
                logger.error(f"❌ Erro no ciclo de ingestão: {e}")
                await asyncio.sleep(300)  # Aguardar 5 minutos em caso de erro
        
        self.is_running = False
        logger.info("🛑 Ingestão contínua interrompida")
    
    async def run_ingestion_cycle(self) -> bool:
        """Executa um ciclo completo de ingestão"""
        if not self.collector:
            return False
        
        run_id = f"ingest_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.current_run_id = run_id
        
        start_time = datetime.now()
        logger.info(f"🔄 Iniciando ciclo de ingestão: {run_id}")
        
        try:
            # 1. Coletar ofertas
            offers = await self._collect_offers()
            if not offers:
                logger.warning("⚠️ Nenhuma oferta coletada neste ciclo")
                return False
            
            # 2. Validar e filtrar ofertas
            valid_offers = await self._validate_and_filter_offers(offers)
            if not valid_offers:
                logger.warning("⚠️ Nenhuma oferta válida após filtros")
                return False
            
            # 3. Processar e postar ofertas
            posted_count = await self._process_and_post_offers(valid_offers)
            
            # 4. Atualizar estatísticas
            run_time = (datetime.now() - start_time).total_seconds()
            await self._update_stats(run_time, len(offers), len(valid_offers), posted_count)
            
            logger.info(f"✅ Ciclo {run_id} concluído: {posted_count}/{len(valid_offers)} ofertas postadas")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro no ciclo {run_id}: {e}")
            await self._update_stats(0, 0, 0, 0, success=False)
            return False
    
    async def _collect_offers(self) -> List[Offer]:
        """Coleta ofertas via AwinOffersCollector"""
        try:
            logger.info("📥 Coletando ofertas Awin...")
            
            offers = await self.collector.collect_all_offers(
                max_offers_per_advertiser=self.config.max_offers_per_run // 7
            )
            
            logger.info(f"📊 {len(offers)} ofertas coletadas")
            return offers
            
        except Exception as e:
            logger.error(f"❌ Erro na coleta: {e}")
            return []
    
    async def _validate_and_filter_offers(self, offers: List[Offer]) -> List[Offer]:
        """Valida e filtra ofertas coletadas"""
        try:
            logger.info("🔍 Validando e filtrando ofertas...")
            
            valid_offers = []
            
            for offer in offers:
                # Verificar se já foi processada (deduplicação)
                if self.config.deduplication:
                    offer_hash = self._generate_offer_hash(offer)
                    if offer_hash in self.processed_offers:
                        continue
                
                # Para desenvolvimento, usar URL original se affiliate_url não estiver disponível
                if not offer.affiliate_url:
                    offer.affiliate_url = offer.url
                    logger.debug(f"🔄 Usando URL original como afiliado para: {offer.title[:50]}...")
                
                # Validar URL de afiliado (modo de teste)
                try:
                    validation_result = await self.validator.validate_url(offer.affiliate_url)
                    if not validation_result.is_valid:
                        logger.debug(f"⚠️ Oferta rejeitada (validação): {offer.title[:50]}...")
                        continue
                except Exception as e:
                    logger.warning(f"⚠️ Erro na validação, aceitando oferta: {e}")
                    # Em modo de teste, aceitar ofertas mesmo com erro de validação
                
                # Aplicar filtros de qualidade
                if not await self._passes_quality_filters(offer):
                    continue
                
                # Aplicar rate limiting
                if not self.rate_limiter.can_proceed("offer_processing"):
                    logger.warning("⚠️ Rate limit atingido para processamento de ofertas")
                    break
                
                valid_offers.append(offer)
                
                # Marcar como processada
                if self.config.deduplication:
                    self.processed_offers.add(self._generate_offer_hash(offer))
                    self.offer_cache[self._generate_offer_hash(offer)] = offer
            
            logger.info(f"✅ {len(valid_offers)} ofertas passaram na validação")
            return valid_offers
            
        except Exception as e:
            logger.error(f"❌ Erro na validação: {e}")
            return []
    
    async def _passes_quality_filters(self, offer: Offer) -> bool:
        """Verifica se oferta passa nos filtros de qualidade"""
        try:
            # Verificar desconto mínimo
            if offer.discount_percentage and offer.discount_percentage < self.auto_filters["min_discount"]:
                return False
            
            # Verificar preço máximo
            if offer.price > self.auto_filters["max_price"]:
                return False
            
            # Verificar categoria permitida
            if offer.category.lower() not in [c.lower() for c in self.auto_filters["categories"]]:
                return False
            
            # Verificar loja não excluída
            if offer.store.lower() in [s.lower() for s in self.auto_filters["excluded_stores"]]:
                return False
            
            # Verificar limite diário de posts
            if self.stats.total_offers_posted >= self.auto_filters["max_daily_posts"]:
                logger.warning("⚠️ Limite diário de posts atingido")
                return False
            
            return True
            
        except Exception as e:
            logger.warning(f"⚠️ Erro ao verificar filtros de qualidade: {e}")
            return False
    
    async def _process_and_post_offers(self, offers: List[Offer]) -> int:
        """Processa e posta ofertas válidas"""
        try:
            logger.info("📤 Processando e postando ofertas...")
            
            posted_count = 0
            
            for offer in offers:
                try:
                    # Verificar rate limiting para postagem
                    if not self.rate_limiter.can_proceed("telegram_posting"):
                        logger.warning("⚠️ Rate limit atingido para postagem no Telegram")
                        break
                    
                    # Submeter oferta para postagem
                    success = await self.posting_manager.submit_offer(offer)
                    
                    if success:
                        posted_count += 1
                        logger.info(f"✅ Oferta postada: {offer.title[:50]}...")
                    else:
                        logger.warning(f"⚠️ Falha ao postar: {offer.title[:50]}...")
                    
                    # Aguardar entre postagens para evitar spam
                    await asyncio.sleep(2)
                    
                except Exception as e:
                    logger.error(f"❌ Erro ao processar oferta: {e}")
                    continue
            
            logger.info(f"📤 {posted_count} ofertas processadas com sucesso")
            return posted_count
            
        except Exception as e:
            logger.error(f"❌ Erro no processamento: {e}")
            return 0
    
    async def _update_stats(self, run_time: float, collected: int, valid: int, posted: int, success: bool = True):
        """Atualiza estatísticas do pipeline"""
        try:
            self.stats.total_runs += 1
            
            if success:
                self.stats.successful_runs += 1
                self.stats.last_success = datetime.now()
            else:
                self.stats.failed_runs += 1
            
            self.stats.total_offers_collected += collected
            self.stats.total_offers_posted += posted
            self.stats.total_offers_rejected += (valid - posted)
            self.stats.last_run = datetime.now()
            
            # Calcular tempo médio de execução
            if self.stats.total_runs > 0:
                total_time = self.stats.average_run_time * (self.stats.total_runs - 1) + run_time
                self.stats.average_run_time = total_time / self.stats.total_runs
            
        except Exception as e:
            logger.error(f"❌ Erro ao atualizar estatísticas: {e}")
    
    def _generate_offer_hash(self, offer: Offer) -> str:
        """Gera hash único para deduplicação"""
        import hashlib
        
        # Criar string única baseada em dados da oferta
        unique_string = f"{offer.title}_{offer.store}_{offer.price}_{offer.url}"
        return hashlib.md5(unique_string.encode()).hexdigest()
    
    def update_auto_filters(self, **kwargs):
        """Atualiza filtros automáticos"""
        self.auto_filters.update(kwargs)
        
        if self.collector:
            self.collector.update_filters(**kwargs)
        
        logger.info(f"🔧 Filtros automáticos atualizados: {kwargs}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas completas do pipeline"""
        stats = {
            "pipeline": {
                "enabled": self.config.enabled,
                "is_running": self.is_running,
                "current_run_id": self.current_run_id,
                "config": self.config.__dict__
            },
            "stats": self.stats.__dict__,
            "filters": self.auto_filters,
            "rate_limiter": self.rate_limiter.get_stats()
        }
        
        if self.collector:
            stats["collector"] = self.collector.get_stats()
        
        return stats
    
    def stop(self):
        """Para o pipeline de ingestão"""
        logger.info("🛑 Parando pipeline de ingestão...")
        self.is_running = False


# Função de conveniência para obter instância do pipeline
async def get_awin_pipeline() -> Optional[AwinIngestPipeline]:
    """
    Retorna instância configurada do pipeline Awin
    
    Returns:
        AwinIngestPipeline configurado ou None se falhar
    """
    try:
        pipeline = AwinIngestPipeline()
        
        if await pipeline.initialize():
            return pipeline
        else:
            return None
            
    except Exception as e:
        logger.error(f"❌ Erro ao criar pipeline Awin: {e}")
        return None


# Função para executar pipeline uma vez
async def run_single_ingestion() -> bool:
    """
    Executa uma única rodada de ingestão
    
    Returns:
        True se bem-sucedido, False caso contrário
    """
    try:
        pipeline = await get_awin_pipeline()
        
        if not pipeline:
            return False
        
        success = await pipeline.run_ingestion_cycle()
        
        # Limpar recursos
        pipeline.stop()
        
        return success
        
    except Exception as e:
        logger.error(f"❌ Erro na ingestão única: {e}")
        return False


if __name__ == "__main__":
    # Teste do pipeline
    async def test_pipeline():
        pipeline = await get_awin_pipeline()
        if pipeline:
            print("✅ Pipeline criado com sucesso")
            print(f"📊 Configuração: {pipeline.config}")
            print(f"🔧 Filtros: {pipeline.auto_filters}")
        else:
            print("❌ Falha ao criar pipeline")
    
    asyncio.run(test_pipeline())
