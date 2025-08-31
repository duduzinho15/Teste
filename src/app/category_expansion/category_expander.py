"""
Expansor de Categorias
Implementa sugestões de expansão de categorias baseado na análise
"""

import asyncio
import json
import sqlite3
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from decimal import Decimal
from typing import Dict, List, Optional, Tuple, Set
from enum import Enum
import re

from src.core.geek_prioritizer import GeekPrioritizer


class ExpansionType(Enum):
    """Tipos de expansão de categoria"""
    SUB_CATEGORY_EXPANSION = "sub_category_expansion"
    KEYWORD_EXPANSION = "keyword_expansion"
    RELATED_CATEGORY_EXPANSION = "related_category_expansion"
    SEASONAL_EXPANSION = "seasonal_expansion"
    TREND_BASED_EXPANSION = "trend_based_expansion"


@dataclass
class ExpansionSuggestion:
    """Sugestão de expansão de categoria"""
    original_category: str
    new_category: str
    expansion_type: ExpansionType
    confidence_score: float
    reasoning: str
    expected_impact: str  # "high", "medium", "low"
    implementation_priority: int  # 1-5, onde 1 é mais alta
    created_at: datetime


@dataclass
class CategoryMapping:
    """Mapeamento de categoria"""
    source_category: str
    target_category: str
    mapping_type: str
    confidence: float
    keywords: List[str]
    synonyms: List[str]
    created_at: datetime


