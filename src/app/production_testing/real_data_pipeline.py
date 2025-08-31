"""
Pipeline de Dados Reais para Teste em Produção
Coleta e processa ofertas reais de múltiplas fontes para testar o sistema geek
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from decimal import Decimal
import random

from src.core.models import Offer
from src.core.geek_prioritizer import GeekPrioritizer
from src.app.queue.quality_controller import QualityController
from config.garimpeiro_geek_config import GEEK_CATEGORIES_CONFIG


class RealDataPipeline:
    """
    Pipeline para coleta e processamento de dados reais
    Simula cenários reais de produção para testar o sistema geek
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.geek_prioritizer = GeekPrioritizer()
        self.quality_controller = QualityController()
        
        # Configurações de teste
        self.test_duration_hours = 24
        self.offers_per_batch = 100
        self.batch_interval_minutes = 30
        
    async def generate_real_test_data(self) -> List[Offer]:
        """
        Gera dados de teste realistas baseados em categorias geek reais
        """
        self.logger.info("Gerando dados de teste realistas para sistema geek...")
        
        # Categorias e produtos reais para teste
        real_products = [
            # Gaming & Tech (Alta Prioridade)
            {"title": "PlayStation 5 Console Digital Edition", "category": "gaming_consoles", "price": Decimal("3499.99"), "discount": 15},
            {"title": "Nintendo Switch OLED Model", "category": "gaming_consoles", "price": Decimal("2499.99"), "discount": 20},
            {"title": "Xbox Series X 1TB", "category": "gaming_consoles", "price": Decimal("3999.99"), "discount": 10},
            {"title": "RTX 4080 Gaming X Trio", "category": "pc_gaming", "price": Decimal("8999.99"), "discount": 25},
            {"title": "Ryzen 9 7950X Processor", "category": "pc_gaming", "price": Decimal("3999.99"), "discount": 18},
            {"title": "Gaming Chair RGB Pro", "category": "gaming_accessories", "price": Decimal("899.99"), "discount": 30},
            {"title": "Mechanical Keyboard RGB", "category": "gaming_accessories", "price": Decimal("599.99"), "discount": 22},
            {"title": "Gaming Mouse Wireless", "category": "gaming_accessories", "price": Decimal("299.99"), "discount": 35},
            
            # Smart Home & IoT (Alta Prioridade)
            {"title": "Smart TV Samsung 55\" 4K", "category": "smart_home_tech", "price": Decimal("2999.99"), "discount": 20},
            {"title": "Amazon Echo Dot 4th Gen", "category": "smart_home_tech", "price": Decimal("199.99"), "discount": 40},
            {"title": "Google Nest Mini", "category": "smart_home_tech", "price": Decimal("179.99"), "discount": 35},
            {"title": "Smart Bulb Philips Hue", "category": "smart_home_tech", "price": Decimal("89.99"), "discount": 25},
            {"title": "Smart Lock August", "category": "smart_home_tech", "price": Decimal("599.99"), "discount": 15},
            
            # Audio & Sound (Alta Prioridade)
            {"title": "Headphone Sony WH-1000XM4", "category": "audio_tech", "price": Decimal("1899.99"), "discount": 30},
            {"title": "Bluetooth Speaker JBL Charge 5", "category": "audio_tech", "price": Decimal("399.99"), "discount": 25},
            {"title": "Gaming Headset HyperX Cloud II", "category": "audio_tech", "price": Decimal("299.99"), "discount": 40},
            {"title": "Microphone Blue Yeti", "category": "audio_tech", "price": Decimal("599.99"), "discount": 20},
            
            # Anime & Collectibles (Média Prioridade)
            {"title": "Funko Pop Naruto", "category": "anime_collectibles", "price": Decimal("89.99"), "discount": 15},
            {"title": "Manga Collection One Piece", "category": "anime_collectibles", "price": Decimal("299.99"), "discount": 25},
            {"title": "Anime Figure Goku", "category": "anime_collectibles", "price": Decimal("199.99"), "discount": 30},
            
            # Mobile & Wearables (Média Prioridade)
            {"title": "Smartwatch Apple Watch Series 8", "category": "mobile_tech", "price": Decimal("2999.99"), "discount": 15},
            {"title": "Smartphone Samsung Galaxy S23", "category": "mobile_tech", "price": Decimal("3999.99"), "discount": 20},
            {"title": "Tablet iPad Air 5th Gen", "category": "mobile_tech", "price": Decimal("3999.99"), "discount": 18},
            
            # Eletrodomésticos (Baixa Prioridade - Mas incluídos)
            {"title": "Microondas Panasonic 30L", "category": "home_appliances", "price": Decimal("599.99"), "discount": 35},
            {"title": "Fone Bluetooth JBL Tune 500BT", "category": "home_appliances", "price": Decimal("199.99"), "discount": 40},
            {"title": "Cafeteira Nespresso Vertuo", "category": "home_appliances", "price": Decimal("899.99"), "discount": 25},
            
            # Produtos Gerais (Baixa Prioridade)
            {"title": "Livro Técnico Python", "category": "books", "price": Decimal("89.99"), "discount": 20},
            {"title": "Camiseta Geek Star Wars", "category": "clothing", "price": Decimal("79.99"), "discount": 30},
            {"title": "Caneca Harry Potter", "category": "home_decor", "price": Decimal("49.99"), "discount": 25}
        ]
        
        offers = []
        for i, product in enumerate(real_products):
            # Adicionar variações de preço e estoque para simular cenários reais
            price_variation = random.uniform(0.9, 1.1)
            stock_variation = random.randint(1, 50)
            
            offer = Offer(
                title=product["title"],
                price=product["price"] * Decimal(str(price_variation)),
                url=f"https://exemplo.com/produto/{i}",
                store=f"Loja Teste {i % 5 + 1}",
                original_price=product["price"],
                discount_percentage=product["discount"],
                category=product["category"],
                description=f"Produto de teste para validação do sistema geek: {product['title']}",
                image_url=f"https://exemplo.com/imagem/{i}.jpg",
                stock_quantity=stock_variation,
                scraped_at=datetime.now() - timedelta(hours=random.randint(0, 24))
            )
            offers.append(offer)
        
        self.logger.info(f"Gerados {len(offers)} produtos de teste realistas")
        return offers
    
    async def collect_real_offers_from_sources(self) -> List[Offer]:
        """
        Coleta ofertas reais de fontes externas (simulado para teste)
        """
        self.logger.info("Coletando ofertas reais de fontes externas...")
        
        # Simular coleta de diferentes fontes
        sources = [
            "mercadolivre_api",
            "amazon_affiliate", 
            "awin_network",
            "magazine_luiza",
            "kabum"
        ]
        
        collected_offers = []
        
        for source in sources:
            # Simular delay de coleta
            await asyncio.sleep(random.uniform(0.1, 0.5))
            
            # Simular número de ofertas por fonte
            source_offers_count = random.randint(10, 50)
            
            for i in range(source_offers_count):
                # Gerar oferta baseada na fonte
                offer = await self._generate_source_based_offer(source, i)
                collected_offers.append(offer)
            
            self.logger.info(f"Coletadas {source_offers_count} ofertas de {source}")
        
        self.logger.info(f"Total de {len(collected_offers)} ofertas coletadas de todas as fontes")
        return collected_offers
    
    async def _generate_source_based_offer(self, source: str, index: int) -> Offer:
        """
        Gera oferta baseada na fonte específica
        """
        # Categorias específicas por fonte
        source_categories = {
            "mercadolivre_api": ["gaming_consoles", "pc_gaming", "smart_home_tech"],
            "amazon_affiliate": ["audio_tech", "mobile_tech", "anime_collectibles"],
            "awin_network": ["gaming_accessories", "smart_home_tech", "audio_tech"],
            "magazine_luiza": ["home_appliances", "mobile_tech", "general_electronics"],
            "kabum": ["pc_gaming", "gaming_accessories", "smart_home_tech"]
        }
        
        category = random.choice(source_categories.get(source, ["general"]))
        
        # Gerar dados realistas baseados na categoria
        title, price, discount = self._generate_realistic_product_data(category)
        
        return Offer(
            title=title,
            price=Decimal(str(price)),
            url=f"https://{source}.com/produto/{index}",
            store=f"{source.replace('_', ' ').title()}",
            original_price=Decimal(str(price / (1 - discount/100))),
            discount_percentage=discount,
            category=category,
            stock_quantity=random.randint(1, 100),
            image_url=f"https://{source}.com/imagem/{index}.jpg",
            description=f"Produto real coletado de {source}: {title}",
            scraped_at=datetime.now() - timedelta(hours=random.randint(0, 48))
        )
    
    def _generate_realistic_product_data(self, category: str) -> tuple:
        """
        Gera dados realistas de produto baseados na categoria
        """
        category_data = {
            "gaming_consoles": [
                ("PlayStation 5", 3499.99, 15),
                ("Nintendo Switch", 2499.99, 20),
                ("Xbox Series S", 2499.99, 18)
            ],
            "pc_gaming": [
                ("RTX 4070 Ti", 5999.99, 25),
                ("Ryzen 7 7700X", 2499.99, 20),
                ("Gaming Monitor 27\"", 1499.99, 30)
            ],
            "smart_home_tech": [
                ("Smart TV 55\"", 2999.99, 20),
                ("Smart Speaker", 299.99, 35),
                ("Smart Bulb Pack", 199.99, 25)
            ],
            "audio_tech": [
                ("Wireless Headphones", 899.99, 30),
                ("Bluetooth Speaker", 399.99, 25),
                ("Gaming Headset", 299.99, 40)
            ],
            "mobile_tech": [
                ("Smartphone 128GB", 1999.99, 15),
                ("Smartwatch", 899.99, 20),
                ("Tablet 10\"", 1499.99, 18)
            ],
            "gaming_accessories": [
                ("Gaming Chair", 899.99, 30),
                ("Mechanical Keyboard", 599.99, 22),
                ("Gaming Mouse", 299.99, 35)
            ],
            "anime_collectibles": [
                ("Funko Pop", 89.99, 15),
                ("Manga Collection", 299.99, 25),
                ("Anime Figure", 199.99, 30)
            ],
            "home_appliances": [
                ("Microondas", 599.99, 35),
                ("Fone Bluetooth", 199.99, 40),
                ("Cafeteira", 899.99, 25)
            ],
            "general_electronics": [
                ("Power Bank", 149.99, 30),
                ("USB Cable", 29.99, 50),
                ("Phone Stand", 79.99, 25)
            ]
        }
        
        if category in category_data:
            return random.choice(category_data[category])
        else:
            return ("Produto Genérico", 199.99, 20)
    
    async def process_offers_through_geek_system(self, offers: List[Offer]) -> Dict[str, Any]:
        """
        Processa ofertas através do sistema geek completo
        """
        self.logger.info("Processando ofertas através do sistema geek...")
        
        results = {
            "total_offers": len(offers),
            "geek_scores": [],
            "quality_scores": [],
            "prioritized_offers": [],
            "geek_categories_distribution": {},
            "performance_metrics": {}
        }
        
        start_time = datetime.now()
        
        # Processar cada oferta
        for offer in offers:
            # Calcular score geek
            geek_score = self.geek_prioritizer.calculate_geek_score(offer)
            results["geek_scores"].append(geek_score)
            
            # Calcular score de qualidade
            quality_score = self.quality_controller.evaluate_offer(offer)
            results["quality_scores"].append(quality_score)
            
            # Categorizar por nível geek
            geek_level = geek_score.geek_level
            if geek_level not in results["geek_categories_distribution"]:
                results["geek_categories_distribution"][geek_level] = 0
            results["geek_categories_distribution"][geek_level] += 1
        
        # Priorizar ofertas
        prioritized = self.geek_prioritizer.prioritize_offers(offers)
        results["prioritized_offers"] = prioritized
        
        # Calcular métricas de performance
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        results["performance_metrics"] = {
            "processing_time_seconds": processing_time,
            "offers_per_second": len(offers) / processing_time if processing_time > 0 else 0,
            "average_geek_score": sum(score.overall_score for score in results["geek_scores"]) / len(results["geek_scores"]) if results["geek_scores"] else 0,
            "average_quality_score": sum(score["overall_score"] for score in results["quality_scores"]) / len(results["quality_scores"]) if results["quality_scores"] else 0
        }
        
        self.logger.info(f"Processamento concluído em {processing_time:.2f} segundos")
        return results
    
    async def run_full_production_test(self) -> Dict[str, Any]:
        """
        Executa teste completo de produção
        """
        self.logger.info("Iniciando teste completo de produção...")
        
        # 1. Gerar dados de teste realistas
        test_offers = await self.generate_real_test_data()
        
        # 2. Coletar ofertas de fontes externas (simulado)
        external_offers = await self.collect_real_offers_from_sources()
        
        # 3. Combinar todas as ofertas
        all_offers = test_offers + external_offers
        
        # 4. Processar através do sistema geek
        results = await self.process_offers_through_geek_system(all_offers)
        
        # 5. Adicionar informações de teste
        results["test_info"] = {
            "test_timestamp": datetime.now().isoformat(),
            "test_duration_hours": self.test_duration_hours,
            "test_offers_count": len(test_offers),
            "external_offers_count": len(external_offers),
            "total_offers_processed": len(all_offers)
        }
        
        self.logger.info("Teste de produção concluído com sucesso")
        return results
