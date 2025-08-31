#!/usr/bin/env python3
"""
Scraper Avançado para Amazon com ASIN
Usa Playwright para scraping real com rate limiting
"""

import asyncio
import os
import re
import logging
from datetime import datetime
from decimal import Decimal
from urllib.parse import urlparse, parse_qs
from playwright.async_api import async_playwright
from src.core.models import Offer

class AmazonASINScraper:
    """Scraper Amazon com conversão via ASIN usando Playwright"""
    
    def __init__(self):
        self.base_url = "https://www.amazon.com.br"
        self.affiliate_tag = os.getenv("AMAZON_AFFILIATE_TAG", "garimpeirogee-20")
        
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
        self.logger = logging.getLogger("AmazonASINScraper")
        
        # User agents para rotação
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ]
        
        # Headers customizados para evitar detecção
        self.custom_headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }
    
    async def scrape_offers(self, search_term=None, max_price=3000, min_discount=20):
        """Coleta ofertas da Amazon via ASIN com rate limiting"""
        offers = []
        
        # Verificar se scraping real está habilitado
        if not os.getenv("ENABLE_REAL_SCRAPING", "false").lower() == "true":
            self.logger.info("Scraping real desabilitado, retornando ofertas simuladas")
            return self._get_simulated_offers()
        
        self.logger.info(f"Iniciando scraping da Amazon - Termo: {search_term}, Preço max: R$ {max_price}")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=self.headless,
                args=[
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-blink-features=AutomationControlled",
                    "--disable-web-security",
                    "--disable-features=VizDisplayCompositor"
                ]
            )
            
            page = await browser.new_page(
                viewport={"width": self.viewport_width, "height": self.viewport_height},
                user_agent=self.user_agents[0]
            )
            
            try:
                # Configurar timeout
                page.set_default_timeout(self.timeout)
                
                # Configurar headers customizados
                await page.set_extra_http_headers(self.custom_headers)
                
                # URLs de busca
                urls = []
                if search_term:
                    urls.append(f"{self.base_url}/s?k={search_term}")
                urls.extend([
                    f"{self.base_url}/gp/goldbox",
                    f"{self.base_url}/s?k=ofertas",
                    f"{self.base_url}/s?k=promocoes"
                ])
                
                for url in urls:
                    try:
                        self.logger.info(f"Acessando: {url}")
                        
                        # Rate limiting entre URLs
                        if len(offers) > 0:
                            await asyncio.sleep(self.delay)
                        
                        await page.goto(url, wait_until='domcontentloaded')
                        
                        # Aguardar carregamento da página
                        await page.wait_for_timeout(3000)
                        
                        # Scroll para carregar mais produtos
                        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                        await page.wait_for_timeout(2000)
                        
                        # Selecionar produtos
                        products = await page.query_selector_all('[data-asin]')
                        self.logger.info(f"Encontrados {len(products)} produtos em {url}")
                        
                        for i, product in enumerate(products[:15]):  # Limitar a 15 produtos por URL
                            try:
                                # Rate limiting entre produtos
                                if i > 0 and i % 3 == 0:
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
            # Extrair ASIN
            asin = await product.get_attribute('data-asin')
            if not asin or len(asin) != 10:
                return None
            
            # Extrair título
            title_elem = await product.query_selector('h2 a span, .s-title-instructions-style span, .a-size-medium')
            if not title_elem:
                return None
            
            title = await title_elem.text_content()
            if not title or len(title.strip()) < 5:
                return None
            
            # Extrair preço
            price_elem = await product.query_selector('.a-price-whole, .a-price .a-offscreen')
            if not price_elem:
                return None
            
            price_text = await price_elem.text_content()
            price = self._parse_price(price_text)
            if not price or price <= 0:
                return None
            
            # Extrair preço original
            original_elem = await product.query_selector('.a-price.a-text-price .a-offscreen, .a-text-strike')
            original_price = None
            if original_elem:
                original_text = await original_elem.text_content()
                original_price = self._parse_price(original_text)
            
            # Extrair link
            link_elem = await product.query_selector('h2 a, .a-link-normal')
            if not link_elem:
                return None
            
            relative_url = await link_elem.get_attribute('href')
            if not relative_url:
                return None
            
            product_url = f"{self.base_url}{relative_url}"
            
            # Extrair imagem
            image_elem = await product.query_selector('img')
            image_url = None
            if image_elem:
                image_url = await image_elem.get_attribute('src')
                if image_url and not image_url.startswith('http'):
                    image_url = f"https:{image_url}"
            
            # Converter para link afiliado
            affiliate_url = self.convert_to_affiliate(asin)
            
            # Calcular desconto
            discount_percentage = None
            if original_price and original_price > price:
                discount_percentage = float(((original_price - price) / original_price) * 100)
            
            # Criar objeto Offer
            offer = Offer(
                title=title.strip(),
                price=Decimal(str(price)),
                original_price=Decimal(str(original_price)) if original_price else None,
                url=product_url,
                affiliate_url=affiliate_url,
                image_url=image_url,
                store="amazon",
                category=self._categorize_product(title),
                discount_percentage=discount_percentage,
                scraped_at=datetime.now()
            )
            
            return offer
            
        except Exception as e:
            self.logger.warning(f"Erro ao extrair dados do produto: {e}")
            return None
    
    def _parse_price(self, price_text):
        """Parse robusto de preços da Amazon"""
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
    
    def convert_to_affiliate(self, asin):
        """Converte ASIN para link afiliado Amazon"""
        if not asin:
            return None
        
        # Formato padrão Amazon afiliado
        affiliate_url = f"https://www.amazon.com.br/dp/{asin}?tag={self.affiliate_tag}"
        
        # Adicionar tracking
        affiliate_url += "&linkCode=ogi&th=1&psc=1"
        
        return affiliate_url
    
    def extract_asin_from_url(self, url):
        """Extrai ASIN de qualquer URL Amazon"""
        patterns = [
            r'/dp/([A-Z0-9]{10})',
            r'/gp/product/([A-Z0-9]{10})',
            r'ASIN=([A-Z0-9]{10})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    def _categorize_product(self, title):
        """Categoriza produtos baseado no título"""
        title_lower = title.lower()
        
        categories = {
            "notebook": ["notebook", "laptop", "computador portátil", "macbook"],
            "smartphone": ["iphone", "galaxy", "smartphone", "celular", "mobile"],
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
    
    def _get_simulated_offers(self):
        """Retorna ofertas simuladas quando scraping real está desabilitado"""
        return [
            Offer(
                title="iPhone 15 Pro Max - 256GB - Titânio Natural",
                price=Decimal("8999.00"),
                original_price=Decimal("9999.00"),
                url="https://www.amazon.com.br/iPhone-15-Pro-Max-256GB/dp/B0CHX3V7QM",
                affiliate_url="https://www.amazon.com.br/dp/B0CHX3V7QM?tag=garimpeirogee-20",
                image_url="https://m.media-amazon.com/images/I/71C-HJ7KzQL._AC_SL1500_.jpg",
                store="amazon",
                category="smartphone",
                discount_percentage=10.0,
                scraped_at=datetime.now()
            ),
            Offer(
                title="Samsung Galaxy S23 Ultra - 256GB - Verde",
                price=Decimal("5499.00"),
                original_price=Decimal("6499.00"),
                url="https://www.amazon.com.br/Samsung-Galaxy-Ultra-256GB-Verde/dp/B0BSJQVLBL",
                affiliate_url="https://www.amazon.com.br/dp/B0BSJQVLBL?tag=garimpeirogee-20",
                image_url="https://m.media-amazon.com/images/I/71P9NpnsuEL._AC_SL1500_.jpg",
                store="amazon",
                category="smartphone",
                discount_percentage=15.0,
                scraped_at=datetime.now()
            )
        ]
    
    async def health_check(self):
        """Verifica saúde do scraper"""
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                
                await page.goto(f"{self.base_url}/gp/goldbox", timeout=10000)
                await page.wait_for_selector('[data-asin]', timeout=5000)
                
                await browser.close()
                return True
                
        except Exception as e:
            self.logger.error(f"Health check falhou: {e}")
            return False
