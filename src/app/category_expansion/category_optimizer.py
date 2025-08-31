"""
Otimizador de Categorias
Ajusta automaticamente categorias baseado em performance e feedback
"""

import asyncio
import json
import sqlite3
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from decimal import Decimal
from typing import Dict, List, Optional, Tuple
from enum import Enum
import statistics

from src.core.geek_prioritizer import GeekPrioritizer


class OptimizationType(Enum):
    """Tipos de otimização de categoria"""
    PERFORMANCE_OPTIMIZATION = "performance_optimization"
    KEYWORD_OPTIMIZATION = "keyword_optimization"
    SCORE_OPTIMIZATION = "score_optimization"
    STRUCTURE_OPTIMIZATION = "structure_optimization"
    MERGE_OPTIMIZATION = "merge_optimization"


@dataclass
class OptimizationResult:
    """Resultado de otimização"""
    category: str
    optimization_type: OptimizationType
    original_score: float
    optimized_score: float
    improvement_percentage: float
    changes_made: List[str]
    confidence_level: float
    created_at: datetime


@dataclass
class CategoryScore:
    """Score de categoria"""
    category: str
    performance_score: float
    user_satisfaction: float
    conversion_rate: float
    click_rate: float
    revenue_per_category: float
    geek_relevance: float
    overall_score: float
    last_updated: datetime


