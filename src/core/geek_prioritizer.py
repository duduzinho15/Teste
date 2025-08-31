"""
Sistema de Priorização Geek/Gamer para o Garimpeiro Geek
Prioriza ofertas relacionadas à cultura geek, otaku, nerd, gamer e tech
"""

import logging
import re
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from pathlib import Path
import sys

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.models import Offer

logger = logging.getLogger(__name__)

@dataclass
class GeekScore:
    """Score de priorização geek para uma oferta"""
    overall_score: float
    category_score: float
    keyword_score: float
    product_type_score: float
    geek_level: str  # "primary", "secondary", "general"
    matched_categories: List[str]
    matched_keywords: List[str]
    priority_multiplier: float
    recommendations: List[str]

class GeekPrioritizer:
    """Sistema de priorização para categorias geek/gamer"""
    
    def __init__(self):
        """Inicializa o prioritizador geek"""
        self.logger = logging.getLogger(__name__)
        
        # Carregar configurações geek
        self.geek_config = self._load_geek_config()
        
        # Compilar regex para palavras-chave
        self.geek_keywords_regex = self._compile_keywords_regex()
        
        self.logger.info("GeekPrioritizer inicializado")
    
    def _load_geek_config(self) -> Dict[str, Any]:
        """Carrega configurações geek do arquivo de configuração"""
        try:
            from config.garimpeiro_geek_config import GEEK_CATEGORIES_CONFIG
            return GEEK_CATEGORIES_CONFIG
        except ImportError:
            self.logger.warning("Configuração geek não encontrada, usando padrão")
            return self._get_default_geek_config()
    
    def _get_default_geek_config(self) -> Dict[str, Any]:
        """Configuração padrão caso não encontre o arquivo"""
        return {
            "enabled": True,
            "priority_boost": 0.3,
            "primary_categories": {
                "gaming": {"priority_score": 1.0, "keywords": ["gaming", "gamer"]},
                "tech_geek": {"priority_score": 0.9, "keywords": ["tech", "geek"]},
                "pc_gaming": {"priority_score": 0.95, "keywords": ["pc gamer", "desktop gaming"]}
            },
            "geek_keywords": ["gaming", "gamer", "tech", "geek", "nerd", "otaku"],
            "always_priority": ["playstation", "xbox", "nintendo", "rtx", "gaming"]
        }
    
    def _compile_keywords_regex(self) -> re.Pattern:
        """Compila regex para busca de palavras-chave geek"""
        keywords = self.geek_config.get("geek_keywords", [])
        pattern = "|".join(map(re.escape, keywords))
        return re.compile(pattern, re.IGNORECASE)
    
    def calculate_geek_score(self, offer_or_category: Offer | str) -> GeekScore | float:
        """
        Calcula score de priorização geek para uma oferta ou categoria
        
        Args:
            offer_or_category: Oferta a ser avaliada ou string da categoria
            
        Returns:
            GeekScore com detalhes da priorização ou float para categoria
        """
        if isinstance(offer_or_category, str):
            # Se for string, calcular score simples para categoria
            return self._calculate_category_score(offer_or_category)
        
        # Se for Offer, calcular score completo
        offer = offer_or_category
        self.logger.info(f"Calculando score geek para: {offer.title[:50]}...")
        
        # Scores individuais
        category_score = self._evaluate_category(offer)
        keyword_score = self._evaluate_keywords(offer)
        product_type_score = self._evaluate_product_type(offer)
        
        # Score geral
        overall_score = self._calculate_overall_score(
            category_score, keyword_score, product_type_score
        )
        
        # Determinar nível geek
        geek_level = self._determine_geek_level(overall_score)
    
    def _calculate_category_score(self, category: str) -> float:
        """
        Calcula score simples para uma categoria
        
        Args:
            category: Nome da categoria
            
        Returns:
            Score de relevância geek (0.0 a 1.0)
        """
        try:
            # Verificar se é uma categoria primária
            primary_categories = self.geek_config.get("primary_categories", {})
            if category in primary_categories:
                return primary_categories[category].get("priority_score", 0.8)
            
            # Verificar se contém palavras-chave geek
            category_lower = category.lower()
            geek_keywords = self.geek_config.get("geek_keywords", [])
            
            for keyword in geek_keywords:
                if keyword.lower() in category_lower:
                    return 0.7
            
            # Verificar sempre prioritário
            always_priority = self.geek_config.get("always_priority", [])
            for keyword in always_priority:
                if keyword.lower() in category_lower:
                    return 0.9
            
            # Score base para categorias gerais
            return 0.3
            
        except Exception as e:
            self.logger.error(f"Erro ao calcular score para categoria {category}: {e}")
            return 0.5
        
        # Multiplicador de prioridade
        priority_multiplier = self._calculate_priority_multiplier(overall_score, geek_level)
        
        # Recomendações
        recommendations = self._generate_recommendations(offer, overall_score)
        
        return GeekScore(
            overall_score=overall_score,
            category_score=category_score,
            keyword_score=keyword_score,
            product_type_score=product_type_score,
            geek_level=geek_level,
            matched_categories=self._get_matched_categories(offer),
            matched_keywords=self._get_matched_keywords(offer),
            priority_multiplier=priority_multiplier,
            recommendations=recommendations
        )
    
    def _evaluate_category(self, offer: Offer) -> float:
        """Avalia a categoria da oferta"""
        if not offer.category:
            return 0.0
        
        category_lower = offer.category.lower()
        score = 0.0
        
        # Verificar categorias primárias
        for cat_name, cat_info in self.geek_config["primary_categories"].items():
            if cat_name in category_lower:
                score = max(score, cat_info["priority_score"])
                break
        
        # Verificar subcategorias
        subcategories = self.geek_config.get("subcategories", {})
        for sub_cat_name, sub_cats in subcategories.items():
            if any(sub_cat in category_lower for sub_cat in sub_cats):
                score = max(score, 0.8)  # Boost para subcategorias específicas
                break
        
        return score
    
    def _evaluate_keywords(self, offer: Offer) -> float:
        """Avalia palavras-chave na oferta"""
        if not offer.title:
            return 0.0
        
        title_lower = offer.title.lower()
        matched_keywords = []
        score = 0.0
        
        # Buscar palavras-chave geek
        for keyword in self.geek_config["geek_keywords"]:
            if keyword.lower() in title_lower:
                matched_keywords.append(keyword)
                score += 0.1  # 0.1 por palavra-chave encontrada
        
        # Verificar produtos sempre prioritários
        for priority_product in self.geek_config["always_priority"]:
            if priority_product.lower() in title_lower:
                score += 0.3  # Boost extra para produtos prioritários
                break
        
        return min(1.0, score)
    
    def _evaluate_product_type(self, offer: Offer) -> float:
        """Avalia o tipo de produto"""
        if not offer.title:
            return 0.0
        
        title_lower = offer.title.lower()
        score = 0.0
        
        # Produtos de alta tecnologia
        high_tech_indicators = [
            "rtx", "gtx", "ryzen", "intel i9", "intel i7", "ssd nvme",
            "mechanical", "wireless", "bluetooth", "rgb", "gaming"
        ]
        
        for indicator in high_tech_indicators:
            if indicator in title_lower:
                score += 0.2
        
        # Produtos premium
        premium_indicators = [
            "premium", "flagship", "latest", "newest", "high-end",
            "professional", "enthusiast", "custom"
        ]
        
        for indicator in premium_indicators:
            if indicator in title_lower:
                score += 0.15
        
        return min(1.0, score)
    
    def _calculate_overall_score(self, category_score: float, keyword_score: float, product_type_score: float) -> float:
        """Calcula score geral baseado nos pesos configurados"""
        weights = self.geek_config["prioritization"]
        
        overall = (
            category_score * weights["category_matching_weight"] +
            keyword_score * weights["keyword_matching_weight"] +
            product_type_score * weights["price_quality_weight"]
        )
        
        return min(1.0, overall)
    
    def _determine_geek_level(self, overall_score: float) -> str:
        """Determina o nível geek da oferta"""
        min_geek_score = self.geek_config["prioritization"]["min_geek_score"]
        
        if overall_score >= min_geek_score:
            return "primary"
        elif overall_score >= min_geek_score * 0.7:
            return "secondary"
        else:
            return "general"
    
    def _calculate_priority_multiplier(self, overall_score: float, geek_level: str) -> float:
        """Calcula multiplicador de prioridade"""
        base_multiplier = 1.0
        
        if geek_level == "primary":
            base_multiplier = self.geek_config["prioritization"]["geek_boost_multiplier"]
        elif geek_level == "secondary":
            base_multiplier = 1.2
        
        return base_multiplier
    
    def _get_matched_categories(self, offer: Offer) -> List[str]:
        """Retorna categorias que correspondem à oferta"""
        if not offer.category:
            return []
        
        category_lower = offer.category.lower()
        matched = []
        
        for cat_name in self.geek_config["primary_categories"]:
            if cat_name in category_lower:
                matched.append(cat_name)
        
        return matched
    
    def _get_matched_keywords(self, offer: Offer) -> List[str]:
        """Retorna palavras-chave encontradas na oferta"""
        if not offer.title:
            return []
        
        title_lower = offer.title.lower()
        matched = []
        
        for keyword in self.geek_config["geek_keywords"]:
            if keyword.lower() in title_lower:
                matched.append(keyword)
        
        return matched
    
    def _generate_recommendations(self, offer: Offer, score: float) -> List[str]:
        """Gera recomendações para melhorar o score geek"""
        recommendations = []
        
        if score < 0.5:
            recommendations.append("Considerar categorização mais específica")
            recommendations.append("Adicionar palavras-chave geek no título")
        
        if score < 0.7:
            recommendations.append("Verificar se produto se encaixa em categorias primárias")
            recommendations.append("Considerar subcategorias específicas")
        
        if score >= 0.8:
            recommendations.append("Produto com alto potencial geek - priorizar!")
        
        return recommendations
    
    def prioritize_offers(self, offers: List[Offer]) -> List[Tuple[Offer, GeekScore]]:
        """
        Prioriza lista de ofertas por score geek
        
        Args:
            offers: Lista de ofertas para priorizar
            
        Returns:
            Lista de tuplas (oferta, score_geek) ordenadas por prioridade
        """
        self.logger.info(f"Priorizando {len(offers)} ofertas por score geek...")
        
        # Calcular scores para todas as ofertas
        offer_scores = []
        for offer in offers:
            geek_score = self.calculate_geek_score(offer)
            offer_scores.append((offer, geek_score))
        
        # Ordenar por score geral (decrescente)
        offer_scores.sort(key=lambda x: x[1].overall_score, reverse=True)
        
        self.logger.info(f"Priorização concluída. Melhor score: {offer_scores[0][1].overall_score:.2f}")
        
        return offer_scores
    
    def get_geek_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do sistema de priorização geek"""
        return {
            "enabled": self.geek_config["enabled"],
            "priority_boost": self.geek_config["priority_boost"],
            "primary_categories_count": len(self.geek_config["primary_categories"]),
            "geek_keywords_count": len(self.geek_config["geek_keywords"]),
            "always_priority_count": len(self.geek_config["always_priority"]),
            "min_geek_score": self.geek_config["prioritization"]["min_geek_score"]
        }
