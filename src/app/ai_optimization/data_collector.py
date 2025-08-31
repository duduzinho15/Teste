"""
Coletor de Dados para IA de Otimização
Coleta dados históricos e features para treinamento dos modelos de IA
"""

import asyncio
import json
import sqlite3
from datetime import datetime, timedelta
from decimal import Decimal
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional
import logging
from pathlib import Path

from src.core.models import Offer
from src.core.geek_prioritizer import GeekPrioritizer


@dataclass
class FeatureSet:
    """Conjunto de features para treinamento da IA"""
    offer_id: str
    title: str
    category: str
    price: float
    store: str
    geek_score: float
    conversion_rate: float
    click_rate: float
    engagement_rate: float
    time_of_day: int
    day_of_week: int
    season: str
    price_range: str
    category_popularity: float
    store_reputation: float
    title_length: int
    has_discount: bool
    discount_percentage: float
    created_at: datetime


@dataclass
class TrainingData:
    """Dados de treinamento para a IA"""
    features: List[FeatureSet]
    target_scores: List[float]
    metadata: Dict[str, Any]
    created_at: datetime


class DataCollector:
    """Coletor de dados para treinamento da IA"""
    
    def __init__(self, db_path: str = "data/ai_training.db"):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        self.geek_prioritizer = GeekPrioritizer()
        
        # Criar diretório se não existir
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        self._init_database()
    
    def _init_database(self):
        """Inicializa o banco de dados"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS training_data (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        offer_id TEXT NOT NULL,
                        title TEXT NOT NULL,
                        category TEXT NOT NULL,
                        price REAL NOT NULL,
                        store TEXT NOT NULL,
                        geek_score REAL NOT NULL,
                        conversion_rate REAL NOT NULL,
                        click_rate REAL NOT NULL,
                        engagement_rate REAL NOT NULL,
                        time_of_day INTEGER NOT NULL,
                        day_of_week INTEGER NOT NULL,
                        season TEXT NOT NULL,
                        price_range TEXT NOT NULL,
                        category_popularity REAL NOT NULL,
                        store_reputation REAL NOT NULL,
                        title_length INTEGER NOT NULL,
                        has_discount BOOLEAN NOT NULL,
                        discount_percentage REAL NOT NULL,
                        target_score REAL NOT NULL,
                        created_at TIMESTAMP NOT NULL
                    )
                """)
                
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS feature_metadata (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        feature_name TEXT NOT NULL,
                        feature_type TEXT NOT NULL,
                        min_value REAL,
                        max_value REAL,
                        mean_value REAL,
                        std_value REAL,
                        created_at TIMESTAMP NOT NULL
                    )
                """)
                
                conn.commit()
                self.logger.info("Banco de dados inicializado com sucesso")
                
        except Exception as e:
            self.logger.error(f"Erro ao inicializar banco de dados: {e}")
    
    async def collect_historical_data(self, days_back: int = 30) -> List[FeatureSet]:
        """Coleta dados históricos das últimas N dias"""
        try:
            self.logger.info(f"Coletando dados históricos dos últimos {days_back} dias...")
            
            # Simular dados históricos (em produção, viria de APIs/databases reais)
            historical_data = []
            base_date = datetime.now() - timedelta(days=days_back)
            
            # Categorias geek com diferentes níveis de performance
            geek_categories = [
                ("Action Figures", 0.85, 0.12, 0.08, 0.15),
                ("Manga", 0.90, 0.15, 0.10, 0.18),
                ("Video Games", 0.88, 0.18, 0.12, 0.20),
                ("Anime DVDs", 0.82, 0.10, 0.06, 0.12),
                ("Cosplay", 0.87, 0.14, 0.09, 0.16),
                ("Board Games", 0.83, 0.11, 0.07, 0.13),
                ("Tech Gadgets", 0.86, 0.16, 0.11, 0.17),
                ("Comic Books", 0.84, 0.13, 0.08, 0.14),
                ("Gaming Accessories", 0.89, 0.17, 0.13, 0.19),
                ("Collectibles", 0.81, 0.09, 0.05, 0.11)
            ]
            
            stores = ["Amazon", "Magalu", "Americanas", "Submarino", "Casas Bahia"]
            
            for i in range(days_back * 50):  # 50 ofertas por dia
                day_offset = i // 50
                current_date = base_date + timedelta(days=day_offset)
                
                category, geek_score, conv_rate, click_rate, eng_rate = geek_categories[i % len(geek_categories)]
                store = stores[i % len(stores)]
                
                # Variação de preços
                base_price = 50 + (i % 1000)
                price = base_price + (i % 100)
                
                # Variação temporal
                time_of_day = (i % 24)
                day_of_week = current_date.weekday()
                
                # Determinar estação
                month = current_date.month
                if month in [12, 1, 2]:
                    season = "Verão"
                elif month in [3, 4, 5]:
                    season = "Outono"
                elif month in [6, 7, 8]:
                    season = "Inverno"
                else:
                    season = "Primavera"
                
                # Faixa de preço
                if price < 50:
                    price_range = "Baixo"
                elif price < 200:
                    price_range = "Médio"
                else:
                    price_range = "Alto"
                
                # Popularidade da categoria (simulada)
                category_popularity = 0.6 + (i % 40) / 100
                
                # Reputação da loja (simulada)
                store_reputation = 0.7 + (i % 30) / 100
                
                # Título com variação de comprimento
                title_length = 20 + (i % 40)
                
                # Desconto (30% das ofertas)
                has_discount = (i % 10) < 3
                discount_percentage = (i % 30) if has_discount else 0
                
                # Adicionar ruído aos scores para simular variação real
                noise_factor = 0.1
                geek_score += (i % 20 - 10) / 100 * noise_factor
                conv_rate += (i % 15 - 7) / 100 * noise_factor
                click_rate += (i % 12 - 6) / 100 * noise_factor
                eng_rate += (i % 10 - 5) / 100 * noise_factor
                
                # Garantir valores válidos
                geek_score = max(0.0, min(1.0, geek_score))
                conv_rate = max(0.0, min(1.0, conv_rate))
                click_rate = max(0.0, min(1.0, click_rate))
                eng_rate = max(0.0, min(1.0, eng_rate))
                
                feature_set = FeatureSet(
                    offer_id=f"hist_{i}",
                    title=f"Produto {category} {i}",
                    category=category,
                    price=float(price),
                    store=store,
                    geek_score=geek_score,
                    conversion_rate=conv_rate,
                    click_rate=click_rate,
                    engagement_rate=eng_rate,
                    time_of_day=time_of_day,
                    day_of_week=day_of_week,
                    season=season,
                    price_range=price_range,
                    category_popularity=category_popularity,
                    store_reputation=store_reputation,
                    title_length=title_length,
                    has_discount=has_discount,
                    discount_percentage=discount_percentage,
                    created_at=current_date
                )
                
                historical_data.append(feature_set)
            
            self.logger.info(f"Coletados {len(historical_data)} registros históricos")
            return historical_data
            
        except Exception as e:
            self.logger.error(f"Erro ao coletar dados históricos: {e}")
            return []
    
    async def extract_features_from_offer(self, offer: Offer, 
                                        conversion_data: Optional[Dict] = None) -> FeatureSet:
        """Extrai features de uma oferta específica"""
        try:
            # Calcular score geek
            geek_score = self.geek_prioritizer.calculate_geek_score(offer)
            if isinstance(geek_score, float):
                geek_score_value = geek_score
            else:
                geek_score_value = geek_score.score if hasattr(geek_score, 'score') else 0.5
            
            # Dados de conversão (padrão se não fornecidos)
            if not conversion_data:
                conversion_data = {
                    'conversion_rate': 0.1,
                    'click_rate': 0.05,
                    'engagement_rate': 0.08
                }
            
            # Features temporais
            now = datetime.now()
            time_of_day = now.hour
            day_of_week = now.weekday()
            
            # Estação
            month = now.month
            if month in [12, 1, 2]:
                season = "Verão"
            elif month in [3, 4, 5]:
                season = "Outono"
            elif month in [6, 7, 8]:
                season = "Inverno"
            else:
                season = "Primavera"
            
            # Faixa de preço
            price = float(offer.price)
            if price < 50:
                price_range = "Baixo"
            elif price < 200:
                price_range = "Médio"
            else:
                price_range = "Alto"
            
            # Popularidade da categoria (simulada)
            category_popularity = 0.6 + (hash(offer.category) % 40) / 100
            
            # Reputação da loja (simulada)
            store_reputation = 0.7 + (hash(offer.store) % 30) / 100
            
            # Comprimento do título
            title_length = len(offer.title)
            
            # Desconto (simulado)
            has_discount = (hash(offer.title) % 10) < 3
            discount_percentage = (hash(offer.title) % 30) if has_discount else 0
            
            return FeatureSet(
                offer_id=offer.url,
                title=offer.title,
                category=offer.category,
                price=price,
                store=offer.store,
                geek_score=geek_score_value,
                conversion_rate=conversion_data['conversion_rate'],
                click_rate=conversion_data['click_rate'],
                engagement_rate=conversion_data['engagement_rate'],
                time_of_day=time_of_day,
                day_of_week=day_of_week,
                season=season,
                price_range=price_range,
                category_popularity=category_popularity,
                store_reputation=store_reputation,
                title_length=title_length,
                has_discount=has_discount,
                discount_percentage=discount_percentage,
                created_at=now
            )
            
        except Exception as e:
            self.logger.error(f"Erro ao extrair features da oferta: {e}")
            raise
    
    async def save_training_data(self, features: List[FeatureSet], 
                               target_scores: List[float]) -> bool:
        """Salva dados de treinamento no banco"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                for feature, target_score in zip(features, target_scores):
                    conn.execute("""
                        INSERT INTO training_data (
                            offer_id, title, category, price, store, geek_score,
                            conversion_rate, click_rate, engagement_rate, time_of_day,
                            day_of_week, season, price_range, category_popularity,
                            store_reputation, title_length, has_discount, discount_percentage,
                            target_score, created_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        feature.offer_id, feature.title, feature.category, feature.price,
                        feature.store, feature.geek_score, feature.conversion_rate,
                        feature.click_rate, feature.engagement_rate, feature.time_of_day,
                        feature.day_of_week, feature.season, feature.price_range,
                        feature.category_popularity, feature.store_reputation,
                        feature.title_length, feature.has_discount, feature.discount_percentage,
                        target_score, feature.created_at
                    ))
                
                conn.commit()
                self.logger.info(f"Salvos {len(features)} registros de treinamento")
                return True
                
        except Exception as e:
            self.logger.error(f"Erro ao salvar dados de treinamento: {e}")
            return False
    
    async def load_training_data(self, limit: int = 1000) -> TrainingData:
        """Carrega dados de treinamento do banco"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT * FROM training_data 
                    ORDER BY created_at DESC 
                    LIMIT ?
                """, (limit,))
                
                features = []
                target_scores = []
                
                for row in cursor.fetchall():
                    feature = FeatureSet(
                        offer_id=row[1],
                        title=row[2],
                        category=row[3],
                        price=row[4],
                        store=row[5],
                        geek_score=row[6],
                        conversion_rate=row[7],
                        click_rate=row[8],
                        engagement_rate=row[9],
                        time_of_day=row[10],
                        day_of_week=row[11],
                        season=row[12],
                        price_range=row[13],
                        category_popularity=row[14],
                        store_reputation=row[15],
                        title_length=row[16],
                        has_discount=bool(row[17]),
                        discount_percentage=row[18],
                        created_at=datetime.fromisoformat(row[20])
                    )
                    
                    features.append(feature)
                    target_scores.append(row[19])  # target_score
                
                metadata = {
                    'total_records': len(features),
                    'date_range': {
                        'start': min(f.created_at for f in features) if features else None,
                        'end': max(f.created_at for f in features) if features else None
                    }
                }
                
                return TrainingData(
                    features=features,
                    target_scores=target_scores,
                    metadata=metadata,
                    created_at=datetime.now()
                )
                
        except Exception as e:
            self.logger.error(f"Erro ao carregar dados de treinamento: {e}")
            return TrainingData(features=[], target_scores=[], metadata={}, created_at=datetime.now())
    
    async def get_feature_statistics(self) -> Dict[str, Any]:
        """Obtém estatísticas das features"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT 
                        COUNT(*) as total,
                        AVG(geek_score) as avg_geek_score,
                        AVG(conversion_rate) as avg_conversion,
                        AVG(click_rate) as avg_clicks,
                        AVG(engagement_rate) as avg_engagement,
                        AVG(price) as avg_price
                    FROM training_data
                """)
                
                row = cursor.fetchone()
                if row:
                    return {
                        'total_records': row[0],
                        'avg_geek_score': row[1],
                        'avg_conversion_rate': row[2],
                        'avg_click_rate': row[3],
                        'avg_engagement_rate': row[4],
                        'avg_price': row[5]
                    }
                
                return {}
                
        except Exception as e:
            self.logger.error(f"Erro ao obter estatísticas: {e}")
            return {}