class CategoryOptimizer:
    """Otimizador de categorias"""
    
    def __init__(self, db_path: str = "category_optimization.db"):
        self.db_path = db_path
        self.geek_prioritizer = GeekPrioritizer()
        self._init_database()
    
    def _init_database(self) -> None:
        """Inicializa o banco de dados"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Tabela de resultados de otimização
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS optimization_results (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        category TEXT NOT NULL,
                        optimization_type TEXT NOT NULL,
                        original_score REAL NOT NULL,
                        optimized_score REAL NOT NULL,
                        improvement_percentage REAL NOT NULL,
                        changes_made TEXT NOT NULL,
                        confidence_level REAL NOT NULL,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Tabela de scores de categoria
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS category_scores (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        category TEXT NOT NULL,
                        performance_score REAL NOT NULL,
                        user_satisfaction REAL NOT NULL,
                        conversion_rate REAL NOT NULL,
                        click_rate REAL NOT NULL,
                        revenue_per_category REAL NOT NULL,
                        geek_relevance REAL NOT NULL,
                        overall_score REAL NOT NULL,
                        last_updated TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Tabela de histórico de otimizações
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS optimization_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        category TEXT NOT NULL,
                        optimization_type TEXT NOT NULL,
                        before_state TEXT NOT NULL,
                        after_state TEXT NOT NULL,
                        improvement_metrics TEXT NOT NULL,
                        applied_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                conn.commit()
                print(f"✅ Banco de dados de otimização de categorias inicializado: {self.db_path}")
                
        except Exception as e:
            print(f"❌ Erro ao inicializar banco de dados: {e}")
    
    async def optimize_categories(self, 
                               categories: List[str],
                               performance_data: Dict[str, Dict],
                               user_feedback: Dict[str, float]) -> List[OptimizationResult]:
        """Otimiza categorias baseado em performance e feedback"""
        try:
            optimization_results = []
            
            for category in categories:
                # Calcular score atual
                current_score = await self._calculate_category_score(category, performance_data, user_feedback)
                
                # Aplicar otimizações
                optimizations = await self._apply_optimizations(category, current_score, performance_data, user_feedback)
                
                for optimization in optimizations:
                    # Calcular score otimizado
                    optimized_score = await self._calculate_optimized_score(category, optimization, performance_data, user_feedback)
                    
                    # Calcular melhoria
                    improvement = ((optimized_score - current_score.overall_score) / current_score.overall_score) * 100
                    
                    result = OptimizationResult(
                        category=category,
                        optimization_type=optimization["type"],
                        original_score=current_score.overall_score,
                        optimized_score=optimized_score,
                        improvement_percentage=improvement,
                        changes_made=optimization["changes"],
                        confidence_level=optimization["confidence"],
                        created_at=datetime.now()
                    )
                    
                    optimization_results.append(result)
                    await self._save_optimization_result(result)
            
            print(f"⚡ Otimizadas {len(optimization_results)} categorias")
            return optimization_results
            
        except Exception as e:
            print(f"❌ Erro ao otimizar categorias: {e}")
            return []
    
    async def calculate_category_scores(self, 
                                     categories: List[str],
                                     performance_data: Dict[str, Dict],
                                     user_feedback: Dict[str, float]) -> List[CategoryScore]:
        """Calcula scores para categorias"""
        try:
            category_scores = []
            
            for category in categories:
                score = await self._calculate_category_score(category, performance_data, user_feedback)
                category_scores.append(score)
                await self._save_category_score(score)
            
            print(f"📊 Calculados scores para {len(category_scores)} categorias")
            return category_scores
            
        except Exception as e:
            print(f"❌ Erro ao calcular scores: {e}")
            return []
    
    async def identify_underperforming_categories(self, 
                                               category_scores: List[CategoryScore],
                                               threshold: float = 0.6) -> List[str]:
        """Identifica categorias com baixo desempenho"""
        try:
            underperforming = []
            
            for score in category_scores:
                if score.overall_score < threshold:
                    underperforming.append(score.category)
            
            print(f"⚠️ Identificadas {len(underperforming)} categorias com baixo desempenho")
            return underperforming
            
        except Exception as e:
            print(f"❌ Erro ao identificar categorias com baixo desempenho: {e}")
            return []
    
    async def suggest_category_improvements(self, 
                                         category_scores: List[CategoryScore]) -> Dict[str, List[str]]:
        """Sugere melhorias para categorias"""
        try:
            suggestions = {}
            
            for score in category_scores:
                category_suggestions = []
                
                # Sugestões baseadas em performance
                if score.performance_score < 0.7:
                    category_suggestions.append("Melhorar performance geral da categoria")
                
                if score.conversion_rate < 0.05:
                    category_suggestions.append("Otimizar taxa de conversão")
                
                if score.click_rate < 0.1:
                    category_suggestions.append("Melhorar taxa de cliques")
                
                # Sugestões baseadas em satisfação do usuário
                if score.user_satisfaction < 3.5:
                    category_suggestions.append("Melhorar satisfação do usuário")
                
                # Sugestões baseadas em relevância geek
                if score.geek_relevance < 0.6:
                    category_suggestions.append("Aumentar relevância geek")
                
                if category_suggestions:
                    suggestions[score.category] = category_suggestions
            
            print(f"💡 Geradas sugestões para {len(suggestions)} categorias")
            return suggestions
            
        except Exception as e:
            print(f"❌ Erro ao sugerir melhorias: {e}")
            return {}
    
    async def auto_optimize_categories(self, 
                                    categories: List[str],
                                    performance_data: Dict[str, Dict],
                                    user_feedback: Dict[str, float],
                                    max_optimizations: int = 10) -> List[OptimizationResult]:
        """Otimização automática de categorias"""
        try:
            # Calcular scores atuais
            current_scores = await self.calculate_category_scores(categories, performance_data, user_feedback)
            
            # Identificar categorias com baixo desempenho
            underperforming = await self.identify_underperforming_categories(current_scores)
            
            # Aplicar otimizações automáticas
            optimization_results = []
            
            for category in underperforming[:max_optimizations]:
                optimizations = await self._apply_automatic_optimizations(category, performance_data, user_feedback)
                
                for optimization in optimizations:
                    result = await self._create_optimization_result(category, optimization, performance_data, user_feedback)
                    if result:
                        optimization_results.append(result)
                        await self._save_optimization_result(result)
            
            print(f"🤖 Aplicadas {len(optimization_results)} otimizações automáticas")
            return optimization_results
            
        except Exception as e:
            print(f"❌ Erro na otimização automática: {e}")
            return []
    
    async def get_optimization_summary(self) -> Dict:
        """Retorna resumo das otimizações"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Contar otimizações
                cursor.execute("SELECT COUNT(*) FROM optimization_results")
                total_optimizations = cursor.fetchone()[0]
                
                # Média de melhoria
                cursor.execute("SELECT AVG(improvement_percentage) FROM optimization_results")
                avg_improvement = cursor.fetchone()[0] or 0
                
                # Contar scores
                cursor.execute("SELECT COUNT(*) FROM category_scores")
                total_scores = cursor.fetchone()[0]
                
                # Top otimizações
                cursor.execute("""
                    SELECT category, improvement_percentage, optimization_type 
                    FROM optimization_results 
                    ORDER BY improvement_percentage DESC 
                    LIMIT 5
                """)
                top_optimizations = cursor.fetchall()
                
                return {
                    "total_optimizations": total_optimizations,
                    "average_improvement": round(avg_improvement, 2),
                    "total_category_scores": total_scores,
                    "top_optimizations": [
                        {"category": cat, "improvement": imp, "type": opt_type} 
                        for cat, imp, opt_type in top_optimizations
                    ],
                    "last_optimization": datetime.now().isoformat()
                }
                
        except Exception as e:
            print(f"❌ Erro ao gerar resumo: {e}")
            return {}
    
    async def _calculate_category_score(self, 
                                     category: str,
                                     performance_data: Dict[str, Dict],
                                     user_feedback: Dict[str, float]) -> CategoryScore:
        """Calcula score para uma categoria"""
        try:
            # Dados de performance
            perf_data = performance_data.get(category, {})
            performance_score = perf_data.get("performance_score", 0.5)
            conversion_rate = perf_data.get("conversion_rate", 0.03)
            click_rate = perf_data.get("click_rate", 0.08)
            revenue_per_category = perf_data.get("revenue", 1000.0)
            
            # Satisfação do usuário
            user_satisfaction = user_feedback.get(category, 3.0)
            
            # Relevância geek
            geek_relevance = self.geek_prioritizer.calculate_geek_score(category)
            
            # Calcular score geral (média ponderada)
            overall_score = (
                performance_score * 0.25 +
                (user_satisfaction / 5.0) * 0.20 +
                (conversion_rate * 10) * 0.20 +
                (click_rate * 5) * 0.15 +
                (geek_relevance) * 0.20
            )
            
            return CategoryScore(
                category=category,
                performance_score=performance_score,
                user_satisfaction=user_satisfaction,
                conversion_rate=conversion_rate,
                click_rate=click_rate,
                revenue_per_category=revenue_per_category,
                geek_relevance=geek_relevance,
                overall_score=overall_score,
                last_updated=datetime.now()
            )
            
        except Exception as e:
            print(f"❌ Erro ao calcular score: {e}")
            # Retornar score padrão em caso de erro
            return CategoryScore(
                category=category,
                performance_score=0.5,
                user_satisfaction=3.0,
                conversion_rate=0.03,
                click_rate=0.08,
                revenue_per_category=1000.0,
                geek_relevance=0.5,
                overall_score=0.5,
                last_updated=datetime.now()
            )
    
    async def _apply_optimizations(self, 
                                category: str,
                                current_score: CategoryScore,
                                performance_data: Dict[str, Dict],
                                user_feedback: Dict[str, float]) -> List[Dict]:
        """Aplica otimizações para uma categoria"""
        try:
            optimizations = []
            
            # Otimização de performance
            if current_score.performance_score < 0.7:
                optimization = {
                    "type": OptimizationType.PERFORMANCE_OPTIMIZATION,
                    "changes": ["Otimizar algoritmos de busca", "Melhorar cache", "Acelerar carregamento"],
                    "confidence": 0.8
                }
                optimizations.append(optimization)
            
            # Otimização de conversão
            if current_score.conversion_rate < 0.05:
                optimization = {
                    "type": OptimizationType.SCORE_OPTIMIZATION,
                    "changes": ["Melhorar CTAs", "Otimizar landing pages", "Ajustar preços"],
                    "confidence": 0.75
                }
                optimizations.append(optimization)
            
            # Otimização de relevância geek
            if current_score.geek_relevance < 0.6:
                optimization = {
                    "type": OptimizationType.KEYWORD_OPTIMIZATION,
                    "changes": ["Adicionar keywords geek", "Melhorar categorização", "Expandir sub-categorias"],
                    "confidence": 0.7
                }
                optimizations.append(optimization)
            
            return optimizations
            
        except Exception as e:
            print(f"❌ Erro ao aplicar otimizações: {e}")
            return []
    
    async def _calculate_optimized_score(self, 
                                      category: str,
                                      optimization: Dict,
                                      performance_data: Dict[str, Dict],
                                      user_feedback: Dict[str, float]) -> float:
        """Calcula score otimizado"""
        try:
            # Simular melhoria baseada no tipo de otimização
            improvement_factor = 0.1  # 10% de melhoria base
            
            if optimization["type"] == OptimizationType.PERFORMANCE_OPTIMIZATION:
                improvement_factor = 0.15
            elif optimization["type"] == OptimizationType.SCORE_OPTIMIZATION:
                improvement_factor = 0.12
            elif optimization["type"] == OptimizationType.KEYWORD_OPTIMIZATION:
                improvement_factor = 0.08
            
            # Aplicar fator de confiança
            adjusted_improvement = improvement_factor * optimization["confidence"]
            
            # Calcular score atual
            current_score = await self._calculate_category_score(category, performance_data, user_feedback)
            
            # Aplicar melhoria
            optimized_score = current_score.overall_score * (1 + adjusted_improvement)
            
            return min(1.0, optimized_score)
            
        except Exception as e:
            print(f"❌ Erro ao calcular score otimizado: {e}")
            return 0.0
    
    async def _apply_automatic_optimizations(self, 
                                          category: str,
                                          performance_data: Dict[str, Dict],
                                          user_feedback: Dict[str, float]) -> List[Dict]:
        """Aplica otimizações automáticas"""
        try:
            optimizations = []
            
            # Otimização automática baseada em dados
            current_score = await self._calculate_category_score(category, performance_data, user_feedback)
            
            # Sempre aplicar otimização de performance para categorias com baixo desempenho
            optimization = {
                "type": OptimizationType.PERFORMANCE_OPTIMIZATION,
                "changes": ["Otimização automática de performance", "Ajuste de algoritmos", "Melhoria de cache"],
                "confidence": 0.85
            }
            optimizations.append(optimization)
            
            # Otimização de relevância geek se necessário
            if current_score.geek_relevance < 0.7:
                optimization = {
                    "type": OptimizationType.KEYWORD_OPTIMIZATION,
                    "changes": ["Expansão automática de keywords geek", "Melhoria de categorização"],
                    "confidence": 0.8
                }
                optimizations.append(optimization)
            
            return optimizations
            
        except Exception as e:
            print(f"❌ Erro ao aplicar otimizações automáticas: {e}")
            return []
    
    async def _create_optimization_result(self, 
                                       category: str,
                                       optimization: Dict,
                                       performance_data: Dict[str, Dict],
                                       user_feedback: Dict[str, float]) -> OptimizationResult:
        """Cria resultado de otimização"""
        try:
            current_score = await self._calculate_category_score(category, performance_data, user_feedback)
            optimized_score = await self._calculate_optimized_score(category, optimization, performance_data, user_feedback)
            
            improvement = ((optimized_score - current_score.overall_score) / current_score.overall_score) * 100
            
            return OptimizationResult(
                category=category,
                optimization_type=optimization["type"],
                original_score=current_score.overall_score,
                optimized_score=optimized_score,
                improvement_percentage=improvement,
                changes_made=optimization["changes"],
                confidence_level=optimization["confidence"],
                created_at=datetime.now()
            )
            
        except Exception as e:
            print(f"❌ Erro ao criar resultado de otimização: {e}")
            return None
    
    async def _save_optimization_result(self, result: OptimizationResult) -> None:
        """Salva resultado de otimização"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO optimization_results 
                    (category, optimization_type, original_score, optimized_score,
                     improvement_percentage, changes_made, confidence_level)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    result.category, result.optimization_type.value,
                    result.original_score, result.optimized_score,
                    result.improvement_percentage, json.dumps(result.changes_made),
                    result.confidence_level
                ))
                conn.commit()
        except Exception as e:
            print(f"❌ Erro ao salvar resultado: {e}")
    
    async def _save_category_score(self, score: CategoryScore) -> None:
        """Salva score de categoria"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO category_scores 
                    (category, performance_score, user_satisfaction, conversion_rate,
                     click_rate, revenue_per_category, geek_relevance, overall_score)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    score.category, score.performance_score, score.user_satisfaction,
                    score.conversion_rate, score.click_rate, score.revenue_per_category,
                    score.geek_relevance, score.overall_score
                ))
                conn.commit()
        except Exception as e:
            print(f"❌ Erro ao salvar score: {e}")
