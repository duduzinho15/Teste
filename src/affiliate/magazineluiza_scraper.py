"""
Scraper avançado da Magazine Luiza com Playwright e conversão de afiliados.
Implementa scraping real da loja com extração de produtos e conversão automática.
"""

import asyncio
import logging
import re
from decimal import Decimal
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin, urlparse

try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    logging.warning("Playwright não disponível. Usando modo simulado.")

from src.core.models import Offer

logger = logging.getLogger(__name__)


class MagazineLuizaScraper:
    """Scraper e conversor avançado para Magazine Luiza"""
    
    def __init__(self):
        self.base_url = "https://www.magazineluiza.com.br"
        self.affiliate_id = "magazinegarimpeirogeek"  # Configurar no .env
        self.max_retries = 3
        self.rate_limit_delay = 2.0
        
        # Configurações de scraping
        self.selectors = {
            "product_card": '[data-testid="product-card"], .product-card, .product-item',
            "title": 'h2, .product-title, .product-name',
            "price": '[data-testid="price-value"], .price-value, .price',
            "original_price": '[data-testid="price-original"], .price-original, .old-price',
            "image": 'img[src*="product"], .product-image img',
            "link": 'a[href*="/p/"], .product-link',
            "discount": '.discount-badge, .discount, .promo-badge'
        }
        
    async def scrape_offers(
        self, 
        search_term: Optional[str] = None, 
        max_price: float = 3000, 
        min_discount: int = 20,
        max_results: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Coleta ofertas reais da Magazine Luiza usando Playwright
        
        Args:
            search_term: Termo de busca (opcional)
            max_price: Preço máximo das ofertas
            min_discount: Desconto mínimo em porcentagem
            max_results: Número máximo de resultados
            
        Returns:
            Lista de ofertas encontradas
        """
        if not PLAYWRIGHT_AVAILABLE:
            logger.warning("Playwright não disponível. Retornando dados simulados.")
            return await self._get_simulated_offers(search_term, max_results)
        
        offers = []
        
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=True,
                    args=[
                        '--no-sandbox',
                        '--disable-setuid-sandbox',
                        '--disable-dev-shm-usage',
                        '--disable-accelerated-2d-canvas',
                        '--no-first-run',
                        '--no-zygote',
                        '--disable-gpu'
                    ]
                )
                
                page = await browser.new_page(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                )
                
                # Configurar viewport
                await page.set_viewport_size({"width": 1920, "height": 1080})
                
                try:
                    # URLs de busca baseadas no termo
                    urls = self._generate_search_urls(search_term)
                    
                    for url in urls:
                        if len(offers) >= max_results:
                            break
                            
                        logger.info(f"Scraping URL: {url}")
                        page_offers = await self._scrape_page(page, url, max_price, min_discount)
                        offers.extend(page_offers)
                        
                        # Rate limiting entre páginas
                        await asyncio.sleep(self.rate_limit_delay)
                
                finally:
                    await browser.close()
                    
        except Exception as e:
            logger.error(f"Erro no scraping Magazine Luiza: {e}")
            # Fallback para dados simulados
            return await self._get_simulated_offers(search_term, max_results)
        
        # Filtrar e limitar resultados
        filtered_offers = self._filter_offers(offers, max_price, min_discount)
        return filtered_offers[:max_results]
    
    def _generate_search_urls(self, search_term: Optional[str]) -> List[str]:
        """Gera URLs de busca para Magazine Luiza"""
        urls = []
        
        if search_term:
            # URL de busca específica
            search_url = f"{self.base_url}/busca/{search_term.replace(' ', '-')}/"
            urls.append(search_url)
        else:
            # URLs de ofertas gerais
            urls.extend([
                f"{self.base_url}/ofertas/",
                f"{self.base_url}/ofertas-do-dia/",
                f"{self.base_url}/promocoes/",
                f"{self.base_url}/lancamentos/"
            ])
        
        return urls
    
    async def _scrape_page(
        self, 
        page, 
        url: str, 
        max_price: float, 
        min_discount: int
    ) -> List[Dict[str, Any]]:
        """Scraping de uma página específica"""
        offers = []
        
        try:
            # Navegar para a página
            await page.goto(url, wait_until='domcontentloaded', timeout=30000)
            
            # Aguardar carregamento dos produtos
            await self._wait_for_products(page)
            
            # Scroll para carregar mais produtos
            await self._scroll_page(page)
            
            # Extrair produtos
            products = await page.query_selector_all(self.selectors["product_card"])
            
            logger.info(f"Encontrados {len(products)} produtos na página")
            
            for product in products:
                try:
                    offer = await self._extract_product_data(product)
                    if offer and self._validate_offer(offer, max_price, min_discount):
                        offers.append(offer)
                        
                except Exception as e:
                    logger.debug(f"Erro ao extrair produto: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Erro ao fazer scraping da página {url}: {e}")
        
        return offers
    
    async def _wait_for_products(self, page):
        """Aguarda carregamento dos produtos"""
        try:
            await page.wait_for_selector(
                self.selectors["product_card"], 
                timeout=10000
            )
        except Exception:
            logger.warning("Timeout aguardando produtos. Continuando...")
    
    async def _scroll_page(self, page):
        """Faz scroll na página para carregar mais produtos"""
        try:
            # Scroll para baixo
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(2)
            
            # Scroll para cima
            await page.evaluate("window.scrollTo(0, 0)")
            await asyncio.sleep(1)
            
        except Exception as e:
            logger.debug(f"Erro no scroll: {e}")
    
    async def _extract_product_data(self, product_element) -> Optional[Dict[str, Any]]:
        """Extrai dados de um produto individual"""
        try:
            # Título
            title_elem = await product_element.query_selector(self.selectors["title"])
            if not title_elem:
                return None
                
            title = await title_elem.text_content()
            if not title or len(title.strip()) < 5:
                return None
            
            # Preço
            price_elem = await product_element.query_selector(self.selectors["price"])
            if not price_elem:
                return None
                
            price_text = await price_elem.text_content()
            price = self._parse_price(price_text)
            if not price:
                return None
            
            # Preço original
            original_price = None
            original_elem = await product_element.query_selector(self.selectors["original_price"])
            if original_elem:
                original_text = await original_elem.text_content()
                original_price = self._parse_price(original_text)
            
            # Link do produto
            link_elem = await product_element.query_selector(self.selectors["link"])
            if not link_elem:
                return None
                
            product_url = await link_elem.get_attribute('href')
            if not product_url:
                return None
            
            # Normalizar URL
            if not product_url.startswith('http'):
                product_url = urljoin(self.base_url, product_url)
            
            # Imagem
            image_url = None
            image_elem = await product_element.query_selector(self.selectors["image"])
            if image_elem:
                image_url = await image_elem.get_attribute('src')
                if image_url and not image_url.startswith('http'):
                    image_url = urljoin(self.base_url, image_url)
            
            # Extrair ID do produto
            product_id = self.extract_product_id(product_url)
            
            # Criar oferta
            offer = {
                "title": title.strip(),
                "price": price,
                "original_price": original_price,
                "product_url": product_url,
                "product_id": product_id,
                "image_url": image_url,
                "store": "magazineluiza",
                "source": "real_scraper"
            }
            
            # Calcular desconto
            if original_price and original_price > price:
                discount_percent = int(((original_price - price) / original_price) * 100)
                offer["discount_percent"] = discount_percent
            
            return offer
            
        except Exception as e:
            logger.debug(f"Erro ao extrair dados do produto: {e}")
            return None
    
    def _parse_price(self, price_text: str) -> Optional[float]:
        """Converte texto de preço para float"""
        try:
            if not price_text:
                return None
            
            # Remover R$ e espaços
            clean_price = price_text.replace('R$', '').replace(' ', '').strip()
            
            # Remover pontos de milhares e converter vírgula para ponto
            clean_price = clean_price.replace('.', '').replace(',', '.')
            
            # Extrair apenas números e ponto
            clean_price = re.sub(r'[^\d.]', '', clean_price)
            
            if not clean_price:
                return None
            
            return float(clean_price)
            
        except Exception as e:
            logger.debug(f"Erro ao parsear preço '{price_text}': {e}")
            return None
    
    def extract_product_id(self, url: str) -> Optional[str]:
        """Extrai ID do produto da URL Magazine Luiza"""
        patterns = [
            r'/p/(\d+)/',
            r'/produto/(\d+)/',
            r'p/(\d+)$',
            r'produto/(\d+)',
            r'(\d{6,})'  # ID genérico de 6+ dígitos
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    def convert_to_affiliate(self, product_url: str, product_id: Optional[str] = None) -> str:
        """Converte para link afiliado Magazine Luiza"""
        try:
            if not product_id:
                product_id = self.extract_product_id(product_url)
            
            if not product_id:
                logger.warning(f"Não foi possível extrair ID do produto: {product_url}")
                return product_url
            
            # Formato padrão Magazine Luiza afiliado
            affiliate_url = f"https://www.magazinevoce.com.br/{self.affiliate_id}/produto/{product_id}"
            
            # Adicionar tracking
            affiliate_url += "?utm_source=telegram&utm_medium=bot&utm_campaign=garimpeirogeek"
            
            logger.info(f"Link afiliado gerado: {affiliate_url}")
            return affiliate_url
            
        except Exception as e:
            logger.error(f"Erro ao gerar link afiliado: {e}")
            return product_url
    
    def _validate_offer(self, offer: Dict[str, Any], max_price: float, min_discount: int) -> bool:
        """Valida se a oferta atende aos critérios"""
        try:
            # Validar preço
            if offer["price"] > max_price:
                return False
            
            # Validar desconto mínimo
            if "discount_percent" in offer:
                if offer["discount_percent"] < min_discount:
                    return False
            
            # Validar dados obrigatórios
            required_fields = ["title", "price", "product_url", "product_id"]
            for field in required_fields:
                if not offer.get(field):
                    return False
            
            return True
            
        except Exception as e:
            logger.debug(f"Erro na validação da oferta: {e}")
            return False
    
    def _filter_offers(self, offers: List[Dict[str, Any]], max_price: float, min_discount: int) -> List[Dict[str, Any]]:
        """Filtra ofertas por critérios"""
        filtered = []
        
        for offer in offers:
            if self._validate_offer(offer, max_price, min_discount):
                filtered.append(offer)
        
        return filtered
    
    async def _get_simulated_offers(self, search_term: Optional[str], max_results: int) -> List[Dict[str, Any]]:
        """Retorna ofertas simuladas quando Playwright não está disponível"""
        logger.info("Usando modo simulado para Magazine Luiza")
        
        # Simular delay
        await asyncio.sleep(1)
        
        sample_offers = [
            {
                "title": "Smartphone Samsung Galaxy A54 5G 128GB",
                "price": 1999.99,
                "original_price": 2499.99,
                "discount_percent": 20,
                "product_url": "https://www.magazineluiza.com.br/smartphone-samsung-galaxy-a54-5g-128gb/p/123456",
                "product_id": "123456",
                "image_url": "https://example.com/galaxy-a54.jpg",
                "store": "magazineluiza",
                "source": "simulated"
            },
            {
                "title": "Notebook Dell Inspiron 15 3000 Intel i5",
                "price": 2799.99,
                "original_price": 3299.99,
                "discount_percent": 15,
                "product_url": "https://www.magazineluiza.com.br/notebook-dell-inspiron-15-3000/p/789012",
                "product_id": "789012",
                "image_url": "https://example.com/dell-inspiron.jpg",
                "store": "magazineluiza",
                "source": "simulated"
            },
            {
                "title": "Smart TV LG 55\" 4K UHD OLED",
                "price": 2499.99,
                "original_price": 3199.99,
                "discount_percent": 22,
                "product_url": "https://www.magazineluiza.com.br/smart-tv-lg-55-4k-uhd-oled/p/345678",
                "product_id": "345678",
                "image_url": "https://example.com/lg-55-oled.jpg",
                "store": "magazineluiza",
                "source": "simulated"
            }
        ]
        
        # Filtrar por termo de busca se especificado
        if search_term:
            search_lower = search_term.lower()
            sample_offers = [
                offer for offer in sample_offers
                if search_lower in offer["title"].lower()
            ]
        
        return sample_offers[:max_results]
    
    async def scrape_single_product(self, product_url: str) -> Optional[Dict[str, Any]]:
        """Extrai dados de um produto específico"""
        try:
            if not PLAYWRIGHT_AVAILABLE:
                logger.warning("Playwright não disponível para scraping individual")
                return None
            
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                
                try:
                    await page.goto(product_url, wait_until='domcontentloaded')
                    
                    # Aguardar carregamento
                    await page.wait_for_timeout(3000)
                    
                    # Extrair dados da página
                    product_data = await self._extract_single_product(page, product_url)
                    
                    return product_data
                    
                finally:
                    await browser.close()
                    
        except Exception as e:
            logger.error(f"Erro ao extrair produto individual: {e}")
            return None
    
    async def _extract_single_product(self, page, product_url: str) -> Optional[Dict[str, Any]]:
        """Extrai dados de uma página de produto individual"""
        try:
            # Título
            title_elem = await page.query_selector('h1, .product-title, .product-name')
            if not title_elem:
                return None
            
            title = await title_elem.text_content()
            
            # Preço
            price_elem = await page.query_selector('.price-value, .price, .current-price')
            if not price_elem:
                return None
            
            price_text = await price_elem.text_content()
            price = self._parse_price(price_text)
            
            # Preço original
            original_price = None
            original_elem = await page.query_selector('.price-original, .old-price, .list-price')
            if original_elem:
                original_text = await original_elem.text_content()
                original_price = self._parse_price(original_text)
            
            # Imagem
            image_url = None
            image_elem = await page.query_selector('.product-image img, .gallery-image img')
            if image_elem:
                image_url = await image_elem.get_attribute('src')
            
            # Extrair ID
            product_id = self.extract_product_id(product_url)
            
            # Criar dados do produto
            product_data = {
                "title": title.strip() if title else "Produto Magazine Luiza",
                "price": price,
                "original_price": original_price,
                "product_url": product_url,
                "product_id": product_id,
                "image_url": image_url,
                "store": "magazineluiza",
                "source": "single_product_scraper"
            }
            
            # Calcular desconto
            if original_price and original_price > price:
                discount_percent = int(((original_price - price) / original_price) * 100)
                product_data["discount_percent"] = discount_percent
            
            return product_data
            
        except Exception as e:
            logger.error(f"Erro ao extrair dados do produto individual: {e}")
            return None
    
    def get_scraper_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do scraper"""
        return {
            "name": "Magazine Luiza Scraper",
            "base_url": self.base_url,
            "affiliate_id": self.affiliate_id,
            "playwright_available": PLAYWRIGHT_AVAILABLE,
            "max_retries": self.max_retries,
            "rate_limit_delay": self.rate_limit_delay,
            "selectors": self.selectors
        }


# Instância global para uso em outros módulos
magazine_luiza_scraper = MagazineLuizaScraper()
