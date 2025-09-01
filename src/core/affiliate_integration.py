"""
Sistema de Integração com Redes de Afiliados Reais
==================================================

Este módulo implementa integração com APIs oficiais de redes de afiliados
e validação robusta de links de afiliado para o Garimpeiro Geek.
"""

import asyncio
import aiohttp
import json
import re
import hashlib
import time
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass, field
from enum import Enum
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
import logging
from datetime import datetime, timedelta
import sqlite3
from pathlib import Path

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AffiliateNetwork(Enum):
    """Redes de afiliados suportadas"""
    AMAZON = "amazon"
    AWIN = "awin"
    HOTMART = "hotmart"
    MONETIZZE = "monetizze"
    EDUZZ = "eduzz"
    BRAIP = "braip"
    PERFECT_PAY = "perfect_pay"
    KIWIFY = "kiwify"
    HOTMART_PLUS = "hotmart_plus"
    DIGITAL_PRODUCTS = "digital_products"


class LinkStatus(Enum):
    """Status de validação de links"""
    VALID = "valid"
    INVALID = "invalid"
    EXPIRED = "expired"
    BLOCKED = "blocked"
    RATE_LIMITED = "rate_limited"
    PENDING = "pending"


@dataclass
class AffiliateConfig:
    """Configuração para uma rede de afiliados"""
    network: AffiliateNetwork
    api_key: str
    api_secret: str = ""
    base_url: str = ""
    timeout: int = 30
    retry_attempts: int = 3
    rate_limit_delay: float = 1.0
    enabled: bool = True
    priority: int = 1  # 1 = mais alta prioridade


@dataclass
class AffiliateProduct:
    """Produto de afiliado"""
    id: str
    name: str
    description: str
    price: float
    original_price: float
    discount_percentage: float
    category: str
    subcategory: str
    affiliate_link: str
    network: AffiliateNetwork
    commission_rate: float
    status: str = "active"
    image_url: str = ""
    rating: float = 0.0
    review_count: int = 0
    availability: str = "in_stock"
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class LinkValidationResult:
    """Resultado da validação de link"""
    url: str
    network: AffiliateNetwork
    status: LinkStatus
    is_valid: bool
    response_time: float
    status_code: int = 0
    error_message: str = ""
    redirect_url: str = ""
    final_url: str = ""
    validation_timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class AffiliateMetrics:
    """Métricas de performance de afiliados"""
    network: AffiliateNetwork
    total_clicks: int
    total_conversions: int
    conversion_rate: float
    total_revenue: float
    total_commission: float
    ctr: float  # Click-through rate
    epc: float  # Earnings per click
    date_range: str
    period: str = "daily"


