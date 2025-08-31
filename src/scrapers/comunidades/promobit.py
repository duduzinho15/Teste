"""
Scraper do Promobit para o sistema Garimpeiro Geek.
Coleta ofertas em tempo real da comunidade Promobit com Playwright.
"""

import asyncio
import logging
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
import re
import json
import random
from pathlib import Path

from playwright.async_api import async_playwright, Browser, Page, BrowserContext
from src.core.models import Offer
from src.core.affiliate_validator import AffiliateValidator
from src.utils.anti_bot import AntiBotUtils


@dataclass
class PromobitOffer:
    """Oferta do Promobit."""
    title: str
    price: float
    original_price: Optional[float]
    discount: Optional[int]
    store: str
    category: str
    url: str
    image_url: Optional[str]
    posted_at: datetime
    votes: int
    comments: int
    hot: bool


class PromobitScraper:
    """Scraper para o site Promobit com Playwright."""
    
    def __init__(self):
        """Inicializa o scraper."""
        self.logger = logging.getLogger(__name__)
        self.base_url = "https://www.promobit.com.br"
        self.validator = AffiliateValidator()
        
        # Configurações Playwright
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        
        # Configurações de scraping
        self.max_offers_per_page = 50
        self.rate_limit_delay = 2.0  # segundos entre requisições
        self.max_retries = 3
        self.timeout = 30000  # 30 segundos
        
        # Filtros automáticos
        self.auto_filters = {
            "min_discount": 15,
            "max_price": 1500.0,
            "categories": ["eletronicos", "informatica", "games", "casa", "moda"],
            "min_votes": 5,
            "min_comments": 2,
            "hot_only": False
        }
        
        # Cache de ofertas já processadas
        self.processed_offers = set()
        
        # Estatísticas
        self.stats = {
            "total_scraped": 0,
            "valid_offers": 0,
            "invalid_offers": 0,
            "filtered_out": 0,
            "last_scrape": None,
            "errors": 0,
            "browser_sessions": 0
        }
        
        # Anti-bot measures
        self.anti_bot = AntiBotUtils()
        
        # User agents rotativos
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ]
    
    async def initialize_browser(self):
        """Inicializa o navegador Playwright."""
        try:
            if not self.browser:
                self.playwright = await async_playwright().start()
                
                # Configurações do navegador
                browser_options = {
                    "headless": True,  # False para debug
                    "args": [
                        "--no-sandbox",
                        "--disable-setuid-sandbox",
                        "--disable-dev-shm-usage",
                        "--disable-accelerated-2d-canvas",
                        "--no-first-run",
                        "--no-zygote",
                        "--disable-gpu"
                    ]
                }
                
                self.browser = await self.playwright.chromium.launch(**browser_options)
                self.stats["browser_sessions"] += 1
                
                # Criar contexto com configurações anti-bot
                context_options = {
                    "viewport": {"width": 1920, "height": 1080},
                    "user_agent": random.choice(self.user_agents),
                    "locale": "pt-BR",
                    "timezone_id": "America/Sao_Paulo"
                }
                
                self.context = await self.browser.new_context(**context_options)
                
                # Configurar página
                self.page = await self.context.new_page()
                
                # Configurar timeouts
                self.page.set_default_timeout(self.timeout)
                
                # Configurar headers extras
                await self.page.set_extra_http_headers({
                    "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
                    "Accept-Encoding": "gzip, deflate, br",
                    "DNT": "1",
                    "Connection": "keep-alive",
                    "Upgrade-Insecure-Requests": "1"
                })
                
                self.logger.info("✅ Navegador Playwright inicializado")
                
        except Exception as e:
            self.logger.error(f"❌ Erro ao inicializar navegador: {e}")
            raise
    
    async def close_browser(self):
        """Fecha o navegador Playwright."""
        try:
            if self.page:
                await self.page.close()
                self.page = None
            
            if self.context:
                await self.context.close()
                self.context = None
            
            if self.browser:
                await self.browser.close()
                self.browser = None
            
            if hasattr(self, 'playwright'):
                await self.playwright.stop()
            
            self.logger.info("🔒 Navegador Playwright fechado")
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao fechar navegador: {e}")
    
    async def scrape_offers(self, max_offers: int = 100) -> List[Offer]:
        """
        Coleta ofertas do Promobit com Playwright.
        
        Args:
            max_offers: Máximo de ofertas a coletar
            
        Returns:
            Lista de ofertas válidas
        """
        try:
            self.logger.info(f"🕷️ Iniciando coleta de ofertas do Promobit (máx: {max_offers})")
            
            # Inicializar navegador se necessário
            if not self.browser:
                await self.initialize_browser()
            
            offers = []
            page_num = 1
            
            while len(offers) < max_offers:
                self.logger.info(f"  📄 Coletando página {page_num}")
                
                # Coletar ofertas da página
                page_offers = await self._scrape_page_with_playwright(page_num)
                
                if not page_offers:
                    self.logger.info("  ⚠️ Nenhuma oferta encontrada na página, parando")
                    break
                
                # Processar ofertas da página
                for promobit_offer in page_offers:
                    if len(offers) >= max_offers:
                        break
                    
                    # Aplicar filtros automáticos
                    if not await self._passes_auto_filters(promobit_offer):
                        self.stats["filtered_out"] += 1
                        continue
                    
                    # Converter para modelo Offer
                    offer = await self._convert_to_offer(promobit_offer)
                    
                    if offer and await self._validate_offer(offer):
                        offers.append(offer)
                        self.stats["valid_offers"] += 1
                    else:
                        self.stats["invalid_offers"] += 1
                
                # Rate limiting entre páginas
                await asyncio.sleep(self.rate_limit_delay)
                page_num += 1
            
            # Atualizar estatísticas
            self.stats["total_scraped"] = len(offers)
            self.stats["last_scrape"] = datetime.now()
            
            self.logger.info(f"✅ Coleta concluída: {len(offers)} ofertas válidas")
            return offers
            
        except Exception as e:
            self.logger.error(f"❌ Erro na coleta: {e}")
            self.stats["errors"] += 1
            return []
    
    async def _scrape_page_with_playwright(self, page_num: int) -> List[PromobitOffer]:
        """Coleta ofertas de uma página usando Playwright."""
        try:
            # Navegar para a página
            url = f"{self.base_url}/ofertas"
            if page_num > 1:
                url += f"?page={page_num}"
            
            await self.page.goto(url, wait_until="networkidle")
            
            # Aguardar carregamento das ofertas
            await self.page.wait_for_selector(".offer-item", timeout=10000)
            
            # Aplicar medidas anti-bot
            await self._apply_anti_bot_measures()
            
            # Extrair ofertas da página
            offers = await self._extract_offers_from_page()
            
            return offers
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao coletar página {page_num}: {e}")
            return []
    
    async def _apply_anti_bot_measures(self):
        """Aplica medidas anti-bot."""
        try:
            # Scroll natural
            await self.page.evaluate("""
                window.scrollTo({
                    top: Math.random() * 1000,
                    behavior: 'smooth'
                });
            """)
            
            # Aguardar tempo aleatório
            await asyncio.sleep(random.uniform(1, 3))
            
            # Mover mouse aleatoriamente
            await self.page.mouse.move(
                random.randint(100, 800),
                random.randint(100, 600)
            )
            
        except Exception as e:
            self.logger.debug(f"⚠️ Erro ao aplicar medidas anti-bot: {e}")
    
    async def _extract_offers_from_page(self) -> List[PromobitOffer]:
        """Extrai ofertas da página atual."""
        try:
            # Seletores CSS para elementos das ofertas
            offer_selectors = {
                "container": ".offer-item",
                "title": ".offer-title",
                "price": ".offer-price",
                "original_price": ".offer-original-price",
                "store": ".offer-store",
                "category": ".offer-category",
                "url": "a.offer-link",
                "image": ".offer-image img",
                "votes": ".offer-votes",
                "comments": ".offer-comments",
                "hot_badge": ".hot-badge"
            }
            
            # Extrair ofertas
            offers = await self.page.evaluate("""
                (selectors) => {
                    const offers = [];
                    const offerElements = document.querySelectorAll(selectors.container);
                    
                    offerElements.forEach(element => {
                        try {
                            const titleEl = element.querySelector(selectors.title);
                            const priceEl = element.querySelector(selectors.price);
                            const originalPriceEl = element.querySelector(selectors.original_price);
                            const storeEl = element.querySelector(selectors.store);
                            const categoryEl = element.querySelector(selectors.category);
                            const linkEl = element.querySelector(selectors.url);
                            const imageEl = element.querySelector(selectors.image);
                            const votesEl = element.querySelector(selectors.votes);
                            const commentsEl = element.querySelector(selectors.comments);
                            const hotEl = element.querySelector(selectors.hot_badge);
                            
                            if (titleEl && priceEl && linkEl) {
                                offers.push({
                                    title: titleEl.textContent.trim(),
                                    price: priceEl.textContent.trim(),
                                    original_price: originalPriceEl ? originalPriceEl.textContent.trim() : null,
                                    store: storeEl ? storeEl.textContent.trim() : 'Loja',
                                    category: categoryEl ? categoryEl.textContent.trim() : 'Geral',
                                    url: linkEl.href,
                                    image_url: imageEl ? imageEl.src : null,
                                    votes: votesEl ? parseInt(votesEl.textContent) || 0 : 0,
                                    comments: commentsEl ? parseInt(commentsEl.textContent) || 0 : 0,
                                    hot: !!hotEl
                                });
                            }
                        } catch (e) {
                            console.error('Erro ao extrair oferta:', e);
                        }
                    });
                    
                    return offers;
                }
            """, offer_selectors)
            
            # Converter para objetos PromobitOffer
            promobit_offers = []
            for offer_data in offers:
                try:
                    # Parse de preços
                    price = self._parse_price(offer_data["price"])
                    original_price = None
                    if offer_data["original_price"]:
                        original_price = self._parse_price(offer_data["original_price"])
                    
                    # Calcular desconto
                    discount = None
                    if original_price and original_price > price:
                        discount = int(((original_price - price) / original_price) * 100)
                    
                    # Criar oferta
                    offer = PromobitOffer(
                        title=offer_data["title"],
                        price=price,
                        original_price=original_price,
                        discount=discount,
                        store=offer_data["store"],
                        category=offer_data["category"],
                        url=offer_data["url"],
                        image_url=offer_data["image_url"],
                        posted_at=datetime.now(),
                        votes=offer_data["votes"],
                        comments=offer_data["comments"],
                        hot=offer_data["hot"]
                    )
                    
                    promobit_offers.append(offer)
                    
                except Exception as e:
                    self.logger.debug(f"⚠️ Erro ao processar oferta: {e}")
                    continue
            
            return promobit_offers
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao extrair ofertas: {e}")
            return []
    
    def _parse_price(self, price_text: str) -> float:
        """Parse de texto de preço para float."""
        try:
            # Remover símbolos e caracteres especiais
            price_clean = re.sub(r'[^\d,.]', '', price_text)
            
            # Substituir vírgula por ponto
            price_clean = price_clean.replace(',', '.')
            
            return float(price_clean)
            
        except Exception:
            return 0.0
    
    async def _passes_auto_filters(self, offer: PromobitOffer) -> bool:
        """Verifica se oferta passa nos filtros automáticos."""
        try:
            # Verificar desconto mínimo
            if self.auto_filters["min_discount"] > 0:
                if not offer.discount or offer.discount < self.auto_filters["min_discount"]:
                    return False
            
            # Verificar preço máximo
            if offer.price > self.auto_filters["max_price"]:
                return False
            
            # Verificar categoria permitida
            if offer.category.lower() not in [c.lower() for c in self.auto_filters["categories"]]:
                return False
            
            # Verificar votos mínimos
            if offer.votes < self.auto_filters["min_votes"]:
                return False
            
            # Verificar comentários mínimos
            if offer.comments < self.auto_filters["min_comments"]:
                return False
            
            # Verificar se é hot (se configurado)
            if self.auto_filters["hot_only"] and not offer.hot:
                return False
            
            return True
            
        except Exception as e:
            self.logger.debug(f"⚠️ Erro ao verificar filtros: {e}")
            return False
    
    async def _convert_to_offer(self, promobit_offer: PromobitOffer) -> Optional[Offer]:
        """
        Converte oferta do Promobit para modelo Offer.
        
        Args:
            promobit_offer: Oferta do Promobit
            
        Returns:
            Oferta convertida ou None se inválida
        """
        try:
            # Validar dados básicos
            if not promobit_offer.title or not promobit_offer.url:
                return None
            
            # Calcular desconto
            discount_percentage = None
            if promobit_offer.original_price and promobit_offer.price < promobit_offer.original_price:
                discount_percentage = int(
                    ((promobit_offer.original_price - promobit_offer.price) / promobit_offer.original_price) * 100
                )
            
            # Criar oferta
            offer = Offer(
                title=promobit_offer.title,
                price=Decimal(str(promobit_offer.price)),
                original_price=Decimal(str(promobit_offer.original_price)) if promobit_offer.original_price else None,
                url=promobit_offer.url,
                store=promobit_offer.store,
                category=promobit_offer.category,
                affiliate_url=promobit_offer.url,
                image_url=promobit_offer.image_url
            )
            
            return offer
            
        except Exception as e:
            self.logger.error(f"Erro ao converter oferta: {e}")
            return None
    
    async def _validate_offer(self, offer: Offer) -> bool:
        """
        Valida se uma oferta pode ser processada.
        
        Args:
            offer: Oferta a ser validada
            
        Returns:
            True se válida
        """
        try:
            # Verificar se já foi processada
            offer_hash = f"{offer.title}_{offer.affiliate_url}"
            if offer_hash in self.processed_offers:
                return False
            
            # Validar URL de afiliado
            validation = await self.validator.validate_url(offer.affiliate_url)
            if not validation.is_valid:
                return False
            
            # Validar preço
            if offer.price <= 0:
                return False
            
            # Adicionar ao cache de processadas
            self.processed_offers.add(offer_hash)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erro na validação da oferta: {e}")
            return False
    
    def update_auto_filters(self, **kwargs):
        """Atualiza filtros automáticos."""
        self.auto_filters.update(kwargs)
        self.logger.info(f"🔧 Filtros automáticos atualizados: {kwargs}")
    
    async def scrape_hot_offers(self, max_offers: int = 20) -> List[Offer]:
        """Coleta apenas ofertas em alta (hot)."""
        # Ativar filtro hot temporariamente
        original_hot_only = self.auto_filters["hot_only"]
        self.auto_filters["hot_only"] = True
        
        try:
            offers = await self.scrape_offers(max_offers)
            return offers
        finally:
            # Restaurar configuração original
            self.auto_filters["hot_only"] = original_hot_only
    
    async def scrape_by_category(self, category: str, max_offers: int = 50) -> List[Offer]:
        """Coleta ofertas por categoria."""
        # Filtrar por categoria específica
        original_categories = self.auto_filters["categories"]
        self.auto_filters["categories"] = [category]
        
        try:
            offers = await self.scrape_offers(max_offers)
            return offers
        finally:
            # Restaurar configuração original
            self.auto_filters["categories"] = original_categories
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do scraper."""
        return self.stats.copy()
    
    def clear_cache(self):
        """Limpa cache de ofertas processadas."""
        self.processed_offers.clear()
        self.logger.info("🗑️ Cache de ofertas processadas limpo")
    
    async def health_check(self) -> bool:
        """Verifica saúde do scraper."""
        try:
            # Testar coleta de uma página
            offers = await self._scrape_page_with_playwright(1)
            return len(offers) > 0
            
        except Exception as e:
            self.logger.error(f"Health check falhou: {e}")
            return False


# Instância global do scraper
promobit_scraper = PromobitScraper()
