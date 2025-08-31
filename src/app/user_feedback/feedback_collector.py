"""
Sistema de Coleta de Feedback dos Usuários
Coleta feedback através de múltiplas fontes e armazena para análise
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any, Union
from decimal import Decimal
from enum import Enum
import sqlite3
from pathlib import Path

from src.core.geek_prioritizer import GeekPrioritizer
from src.core.models import Offer


class FeedbackType(Enum):
    """Tipos de feedback disponíveis"""
    CLICK = "click"
    PURCHASE = "purchase"
    LIKE = "like"
    DISLIKE = "dislike"
    SHARE = "share"
    SAVE = "save"
    RATING = "rating"
    COMMENT = "comment"
    CATEGORY_PREFERENCE = "category_preference"
    PRICE_RANGE = "price_range"


class FeedbackSource(Enum):
    """Fontes de feedback"""
    TELEGRAM = "telegram"
    DASHBOARD = "dashboard"
    WEB_APP = "web_app"
    API = "api"
    AUTOMATED = "automated"


@dataclass
class UserFeedback:
    """Dados de feedback de um usuário"""
    user_id: str
    offer_id: str
    feedback_type: FeedbackType
    feedback_value: Union[int, float, str]
    source: FeedbackSource
    timestamp: datetime
    session_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        data = asdict(self)
        data['feedback_type'] = self.feedback_type.value
        data['source'] = self.source.value
        data['timestamp'] = self.timestamp.isoformat()
        return data


@dataclass
class FeedbackSession:
    """Sessão de feedback do usuário"""
    session_id: str
    user_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    feedback_count: int = 0
    geek_products_viewed: int = 0
    general_products_viewed: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        data = asdict(self)
        data['start_time'] = self.start_time.isoformat()
        if self.end_time:
            data['end_time'] = self.end_time.isoformat()
        return data


class FeedbackCollector:
    """Sistema de coleta de feedback dos usuários"""
    
    def __init__(self, db_path: str = "data/user_feedback.db"):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        self.geek_prioritizer = GeekPrioritizer()
        
        # Criar diretório se não existir
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Inicializar banco de dados
        self._init_database()
    
    def _init_database(self) -> None:
        """Inicializa o banco de dados SQLite"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Tabela de feedback
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS user_feedback (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT NOT NULL,
                        offer_id TEXT NOT NULL,
                        feedback_type TEXT NOT NULL,
                        feedback_value TEXT NOT NULL,
                        source TEXT NOT NULL,
                        timestamp TEXT NOT NULL,
                        session_id TEXT,
                        metadata TEXT,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Tabela de sessões
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS feedback_sessions (
                        session_id TEXT PRIMARY KEY,
                        user_id TEXT NOT NULL,
                        start_time TEXT NOT NULL,
                        end_time TEXT,
                        feedback_count INTEGER DEFAULT 0,
                        geek_products_viewed INTEGER DEFAULT 0,
                        general_products_viewed INTEGER DEFAULT 0,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Índices para performance
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_feedback_user_id ON user_feedback(user_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_feedback_timestamp ON user_feedback(timestamp)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_feedback_type ON user_feedback(feedback_type)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_feedback_sessions_user_id ON feedback_sessions(user_id)")
                
                conn.commit()
                self.logger.info("Banco de dados de feedback inicializado com sucesso")
                
        except Exception as e:
            self.logger.error(f"Erro ao inicializar banco de dados: {e}")
            raise
    
    async def collect_feedback(
        self,
        user_id: str,
        offer: Offer,
        feedback_type: FeedbackType,
        feedback_value: Union[int, float, str],
        source: FeedbackSource = FeedbackSource.TELEGRAM,
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> UserFeedback:
        """Coleta feedback de um usuário para uma oferta"""
        try:
            # Criar sessão se não existir
            if not session_id:
                session_id = await self._create_session(user_id)
            
            # Criar objeto de feedback
            feedback = UserFeedback(
                user_id=user_id,
                offer_id=getattr(offer, 'id', f"{offer.url}_{offer.title}"),
                feedback_type=feedback_type,
                feedback_value=feedback_value,
                source=source,
                timestamp=datetime.now(),
                session_id=session_id,
                metadata=metadata or {}
            )
            
            # Salvar no banco de dados
            await self._save_feedback(feedback)
            
            # Atualizar sessão
            await self._update_session(session_id, offer)
            
            self.logger.info(f"Feedback coletado: {user_id} -> {feedback_type.value} -> {feedback_value}")
            return feedback
            
        except Exception as e:
            self.logger.error(f"Erro ao coletar feedback: {e}")
            raise
    
    async def collect_telegram_feedback(
        self,
        user_id: str,
        offer: Offer,
        message_text: str
    ) -> UserFeedback:
        """Coleta feedback de mensagens do Telegram"""
        try:
            # Analisar texto da mensagem para determinar tipo de feedback
            feedback_type, feedback_value = self._parse_telegram_message(message_text)
            
            return await self.collect_feedback(
                user_id=user_id,
                offer=offer,
                feedback_type=feedback_type,
                feedback_value=feedback_value,
                source=FeedbackSource.TELEGRAM,
                metadata={"message_text": message_text}
            )
            
        except Exception as e:
            self.logger.error(f"Erro ao coletar feedback do Telegram: {e}")
            raise
    
    async def collect_click_feedback(
        self,
        user_id: str,
        offer: Offer,
        session_id: Optional[str] = None
    ) -> UserFeedback:
        """Coleta feedback de clique em oferta"""
        return await self.collect_feedback(
            user_id=user_id,
            offer=offer,
            feedback_type=FeedbackType.CLICK,
            feedback_value=1,
            source=FeedbackSource.TELEGRAM,
            session_id=session_id,
            metadata={"action": "click"}
        )
    
    async def collect_purchase_feedback(
        self,
        user_id: str,
        offer: Offer,
        purchase_value: Decimal,
        session_id: Optional[str] = None
    ) -> UserFeedback:
        """Coleta feedback de compra"""
        return await self.collect_feedback(
            user_id=user_id,
            offer=offer,
            feedback_type=FeedbackType.PURCHASE,
            feedback_value=str(purchase_value),
            source=FeedbackSource.TELEGRAM,
            session_id=session_id,
            metadata={"purchase_value": str(purchase_value)}
        )
    
    async def collect_rating_feedback(
        self,
        user_id: str,
        offer: Offer,
        rating: int,
        session_id: Optional[str] = None
    ) -> UserFeedback:
        """Coleta feedback de avaliação (1-5)"""
        if not 1 <= rating <= 5:
            raise ValueError("Rating deve estar entre 1 e 5")
        
        return await self.collect_feedback(
            user_id=user_id,
            offer=offer,
            feedback_type=FeedbackType.RATING,
            feedback_value=rating,
            source=FeedbackSource.TELEGRAM,
            session_id=session_id,
            metadata={"rating": rating}
        )
    
    async def collect_category_preference(
        self,
        user_id: str,
        category: str,
        preference_score: float,
        session_id: Optional[str] = None
    ) -> UserFeedback:
        """Coleta preferência de categoria"""
        return await self.collect_feedback(
            user_id=user_id,
            offer=Offer(
                title=f"Preferência {category}",
                price=Decimal("0.01"),
                url="https://exemplo.com/preferencia",
                store="Sistema",
                category=category,
                scraped_at=datetime.now()
            ),  # Oferta dummy
            feedback_type=FeedbackType.CATEGORY_PREFERENCE,
            feedback_value=preference_score,
            source=FeedbackSource.TELEGRAM,
            session_id=session_id,
            metadata={"category": category, "preference_score": preference_score}
        )
    
    def _parse_telegram_message(self, message_text: str) -> tuple[FeedbackType, Union[int, float, str]]:
        """Analisa mensagem do Telegram para extrair feedback"""
        text = message_text.lower().strip()
        
        # Avaliações
        if "5" in text or "excelente" in text or "ótimo" in text:
            return FeedbackType.RATING, 5
        elif "4" in text or "bom" in text or "gostei" in text:
            return FeedbackType.RATING, 4
        elif "3" in text or "regular" in text or "ok" in text:
            return FeedbackType.RATING, 3
        elif "2" in text or "ruim" in text or "não gostei" in text:
            return FeedbackType.RATING, 2
        elif "1" in text or "péssimo" in text or "horrível" in text:
            return FeedbackType.RATING, 1
        
        # Likes/Dislikes
        elif any(word in text for word in ["👍", "like", "gosto", "legal", "show"]):
            return FeedbackType.LIKE, 1
        elif any(word in text for word in ["👎", "dislike", "não gosto", "ruim"]):
            return FeedbackType.DISLIKE, 1
        
        # Compra
        elif any(word in text for word in ["comprei", "comprado", "adquirido", "purchase"]):
            return FeedbackType.PURCHASE, "confirmed"
        
        # Compartilhamento
        elif any(word in text for word in ["compartilhar", "share", "enviar"]):
            return FeedbackType.SHARE, 1
        
        # Salvar
        elif any(word in text for word in ["salvar", "save", "guardar"]):
            return FeedbackType.SAVE, 1
        
        # Padrão: clique
        return FeedbackType.CLICK, 1
    
    async def _create_session(self, user_id: str) -> str:
        """Cria uma nova sessão de feedback"""
        session_id = f"{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO feedback_sessions 
                    (session_id, user_id, start_time) 
                    VALUES (?, ?, ?)
                """, (session_id, user_id, datetime.now().isoformat()))
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"Erro ao criar sessão: {e}")
            raise
        
        return session_id
    
    async def _update_session(self, session_id: str, offer: Offer) -> None:
        """Atualiza estatísticas da sessão"""
        try:
            # Determinar se é produto geek
            category = offer.category if hasattr(offer, 'category') else ''
            is_geek = self.geek_prioritizer.calculate_geek_score(category) > 0.5
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Atualizar contadores
                if is_geek:
                    cursor.execute("""
                        UPDATE feedback_sessions 
                        SET feedback_count = feedback_count + 1,
                            geek_products_viewed = geek_products_viewed + 1
                        WHERE session_id = ?
                    """, (session_id,))
                else:
                    cursor.execute("""
                        UPDATE feedback_sessions 
                        SET feedback_count = feedback_count + 1,
                            general_products_viewed = general_products_viewed + 1
                        WHERE session_id = ?
                    """, (session_id,))
                
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"Erro ao atualizar sessão: {e}")
    
    async def _save_feedback(self, feedback: UserFeedback) -> None:
        """Salva feedback no banco de dados"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO user_feedback 
                    (user_id, offer_id, feedback_type, feedback_value, source, 
                     timestamp, session_id, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    feedback.user_id,
                    feedback.offer_id,
                    feedback.feedback_type.value,
                    str(feedback.feedback_value),
                    feedback.source.value,
                    feedback.timestamp.isoformat(),
                    feedback.session_id,
                    json.dumps(feedback.metadata) if feedback.metadata else None
                ))
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"Erro ao salvar feedback: {e}")
            raise
    
    async def get_user_feedback_history(
        self,
        user_id: str,
        days: int = 30
    ) -> List[UserFeedback]:
        """Obtém histórico de feedback de um usuário"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT user_id, offer_id, feedback_type, feedback_value, source,
                           timestamp, session_id, metadata
                    FROM user_feedback
                    WHERE user_id = ? AND timestamp >= ?
                    ORDER BY timestamp DESC
                """, (user_id, cutoff_date.isoformat()))
                
                feedbacks = []
                for row in cursor.fetchall():
                    feedback = UserFeedback(
                        user_id=row[0],
                        offer_id=row[1],
                        feedback_type=FeedbackType(row[2]),
                        feedback_value=row[3],
                        source=FeedbackSource(row[4]),
                        timestamp=datetime.fromisoformat(row[5]),
                        session_id=row[6],
                        metadata=json.loads(row[7]) if row[7] else {}
                    )
                    feedbacks.append(feedback)
                
                return feedbacks
                
        except Exception as e:
            self.logger.error(f"Erro ao obter histórico de feedback: {e}")
            return []
    
    async def get_feedback_summary(self, days: int = 7) -> Dict[str, Any]:
        """Obtém resumo de feedback dos últimos dias"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Total de feedbacks
                cursor.execute("""
                    SELECT COUNT(*) FROM user_feedback 
                    WHERE timestamp >= ?
                """, (cutoff_date.isoformat(),))
                total_feedback = cursor.fetchone()[0]
                
                # Feedback por tipo
                cursor.execute("""
                    SELECT feedback_type, COUNT(*) 
                    FROM user_feedback 
                    WHERE timestamp >= ?
                    GROUP BY feedback_type
                """, (cutoff_date.isoformat(),))
                feedback_by_type = dict(cursor.fetchall())
                
                # Usuários únicos
                cursor.execute("""
                    SELECT COUNT(DISTINCT user_id) 
                    FROM user_feedback 
                    WHERE timestamp >= ?
                """, (cutoff_date.isoformat(),))
                unique_users = cursor.fetchone()[0]
                
                return {
                    "period_days": days,
                    "total_feedback": total_feedback,
                    "unique_users": unique_users,
                    "feedback_by_type": feedback_by_type,
                    "cutoff_date": cutoff_date.isoformat()
                }
                
        except Exception as e:
            self.logger.error(f"Erro ao obter resumo de feedback: {e}")
            return {}
