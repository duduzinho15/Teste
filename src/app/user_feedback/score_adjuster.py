"""
Sistema de Ajuste Automático de Scores
Aplica ajustes de score baseado no feedback dos usuários
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any
from pathlib import Path
import sqlite3

from .feedback_analyzer import FeedbackAnalyzer, ScoreAdjustment
from .feedback_collector import FeedbackCollector
from src.core.geek_prioritizer import GeekPrioritizer


@dataclass
class ScoreAdjustmentHistory:
    """Histórico de ajustes de score"""
    category: str
    old_score: float
    new_score: float
    adjustment_factor: float
    confidence: float
    reasoning: str
    applied_at: datetime
    feedback_sample_size: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        data = asdict(self)
        data['applied_at'] = self.applied_at.isoformat()
        return data


@dataclass
class AdjustmentConfig:
    """Configuração para ajustes de score"""
    min_confidence: float = 0.5
    max_adjustment_factor: float = 2.0
    min_feedback_sample: int = 10
    auto_apply: bool = False
    adjustment_cooldown_days: int = 7
    backup_before_adjustment: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return asdict(self)


class ScoreAdjuster:
    """Sistema de ajuste automático de scores baseado no feedback"""
    
    def __init__(
        self,
        feedback_collector: FeedbackCollector,
        feedback_analyzer: FeedbackAnalyzer,
        config: Optional[AdjustmentConfig] = None
    ):
        self.feedback_collector = feedback_collector
        self.feedback_analyzer = feedback_analyzer
        self.geek_prioritizer = GeekPrioritizer()
        self.config = config or AdjustmentConfig()
        self.logger = logging.getLogger(__name__)
        
        # Inicializar banco de dados de histórico
        self._init_adjustment_history_db()
    
    def _init_adjustment_history_db(self) -> None:
        """Inicializa banco de dados para histórico de ajustes"""
        try:
            db_path = Path("data/score_adjustments.db")
            db_path.parent.mkdir(parents=True, exist_ok=True)
            
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                
                # Tabela de histórico de ajustes
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS score_adjustment_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        category TEXT NOT NULL,
                        old_score REAL NOT NULL,
                        new_score REAL NOT NULL,
                        adjustment_factor REAL NOT NULL,
                        confidence REAL NOT NULL,
                        reasoning TEXT NOT NULL,
                        applied_at TEXT NOT NULL,
                        feedback_sample_size INTEGER NOT NULL,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Tabela de configurações de ajuste
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS adjustment_configs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        config_name TEXT UNIQUE NOT NULL,
                        config_data TEXT NOT NULL,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Índices
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_adjustment_category ON score_adjustment_history(category)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_adjustment_applied_at ON score_adjustment_history(applied_at)")
                
                conn.commit()
                self.logger.info("Banco de dados de histórico de ajustes inicializado")
                
        except Exception as e:
            self.logger.error(f"Erro ao inicializar banco de dados de ajustes: {e}")
            raise
    
    async def analyze_and_suggest_adjustments(
        self,
        days: int = 30,
        min_confidence: Optional[float] = None,
        min_sample_size: Optional[int] = None
    ) -> List[ScoreAdjustment]:
        """Analisa feedback e sugere ajustes de score"""
        try:
            # Usar configurações padrão se não especificadas
            min_confidence = min_confidence or self.config.min_confidence
            min_sample_size = min_sample_size or self.config.min_feedback_sample
            
            # Obter sugestões de ajuste
            suggestions = await self.feedback_analyzer.suggest_score_adjustments(days)
            
            # Filtrar por critérios
            filtered_suggestions = []
            for suggestion in suggestions:
                # Verificar confiança mínima
                if suggestion.confidence < min_confidence:
                    self.logger.debug(f"Rejeitado ajuste para {suggestion.category}: confiança baixa ({suggestion.confidence:.2f})")
                    continue
                
                # Verificar tamanho mínimo da amostra
                sample_size = suggestion.supporting_data.get('total_feedback', 0)
                if sample_size < min_sample_size:
                    self.logger.debug(f"Rejeitado ajuste para {suggestion.category}: amostra pequena ({sample_size})")
                    continue
                
                # Verificar se já foi ajustado recentemente
                if await self._was_recently_adjusted(suggestion.category):
                    self.logger.debug(f"Rejeitado ajuste para {suggestion.category}: ajustado recentemente")
                    continue
                
                filtered_suggestions.append(suggestion)
            
            self.logger.info(f"Sugeridos {len(filtered_suggestions)} ajustes de score (de {len(suggestions)} total)")
            return filtered_suggestions
            
        except Exception as e:
            self.logger.error(f"Erro ao analisar e sugerir ajustes: {e}")
            return []
    
    async def apply_score_adjustment(
        self,
        adjustment: ScoreAdjustment,
        force: bool = False
    ) -> bool:
        """Aplica um ajuste de score específico"""
        try:
            # Verificações de segurança
            if not force:
                if not await self._validate_adjustment(adjustment):
                    return False
            
            # Backup antes do ajuste (se habilitado)
            if self.config.backup_before_adjustment:
                await self._backup_current_scores()
            
            # Aplicar ajuste no GeekPrioritizer
            success = await self._apply_adjustment_to_prioritizer(adjustment)
            
            if success:
                # Registrar no histórico
                await self._record_adjustment_history(adjustment)
                
                self.logger.info(
                    f"Ajuste aplicado: {adjustment.category} "
                    f"({adjustment.current_score:.2f} -> {adjustment.suggested_score:.2f})"
                )
                return True
            else:
                self.logger.error(f"Falha ao aplicar ajuste para {adjustment.category}")
                return False
                
        except Exception as e:
            self.logger.error(f"Erro ao aplicar ajuste de score: {e}")
            return False
    
    async def apply_automatic_adjustments(
        self,
        days: int = 30,
        max_adjustments: int = 10
    ) -> List[ScoreAdjustment]:
        """Aplica ajustes automaticamente baseado no feedback"""
        try:
            if not self.config.auto_apply:
                self.logger.warning("Ajuste automático desabilitado na configuração")
                return []
            
            # Obter sugestões de ajuste
            suggestions = await self.analyze_and_suggest_adjustments(days)
            
            # Limitar número de ajustes
            suggestions = suggestions[:max_adjustments]
            
            # Aplicar ajustes
            applied_adjustments = []
            for suggestion in suggestions:
                success = await self.apply_score_adjustment(suggestion, force=False)
                if success:
                    applied_adjustments.append(suggestion)
                
                # Pequena pausa entre ajustes
                await asyncio.sleep(0.1)
            
            self.logger.info(f"Aplicados {len(applied_adjustments)} ajustes automáticos")
            return applied_adjustments
            
        except Exception as e:
            self.logger.error(f"Erro ao aplicar ajustes automáticos: {e}")
            return []
    
    async def get_adjustment_history(
        self,
        category: Optional[str] = None,
        days: int = 90
    ) -> List[ScoreAdjustmentHistory]:
        """Obtém histórico de ajustes de score"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            with sqlite3.connect("data/score_adjustments.db") as conn:
                cursor = conn.cursor()
                
                if category:
                    cursor.execute("""
                        SELECT category, old_score, new_score, adjustment_factor, confidence,
                               reasoning, applied_at, feedback_sample_size
                        FROM score_adjustment_history
                        WHERE category = ? AND applied_at >= ?
                        ORDER BY applied_at DESC
                    """, (category, cutoff_date.isoformat()))
                else:
                    cursor.execute("""
                        SELECT category, old_score, new_score, adjustment_factor, confidence,
                               reasoning, applied_at, feedback_sample_size
                        FROM score_adjustment_history
                        WHERE applied_at >= ?
                        ORDER BY applied_at DESC
                    """, (cutoff_date.isoformat(),))
                
                history = []
                for row in cursor.fetchall():
                    adjustment = ScoreAdjustmentHistory(
                        category=row[0],
                        old_score=row[1],
                        new_score=row[2],
                        adjustment_factor=row[3],
                        confidence=row[4],
                        reasoning=row[5],
                        applied_at=datetime.fromisoformat(row[6]),
                        feedback_sample_size=row[7]
                    )
                    history.append(adjustment)
                
                return history
                
        except Exception as e:
            self.logger.error(f"Erro ao obter histórico de ajustes: {e}")
            return []
    
    async def rollback_last_adjustment(
        self,
        category: str
    ) -> bool:
        """Reverte o último ajuste aplicado para uma categoria"""
        try:
            # Obter último ajuste
            history = await self.get_adjustment_history(category, days=365)
            if not history:
                self.logger.warning(f"Nenhum ajuste encontrado para categoria {category}")
                return False
            
            last_adjustment = history[0]
            
            # Criar ajuste de reversão
            rollback_adjustment = ScoreAdjustment(
                category=category,
                current_score=last_adjustment.new_score,
                suggested_score=last_adjustment.old_score,
                adjustment_factor=1.0 / last_adjustment.adjustment_factor,
                confidence=1.0,
                reasoning=f"Rollback do ajuste aplicado em {last_adjustment.applied_at.strftime('%Y-%m-%d %H:%M')}",
                supporting_data={"rollback_of": last_adjustment.to_dict()}
            )
            
            # Aplicar reversão
            success = await self.apply_score_adjustment(rollback_adjustment, force=True)
            
            if success:
                self.logger.info(f"Rollback aplicado para {category}: {last_adjustment.new_score:.2f} -> {last_adjustment.old_score:.2f}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Erro ao fazer rollback: {e}")
            return False
    
    async def _validate_adjustment(self, adjustment: ScoreAdjustment) -> bool:
        """Valida se um ajuste pode ser aplicado"""
        try:
            # Verificar fator de ajuste máximo
            if adjustment.adjustment_factor > self.config.max_adjustment_factor:
                self.logger.warning(
                    f"Ajuste rejeitado para {adjustment.category}: "
                    f"fator muito alto ({adjustment.adjustment_factor:.2f})"
                )
                return False
            
            # Verificar se o score sugerido está em um intervalo razoável
            if adjustment.suggested_score < 0 or adjustment.suggested_score > 10:
                self.logger.warning(
                    f"Ajuste rejeitado para {adjustment.category}: "
                    f"score fora do intervalo válido ({adjustment.suggested_score:.2f})"
                )
                return False
            
            # Verificar se já foi ajustado recentemente
            if await self._was_recently_adjusted(adjustment.category):
                self.logger.warning(
                    f"Ajuste rejeitado para {adjustment.category}: "
                    f"ajustado recentemente"
                )
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao validar ajuste: {e}")
            return False
    
    async def _was_recently_adjusted(self, category: str) -> bool:
        """Verifica se uma categoria foi ajustada recentemente"""
        try:
            cutoff_date = datetime.now() - timedelta(days=self.config.adjustment_cooldown_days)
            
            with sqlite3.connect("data/score_adjustments.db") as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT COUNT(*) FROM score_adjustment_history
                    WHERE category = ? AND applied_at >= ?
                """, (category, cutoff_date.isoformat()))
                
                count = cursor.fetchone()[0]
                return count > 0
                
        except Exception as e:
            self.logger.error(f"Erro ao verificar ajustes recentes: {e}")
            return False
    
    async def _backup_current_scores(self) -> None:
        """Faz backup dos scores atuais"""
        try:
            # Implementar backup dos scores atuais do GeekPrioritizer
            # Por enquanto, apenas log
            self.logger.info("Backup de scores solicitado (não implementado)")
            
        except Exception as e:
            self.logger.error(f"Erro ao fazer backup: {e}")
    
    async def _apply_adjustment_to_prioritizer(self, adjustment: ScoreAdjustment) -> bool:
        """Aplica ajuste no GeekPrioritizer"""
        try:
            # Por enquanto, apenas simular aplicação
            # Em uma implementação real, isso modificaria os pesos do GeekPrioritizer
            
            self.logger.info(
                f"Simulando aplicação de ajuste: {adjustment.category} "
                f"({adjustment.current_score:.2f} -> {adjustment.suggested_score:.2f})"
            )
            
            # Aqui você implementaria a lógica real de ajuste
            # Por exemplo:
            # self.geek_prioritizer.update_category_weight(adjustment.category, adjustment.suggested_score)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao aplicar ajuste no prioritizer: {e}")
            return False
    
    async def _record_adjustment_history(self, adjustment: ScoreAdjustment) -> None:
        """Registra ajuste no histórico"""
        try:
            with sqlite3.connect("data/score_adjustments.db") as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO score_adjustment_history
                    (category, old_score, new_score, adjustment_factor, confidence,
                     reasoning, applied_at, feedback_sample_size)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    adjustment.category,
                    adjustment.current_score,
                    adjustment.suggested_score,
                    adjustment.adjustment_factor,
                    adjustment.confidence,
                    adjustment.reasoning,
                    datetime.now().isoformat(),
                    adjustment.supporting_data.get('total_feedback', 0)
                ))
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"Erro ao registrar histórico de ajuste: {e}")
    
    async def get_adjustment_summary(self, days: int = 30) -> Dict[str, Any]:
        """Obtém resumo dos ajustes aplicados"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            with sqlite3.connect("data/score_adjustments.db") as conn:
                cursor = conn.cursor()
                
                # Total de ajustes
                cursor.execute("""
                    SELECT COUNT(*) FROM score_adjustment_history
                    WHERE applied_at >= ?
                """, (cutoff_date.isoformat(),))
                total_adjustments = cursor.fetchone()[0]
                
                # Ajustes por categoria
                cursor.execute("""
                    SELECT category, COUNT(*) FROM score_adjustment_history
                    WHERE applied_at >= ?
                    GROUP BY category
                """, (cutoff_date.isoformat(),))
                adjustments_by_category = dict(cursor.fetchall())
                
                # Média de confiança
                cursor.execute("""
                    SELECT AVG(confidence) FROM score_adjustment_history
                    WHERE applied_at >= ?
                """, (cutoff_date.isoformat(),))
                avg_confidence = cursor.fetchone()[0] or 0
                
                return {
                    "period_days": days,
                    "total_adjustments": total_adjustments,
                    "adjustments_by_category": adjustments_by_category,
                    "average_confidence": avg_confidence,
                    "cutoff_date": cutoff_date.isoformat()
                }
                
        except Exception as e:
            self.logger.error(f"Erro ao obter resumo de ajustes: {e}")
            return {}
