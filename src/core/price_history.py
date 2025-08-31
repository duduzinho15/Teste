"""
Sistema de Rastreamento de Preços Históricos
Detecta descontos, menores preços e tendências de preços
"""

import asyncio
import logging
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class PriceRecord:
    """Registro de preço histórico"""
    
    product_id: str
    title: str
    platform: str
    price: float
    original_price: Optional[float]
    discount_percentage: Optional[float]
    timestamp: datetime
    url: str
    category: str


@dataclass
class PriceAnalysis:
    """Análise de preços para um produto"""
    
    current_price: float
    original_price: Optional[float]
    discount_percentage: Optional[float]
    is_lowest_3m: bool
    is_lowest_6m: bool
    is_lowest_ever: bool
    price_trend: str  # "rising", "falling", "stable"
    price_history: List[PriceRecord]
    recommendations: List[str]


class PriceHistoryTracker:
    """Rastreador de preços históricos"""
    
    def __init__(self, db_path: str = "price_history.db"):
        self.db_path = db_path
        self._ensure_db()
    
    def _ensure_db(self) -> None:
        """Garante que o banco de dados existe"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Tabela de produtos
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    platform TEXT NOT NULL,
                    category TEXT,
                    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Tabela de preços históricos
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS price_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id TEXT NOT NULL,
                    price REAL NOT NULL,
                    original_price REAL,
                    discount_percentage REAL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    url TEXT,
                    FOREIGN KEY (product_id) REFERENCES products (id)
                )
            """)
            
            # Índices para performance
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_product_id ON price_history (product_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp ON price_history (timestamp)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_platform ON products (platform)
            """)
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Erro ao criar banco de dados: {e}")
    
    def _generate_product_id(self, title: str, platform: str) -> str:
        """Gera ID único para o produto"""
        import hashlib
        # Normalizar título e plataforma
        normalized = f"{title.lower().strip()}_{platform.lower()}"
        return hashlib.md5(normalized.encode()).hexdigest()[:16]
    
    async def record_price(self, title: str, platform: str, price: float, 
                          original_price: Optional[float] = None, 
                          url: str = "", category: str = "") -> str:
        """Registra um novo preço para um produto"""
        try:
            product_id = self._generate_product_id(title, platform)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Calcular desconto se preço original fornecido
            discount_percentage = None
            if original_price and original_price > price:
                discount_percentage = ((original_price - price) / original_price) * 100
            
            # Inserir/atualizar produto
            cursor.execute("""
                INSERT OR REPLACE INTO products (id, title, platform, category, last_updated)
                VALUES (?, ?, ?, ?, ?)
            """, (product_id, title, platform, category, datetime.now()))
            
            # Inserir registro de preço
            cursor.execute("""
                INSERT INTO price_history (product_id, price, original_price, discount_percentage, url, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (product_id, price, original_price, discount_percentage, url, datetime.now()))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Preço registrado: {title} - R$ {price:.2f} ({platform})")
            return product_id
            
        except Exception as e:
            logger.error(f"Erro ao registrar preço: {e}")
            raise
    
    async def analyze_price(self, title: str, current_price: float, 
                           platform: str) -> Optional[PriceAnalysis]:
        """Analisa preços históricos para um produto"""
        try:
            product_id = self._generate_product_id(title, platform)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Buscar histórico de preços
            cursor.execute("""
                SELECT price, original_price, discount_percentage, timestamp, url
                FROM price_history 
                WHERE product_id = ? 
                ORDER BY timestamp DESC
            """, (product_id,))
            
            price_records = []
            for row in cursor.fetchall():
                price_records.append(PriceRecord(
                    product_id=product_id,
                    title=title,
                    platform=platform,
                    price=row[0],
                    original_price=row[1],
                    discount_percentage=row[2],
                    timestamp=datetime.fromisoformat(row[3]),
                    url=row[4],
                    category=""
                ))
            
            if not price_records:
                # Primeiro registro deste produto
                return PriceAnalysis(
                    current_price=current_price,
                    original_price=None,
                    discount_percentage=None,
                    is_lowest_3m=True,
                    is_lowest_6m=True,
                    is_lowest_ever=True,
                    price_trend="stable",
                    price_history=[],
                    recommendations=["Novo produto - monitorar preços"]
                )
            
            # Análise de preços
            all_prices = [record.price for record in price_records]
            min_price = min(all_prices)
            max_price = max(all_prices)
            
            # Verificar menores preços por período
            now = datetime.now()
            three_months_ago = now - timedelta(days=90)
            six_months_ago = now - timedelta(days=180)
            
            prices_3m = [r.price for r in price_records if r.timestamp >= three_months_ago]
            prices_6m = [r.price for r in price_records if r.timestamp >= six_months_ago]
            
            min_price_3m = min(prices_3m) if prices_3m else current_price
            min_price_6m = min(prices_6m) if prices_6m else current_price
            
            # Determinar tendência de preço
            if len(price_records) >= 2:
                recent_prices = [r.price for r in price_records[:5]]  # Últimos 5 preços
                if len(recent_prices) >= 2:
                    if recent_prices[0] < recent_prices[-1]:
                        price_trend = "rising"
                    elif recent_prices[0] > recent_prices[-1]:
                        price_trend = "falling"
                    else:
                        price_trend = "stable"
                else:
                    price_trend = "stable"
            else:
                price_trend = "stable"
            
            # Gerar recomendações
            recommendations = []
            
            if current_price <= min_price_3m:
                recommendations.append("🔥 Menor preço em 3 meses!")
            
            if current_price <= min_price_6m:
                recommendations.append("🔥 Menor preço em 6 meses!")
            
            if current_price <= min_price:
                recommendations.append("🔥 Menor preço histórico!")
            
            if current_price < price_records[0].price:
                recommendations.append("📉 Preço caiu desde a última verificação")
            
            if current_price > price_records[0].price:
                recommendations.append("📈 Preço subiu desde a última verificação")
            
            # Verificar se é um bom momento para compra
            if current_price <= min_price * 1.1:  # Dentro de 10% do menor preço
                recommendations.append("💡 Bom momento para compra")
            
            conn.close()
            
            return PriceAnalysis(
                current_price=current_price,
                original_price=price_records[0].original_price if price_records else None,
                discount_percentage=price_records[0].discount_percentage if price_records else None,
                is_lowest_3m=current_price <= min_price_3m,
                is_lowest_6m=current_price <= min_price_6m,
                is_lowest_ever=current_price <= min_price,
                price_trend=price_trend,
                price_history=price_records,
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"Erro ao analisar preços: {e}")
            return None
    
    async def get_price_alerts(self, platform: str = None, 
                              min_discount: float = 20.0) -> List[Dict]:
        """Retorna alertas de preço baseados em critérios"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Buscar produtos com desconto significativo
            query = """
                SELECT p.id, p.title, p.platform, p.category,
                       ph.price, ph.original_price, ph.discount_percentage,
                       ph.timestamp, ph.url
                FROM products p
                JOIN price_history ph ON p.id = ph.product_id
                WHERE ph.discount_percentage >= ?
                AND ph.timestamp >= ?
            """
            
            params = [min_discount, (datetime.now() - timedelta(days=7)).isoformat()]
            
            if platform:
                query += " AND p.platform = ?"
                params.append(platform)
            
            query += " ORDER BY ph.discount_percentage DESC, ph.timestamp DESC"
            
            cursor.execute(query, params)
            
            alerts = []
            for row in cursor.fetchall():
                alerts.append({
                    "product_id": row[0],
                    "title": row[1],
                    "platform": row[2],
                    "category": row[3],
                    "current_price": row[4],
                    "original_price": row[5],
                    "discount_percentage": row[6],
                    "timestamp": row[7],
                    "url": row[8]
                })
            
            conn.close()
            return alerts
            
        except Exception as e:
            logger.error(f"Erro ao buscar alertas de preço: {e}")
            return []
    
    async def get_price_trends(self, platform: str = None, 
                              days: int = 30) -> Dict[str, List]:
        """Retorna tendências de preço por categoria"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Buscar tendências de preço por categoria
            query = """
                SELECT p.category, 
                       AVG(ph.price) as avg_price,
                       COUNT(*) as price_count,
                       DATE(ph.timestamp) as date
                FROM products p
                JOIN price_history ph ON p.id = ph.product_id
                WHERE ph.timestamp >= ?
            """
            
            params = [(datetime.now() - timedelta(days=days)).isoformat()]
            
            if platform:
                query += " AND p.platform = ?"
                params.append(platform)
            
            query += """
                GROUP BY p.category, DATE(ph.timestamp)
                ORDER BY p.category, date
            """
            
            cursor.execute(query, params)
            
            trends = {}
            for row in cursor.fetchall():
                category, avg_price, price_count, date = row
                
                if category not in trends:
                    trends[category] = []
                
                trends[category].append({
                    "date": date,
                    "avg_price": avg_price,
                    "price_count": price_count
                })
            
            conn.close()
            return trends
            
        except Exception as e:
            logger.error(f"Erro ao buscar tendências de preço: {e}")
            return {}
    
    async def cleanup_old_records(self, days_to_keep: int = 365) -> int:
        """Remove registros antigos para manter performance"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            
            # Contar registros a serem removidos
            cursor.execute("""
                SELECT COUNT(*) FROM price_history 
                WHERE timestamp < ?
            """, (cutoff_date.isoformat(),))
            
            count_to_delete = cursor.fetchone()[0]
            
            # Remover registros antigos
            cursor.execute("""
                DELETE FROM price_history 
                WHERE timestamp < ?
            """, (cutoff_date.isoformat(),))
            
            # Remover produtos sem histórico
            cursor.execute("""
                DELETE FROM products 
                WHERE id NOT IN (
                    SELECT DISTINCT product_id FROM price_history
                )
            """)
            
            conn.commit()
            conn.close()
            
            logger.info(f"Limpeza concluída: {count_to_delete} registros removidos")
            return count_to_delete
            
        except Exception as e:
            logger.error(f"Erro na limpeza: {e}")
            return 0


# Instância global
price_history_tracker = PriceHistoryTracker()
