"""
Cliente API oficial do Awin Publisher
Implementa Link Builder API e Product Feed para geração de deeplinks
"""

import json
import logging
import asyncio
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from decimal import Decimal

from affiliate.base_api import BaseAPI
from core.models import Offer

logger = logging.getLogger(__name__)


@dataclass
class AwinAdvertiser:
    """Configuração de anunciante Awin"""
    mid: str
    name: str
    category: str
    enabled: bool = True
    min_discount: int = 10
    max_price: float = 1000.0


@dataclass
class AwinOffer:
    """Oferta coletada via API Awin"""
    title: str
    price: float
    original_price: Optional[float]
    discount_percentage: Optional[int]
    store: str
    category: str
    url: str
    image_url: Optional[str]
    description: Optional[str]
    availability: bool
    advertiser_id: str
    collected_at: datetime


class AwinOffersCollector:
    """Coletor automático de ofertas via API Awin"""
    
    def __init__(self, publisher_id: str, access_token: str):
        """
        Inicializa coletor de ofertas Awin
        
        Args:
            publisher_id: ID do publisher Awin
            access_token: Token de acesso OAuth2
        """
        self.publisher_id = publisher_id
        self.access_token = access_token
        self.client = AwinAPIClient(publisher_id, access_token)
        
        # Configuração das 7 afiliações ativas
        self.advertisers = {
            "comfy": AwinAdvertiser("23377", "COMFY", "eletronicos", min_discount=15, max_price=2000.0),
            "trocafy": AwinAdvertiser("51277", "Trocafy", "informatica", min_discount=20, max_price=1500.0),
            "lg": AwinAdvertiser("33061", "LG", "eletronicos", min_discount=25, max_price=3000.0),
            "kabum": AwinAdvertiser("17729", "Kabum", "informatica", min_discount=10, max_price=1000.0),
            "samsung": AwinAdvertiser("25539", "Samsung", "eletronicos", min_discount=20, max_price=2500.0),
            "gigantec": AwinAdvertiser("106765", "Gigantec", "informatica", min_discount=15, max_price=1200.0),
            "ninja": AwinAdvertiser("106765", "Ninja", "games", min_discount=30, max_price=800.0)
        }
        
        # Filtros automáticos
        self.filters = {
            "min_discount": 10,
            "max_price": 1000.0,
            "categories": ["eletronicos", "informatica", "games", "casa", "moda"],
            "excluded_stores": [],
            "min_availability": True
        }
        
        # Estatísticas
        self.stats = {
            "total_collected": 0,
            "valid_offers": 0,
            "filtered_out": 0,
            "errors": 0,
            "last_collection": None
        }
    
    async def collect_all_offers(self, max_offers_per_advertiser: int = 50) -> List[Offer]:
        """
        Coleta ofertas de todos os anunciantes ativos
        
        Args:
            max_offers_per_advertiser: Máximo de ofertas por anunciante
            
        Returns:
            Lista de ofertas válidas convertidas para modelo Offer
        """
        try:
            logger.info(f"🚀 Iniciando coleta automática de ofertas Awin")
            logger.info(f"📊 Anunciantes ativos: {len([a for a in self.advertisers.values() if a.enabled])}")
            
            all_offers = []
            
            # Coletar ofertas de cada anunciante
            for store_key, advertiser in self.advertisers.items():
                if not advertiser.enabled:
                    continue
                    
                logger.info(f"🛍️ Coletando ofertas de {advertiser.name} (MID: {advertiser.mid})")
                
                try:
                    # Coletar ofertas do anunciante
                    advertiser_offers = await self._collect_advertiser_offers(
                        advertiser, max_offers_per_advertiser
                    )
                    
                    if advertiser_offers:
                        # Aplicar filtros específicos do anunciante
                        filtered_offers = await self._apply_advertiser_filters(
                            advertiser_offers, advertiser
                        )
                        
                        # Converter para modelo Offer
                        converted_offers = await self._convert_to_offers(filtered_offers, store_key)
                        
                        all_offers.extend(converted_offers)
                        logger.info(f"✅ {advertiser.name}: {len(converted_offers)} ofertas válidas")
                    else:
                        logger.warning(f"⚠️ {advertiser.name}: Nenhuma oferta coletada")
                        
                except Exception as e:
                    logger.error(f"❌ Erro ao coletar de {advertiser.name}: {e}")
                    self.stats["errors"] += 1
                
                # Rate limiting entre anunciantes
                await asyncio.sleep(2)
            
            # Aplicar filtros globais
            final_offers = await self._apply_global_filters(all_offers)
            
            # Atualizar estatísticas
            self.stats["total_collected"] = len(all_offers)
            self.stats["valid_offers"] = len(final_offers)
            self.stats["filtered_out"] = len(all_offers) - len(final_offers)
            self.stats["last_collection"] = datetime.now()
            
            logger.info(f"🎯 Coleta concluída: {len(final_offers)} ofertas válidas de {len(all_offers)} coletadas")
            
            return final_offers
            
        except Exception as e:
            logger.error(f"❌ Erro na coleta automática: {e}")
            self.stats["errors"] += 1
            return []
    
    async def _collect_advertiser_offers(self, advertiser: AwinAdvertiser, max_offers: int) -> List[AwinOffer]:
        """Coleta ofertas de um anunciante específico"""
        try:
            # Tentar obter via Product Feed API primeiro
            products = await self.client.get_product_feed(advertiser.mid)
            
            if products:
                return await self._parse_product_feed(products, advertiser, max_offers)
            
            # Fallback: tentar via Link Builder API
            logger.info(f"🔄 Fallback para Link Builder API: {advertiser.name}")
            return await self._collect_via_link_builder(advertiser, max_offers)
            
        except Exception as e:
            logger.error(f"❌ Erro ao coletar ofertas de {advertiser.name}: {e}")
            return []
    
    async def _parse_product_feed(self, products: List[Dict], advertiser: AwinAdvertiser, max_offers: int) -> List[AwinOffer]:
        """Parse do feed de produtos"""
        offers = []
        
        for product in products[:max_offers]:
            try:
                # Extrair dados do produto
                title = product.get("title", "")
                price = Decimal(str(product.get("price", 0)))
                original_price = product.get("original_price")
                if original_price:
                    original_price = Decimal(str(original_price))
                
                # Calcular desconto
                discount_percentage = None
                if original_price and original_price > price:
                    discount_percentage = int(((original_price - price) / original_price) * 100)
                
                # Criar oferta Awin
                offer = AwinOffer(
                    title=title,
                    price=price,
                    original_price=original_price,
                    discount_percentage=discount_percentage,
                    store=advertiser.name,
                    category=advertiser.category,
                    url=product.get("url", ""),
                    image_url=product.get("image_url"),
                    description=product.get("description"),
                    availability=product.get("availability", True),
                    advertiser_id=advertiser.mid,
                    collected_at=datetime.now()
                )
                
                offers.append(offer)
                
            except Exception as e:
                logger.warning(f"⚠️ Erro ao parsear produto: {e}")
                continue
        
        return offers
    
    async def _collect_via_link_builder(self, advertiser: AwinAdvertiser, max_offers: int) -> List[AwinOffer]:
        """Coleta via Link Builder API (fallback)"""
        # Implementar coleta via Link Builder se necessário
        logger.info(f"🔄 Coleta via Link Builder não implementada para {advertiser.name}")
        return []
    
    async def _apply_advertiser_filters(self, offers: List[AwinOffer], advertiser: AwinAdvertiser) -> List[AwinOffer]:
        """Aplica filtros específicos do anunciante"""
        filtered = []
        
        for offer in offers:
            # Verificar desconto mínimo
            if advertiser.min_discount > 0:
                if not offer.discount_percentage or offer.discount_percentage < advertiser.min_discount:
                    continue
            
            # Verificar preço máximo
            if advertiser.max_price > 0 and offer.price > advertiser.max_price:
                continue
            
            # Verificar disponibilidade
            if not offer.availability:
                continue
            
            filtered.append(offer)
        
        return filtered
    
    async def _apply_global_filters(self, offers: List[AwinOffer]) -> List[AwinOffer]:
        """Aplica filtros globais do sistema"""
        filtered = []
        
        for offer in offers:
            # Verificar desconto mínimo global
            if offer.discount_percentage and offer.discount_percentage < self.filters["min_discount"]:
                continue
            
            # Verificar preço máximo global
            if offer.price > self.filters["max_price"]:
                continue
            
            # Verificar categoria permitida
            if offer.category.lower() not in [c.lower() for c in self.filters["categories"]]:
                continue
            
            # Verificar loja não excluída
            if offer.store.lower() in [s.lower() for s in self.filters["excluded_stores"]]:
                continue
            
            filtered.append(offer)
        
        return filtered
    
    async def _convert_to_offers(self, awin_offers: List[AwinOffer], store_key: str) -> List[Offer]:
        """Converte ofertas Awin para modelo Offer"""
        offers = []
        
        for awin_offer in awin_offers:
            try:
                # Gerar link de afiliado
                affiliate_url = await self.client.generate_link(
                    awin_offer.advertiser_id,
                    awin_offer.url,
                    sub_id=f"garimpeirogeek_{store_key}"
                )
                
                if not affiliate_url:
                    logger.warning(f"⚠️ Não foi possível gerar link de afiliado para: {awin_offer.title}")
                    continue
                
                # Criar modelo Offer
                offer = Offer(
                    title=awin_offer.title,
                    price=awin_offer.price,
                    original_price=awin_offer.original_price,
                    discount_percentage=awin_offer.discount_percentage,
                    store=awin_offer.store,
                    category=awin_offer.category,
                    url=awin_offer.url,
                    affiliate_url=affiliate_url,
                    image_url=awin_offer.image_url,
                    description=awin_offer.description,
                    source="awin",
                    scraped_at=awin_offer.collected_at
                )
                
                offers.append(offer)
                
            except Exception as e:
                logger.warning(f"⚠️ Erro ao converter oferta: {e}")
                continue
        
        return offers
    
    def update_filters(self, **kwargs):
        """Atualiza filtros do coletor"""
        self.filters.update(kwargs)
        logger.info(f"🔧 Filtros atualizados: {kwargs}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do coletor"""
        return {
            **self.stats,
            "advertisers_count": len(self.advertisers),
            "active_advertisers": len([a for a in self.advertisers.values() if a.enabled]),
            "filters": self.filters
        }


class AwinAPIClient(BaseAPI):
    """Cliente para API oficial do Awin Publisher"""

    def __init__(self, publisher_id: str, access_token: str):
        """
        Inicializa cliente Awin API

        Args:
            publisher_id: ID do publisher
            access_token: Token de acesso
        """
        super().__init__("Awin", "https://api.awin.com", access_token)
        self.publisher_id = publisher_id
        self.access_token = access_token

        # Configurações específicas
        self.api_version = "v1"
        self.base_url = "https://api.awin.com"

        # Headers específicos
        self.headers.update(
            {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": f"Bearer {access_token}",
            }
        )

    async def generate_link(
        self, advertiser_id: str, url: str, sub_id: Optional[str] = None
    ) -> Optional[str]:
        """
        Gera link de afiliado via Link Builder API

        Args:
            advertiser_id: ID do anunciante
            url: URL de destino
            sub_id: Sub-ID para tracking (opcional)

        Returns:
            Link de afiliado ou None se falhar
        """
        try:
            endpoint = f"{self.base_url}/generateLink"

            # Parâmetros da requisição
            params = {
                "publisherId": self.publisher_id,
                "advertiserId": advertiser_id,
                "url": url,
            }

            if sub_id:
                params["subId"] = sub_id

            async with self.session.post(
                endpoint, json=params, headers=self.headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if "affiliateUrl" in data:
                        affiliate_url = data["affiliateUrl"]
                        logger.info(f"Link Awin gerado: {affiliate_url[:80]}...")
                        return affiliate_url
                    else:
                        logger.error(f"Link não encontrado na resposta: {data}")
                        return None
                else:
                    logger.error(f"Erro ao gerar link: {response.status}")
                    return None

        except Exception as e:
            logger.error(f"Erro ao gerar link Awin: {e}")
            return None

    async def generate_batch_links(
        self, links: List[Dict[str, str]]
    ) -> List[Dict[str, Any]]:
        """
        Gera múltiplos links de afiliado em lote

        Args:
            links: Lista de links para gerar
                [{"advertiserId": "123", "url": "https://...", "subId": "optional"}]

        Returns:
            Lista de resultados com links gerados
        """
        try:
            endpoint = f"{self.base_url}/generateBatchLinks"

            # Preparar dados para lote
            batch_data = {"publisherId": self.publisher_id, "links": links}

            async with self.session.post(
                endpoint, json=batch_data, headers=self.headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if "results" in data:
                        results = data["results"]
                        logger.info(
                            f"Lote de {len(links)} links processado: {len(results)} sucessos"
                        )
                        return results
                    else:
                        logger.error(f"Resultados não encontrados na resposta: {data}")
                        return []
                else:
                    logger.error(f"Erro no lote de links: {response.status}")
                    return []

        except Exception as e:
            logger.error(f"Erro no lote de links: {e}")
            return []

    async def search_products(
        self, query: str, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Busca produtos na API Awin
        
        Args:
            query: Termo de busca
            limit: Número máximo de resultados
            
        Returns:
            Lista de produtos encontrados
        """
        try:
            # Implementação básica para satisfazer método abstrato
            logger.info(f"Busca de produtos: {query} (limite: {limit})")
            return []
        except Exception as e:
            logger.error(f"Erro na busca de produtos: {e}")
            return []

    async def get_product_details(self, product_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtém detalhes de um produto específico
        
        Args:
            product_id: ID do produto
            
        Returns:
            Detalhes do produto ou None se não encontrado
        """
        try:
            # Implementação básica para satisfazer método abstrato
            logger.info(f"Obtendo detalhes do produto: {product_id}")
            return None
        except Exception as e:
            logger.error(f"Erro ao obter detalhes do produto: {e}")
            return None

    async def get_product_feed(
        self, advertiser_id: str, feed_type: str = "product"
    ) -> List[Dict[str, Any]]:
        """
        Obtém feed de produtos do anunciante

        Args:
            advertiser_id: ID do anunciante
            feed_type: Tipo de feed (product, category, etc.)

        Returns:
            Lista de produtos do feed
        """
        try:
            endpoint = f"{self.base_url}/feeds/{advertiser_id}"

            params = {"type": feed_type, "publisherId": self.publisher_id}

            async with self.session.get(
                endpoint, params=params, headers=self.headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if "products" in data:
                        products = data["products"]
                        logger.info(f"Feed retornou {len(products)} produtos")
                        return products
                    else:
                        logger.error(f"Produtos não encontrados no feed: {data}")
                        return []
                else:
                    logger.error(f"Erro ao obter feed: {response.status}")
                    return []

        except Exception as e:
            logger.error(f"Erro ao obter feed: {e}")
            return []

    async def download_product_feed(
        self, advertiser_id: str, feed_url: str
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Faz download de feed de produtos via URL

        Args:
            advertiser_id: ID do anunciante
            feed_url: URL do feed para download

        Returns:
            Lista de produtos do feed ou None se falhar
        """
        try:
            # Fazer download do feed
            async with self.session.get(feed_url) as response:
                if response.status == 200:
                    content = await response.text()

                    # Tentar parse como JSON primeiro
                    try:
                        data = json.loads(content)
                        if "products" in data:
                            products = data["products"]
                            logger.info(f"Feed baixado: {len(products)} produtos")
                            return products
                    except json.JSONDecodeError:
                        # Tentar parse como CSV ou XML se necessário
                        logger.info("Feed não é JSON, tentando outros formatos...")
                        # Implementar parse de outros formatos se necessário
                        return []
                else:
                    logger.error(f"Erro ao baixar feed: {response.status}")
                    return None

        except Exception as e:
            logger.error(f"Erro ao baixar feed: {e}")
            return None

    async def list_advertisers(self) -> List[Dict[str, Any]]:
        """
        Lista anunciantes disponíveis para o publisher

        Returns:
            Lista de anunciantes
        """
        try:
            endpoint = f"{self.base_url}/advertisers"

            params = {"publisherId": self.publisher_id}

            async with self.session.get(
                endpoint, params=params, headers=self.headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if "advertisers" in data:
                        advertisers = data["advertisers"]
                        logger.info(f"Lista retornou {len(advertisers)} anunciantes")
                        return advertisers
                    else:
                        logger.error(f"Anunciantes não encontrados na resposta: {data}")
                        return []
                else:
                    logger.error(f"Erro ao listar anunciantes: {response.status}")
                    return []

        except Exception as e:
            logger.error(f"Erro ao listar anunciantes: {e}")
            return []

    async def get_publisher_performance(
        self, start_date: str, end_date: str, granularity: str = "daily"
    ) -> List[Dict[str, Any]]:
        """
        Obtém relatório de performance do publisher

        Args:
            start_date: Data de início (YYYY-MM-DD)
            end_date: Data de fim (YYYY-MM-DD)
            granularity: Granularidade (daily, weekly, monthly)

        Returns:
            Lista de relatórios de performance
        """
        try:
            endpoint = f"{self.base_url}/reports/publisher/performance"

            params = {
                "publisherId": self.publisher_id,
                "startDate": start_date,
                "endDate": end_date,
                "granularity": granularity,
            }

            async with self.session.get(
                endpoint, params=params, headers=self.headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if "performance" in data:
                        performance = data["performance"]
                        logger.info(
                            f"Relatório de performance retornado: {len(performance)} registros"
                        )
                        return performance
                    else:
                        logger.error(f"Performance não encontrada na resposta: {data}")
                        return []
                else:
                    logger.error(f"Erro no relatório: {response.status}")
                    return []

        except Exception as e:
            logger.error(f"Erro ao obter performance: {e}")
            return []

    async def get_advertiser_performance(
        self, advertiser_id: str, start_date: str, end_date: str
    ) -> Optional[Dict[str, Any]]:
        """
        Obtém relatório de performance de um anunciante específico

        Args:
            advertiser_id: ID do anunciante
            start_date: Data de início (YYYY-MM-DD)
            end_date: Data de fim (YYYY-MM-DD)

        Returns:
            Relatório de performance ou None se falhar
        """
        try:
            endpoint = f"{self.base_url}/reports/advertiser/{advertiser_id}/performance"

            params = {
                "publisherId": self.publisher_id,
                "startDate": start_date,
                "endDate": end_date,
            }

            async with self.session.get(
                endpoint, params=params, headers=self.headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if "performance" in data:
                        performance = data["performance"]
                        logger.info(
                            f"Performance do anunciante obtida: {advertiser_id}"
                        )
                        return performance
                    else:
                        logger.error(f"Performance não encontrada na resposta: {data}")
                        return None
                else:
                    logger.error(f"Erro no relatório do anunciante: {response.status}")
                    return None

        except Exception as e:
            logger.error(f"Erro ao obter performance do anunciante: {e}")
            return None

    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas da API com informações específicas"""
        base_stats = super().get_stats()
        base_stats.update(
            {
                "publisher_id": self.publisher_id,
                "access_token_valid": bool(self.access_token),
                "api_version": self.api_version,
            }
        )
        return base_stats


# Função de conveniência
def get_awin_client() -> Optional[AwinAPIClient]:
    """
    Retorna instância do cliente Awin se configurado

    Returns:
        AwinAPIClient ou None se não configurado
    """
    import os

    publisher_id = os.getenv("AWIN_PUBLISHER_ID")
    access_token = os.getenv("AWIN_ACCESS_TOKEN")

    if not publisher_id or not access_token:
        logger.warning("Credenciais Awin não configuradas")
        return None

    return AwinAPIClient(publisher_id, access_token)