class CategoryExpander:
    """Expansor de categorias"""
    
    def __init__(self, db_path: str = "category_expansion.db"):
        self.db_path = db_path
        self.geek_prioritizer = GeekPrioritizer()
        self._init_database()
        self._load_category_mappings()
    
    def _init_database(self) -> None:
        """Inicializa o banco de dados"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Tabela de sugestões de expansão
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS expansion_suggestions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        original_category TEXT NOT NULL,
                        new_category TEXT NOT NULL,
                        expansion_type TEXT NOT NULL,
                        confidence_score REAL NOT NULL,
                        reasoning TEXT NOT NULL,
                        expected_impact TEXT NOT NULL,
                        implementation_priority INTEGER NOT NULL,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        implemented BOOLEAN DEFAULT FALSE,
                        implemented_at TEXT NULL
                    )
                """)
                
                # Tabela de mapeamentos de categoria
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS category_mappings (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        source_category TEXT NOT NULL,
                        target_category TEXT NOT NULL,
                        mapping_type TEXT NOT NULL,
                        confidence REAL NOT NULL,
                        keywords TEXT NOT NULL,
                        synonyms TEXT NOT NULL,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Tabela de categorias expandidas
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS expanded_categories (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        category_name TEXT NOT NULL,
                        parent_category TEXT NULL,
                        keywords TEXT NOT NULL,
                        description TEXT NOT NULL,
                        geek_score REAL NOT NULL,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        is_active BOOLEAN DEFAULT TRUE
                    )
                """)
                
                conn.commit()
                print(f"✅ Banco de dados de expansão de categorias inicializado: {self.db_path}")
                
        except Exception as e:
            print(f"❌ Erro ao inicializar banco de dados: {e}")
    
    def _load_category_mappings(self) -> None:
        """Carrega mapeamentos de categoria pré-definidos"""
        self.category_mappings = {
            # Gaming
            "gaming": {
                "sub_categories": ["pc_gaming", "console_gaming", "mobile_gaming", "retro_gaming"],
                "keywords": ["jogos", "games", "videogame", "esports", "streaming"],
                "related": ["tech", "electronics", "accessories"]
            },
            # Anime
            "anime": {
                "sub_categories": ["manga", "figures", "cosplay", "merchandise", "collectibles"],
                "keywords": ["japonês", "otaku", "mangá", "figuras", "colecionáveis"],
                "related": ["collectibles", "books", "clothing"]
            },
            # Tech
            "tech": {
                "sub_categories": ["smartphones", "laptops", "tablets", "smart_home", "wearables"],
                "keywords": ["tecnologia", "gadgets", "smart", "wireless", "bluetooth"],
                "related": ["electronics", "smart_home", "accessories"]
            },
            # Electronics
            "electronics": {
                "sub_categories": ["smart_tv", "audio", "cameras", "gaming_accessories", "smart_home"],
                "keywords": ["eletrônicos", "smart tv", "micro ondas", "fone bluetooth", "som"],
                "related": ["tech", "smart_home", "accessories"]
            }
        }
    
    async def generate_expansion_suggestions(self, 
                                          opportunities: List[str],
                                          trends: List[Dict],
                                          user_preferences: Dict[str, float]) -> List[ExpansionSuggestion]:
        """Gera sugestões de expansão baseadas em oportunidades"""
        try:
            suggestions = []
            
            for opportunity in opportunities:
                # Gerar sugestões baseadas no tipo de categoria
                if opportunity in self.category_mappings:
                    mapping = self.category_mappings[opportunity]
                    
                    # Sugestões de sub-categorias
                    for sub_category in mapping["sub_categories"]:
                        suggestion = ExpansionSuggestion(
                            original_category=opportunity,
                            new_category=sub_category,
                            expansion_type=ExpansionType.SUB_CATEGORY_EXPANSION,
                            confidence_score=self._calculate_confidence(opportunity, sub_category, user_preferences),
                            reasoning=f"Sub-categoria natural de {opportunity} com alto potencial",
                            expected_impact="high" if sub_category in ["pc_gaming", "smart_tv", "figures"] else "medium",
                            implementation_priority=1 if sub_category in ["pc_gaming", "smart_tv"] else 2,
                            created_at=datetime.now()
                        )
                        suggestions.append(suggestion)
                    
                    # Sugestões de categorias relacionadas
                    for related in mapping["related"]:
                        if related not in opportunities:  # Evitar duplicatas
                            suggestion = ExpansionSuggestion(
                                original_category=opportunity,
                                new_category=related,
                                expansion_type=ExpansionType.RELATED_CATEGORY_EXPANSION,
                                confidence_score=self._calculate_confidence(opportunity, related, user_preferences),
                                reasoning=f"Categoria relacionada a {opportunity} com sinergia natural",
                                expected_impact="medium",
                                implementation_priority=3,
                                created_at=datetime.now()
                            )
                            suggestions.append(suggestion)
                
                # Sugestões baseadas em tendências
                trend_suggestions = await self._generate_trend_based_suggestions(opportunity, trends)
                suggestions.extend(trend_suggestions)
            
            # Salvar sugestões
            for suggestion in suggestions:
                await self._save_expansion_suggestion(suggestion)
            
            print(f"💡 Geradas {len(suggestions)} sugestões de expansão")
            return suggestions
            
        except Exception as e:
            print(f"❌ Erro ao gerar sugestões: {e}")
            return []
    
    async def implement_expansion_suggestions(self, 
                                           suggestions: List[ExpansionSuggestion],
                                           max_implementations: int = 5) -> List[str]:
        """Implementa as sugestões de expansão mais promissoras"""
        try:
            implemented_categories = []
            
            # Ordenar por prioridade e confiança
            sorted_suggestions = sorted(
                suggestions,
                key=lambda x: (x.implementation_priority, -x.confidence_score)
            )
            
            for suggestion in sorted_suggestions[:max_implementations]:
                if suggestion.confidence_score > 0.7:  # Mínimo de confiança
                    success = await self._implement_single_expansion(suggestion)
                    if success:
                        implemented_categories.append(suggestion.new_category)
                        await self._mark_suggestion_implemented(suggestion)
            
            print(f"✅ Implementadas {len(implemented_categories)} expansões de categoria")
            return implemented_categories
            
        except Exception as e:
            print(f"❌ Erro ao implementar expansões: {e}")
            return []
    
    async def expand_category_keywords(self, category: str) -> List[str]:
        """Expande palavras-chave para uma categoria"""
        try:
            keywords = []
            
            if category in self.category_mappings:
                base_keywords = self.category_mappings[category]["keywords"]
                keywords.extend(base_keywords)
                
                # Adicionar variações
                for keyword in base_keywords:
                    variations = self._generate_keyword_variations(keyword)
                    keywords.extend(variations)
                
                # Adicionar termos sazonais
                seasonal_keywords = self._get_seasonal_keywords(category)
                keywords.extend(seasonal_keywords)
            else:
                # Para categorias não mapeadas, usar a própria categoria e variações
                keywords.append(category)
                keywords.extend(self._generate_keyword_variations(category))
            
            # Remover duplicatas
            unique_keywords = list(set(keywords))
            
            print(f"🔍 Expandidas {len(unique_keywords)} palavras-chave para {category}")
            return unique_keywords
            
        except Exception as e:
            print(f"❌ Erro ao expandir palavras-chave: {e}")
            return [category]  # Retornar pelo menos a categoria original
    
    async def create_category_mapping(self, 
                                   source_category: str,
                                   target_category: str,
                                   keywords: List[str],
                                   synonyms: List[str]) -> CategoryMapping:
        """Cria um mapeamento de categoria"""
        try:
            mapping = CategoryMapping(
                source_category=source_category,
                target_category=target_category,
                mapping_type="manual",
                confidence=0.9,
                keywords=keywords,
                synonyms=synonyms,
                created_at=datetime.now()
            )
            
            await self._save_category_mapping(mapping)
            print(f"🗺️ Criado mapeamento: {source_category} → {target_category}")
            return mapping
            
        except Exception as e:
            print(f"❌ Erro ao criar mapeamento: {e}")
            return None
    
    async def get_expansion_summary(self) -> Dict:
        """Retorna resumo das expansões"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Contar sugestões
                cursor.execute("SELECT COUNT(*) FROM expansion_suggestions")
                total_suggestions = cursor.fetchone()[0]
                
                # Contar implementadas
                cursor.execute("SELECT COUNT(*) FROM expansion_suggestions WHERE implemented = TRUE")
                implemented_count = cursor.fetchone()[0]
                
                # Contar categorias expandidas
                cursor.execute("SELECT COUNT(*) FROM expanded_categories WHERE is_active = TRUE")
                active_categories = cursor.fetchone()[0]
                
                # Top sugestões
                cursor.execute("""
                    SELECT original_category, new_category, confidence_score 
                    FROM expansion_suggestions 
                    ORDER BY confidence_score DESC 
                    LIMIT 5
                """)
                top_suggestions = cursor.fetchall()
                
                return {
                    "total_suggestions": total_suggestions,
                    "implemented_suggestions": implemented_count,
                    "active_expanded_categories": active_categories,
                    "top_suggestions": [
                        {"from": orig, "to": new, "confidence": conf} 
                        for orig, new, conf in top_suggestions
                    ],
                    "last_expansion": datetime.now().isoformat()
                }
                
        except Exception as e:
            print(f"❌ Erro ao gerar resumo: {e}")
            return {}
    
    def _calculate_confidence(self, original: str, new: str, user_preferences: Dict[str, float]) -> float:
        """Calcula score de confiança para uma expansão"""
        try:
            base_confidence = 0.5
            
            # Ajustar baseado em preferências do usuário
            user_score = user_preferences.get(original, 3.0)
            if user_score > 4.0:
                base_confidence += 0.2
            elif user_score > 3.5:
                base_confidence += 0.1
            
            # Ajustar baseado em similaridade
            if new in self.category_mappings.get(original, {}).get("sub_categories", []):
                base_confidence += 0.3
            elif new in self.category_mappings.get(original, {}).get("related", []):
                base_confidence += 0.2
            
            return min(1.0, base_confidence)
            
        except Exception as e:
            print(f"❌ Erro ao calcular confiança: {e}")
            return 0.5
    
    async def _generate_trend_based_suggestions(self, category: str, trends: List[Dict]) -> List[ExpansionSuggestion]:
        """Gera sugestões baseadas em tendências"""
        try:
            suggestions = []
            
            # Simular sugestões baseadas em tendências
            trend_keywords = {
                "gaming": ["esports", "streaming", "vr_gaming"],
                "tech": ["ai", "iot", "blockchain"],
                "anime": ["kawaii", "japanese_culture", "anime_fashion"],
                "electronics": ["smart_devices", "wireless_tech", "eco_friendly"]
            }
            
            if category in trend_keywords:
                for keyword in trend_keywords[category]:
                    suggestion = ExpansionSuggestion(
                        original_category=category,
                        new_category=keyword,
                        expansion_type=ExpansionType.TREND_BASED_EXPANSION,
                        confidence_score=0.75,
                        reasoning=f"Baseado em tendências emergentes em {category}",
                        expected_impact="medium",
                        implementation_priority=4,
                        created_at=datetime.now()
                    )
                    suggestions.append(suggestion)
            
            return suggestions
            
        except Exception as e:
            print(f"❌ Erro ao gerar sugestões baseadas em tendências: {e}")
            return []
    
    async def _implement_single_expansion(self, suggestion: ExpansionSuggestion) -> bool:
        """Implementa uma única expansão"""
        try:
            # Criar nova categoria expandida
            keywords = await self.expand_category_keywords(suggestion.new_category)
            geek_score = self.geek_prioritizer.calculate_geek_score(suggestion.new_category)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO expanded_categories 
                    (category_name, parent_category, keywords, description, geek_score)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    suggestion.new_category,
                    suggestion.original_category,
                    json.dumps(keywords),
                    suggestion.reasoning,
                    geek_score
                ))
                conn.commit()
            
            print(f"✅ Implementada expansão: {suggestion.original_category} → {suggestion.new_category}")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao implementar expansão: {e}")
            return False
    
    def _generate_keyword_variations(self, keyword: str) -> List[str]:
        """Gera variações de uma palavra-chave"""
        variations = []
        
        # Variações comuns
        if "gaming" in keyword:
            variations.extend(["gamer", "game", "games"])
        if "tech" in keyword:
            variations.extend(["technology", "technological", "techy"])
        if "smart" in keyword:
            variations.extend(["intelligent", "connected", "wireless"])
        if "bluetooth" in keyword:
            variations.extend(["wireless", "cable_free", "wireless_audio"])
        
        return variations
    
    def _get_seasonal_keywords(self, category: str) -> List[str]:
        """Retorna palavras-chave sazonais para uma categoria"""
        seasonal_keywords = {
            "gaming": ["christmas_gaming", "holiday_games", "summer_gaming"],
            "anime": ["anime_convention", "cosplay_season", "manga_release"],
            "tech": ["black_friday_tech", "cyber_monday", "tech_gifts"],
            "electronics": ["holiday_electronics", "gift_tech", "seasonal_deals"]
        }
        
        return seasonal_keywords.get(category, [])
    
    async def _save_expansion_suggestion(self, suggestion: ExpansionSuggestion) -> None:
        """Salva sugestão de expansão"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO expansion_suggestions 
                    (original_category, new_category, expansion_type, confidence_score,
                     reasoning, expected_impact, implementation_priority)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    suggestion.original_category, suggestion.new_category,
                    suggestion.expansion_type.value, suggestion.confidence_score,
                    suggestion.reasoning, suggestion.expected_impact,
                    suggestion.implementation_priority
                ))
                conn.commit()
        except Exception as e:
            print(f"❌ Erro ao salvar sugestão: {e}")
    
    async def _save_category_mapping(self, mapping: CategoryMapping) -> None:
        """Salva mapeamento de categoria"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO category_mappings 
                    (source_category, target_category, mapping_type, confidence, keywords, synonyms)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    mapping.source_category, mapping.target_category,
                    mapping.mapping_type, mapping.confidence,
                    json.dumps(mapping.keywords), json.dumps(mapping.synonyms)
                ))
                conn.commit()
        except Exception as e:
            print(f"❌ Erro ao salvar mapeamento: {e}")
    
    async def _mark_suggestion_implemented(self, suggestion: ExpansionSuggestion) -> None:
        """Marca sugestão como implementada"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE expansion_suggestions 
                    SET implemented = TRUE, implemented_at = ? 
                    WHERE original_category = ? AND new_category = ?
                """, (
                    datetime.now().isoformat(),
                    suggestion.original_category,
                    suggestion.new_category
                ))
                conn.commit()
        except Exception as e:
            print(f"❌ Erro ao marcar sugestão como implementada: {e}")
