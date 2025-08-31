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
        
        # Headers realistas para contornar bloqueio anti-bot
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "max-age=0",
            "Referer": "https://www.mercadolivre.com.br/",
            "sec-ch-ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"'
        }
        
        # URLs específicas para ofertas e outlet
        self.target_urls = [
            "https://www.mercadolivre.com.br/ofertas",
            "https://www.mercadolivre.com.br/ofertas/outlet",
            "https://lista.mercadolivre.com.br/celulares-telefones/celulares-smartphones/_Container_outlet",
            "https://lista.mercadolivre.com.br/eletronicos-audio-video/televisores/_Container_outlet_NoIndex_True",
            "https://lista.mercadolivre.com.br/_Container_outlet-tech"
        ]
        
        # Categorias de interesse para ofertas
        self.target_categories = [
            "smartphones", "notebooks", "smart-tvs", "consoles", "fones-de-ouvido",
            "tablets", "monitores", "perifericos", "games", "eletronicos"
        ]
        
        # Filtros de qualidade (menos restritivos para teste)
        self.min_discount_percent = 5   # Desconto mínimo de 5%
        self.max_price = 10000.0        # Preço máximo de R$ 10.000
        self.min_rating = 3.5           # Avaliação mínima de 3.5
        
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
            # Inicializar sessão se não existir
            if not self.session:
                self.session = aiohttp.ClientSession(
                    headers=self.headers,
                    timeout=aiohttp.ClientTimeout(total=30)
                )
                self.logger.info("Sessão HTTP inicializada")
            
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
            self.logger.info(f"Buscando em: {search_url}")
            
            if not self.session:
                self.logger.error("Sessão HTTP não inicializada")
                return offers
            
            async with self.session.get(search_url) as response:
                self.logger.info(f"Status da resposta: {response.status}")
                
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Log do HTML para debug
                    self.logger.info(f"HTML recebido: {len(html)} caracteres")
                    
                    # Extrair produtos da página de resultados
                    product_items = soup.find_all('div', class_='ui-search-result__content')
                    self.logger.info(f"Encontrados {len(product_items)} itens de produto")
                    
                    # Se não encontrar com a classe específica, tentar outras
                    if not product_items:
                        product_items = soup.find_all('div', class_='ui-search-result')
                        self.logger.info(f"Tentativa alternativa: {len(product_items)} itens encontrados")
                    
                    if not product_items:
                        product_items = soup.find_all('div', {'data-testid': 'search-result'})
                        self.logger.info(f"Tentativa com data-testid: {len(product_items)} itens encontrados")
                    
                    for item in product_items[:max_results]:
                        try:
                            offer = self._parse_product_item(item)
                            if offer:
                                offers.append(offer)
                        except Exception as e:
                            self.logger.warning(f"Erro ao parsear item: {e}")
                            continue
                else:
                    self.logger.error(f"Resposta HTTP não OK: {response.status}")
                            
        except Exception as e:
            self.logger.error(f"Erro na busca: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            
        return offers

    async def _get_featured_offers(self, max_results: int) -> List[Offer]:
        """Obtém ofertas em destaque das URLs específicas"""
        offers = []
        
        for url in self.target_urls[:3]:  # Limitar a 3 URLs principais
            try:
                self.logger.info(f"Scrapeando ofertas de: {url}")
                # Garantir que max_results seja pelo menos 1
                url_max_results = max(1, max_results // 3)
                url_offers = await self._scrape_url_offers(url, url_max_results)
                offers.extend(url_offers)
                
                # Delay para evitar rate limiting
                await asyncio.sleep(2)
                
            except Exception as e:
                self.logger.error(f"Erro ao scrapear URL {url}: {e}")
                continue
                
        return offers

    async def _scrape_url_offers(self, url: str, max_results: int) -> List[Offer]:
        """Scrapes ofertas de uma URL específica"""
        offers = []
        
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # NOVO: Usar seletores corretos identificados na análise HTML
                    product_items = soup.select('div.andes-card.poly-card.poly-card--grid-card')
                    
                    if not product_items:
                        # Fallback para seletores alternativos
                        product_items = soup.select('div[class*="poly-card"]')
                        self.logger.info(f"Fallback: encontrados {len(product_items)} itens com poly-card")
                    
                    if not product_items:
                        # Fallback adicional
                        product_items = soup.find_all('div', class_=lambda x: x and ('card' in x.lower() or 'product' in x.lower()))
                        self.logger.info(f"Fallback adicional: encontrados {len(product_items)} itens")
                    
                    self.logger.info(f"Encontrados {len(product_items)} produtos para parsear")
                    
                    for i, item in enumerate(product_items[:max_results]):
                        try:
                            self.logger.debug(f"Parseando item {i+1}/{min(len(product_items), max_results)}")
                            offer = self._parse_product_item_updated(item)
                            if offer:
                                offers.append(offer)
                                self.logger.debug(f"✅ Item {i+1} parseado com sucesso")
                            else:
                                self.logger.debug(f"❌ Item {i+1} não pôde ser parseado")
                        except Exception as e:
                            self.logger.debug(f"Erro ao parsear item {i+1}: {e}")
                            continue
                            
        except Exception as e:
            self.logger.error(f"Erro ao scrapear URL {url}: {e}")
            
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

    def _parse_product_item_updated(self, item) -> Optional[Offer]:
        """Parseia um item de produto com seletores atualizados"""
        try:
            self.logger.debug(f"Tentando parsear item: {type(item)}")
            
            # NOVO: Extrair título usando seletor correto
            title_elem = item.select_one('h3.poly-component__title-wrapper a.poly-component__title')
            if not title_elem:
                # Fallback para seletores alternativos
                title_elem = item.select_one('a[class*="title"]')
            
            if not title_elem:
                self.logger.debug("❌ Título não encontrado")
                return None
            
            title = title_elem.get_text(strip=True)
            self.logger.debug(f"✅ Título encontrado: {title[:50]}...")
            
            # NOVO: Extrair URL do link do título
            url = title_elem.get('href')
            if not url:
                self.logger.debug("❌ URL não encontrada")
                return None
            
            # Garantir URL absoluta
            if url.startswith('/'):
                url = f"https://www.mercadolivre.com.br{url}"
            
            self.logger.debug(f"✅ URL encontrada: {url[:100]}...")
            
            # NOVO: Extrair preço atual usando seletor correto
            price_elem = item.select_one('div.poly-price__current span.andes-money-amount')
            if not price_elem:
                # Fallback para seletores alternativos
                price_elem = item.select_one('span[class*="andes-money-amount"]')
            
            if not price_elem:
                self.logger.debug("❌ Preço não encontrado")
                return None
            
            price = self._extract_price(price_elem.get_text(strip=True))
            if price <= 0:
                self.logger.debug("❌ Preço inválido")
                return None
            
            self.logger.debug(f"✅ Preço encontrado: R$ {price}")
            
            # NOVO: Extrair preço original usando seletor correto
            original_price = None
            original_elem = item.select_one('s.andes-money-amount.andes-money-amount--previous')
            if original_elem:
                original_price = self._extract_price(original_elem.get_text(strip=True))
                if original_price > 0:
                    self.logger.debug(f"✅ Preço original encontrado: R$ {original_price}")
            
            # NOVO: Extrair desconto usando seletor correto
            discount = None
            discount_elem = item.select_one('span.andes-money-amount__discount')
            if discount_elem:
                discount_text = discount_elem.get_text(strip=True)
                # Extrair número do texto "26% OFF"
                discount_match = re.search(r'(\d+)%', discount_text)
                if discount_match:
                    discount = float(discount_match.group(1))
                    self.logger.debug(f"✅ Desconto encontrado: {discount}%")
            
            # Calcular desconto se não encontrado mas temos preço original
            if not discount and original_price and price and original_price > price:
                discount = ((original_price - price) / original_price) * 100
                self.logger.debug(f"✅ Desconto calculado: {discount:.1f}%")
            
            # NOVO: Extrair imagem usando seletor correto
            img_elem = item.select_one('img.poly-component__picture')
            if not img_elem:
                img_elem = item.find('img')
            
            image_url = img_elem.get('src') if img_elem else None
            if image_url and image_url.startswith('data:'):
                # Imagem lazy-loaded, tentar data-src
                image_url = img_elem.get('data-src')
            
            # NOVO: Extrair avaliação usando seletor correto
            rating = 0.0
            rating_elem = item.select_one('span.poly-reviews__rating')
            if rating_elem:
                try:
                    rating = float(rating_elem.get_text(strip=True).replace(',', '.'))
                    self.logger.debug(f"✅ Avaliação encontrada: {rating}")
                except:
                    pass
            
            # NOVO: Extrair marca usando seletor correto
            brand = None
            brand_elem = item.select_one('span.poly-component__brand')
            if brand_elem:
                brand = brand_elem.get_text(strip=True)
                self.logger.debug(f"✅ Marca encontrada: {brand}")
            
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
                    "brand": brand,
                    "needs_conversion": True,  # Flag para conversão manual
                    "scraped_at": datetime.now().isoformat()
                }
            )
            
            self.logger.debug(f"✅ Oferta criada com sucesso: {title[:30]}... - R$ {price}")
            return offer
            
        except Exception as e:
            self.logger.error(f"Erro ao parsear produto: {e}")
            import traceback
            self.logger.debug(f"Traceback: {traceback.format_exc()}")
            return None

    def _parse_product_item(self, item) -> Optional[Offer]:
        """Parseia um item de produto da busca (método legado)"""
        # Usar o novo método atualizado
        return self._parse_product_item_updated(item)

    def _parse_promotion_item(self, item) -> Optional[Offer]:
        """Parseia um item de promoção"""
        try:
            # Similar ao _parse_product_item mas para itens em promoção
            # Implementação específica para promoções
            return self._parse_product_item_updated(item)
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
        
        self.logger.info(f"Filtrando {len(offers)} ofertas com critérios: desconto>={self.min_discount_percent}%, preço<={self.max_price}, rating>={self.min_rating}")
        
        for i, offer in enumerate(offers):
            try:
                self.logger.debug(f"Oferta {i+1}: {offer.title[:50]}... - Preço: R$ {offer.price}, Desconto: {offer.store_data.get('discount_percent', 'N/A')}%, Rating: {offer.store_data.get('rating', 'N/A')}")
                
                # Verificar desconto mínimo
                discount = offer.store_data.get("discount_percent", 0)
                if discount < self.min_discount_percent:
                    self.logger.debug(f"  ❌ Desconto insuficiente: {discount}% < {self.min_discount_percent}%")
                    continue
                    
                # Verificar preço máximo
                if offer.price > self.max_price:
                    self.logger.debug(f"  ❌ Preço muito alto: R$ {offer.price} > R$ {self.max_price}")
                    continue
                    
                # Verificar avaliação mínima
                rating = offer.store_data.get("rating", 0)
                if rating < self.min_rating:
                    self.logger.debug(f"  ❌ Rating baixo: {rating} < {self.min_rating}")
                    continue
                    
                # Verificar se precisa de conversão
                if not offer.store_data.get("needs_conversion", False):
                    self.logger.debug(f"  ❌ Não precisa de conversão")
                    continue
                
                self.logger.debug(f"  ✅ Oferta aprovada!")
                filtered.append(offer)
                
            except Exception as e:
                self.logger.warning(f"Erro ao filtrar oferta {offer.title if offer.title else 'sem título'}: {e}")
                continue
        
        self.logger.info(f"Filtradas {len(filtered)} ofertas de {len(offers)}")
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