class AffiliateLinkValidator:
    """Validador de links de afiliado"""
    
    def __init__(self):
        self.validation_cache = {}
        self.cache_duration = timedelta(hours=1)
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def _detect_network(self, url: str) -> Optional[AffiliateNetwork]:
        """Detecta a rede de afiliados baseado na URL"""
        domain = urlparse(url).netloc.lower()
        
        network_patterns = {
            AffiliateNetwork.AMAZON: [
                "amazon.com.br", "amzn.to", "amazon.com", "amazon.co.uk"
            ],
            AffiliateNetwork.AWIN: [
                "awin1.com", "awin.com", "awin.net"
            ],
            AffiliateNetwork.HOTMART: [
                "hotmart.com", "hotm.art", "pay.hotmart.com"
            ],
            AffiliateNetwork.MONETIZZE: [
                "monetizze.com.br", "pay.monetizze.com.br"
            ],
            AffiliateNetwork.EDUZZ: [
                "eduzz.com", "pay.eduzz.com"
            ],
            AffiliateNetwork.BRAIP: [
                "braip.com", "pay.braip.com"
            ],
            AffiliateNetwork.PERFECT_PAY: [
                "perfectpay.com.br", "pay.perfectpay.com.br"
            ],
            AffiliateNetwork.KIWIFY: [
                "kiwify.com.br", "pay.kiwify.com.br"
            ]
        }
        
        for network, patterns in network_patterns.items():
            if any(pattern in domain for pattern in patterns):
                return network
        
        return None
    
    def _validate_amazon_link(self, url: str) -> bool:
        """Valida link da Amazon"""
        # Padrões específicos da Amazon
        amazon_patterns = [
            r'amazon\.com\.br/.*?tag=',
            r'amzn\.to/',
            r'amazon\.com/.*?tag=',
            r'amazon\.co\.uk/.*?tag='
        ]
        
        return any(re.search(pattern, url, re.IGNORECASE) for pattern in amazon_patterns)
    
    def _validate_awin_link(self, url: str) -> bool:
        """Valida link da Awin"""
        # Padrões específicos da Awin
        awin_patterns = [
            r'awin1\.com/.*?awin=',
            r'awin\.com/.*?awin=',
            r'awin\.net/.*?awin='
        ]
        
        return any(re.search(pattern, url, re.IGNORECASE) for pattern in awin_patterns)
    
    def _validate_hotmart_link(self, url: str) -> bool:
        """Valida link da Hotmart"""
        # Padrões específicos da Hotmart
        hotmart_patterns = [
            r'hotmart\.com/.*?ref=',
            r'hotm\.art/.*?ref=',
            r'pay\.hotmart\.com/.*?ref='
        ]
        
        return any(re.search(pattern, url, re.IGNORECASE) for pattern in hotmart_patterns)
    
    async def validate_link(self, url: str) -> LinkValidationResult:
        """Valida um link de afiliado"""
        start_time = time.time()
        
        # Verificar cache
        cache_key = hashlib.md5(url.encode()).hexdigest()
        if cache_key in self.validation_cache:
            cached_result = self.validation_cache[cache_key]
            if datetime.now() - cached_result.validation_timestamp < self.cache_duration:
                return cached_result
        
        # Detectar rede
        network = self._detect_network(url)
        if not network:
            result = LinkValidationResult(
                url=url,
                network=AffiliateNetwork.AMAZON,  # Default
                status=LinkStatus.INVALID,
                is_valid=False,
                response_time=time.time() - start_time,
                error_message="Rede de afiliados não reconhecida"
            )
            return result
        
        # Validação específica por rede
        is_valid_format = False
        if network == AffiliateNetwork.AMAZON:
            is_valid_format = self._validate_amazon_link(url)
        elif network == AffiliateNetwork.AWIN:
            is_valid_format = self._validate_awin_link(url)
        elif network == AffiliateNetwork.HOTMART:
            is_valid_format = self._validate_hotmart_link(url)
        else:
            # Para outras redes, verificar se tem parâmetros de afiliado
            parsed = urlparse(url)
            query_params = parse_qs(parsed.query)
            is_valid_format = any(
                param.lower() in ['ref', 'tag', 'awin', 'aff', 'partner', 'pid']
                for param in query_params.keys()
            )
        
        if not is_valid_format:
            result = LinkValidationResult(
                url=url,
                network=network,
                status=LinkStatus.INVALID,
                is_valid=False,
                response_time=time.time() - start_time,
                error_message="Formato de link inválido para a rede"
            )
            return result
        
        # Testar acessibilidade do link
        try:
            async with self.session.head(url, allow_redirects=True, timeout=10) as response:
                response_time = time.time() - start_time
                
                if response.status == 200:
                    status = LinkStatus.VALID
                    is_valid = True
                elif response.status == 404:
                    status = LinkStatus.INVALID
                    is_valid = False
                elif response.status == 429:
                    status = LinkStatus.RATE_LIMITED
                    is_valid = False
                else:
                    status = LinkStatus.INVALID
                    is_valid = False
                
                result = LinkValidationResult(
                    url=url,
                    network=network,
                    status=status,
                    is_valid=is_valid,
                    response_time=response_time,
                    status_code=response.status,
                    final_url=str(response.url)
                )
                
        except asyncio.TimeoutError:
            result = LinkValidationResult(
                url=url,
                network=network,
                status=LinkStatus.INVALID,
                is_valid=False,
                response_time=time.time() - start_time,
                error_message="Timeout ao acessar link"
            )
        except Exception as e:
            result = LinkValidationResult(
                url=url,
                network=network,
                status=LinkStatus.INVALID,
                is_valid=False,
                response_time=time.time() - start_time,
                error_message=f"Erro ao acessar link: {str(e)}"
            )
        
        # Armazenar no cache
        self.validation_cache[cache_key] = result
        return result
    
    async def validate_batch_links(self, urls: List[str]) -> List[LinkValidationResult]:
        """Valida múltiplos links em paralelo"""
        tasks = [self.validate_link(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filtrar exceções
        valid_results = []
        for result in results:
            if isinstance(result, LinkValidationResult):
                valid_results.append(result)
            else:
                logger.error(f"Erro na validação: {result}")
        
        return valid_results


class AffiliateAPIClient:
    """Cliente para APIs de redes de afiliados"""
    
    def __init__(self, config: AffiliateConfig):
        self.config = config
        self.session = None
        self.last_request_time = 0
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            headers={
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json"
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def _rate_limit_delay(self):
        """Implementa rate limiting"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.config.rate_limit_delay:
            await asyncio.sleep(self.config.rate_limit_delay - time_since_last)
        self.last_request_time = time.time()
    
    async def _make_request(self, method: str, endpoint: str, data: Dict = None) -> Dict:
        """Faz requisição para a API"""
        await self._rate_limit_delay()
        
        url = f"{self.config.base_url}{endpoint}"
        
        for attempt in range(self.config.retry_attempts):
            try:
                async with self.session.request(
                    method, url, json=data, timeout=self.config.timeout
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    elif response.status == 429:
                        # Rate limit - aguardar mais tempo
                        await asyncio.sleep(2 ** attempt)
                        continue
                    else:
                        logger.error(f"API error: {response.status} - {await response.text()}")
                        return {"error": f"HTTP {response.status}"}
                        
            except Exception as e:
                logger.error(f"Request error (attempt {attempt + 1}): {e}")
                if attempt == self.config.retry_attempts - 1:
                    return {"error": str(e)}
                await asyncio.sleep(1)
        
        return {"error": "Max retry attempts reached"}


class AmazonAPIClient(AffiliateAPIClient):
    """Cliente específico para API da Amazon"""
    
    def __init__(self, config: AffiliateConfig):
        super().__init__(config)
        self.config.base_url = "https://webservices.amazon.com"
    
    async def search_products(self, keywords: str, category: str = None) -> List[AffiliateProduct]:
        """Busca produtos na Amazon"""
        endpoint = "/paapi5/searchitems"
        
        data = {
            "Keywords": keywords,
            "SearchIndex": "All",
            "ItemCount": 10,
            "Resources": ["Images.Primary.Medium", "ItemInfo.Title", "Offers.Listings.Price"]
        }
        
        if category:
            data["SearchIndex"] = category
        
        response = await self._make_request("POST", endpoint, data)
        
        if "error" in response:
            return []
        
        products = []
        for item in response.get("SearchResult", {}).get("Items", []):
            try:
                product = AffiliateProduct(
                    id=item.get("ASIN", ""),
                    name=item.get("ItemInfo", {}).get("Title", {}).get("DisplayValue", ""),
                    description=item.get("ItemInfo", {}).get("Features", {}).get("DisplayValues", [""])[0],
                    price=float(item.get("Offers", {}).get("Listings", [{}])[0].get("Price", {}).get("Amount", 0)),
                    original_price=float(item.get("Offers", {}).get("Listings", [{}])[0].get("Price", {}).get("Amount", 0)),
                    discount_percentage=0.0,
                    category=item.get("BrowseNodeInfo", {}).get("BrowseNodes", [{}])[0].get("DisplayName", ""),
                    subcategory="",
                    affiliate_link=f"https://amazon.com.br/dp/{item.get('ASIN', '')}?tag={self.config.api_key}",
                    network=AffiliateNetwork.AMAZON,
                    commission_rate=0.04,  # 4% padrão Amazon
                    image_url=item.get("Images", {}).get("Primary", {}).get("Medium", {}).get("URL", "")
                )
                products.append(product)
            except Exception as e:
                logger.error(f"Erro ao processar produto Amazon: {e}")
        
        return products


class AwinAPIClient(AffiliateAPIClient):
    """Cliente específico para API da Awin"""
    
    def __init__(self, config: AffiliateConfig):
        super().__init__(config)
        self.config.base_url = "https://api.awin.com"
    
    async def get_programs(self) -> List[Dict]:
        """Obtém programas de afiliados disponíveis"""
        endpoint = "/publishers/self/programs"
        response = await self._make_request("GET", endpoint)
        
        if "error" in response:
            return []
        
        return response.get("data", [])
    
    async def get_products(self, program_id: str, keywords: str = None) -> List[AffiliateProduct]:
        """Busca produtos de um programa específico"""
        endpoint = f"/publishers/self/programs/{program_id}/products"
        
        params = {}
        if keywords:
            params["search"] = keywords
        
        response = await self._make_request("GET", endpoint, params)
        
        if "error" in response:
            return []
        
        products = []
        for item in response.get("data", []):
            try:
                product = AffiliateProduct(
                    id=str(item.get("id", "")),
                    name=item.get("name", ""),
                    description=item.get("description", ""),
                    price=float(item.get("price", {}).get("amount", 0)),
                    original_price=float(item.get("price", {}).get("original_amount", 0)),
                    discount_percentage=float(item.get("price", {}).get("discount_percentage", 0)),
                    category=item.get("category", ""),
                    subcategory=item.get("subcategory", ""),
                    affiliate_link=item.get("affiliate_link", ""),
                    network=AffiliateNetwork.AWIN,
                    commission_rate=float(item.get("commission_rate", 0.05)),
                    image_url=item.get("image_url", "")
                )
                products.append(product)
            except Exception as e:
                logger.error(f"Erro ao processar produto Awin: {e}")
        
        return products


class AffiliateIntegrationManager:
    """Gerenciador principal de integração com afiliados"""
    
    def __init__(self, db_path: str = "affiliate_integration.db"):
        self.db_path = db_path
        self.clients = {}
        self.validator = None
        self._init_database()
    
    def _init_database(self):
        """Inicializa banco de dados"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabela de configurações
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS affiliate_configs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                network TEXT NOT NULL,
                api_key TEXT NOT NULL,
                api_secret TEXT,
                base_url TEXT,
                timeout INTEGER DEFAULT 30,
                retry_attempts INTEGER DEFAULT 3,
                rate_limit_delay REAL DEFAULT 1.0,
                enabled BOOLEAN DEFAULT 1,
                priority INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabela de produtos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS affiliate_products (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                price REAL NOT NULL,
                original_price REAL NOT NULL,
                discount_percentage REAL DEFAULT 0.0,
                category TEXT,
                subcategory TEXT,
                affiliate_link TEXT NOT NULL,
                network TEXT NOT NULL,
                commission_rate REAL DEFAULT 0.0,
                status TEXT DEFAULT 'active',
                image_url TEXT,
                rating REAL DEFAULT 0.0,
                review_count INTEGER DEFAULT 0,
                availability TEXT DEFAULT 'in_stock',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabela de validações
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS link_validations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL,
                network TEXT NOT NULL,
                status TEXT NOT NULL,
                is_valid BOOLEAN NOT NULL,
                response_time REAL NOT NULL,
                status_code INTEGER DEFAULT 0,
                error_message TEXT,
                redirect_url TEXT,
                final_url TEXT,
                validation_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabela de métricas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS affiliate_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                network TEXT NOT NULL,
                total_clicks INTEGER DEFAULT 0,
                total_conversions INTEGER DEFAULT 0,
                conversion_rate REAL DEFAULT 0.0,
                total_revenue REAL DEFAULT 0.0,
                total_commission REAL DEFAULT 0.0,
                ctr REAL DEFAULT 0.0,
                epc REAL DEFAULT 0.0,
                date_range TEXT,
                period TEXT DEFAULT 'daily',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    async def add_network_config(self, config: AffiliateConfig):
        """Adiciona configuração de rede de afiliados"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO affiliate_configs 
            (network, api_key, api_secret, base_url, timeout, retry_attempts, 
             rate_limit_delay, enabled, priority)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            config.network.value,
            config.api_key,
            config.api_secret,
            config.base_url,
            config.timeout,
            config.retry_attempts,
            config.rate_limit_delay,
            config.enabled,
            config.priority
        ))
        
        conn.commit()
        conn.close()
        
        # Inicializar cliente
        await self._init_client(config)
    
    async def _init_client(self, config: AffiliateConfig):
        """Inicializa cliente para uma rede"""
        if config.network == AffiliateNetwork.AMAZON:
            self.clients[config.network] = AmazonAPIClient(config)
        elif config.network == AffiliateNetwork.AWIN:
            self.clients[config.network] = AwinAPIClient(config)
        else:
            # Cliente genérico para outras redes
            self.clients[config.network] = AffiliateAPIClient(config)
    
    async def search_products(self, keywords: str, category: str = None, 
                            networks: List[AffiliateNetwork] = None) -> List[AffiliateProduct]:
        """Busca produtos em múltiplas redes"""
        if not networks:
            networks = list(self.clients.keys())
        
        all_products = []
        
        for network in networks:
            if network not in self.clients:
                continue
            
            client = self.clients[network]
            
            try:
                if isinstance(client, AmazonAPIClient):
                    products = await client.search_products(keywords, category)
                elif isinstance(client, AwinAPIClient):
                    # Para Awin, precisamos de um program_id específico
                    # Por enquanto, vamos usar um exemplo
                    products = await client.get_products("example_program_id", keywords)
                else:
                    # Cliente genérico
                    products = []
                
                all_products.extend(products)
                
            except Exception as e:
                logger.error(f"Erro ao buscar produtos em {network.value}: {e}")
        
        return all_products
    
    async def validate_links(self, urls: List[str]) -> List[LinkValidationResult]:
        """Valida múltiplos links"""
        if not self.validator:
            self.validator = AffiliateLinkValidator()
        
        async with self.validator:
            results = await self.validator.validate_batch_links(urls)
        
        # Salvar resultados no banco
        await self._save_validation_results(results)
        
        return results
    
    async def _save_validation_results(self, results: List[LinkValidationResult]):
        """Salva resultados de validação no banco"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for result in results:
            cursor.execute("""
                INSERT INTO link_validations 
                (url, network, status, is_valid, response_time, status_code, 
                 error_message, redirect_url, final_url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                result.url,
                result.network.value,
                result.status.value,
                result.is_valid,
                result.response_time,
                result.status_code,
                result.error_message,
                result.redirect_url,
                result.final_url
            ))
        
        conn.commit()
        conn.close()
    
    async def save_products(self, products: List[AffiliateProduct]):
        """Salva produtos no banco de dados"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for product in products:
            cursor.execute("""
                INSERT OR REPLACE INTO affiliate_products 
                (id, name, description, price, original_price, discount_percentage,
                 category, subcategory, affiliate_link, network, commission_rate,
                 status, image_url, rating, review_count, availability)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                product.id,
                product.name,
                product.description,
                product.price,
                product.original_price,
                product.discount_percentage,
                product.category,
                product.subcategory,
                product.affiliate_link,
                product.network.value,
                product.commission_rate,
                product.status,
                product.image_url,
                product.rating,
                product.review_count,
                product.availability
            ))
        
        conn.commit()
        conn.close()
    
    async def get_products_by_category(self, category: str) -> List[AffiliateProduct]:
        """Obtém produtos por categoria"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM affiliate_products 
            WHERE category LIKE ? AND status = 'active'
            ORDER BY updated_at DESC
        """, (f"%{category}%",))
        
        rows = cursor.fetchall()
        conn.close()
        
        products = []
        for row in rows:
            product = AffiliateProduct(
                id=row[1],
                name=row[2],
                description=row[3],
                price=row[4],
                original_price=row[5],
                discount_percentage=row[6],
                category=row[7],
                subcategory=row[8],
                affiliate_link=row[9],
                network=AffiliateNetwork(row[10]),
                commission_rate=row[11],
                status=row[12],
                image_url=row[13],
                rating=row[14],
                review_count=row[15],
                availability=row[16]
            )
            products.append(product)
        
        return products
    
    async def get_validation_statistics(self) -> Dict:
        """Obtém estatísticas de validação"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total de validações
        cursor.execute("SELECT COUNT(*) FROM link_validations")
        total_validations = cursor.fetchone()[0]
        
        # Validações válidas
        cursor.execute("SELECT COUNT(*) FROM link_validations WHERE is_valid = 1")
        valid_links = cursor.fetchone()[0]
        
        # Por rede
        cursor.execute("""
            SELECT network, COUNT(*), SUM(CASE WHEN is_valid = 1 THEN 1 ELSE 0 END)
            FROM link_validations 
            GROUP BY network
        """)
        network_stats = cursor.fetchall()
        
        # Tempo médio de resposta
        cursor.execute("SELECT AVG(response_time) FROM link_validations")
        avg_response_time = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            "total_validations": total_validations,
            "valid_links": valid_links,
            "invalid_links": total_validations - valid_links,
            "success_rate": (valid_links / total_validations * 100) if total_validations > 0 else 0,
            "avg_response_time": avg_response_time,
            "network_statistics": {
                network: {"total": total, "valid": valid}
                for network, total, valid in network_stats
            }
        }
    
    async def get_network_metrics(self, network: AffiliateNetwork, 
                                period: str = "daily") -> AffiliateMetrics:
        """Obtém métricas de uma rede específica"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM affiliate_metrics 
            WHERE network = ? AND period = ?
            ORDER BY created_at DESC LIMIT 1
        """, (network.value, period))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return AffiliateMetrics(
                network=network,
                total_clicks=row[2],
                total_conversions=row[3],
                conversion_rate=row[4],
                total_revenue=row[5],
                total_commission=row[6],
                ctr=row[7],
                epc=row[8],
                date_range=row[9],
                period=row[10]
            )
        
        # Retornar métricas vazias se não encontrado
        return AffiliateMetrics(
            network=network,
            total_clicks=0,
            total_conversions=0,
            conversion_rate=0.0,
            total_revenue=0.0,
            total_commission=0.0,
            ctr=0.0,
            epc=0.0,
            date_range="",
            period=period
        )


# Instância global
affiliate_manager = AffiliateIntegrationManager()
