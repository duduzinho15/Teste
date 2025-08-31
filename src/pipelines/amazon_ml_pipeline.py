#!/usr/bin/env python3
"""
Pipeline Unificado para Amazon + Magazine Luiza
Integra scrapers com rate limiting e configurações de produção
"""

import asyncio
import os
import logging
from datetime import datetime
from typing import List, Dict, Any
from src.core.models import Offer
from src.scrapers.lojas.magazineluiza import MagazineLuizaScraper
from src.affiliate.amazon_asin_scraper import AmazonASINScraper

class AmazonMLPipeline:
    """Pipeline unificado para Amazon e Magazine Luiza com rate limiting"""
    
    def __init__(self):
        # Configurações de rate limiting
        self.delay = float(os.getenv("SCRAPER_DELAY", "3.0"))
        self.max_retries = int(os.getenv("SCRAPER_MAX_RETRIES", "3"))
        self.retry_delay = int(os.getenv("SCRAPER_RETRY_DELAY", "5"))
        
        # Configurações de filtros
        self.max_price = float(os.getenv("MAX_OFFER_PRICE", "3000.00"))
        self.min_discount = int(os.getenv("MIN_OFFER_DISCOUNT", "15"))
        self.max_offers_per_store = int(os.getenv("MAX_OFFERS_PER_POST", "5"))
        
        # Logging
        self.logger = logging.getLogger("AmazonMLPipeline")
        
        # Inicializar scrapers
        self.amazon_scraper = AmazonASINScraper()
        self.ml_scraper = MagazineLuizaScraper()
        
        # Estatísticas
        self.stats = {
            "amazon_offers": 0,
            "ml_offers": 0,
            "total_offers": 0,
            "filtered_offers": 0,
            "errors": 0,
            "last_run": None
        }
    
    async def collect_offers(self, search_term=None):
        """Coleta ofertas de Amazon e Magazine Luiza com rate limiting"""
        self.logger.info("Iniciando coleta de ofertas unificada")
        self.stats["last_run"] = datetime.now()
        
        all_offers = []
        
        try:
            # Coletar ofertas da Amazon
            self.logger.info("Coletando ofertas da Amazon...")
            amazon_offers = await self._collect_amazon_offers(search_term)
            self.stats["amazon_offers"] = len(amazon_offers)
            all_offers.extend(amazon_offers)
            
            # Rate limiting entre scrapers
            if amazon_offers:
                await asyncio.sleep(self.delay)
            
            # Coletar ofertas da Magazine Luiza
            self.logger.info("Coletando ofertas da Magazine Luiza...")
            ml_offers = await self._collect_ml_offers(search_term)
            self.stats["ml_offers"] = len(ml_offers)
            all_offers.extend(ml_offers)
            
            # Processar e filtrar ofertas
            processed_offers = await self._process_offers(all_offers)
            
            self.stats["total_offers"] = len(all_offers)
            self.stats["filtered_offers"] = len(processed_offers)
            
            self.logger.info(f"Coleta concluída: {len(processed_offers)} ofertas válidas")
            return processed_offers
            
        except Exception as e:
            self.logger.error(f"Erro na coleta unificada: {e}")
            self.stats["errors"] += 1
            return []
    
    async def _collect_amazon_offers(self, search_term):
        """Coleta ofertas da Amazon com retry e rate limiting"""
        for attempt in range(self.max_retries):
            try:
                offers = await self.amazon_scraper.scrape_offers(
                    search_term=search_term,
                    max_price=self.max_price,
                    min_discount=self.min_discount
                )
                return offers
                
            except Exception as e:
                self.logger.warning(f"Tentativa {attempt + 1} da Amazon falhou: {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay)
                else:
                    self.logger.error("Todas as tentativas da Amazon falharam")
                    return []
    
    async def _collect_ml_offers(self, search_term):
        """Coleta ofertas da Magazine Luiza com retry e rate limiting"""
        for attempt in range(self.max_retries):
            try:
                offers = await self.ml_scraper.scrape_offers(
                    search_term=search_term,
                    max_price=self.max_price,
                    min_discount=self.min_discount
                )
                return offers
                
            except Exception as e:
                self.logger.warning(f"Tentativa {attempt + 1} da ML falhou: {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay)
                else:
                    self.logger.error("Todas as tentativas da ML falharam")
                    return []
    
    async def _process_offers(self, offers: List[Offer]) -> List[Offer]:
        """Processa e filtra ofertas coletadas"""
        if not offers:
            return []
        
        processed_offers = []
        
        for offer in offers:
            try:
                # Validar oferta
                if not self._validate_offer(offer):
                    continue
                
                # Categorizar produto
                if not offer.category:
                    offer.category = self._categorize_product(offer.title)
                
                # Adicionar metadados
                offer.source = "amazon_ml_pipeline"
                
                processed_offers.append(offer)
                
            except Exception as e:
                self.logger.warning(f"Erro ao processar oferta: {e}")
                continue
        
        # Remover duplicatas
        unique_offers = self._remove_duplicates(processed_offers)
        
        # Ordenar por desconto (maior primeiro)
        unique_offers.sort(key=lambda x: x.discount_percentage or 0, reverse=True)
        
        # Limitar número de ofertas
        max_offers = int(os.getenv("MAX_OFFERS_PER_POST", "10"))
        return unique_offers[:max_offers]
    
    def _validate_offer(self, offer: Offer) -> bool:
        """Valida se a oferta é válida para publicação"""
        try:
            # Campos obrigatórios
            if not offer.title or not offer.title.strip():
                return False
            
            if not offer.price or offer.price <= 0:
                return False
            
            if not offer.url or not offer.url.startswith(("http://", "https://")):
                return False
            
            if not offer.store or not offer.store.strip():
                return False
            
            # Validar preço máximo
            if offer.price > self.max_price:
                return False
            
            # Validar desconto mínimo
            if offer.discount_percentage and offer.discount_percentage < self.min_discount:
                return False
            
            # Validar link afiliado
            if not offer.affiliate_url:
                return False
            
            return True
            
        except Exception as e:
            self.logger.warning(f"Erro na validação da oferta: {e}")
            return False
    
    def _categorize_product(self, title: str) -> str:
        """Categoriza produtos baseado no título"""
        if not title:
            return "outros"
        
        title_lower = title.lower()
        
        categories = {
            "notebook": ["notebook", "laptop", "computador portátil", "macbook"],
            "smartphone": ["celular", "smartphone", "iphone", "galaxy", "mobile"],
            "tv": ["tv", "televisão", "smart tv", "televisor", "fire tv"],
            "eletrodomesticos": ["geladeira", "fogão", "microondas", "lavadora", "aspirador"],
            "games": ["playstation", "xbox", "nintendo", "controle", "jogo", "console"],
            "audio": ["fone", "caixa de som", "headphone", "earphone", "alexa", "echo"],
            "hardware": ["placa de video", "processador", "memoria", "ssd", "ram", "gpu"]
        }
        
        for category, keywords in categories.items():
            if any(keyword in title_lower for keyword in keywords):
                return category
        
        return "outros"
    
    def _remove_duplicates(self, offers: List[Offer]) -> List[Offer]:
        """Remove ofertas duplicadas baseado no título e preço"""
        seen = set()
        unique_offers = []
        
        for offer in offers:
            # Criar chave única baseada no título e preço
            key = (offer.title.lower().strip(), float(offer.price))
            
            if key not in seen:
                seen.add(key)
                unique_offers.append(offer)
        
        return unique_offers
    
    async def health_check(self) -> Dict[str, Any]:
        """Verifica saúde dos scrapers e pipeline"""
        health_status = {
            "pipeline": "healthy",
            "amazon_scraper": False,
            "ml_scraper": False,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            # Verificar Amazon
            amazon_health = await self.amazon_scraper.health_check()
            health_status["amazon_scraper"] = amazon_health
            
            # Verificar Magazine Luiza
            ml_health = await self.ml_scraper.health_check()
            health_status["ml_scraper"] = ml_health
            
            # Status geral
            if not amazon_health or not ml_health:
                health_status["pipeline"] = "degraded"
            
        except Exception as e:
            self.logger.error(f"Erro no health check: {e}")
            health_status["pipeline"] = "unhealthy"
            health_status["error"] = str(e)
        
        return health_status
    
    def get_pipeline_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do pipeline"""
        return {
            **self.stats,
            "config": {
                "delay": self.delay,
                "max_retries": self.max_retries,
                "retry_delay": self.retry_delay,
                "max_price": self.max_price,
                "min_discount": self.min_discount,
                "max_offers_per_store": self.max_offers_per_store
            }
        }
    
    async def test_pipeline(self) -> bool:
        """Testa o pipeline com uma coleta pequena"""
        try:
            self.logger.info("Testando pipeline...")
            
            # Coletar apenas algumas ofertas para teste
            test_offers = await self.collect_offers("teste")
            
            if test_offers:
                self.logger.info(f"Pipeline funcionando: {len(test_offers)} ofertas coletadas")
                return True
            else:
                self.logger.warning("Pipeline não retornou ofertas")
                return False
                
        except Exception as e:
            self.logger.error(f"Erro no teste do pipeline: {e}")
            return False
