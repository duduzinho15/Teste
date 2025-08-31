#!/usr/bin/env python3
"""
Scraper Automático do Mercado Livre
Coleta as melhores ofertas para serem postadas no Telegram
"""

import asyncio
import logging
import re
from datetime import datetime
from typing import Any, Dict, List, Optional
from decimal import Decimal
from urllib.parse import urljoin, urlparse

import aiohttp
from bs4 import BeautifulSoup

from src.scrapers.base_scraper import BaseScraper
from src.core.models import Offer
from src.utils.anti_bot import AntiBotUtils


class MercadoLivreScraper(BaseScraper):
    """Scraper automático para o Mercado Livre"""
    
    def __init__(self):
        super().__init__(
            name="mercadolivre_scraper",
            base_url="https://www.mercadolivre.com.br",
            enabled=True
        )
        
        # Configurações específicas
        self.session: Optional[aiohttp.ClientSession] = None
        self.anti_bot = AntiBotUtils()
        
        # Headers para simular navegador
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }
        
        # Categorias de interesse para ofertas
        self.target_categories = [
            "smartphones", "notebooks", "smart-tvs", "consoles", "fones-de-ouvido",
            "tablets", "monitores", "perifericos", "games", "eletronicos"
        ]
        
        # Filtros de qualidade
        self.min_discount_percent = 10  # Desconto mínimo de 10%
        self.max_price = 5000.0  # Preço máximo de R$ 5.000
        self.min_rating = 4.0  # Avaliação mínima de 4.0
        
        self.logger.info("Scraper Mercado Livre inicializado")

    async def __aenter__(self):
        """Context manager entry"""
        self.session = aiohttp.ClientSession(
            headers=self.headers,
            timeout=aiohttp.ClientTimeout(total=30)
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if self.session:
            await self.session.close()

    async def scrape(self, query: str = "", max_results: int = 50) -> List[Offer]:
        """
        Scrapes produtos do Mercado Livre
        
        Args:
            query: Termo de busca (opcional)
            max_results: Máximo de resultados
            
        Returns:
            Lista de ofertas encontradas
        """
        try:
            if query:
                self.logger.info(f"Buscando produtos: {query}")
                offers = await self._search_products(query, max_results)
            else:
                self.logger.info("Buscando ofertas em destaque")
                offers = await self._get_featured_offers(max_results)
            
            # Filtrar por qualidade
            filtered_offers = self._filter_by_quality(offers)
            
            self.logger.info(f"Encontradas {len(filtered_offers)} ofertas de qualidade")
            return filtered_offers
            
        except Exception as e:
            self.logger.error(f"Erro no scraping: {e}")
            return []

    async def _search_products(self, query: str, max_results: int) -> List[Offer]:
        """Busca produtos por termo específico"""
        offers = []
        
        try:
            # Construir URL de busca
            search_url = f"{self.base_url}/search?q={query}"
            
            async with self.session.get(search_url) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Extrair produtos da página de resultados
                    product_items = soup.find_all('div', class_='ui-search-result__content')
                    
                    for item in product_items[:max_results]:
                        try:
                            offer = self._parse_product_item(item)
                            if offer:
                                offers.append(offer)
                        except Exception as e:
                            self.logger.warning(f"Erro ao parsear item: {e}")
                            continue
                            
        except Exception as e:
            self.logger.error(f"Erro na busca: {e}")
            
        return offers

    async def _get_featured_offers(self, max_results: int) -> List[Offer]:
        """Obtém ofertas em destaque das categorias principais"""
        offers = []
        
        for category in self.target_categories[:5]:  # Limitar a 5 categorias
            try:
                category_offers = await self._scrape_category_offers(category, max_results // 5)
                offers.extend(category_offers)
                
                # Delay para evitar rate limiting
                await asyncio.sleep(2)
                
            except Exception as e:
                self.logger.error(f"Erro ao scrapear categoria {category}: {e}")
                continue
                
        return offers

    async def _scrape_category_offers(self, category: str, max_results: int) -> List[Offer]:
        """Scrapes ofertas de uma categoria específica"""
        offers = []
        
        try:
            # URL da categoria com filtros de ofertas
            category_url = f"{self.base_url}/{category}/_Promocao_*"
            
            async with self.session.get(category_url) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Extrair produtos em promoção
                    promo_items = soup.find_all('div', class_='promotion-item')
                    
                    for item in promo_items[:max_results]:
                        try:
                            offer = self._parse_promotion_item(item)
                            if offer:
                                offers.append(offer)
                        except Exception as e:
                            self.logger.warning(f"Erro ao parsear promoção: {e}")
                            continue
                            
        except Exception as e:
            self.logger.error(f"Erro ao scrapear categoria {category}: {e}")
            
        return offers

    def _parse_product_item(self, item) -> Optional[Offer]:
        """Parseia um item de produto da busca"""
        try:
            # Extrair título
            title_elem = item.find('h2', class_='ui-search-item__title')
            if not title_elem:
                return None
            title = title_elem.get_text(strip=True)
            
            # Extrair URL
            link_elem = item.find('a', class_='ui-search-item__group__element')
            if not link_elem:
                return None
            url = link_elem.get('href')
            
            # Extrair preço
            price_elem = item.find('span', class_='andes-money-amount__fraction')
            if not price_elem:
                return None
            price = self._extract_price(price_elem.get_text(strip=True))
            
            # Extrair preço original (se houver desconto)
            original_price = None
            original_elem = item.find('span', class_='andes-money-amount--previous')
            if original_elem:
                original_price = self._extract_price(original_elem.get_text(strip=True))
            
            # Extrair imagem
            img_elem = item.find('img')
            image_url = img_elem.get('src') if img_elem else None
            
            # Extrair desconto
            discount = None
            if original_price and price:
                discount = ((original_price - price) / original_price) * 100
            
            # Extrair avaliação
            rating = 0.0
            rating_elem = item.find('span', class_='ui-search-reviews__rating-number')
            if rating_elem:
                rating_text = rating_elem.get_text(strip=True)
                rating = float(rating_text.replace(',', '.'))
            
            # Criar oferta
            offer = Offer(
                title=title,
                price=Decimal(str(price)),
                original_price=Decimal(str(original_price)) if original_price else None,
                url=url,
                store="Mercado Livre",
                image_url=image_url,
                source="mercadolivre_scraper",
                store_data={
                    "platform": "mercadolivre",
                    "category": self._extract_category_from_url(url),
                    "discount_percent": discount,
                    "rating": rating,
                    "needs_conversion": True,  # Flag para conversão manual
                    "scraped_at": datetime.now().isoformat()
                }
            )
            
            return offer
            
        except Exception as e:
            self.logger.error(f"Erro ao parsear produto: {e}")
            return None

    def _parse_promotion_item(self, item) -> Optional[Offer]:
        """Parseia um item de promoção"""
        try:
            # Similar ao _parse_product_item mas para itens em promoção
            # Implementação específica para promoções
            return self._parse_product_item(item)
        except Exception as e:
            self.logger.error(f"Erro ao parsear promoção: {e}")
            return None

    def _extract_price(self, price_text: str) -> float:
        """Extrai preço do texto"""
        try:
            # Remove símbolos e converte para float
            price_clean = re.sub(r'[^\d,.]', '', price_text)
            price_clean = price_clean.replace(',', '.')
            return float(price_clean)
        except:
            return 0.0

    def _extract_category_from_url(self, url: str) -> str:
        """Extrai categoria da URL"""
        try:
            parsed = urlparse(url)
            path_parts = parsed.path.split('/')
            if len(path_parts) > 1:
                return path_parts[1]
        except:
            pass
        return "geral"

    def _filter_by_quality(self, offers: List[Offer]) -> List[Offer]:
        """Filtra ofertas por critérios de qualidade"""
        filtered = []
        
        for offer in offers:
            # Verificar desconto mínimo
            if offer.store_data.get("discount_percent", 0) < self.min_discount_percent:
                continue
                
            # Verificar preço máximo
            if offer.price > self.max_price:
                continue
                
            # Verificar avaliação mínima
            if offer.store_data.get("rating", 0) < self.min_rating:
                continue
                
            # Verificar se precisa de conversão
            if not offer.store_data.get("needs_conversion", False):
                continue
                
            filtered.append(offer)
            
        return filtered

    def parse_offer(self, raw_data: Any) -> Dict[str, Any]:
        """Implementa método abstrato da classe base"""
        # Este método é implementado pelos métodos específicos _parse_product_item
        # e _parse_promotion_item
        pass

    async def run(self, query: str = "", max_results: int = 50) -> List[Offer]:
        """Executa o scraper"""
        async with self:
            return await self.scrape(query, max_results)


# Função de conveniência para uso externo
async def get_mercadolivre_scraper() -> MercadoLivreScraper:
    """Retorna instância do scraper do Mercado Livre"""
    return MercadoLivreScraper()


if __name__ == "__main__":
    # Teste do scraper
    async def test():
        scraper = MercadoLivreScraper()
        offers = await scraper.run("smartphone", 5)
        print(f"Encontradas {len(offers)} ofertas")
        for offer in offers:
            print(f"- {offer.title}: R$ {offer.price}")
    
    asyncio.run(test())
