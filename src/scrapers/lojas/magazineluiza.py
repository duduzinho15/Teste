#!/usr/bin/env python3
"""
Scraper Avançado para Magazine Luiza
Usa Playwright para scraping real com rate limiting
"""

import asyncio
import os
import re
import logging
from datetime import datetime
from decimal import Decimal
from urllib.parse import urljoin, urlparse
from playwright.async_api import async_playwright
from src.core.models import Offer


class MagazineLuizaScraper:
    """Scraper e conversor para Magazine Luiza com Playwright"""
    
    def __init__(self):
        self.base_url = "https://www.magazineluiza.com.br"
        self.affiliate_id = os.getenv("MAGAZINELUIZA_AFFILIATE_ID", "magazinegarimpeirogeek")
        
        # Configurações de rate limiting
        self.delay = float(os.getenv("SCRAPER_DELAY", "3.0"))
        self.max_retries = int(os.getenv("SCRAPER_MAX_RETRIES", "3"))
        self.retry_delay = int(os.getenv("SCRAPER_RETRY_DELAY", "5"))
        
        # Configurações do Playwright
        self.headless = os.getenv("PLAYWRIGHT_HEADLESS", "true").lower() == "true"
        self.timeout = int(os.getenv("PLAYWRIGHT_TIMEOUT", "30000"))
        self.viewport_width = int(os.getenv("PLAYWRIGHT_VIEWPORT_WIDTH", "1920"))
        self.viewport_height = int(os.getenv("PLAYWRIGHT_VIEWPORT_HEIGHT", "1080"))
        
        # Logging
        self.logger = logging.getLogger("MagazineLuizaScraper")
        
        # User agents para rotação
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ]
    
    async def scrape_offers(self, search_term=None, max_price=3000, min_discount=20):
        """Coleta ofertas da Magazine Luiza com rate limiting"""
        offers = []
        
        # Verificar se scraping real está habilitado
        if not os.getenv("ENABLE_REAL_SCRAPING", "false").lower() == "true":
            self.logger.info("Scraping real desabilitado, retornando ofertas simuladas")
            return self._get_simulated_offers()
        
        self.logger.info(f"Iniciando scraping da Magazine Luiza - Termo: {search_term}, Preço max: R$ {max_price}")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=self.headless,
                args=[
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-blink-features=AutomationControlled"
                ]
            )
            
            page = await browser.new_page(
                viewport={"width": self.viewport_width, "height": self.viewport_height},
                user_agent=self.user_agents[0]
            )
            
            try:
                # Configurar timeout
                page.set_default_timeout(self.timeout)
                
                # URLs de busca
                urls = []
                if search_term:
                    urls.append(f"{self.base_url}/busca/{search_term}/")
                urls.extend([
                    f"{self.base_url}/ofertas/",
                    f"{self.base_url}/ofertas-do-dia/"
                ])
                
                for url in urls:
                    try:
                        self.logger.info(f"Acessando: {url}")
                        
                        # Rate limiting entre URLs
                        if len(offers) > 0:
                            await asyncio.sleep(self.delay)
                        
                        await page.goto(url, wait_until='domcontentloaded')
                        
                        # Aguardar carregamento dos produtos
                        try:
                            await page.wait_for_selector('[data-testid="product-card"], .product-card', timeout=10000)
                        except:
                            self.logger.warning(f"Timeout aguardando produtos em: {url}")
                            continue
                        
                        # Scroll para carregar mais produtos
                        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                        await asyncio.sleep(2)
                        
                        # Extrair produtos
                        products = await page.query_selector_all('[data-testid="product-card"], .product-card')
                        self.logger.info(f"Encontrados {len(products)} produtos em {url}")
                        
                        for i, product in enumerate(products[:20]):  # Limitar a 20 produtos por URL
                            try:
                                # Rate limiting entre produtos
                                if i > 0 and i % 5 == 0:
                                    await asyncio.sleep(self.delay)
                                
                                offer = await self._extract_product_data(product)
                                if offer and offer.price <= max_price:
                                    offers.append(offer)
                                    
                            except Exception as e:
                                self.logger.warning(f"Erro ao extrair produto {i}: {e}")
                                continue
                                
                    except Exception as e:
                        self.logger.error(f"Erro ao processar URL {url}: {e}")
                        continue
                        
            finally:
                await browser.close()
        
        self.logger.info(f"Scraping concluído: {len(offers)} ofertas coletadas")
        return offers
    
    async def _extract_product_data(self, product):
        """Extrai dados de um produto individual"""
        try:
            # Extrair título
            title_elem = await product.query_selector('h2, .product-title, [data-testid="product-title"]')
            if not title_elem:
                return None
            
            title = await title_elem.text_content()
            if not title or len(title.strip()) < 5:
                return None
            
            # Extrair preço
            price_elem = await product.query_selector('[data-testid="price-value"], .price-value, .price')
            if not price_elem:
                return None
            
            price_text = await price_elem.text_content()
            price = self._parse_price(price_text)
            if not price or price <= 0:
                return None
            
            # Extrair preço original
            original_elem = await product.query_selector('[data-testid="price-original"], .price-original, .old-price')
            original_price = None
            if original_elem:
                original_text = await original_elem.text_content()
                original_price = self._parse_price(original_text)
            
            # Extrair link
            link_elem = await product.query_selector('a')
            if not link_elem:
                return None
            
            product_url = await link_elem.get_attribute('href')
            if not product_url:
                return None
            
            if not product_url.startswith('http'):
                product_url = urljoin(self.base_url, product_url)
            
            # Extrair ID do produto
            product_id = self.extract_product_id(product_url)
            if not product_id:
                return None
            
            # Extrair imagem
            image_elem = await product.query_selector('img')
            image_url = None
            if image_elem:
                image_url = await image_elem.get_attribute('src')
                if image_url and not image_url.startswith('http'):
                    image_url = urljoin(self.base_url, image_url)
            
            # Converter para link afiliado
            affiliate_url = self.convert_to_affiliate(product_url, product_id)
            
            # Calcular desconto
            discount_percent = None
            if original_price and original_price > price:
                discount_percent = int(((original_price - price) / original_price) * 100)
            
            # Criar objeto Offer
            offer = Offer(
                title=title.strip(),
                price=Decimal(str(price)),
                original_price=Decimal(str(original_price)) if original_price else None,
                url=product_url,
                affiliate_url=affiliate_url,
                image_url=image_url,
                store="magazineluiza",
                category=self._categorize_product(title),
                discount_percentage=discount_percent,
                scraped_at=datetime.now()
            )
            
            return offer
            
        except Exception as e:
            self.logger.warning(f"Erro ao extrair dados do produto: {e}")
            return None
    
    def _parse_price(self, price_text):
        """Parse robusto de preços"""
        try:
            if not price_text:
                return None
            
            # Limpar texto
            price_text = price_text.strip()
            
            # Remover símbolos de moeda
            price_text = re.sub(r'[R$\s]', '', price_text)
            
            # Substituir vírgula por ponto
            price_text = price_text.replace(',', '.')
            
            # Extrair apenas números e ponto decimal
            price_text = re.sub(r'[^\d.]', '', price_text)
            
            # Garantir apenas um ponto decimal
            if price_text.count('.') > 1:
                parts = price_text.split('.')
                price_text = ''.join(parts[:-1]) + '.' + parts[-1]
            
            price = float(price_text)
            return price if price > 0 else None
            
        except (ValueError, AttributeError):
            return None
    
    def extract_product_id(self, url):
        """Extrai ID do produto da URL Magazine Luiza"""
        patterns = [
            r'/p/(\d+)/',
            r'/produto/(\d+)/',
            r'p/(\d+)$',
            r'produto/(\d+)$'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    def convert_to_affiliate(self, product_url, product_id):
        """Converte para link afiliado Magazine Luiza"""
        if not product_id:
            return product_url
        
        # Formato padrão Magazine Luiza afiliado
        affiliate_url = f"https://www.magazinevoce.com.br/{self.affiliate_id}/produto/{product_id}/"
        
        # Adicionar tracking
        affiliate_url += "?utm_source=telegram&utm_medium=bot&utm_campaign=garimpeirogeek"
        
        return affiliate_url
    
    def _categorize_product(self, title):
        """Categoriza produtos baseado no título"""
        title_lower = title.lower()
        
        categories = {
            "notebook": ["notebook", "laptop", "computador portátil"],
            "smartphone": ["celular", "smartphone", "iphone", "galaxy"],
            "tv": ["tv", "televisão", "smart tv", "televisor"],
            "eletrodomesticos": ["geladeira", "fogão", "microondas", "lavadora"],
            "games": ["playstation", "xbox", "nintendo", "controle", "jogo"],
            "audio": ["fone", "caixa de som", "headphone", "earphone"]
        }
        
        for category, keywords in categories.items():
            if any(keyword in title_lower for keyword in keywords):
                return category
        
        return "outros"
    
    def _get_simulated_offers(self):
        """Retorna ofertas simuladas quando scraping real está desabilitado"""
        return [
            Offer(
                title="Smartphone Samsung Galaxy S23 - 128GB",
                price=Decimal("2499.00"),
                original_price=Decimal("2999.00"),
                url="https://www.magazineluiza.com.br/smartphone-samsung-galaxy-s23-128gb/",
                affiliate_url="https://www.magazinevoce.com.br/magazinegarimpeirogeek/produto/123456/",
                image_url="https://a.magalucdn.com/mlstatic/123456.jpg",
                store="magazineluiza",
                category="smartphone",
                discount_percentage=17.0,
                scraped_at=datetime.now()
            ),
            Offer(
                title="Notebook Dell Inspiron 15 - Intel i5",
                price=Decimal("3499.00"),
                original_price=Decimal("3999.00"),
                url="https://www.magazineluiza.com.br/notebook-dell-inspinet-15/",
                affiliate_url="https://www.magazinevoce.com.br/magazinegarimpeirogeek/produto/789012/",
                image_url="https://a.magalucdn.com/mlstatic/789012.jpg",
                store="magazineluiza",
                category="notebook",
                discount_percentage=13.0,
                scraped_at=datetime.now()
            )
        ]
    
    async def health_check(self):
        """Verifica saúde do scraper"""
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                
                await page.goto(f"{self.base_url}/ofertas/", timeout=10000)
                await page.wait_for_selector('[data-testid="product-card"], .product-card', timeout=5000)
                
                await browser.close()
                return True
                
        except Exception as e:
            self.logger.error(f"Health check falhou: {e}")
            return False
