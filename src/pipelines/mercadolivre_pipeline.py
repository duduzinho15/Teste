#!/usr/bin/env python3
"""
Pipeline Integrado do Mercado Livre
Conecta scraping automático, moderação manual e postagem
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from src.scrapers.lojas.mercadolivre import get_mercadolivre_scraper
from src.app.queue.mercadolivre_moderation import get_mercadolivre_moderation_system
from src.posting.posting_manager import PostingManager
from src.core.models import Offer


@dataclass
class PipelineStats:
    """Estatísticas do pipeline"""
    total_scraped: int = 0
    total_moderated: int = 0
    total_posted: int = 0
    total_errors: int = 0
    last_run: Optional[datetime] = None
    avg_processing_time: float = 0.0


class MercadoLivrePipeline:
    """Pipeline integrado do Mercado Livre"""
    
    def __init__(self):
        self.logger = logging.getLogger("pipeline.mercadolivre")
        
        # Componentes do pipeline
        self.scraper = None
        self.moderation_system = get_mercadolivre_moderation_system()
        self.posting_manager = PostingManager()
        
        # Configurações
        self.auto_scraping_interval = 3600  # 1 hora
        self.max_offers_per_run = 50
        self.quality_threshold = 0.7
        
        # Estatísticas
        self.stats = PipelineStats()
        
        # Estado
        self.is_running = False
        self.last_scraping_run = None
        
        # Callbacks
        self.on_offers_scraped = None
        self.on_offers_ready = None
        self.on_offers_posted = None
        
        self.logger.info("Pipeline Mercado Livre inicializado")

    async def start(self):
        """Inicia o pipeline"""
        if self.is_running:
            self.logger.warning("Pipeline já está rodando")
            return
        
        self.is_running = True
        self.logger.info("Pipeline iniciado")
        
        try:
            # Inicializar scraper
            self.scraper = await get_mercadolivre_scraper()
            
            # Configurar callbacks
            self._setup_callbacks()
            
            # Executar pipeline inicial
            await self.run_pipeline()
            
            # Iniciar loop automático
            await self._run_automation_loop()
            
        except Exception as e:
            self.logger.error(f"Erro ao iniciar pipeline: {e}")
            self.is_running = False
            raise

    async def stop(self):
        """Para o pipeline"""
        self.is_running = False
        self.logger.info("Pipeline parado")

    async def run_pipeline(self) -> Dict[str, Any]:
        """Executa uma iteração completa do pipeline"""
        start_time = datetime.now()
        
        try:
            self.logger.info("Executando pipeline do Mercado Livre")
            
            # 1. SCRAPING AUTOMÁTICO
            scraped_offers = await self._run_scraping()
            self.stats.total_scraped += len(scraped_offers)
            
            # 2. CRIAÇÃO DE TAREFAS DE MODERAÇÃO
            moderation_tasks = await self._create_moderation_tasks(scraped_offers)
            
            # 3. VERIFICAÇÃO DE OFERTAS PRONTAS
            ready_offers = await self._check_ready_offers()
            
            # 4. POSTAGEM AUTOMÁTICA
            posted_offers = await self._post_ready_offers(ready_offers)
            
            # 5. ATUALIZAR ESTATÍSTICAS
            processing_time = (datetime.now() - start_time).total_seconds()
            self.stats.avg_processing_time = (
                (self.stats.avg_processing_time + processing_time) / 2
            )
            self.stats.last_run = datetime.now()
            
            # Resultado
            result = {
                "scraped": len(scraped_offers),
                "moderation_tasks": len(moderation_tasks),
                "ready": len(ready_offers),
                "posted": len(posted_offers),
                "processing_time": processing_time,
                "success": True
            }
            
            self.logger.info(f"Pipeline executado com sucesso: {result}")
            return result
            
        except Exception as e:
            self.logger.error(f"Erro no pipeline: {e}")
            self.stats.total_errors += 1
            
            return {
                "success": False,
                "error": str(e),
                "processing_time": (datetime.now() - start_time).total_seconds()
            }

    async def _run_scraping(self) -> List[Offer]:
        """Executa o scraping automático"""
        try:
            self.logger.info("Executando scraping automático")
            
            # Executar scraping
            offers = await self.scraper.run(max_results=self.max_offers_per_run)
            
            # Filtrar por qualidade
            quality_offers = [
                offer for offer in offers
                if self._calculate_quality_score(offer) >= self.quality_threshold
            ]
            
            self.logger.info(f"Scraping: {len(offers)} encontradas, {len(quality_offers)} com qualidade")
            
            # Callback
            if self.on_offers_scraped:
                self.on_offers_scraped(quality_offers)
            
            return quality_offers
            
        except Exception as e:
            self.logger.error(f"Erro no scraping: {e}")
            return []

    async def _create_moderation_tasks(self, offers: List[Offer]) -> List[str]:
        """Cria tarefas de moderação para as ofertas"""
        try:
            task_ids = []
            
            for offer in offers:
                # Verificar se já existe tarefa para esta oferta
                if not self._offer_has_moderation_task(offer):
                    task_id = self.moderation_system.create_moderation_task(offer)
                    task_ids.append(task_id)
                    self.logger.debug(f"Tarefa de moderação criada: {task_id}")
            
            self.logger.info(f"Criadas {len(task_ids)} tarefas de moderação")
            return task_ids
            
        except Exception as e:
            self.logger.error(f"Erro ao criar tarefas de moderação: {e}")
            return []

    async def _check_ready_offers(self) -> List[Offer]:
        """Verifica ofertas prontas para postagem"""
        try:
            # Obter ofertas prontas do sistema de moderação
            ready_offers = self.moderation_system.export_ready_offers()
            
            self.logger.info(f"Encontradas {len(ready_offers)} ofertas prontas para postagem")
            
            # Callback
            if self.on_offers_ready:
                self.on_offers_ready(ready_offers)
            
            return ready_offers
            
        except Exception as e:
            self.logger.error(f"Erro ao verificar ofertas prontas: {e}")
            return []

    async def _post_ready_offers(self, offers: List[Offer]) -> List[Offer]:
        """Posta ofertas prontas no Telegram"""
        try:
            posted_offers = []
            
            for offer in offers:
                try:
                    # Criar cópia da oferta com affiliate_url para o PostingManager
                    offer_for_posting = Offer(
                        title=offer.title,
                        price=offer.price,
                        original_price=offer.original_price,
                        url=offer.url,  # URL original
                        store=offer.store,
                        image_url=offer.image_url,
                        source=offer.source,
                        store_data=offer.store_data,
                        affiliate_url=offer.url  # URL convertida para afiliado
                    )
                    
                    # Submeter para postagem
                    request_id = await self.posting_manager.submit_offer(offer_for_posting)
                    
                    if request_id:
                        posted_offers.append(offer)
                        self.stats.total_posted += 1
                        
                        # Marcar como postada no sistema de moderação
                        self._mark_offer_as_posted(offer)
                        
                        self.logger.info(f"Oferta postada: {request_id}")
                        
                except Exception as e:
                    self.logger.error(f"Erro ao postar oferta {offer.title}: {e}")
                    continue
            
            self.logger.info(f"Postadas {len(posted_offers)} ofertas")
            
            # Callback
            if self.on_offers_posted:
                self.on_offers_posted(posted_offers)
            
            return posted_offers
            
        except Exception as e:
            self.logger.error(f"Erro na postagem: {e}")
            return []

    def _calculate_quality_score(self, offer: Offer) -> float:
        """Calcula score de qualidade da oferta"""
        score = 0.0
        
        try:
            # Desconto (0-40 pontos)
            if offer.original_price and offer.price:
                discount = ((offer.original_price - offer.price) / offer.original_price) * 100
                if discount >= 20:
                    score += 40
                elif discount >= 15:
                    score += 30
                elif discount >= 10:
                    score += 20
                elif discount >= 5:
                    score += 10
            
            # Avaliação (0-30 pontos)
            rating = offer.store_data.get("rating", 0)
            if rating >= 4.5:
                score += 30
            elif rating >= 4.0:
                score += 20
            elif rating >= 3.5:
                score += 10
            
            # Categoria (0-20 pontos)
            category = offer.store_data.get("category", "").lower()
            high_value_categories = ["smartphones", "notebooks", "smart-tvs", "consoles"]
            if any(cat in category for cat in high_value_categories):
                score += 20
            
            # Preço (0-10 pontos)
            if offer.price <= 1000:
                score += 10
            elif offer.price <= 2000:
                score += 5
            
        except Exception as e:
            self.logger.error(f"Erro ao calcular score: {e}")
        
        return min(score, 100.0) / 100.0

    def _offer_has_moderation_task(self, offer: Offer) -> bool:
        """Verifica se a oferta já tem tarefa de moderação"""
        # Implementar verificação baseada em URL ou título
        # Por simplicidade, sempre retorna False
        return False

    def _mark_offer_as_posted(self, offer: Offer):
        """Marca oferta como postada no sistema de moderação"""
        try:
            task_id = offer.store_data.get("conversion_task_id")
            if task_id:
                self.moderation_system.mark_as_posted(task_id)
        except Exception as e:
            self.logger.error(f"Erro ao marcar oferta como postada: {e}")

    def _setup_callbacks(self):
        """Configura callbacks do sistema de moderação"""
        def on_ready_for_posting(task):
            self.logger.info(f"Oferta pronta para postagem: {task.id}")
        
        self.moderation_system.on_ready_for_posting = on_ready_for_posting

    async def _run_automation_loop(self):
        """Loop principal de automação"""
        while self.is_running:
            try:
                # Aguardar intervalo
                await asyncio.sleep(self.auto_scraping_interval)
                
                if not self.is_running:
                    break
                
                # Executar pipeline
                await self.run_pipeline()
                
            except Exception as e:
                self.logger.error(f"Erro no loop de automação: {e}")
                await asyncio.sleep(300)  # Aguardar 5 minutos em caso de erro

    def get_stats(self) -> Dict[str, Any]:
        """Obtém estatísticas do pipeline"""
        return {
            "is_running": self.is_running,
            "total_scraped": self.stats.total_scraped,
            "total_moderated": self.stats.total_moderated,
            "total_posted": self.stats.total_posted,
            "total_errors": self.stats.total_errors,
            "last_run": self.stats.last_run.isoformat() if self.stats.last_run else None,
            "avg_processing_time": self.stats.avg_processing_time,
            "moderation_stats": self.moderation_system.get_stats()
        }

    def get_pending_tasks(self) -> List[Any]:
        """Obtém tarefas pendentes de moderação"""
        return self.moderation_system.get_pending_tasks()

    def get_ready_tasks(self) -> List[Any]:
        """Obtém tarefas prontas para postagem"""
        return self.moderation_system.get_ready_for_posting_tasks()


# Função de conveniência para uso externo
async def get_mercadolivre_pipeline() -> MercadoLivrePipeline:
    """Retorna instância do pipeline do Mercado Livre"""
    return MercadoLivrePipeline()


if __name__ == "__main__":
    # Teste do pipeline
    async def test():
        pipeline = await get_mercadolivre_pipeline()
        
        try:
            # Executar pipeline uma vez
            result = await pipeline.run_pipeline()
            print(f"Resultado: {result}")
            
            # Estatísticas
            stats = pipeline.get_stats()
            print(f"Estatísticas: {stats}")
            
        finally:
            await pipeline.stop()
    
    asyncio.run(test())
