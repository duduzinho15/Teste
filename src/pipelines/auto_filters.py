"""
Sistema de Filtros Automáticos Inteligentes
Configura e aplica filtros automáticos para ofertas coletadas
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
from pathlib import Path

from core.models import Offer

logger = logging.getLogger(__name__)


class FilterType(Enum):
    """Tipos de filtros disponíveis"""
    PRICE = "price"
    DISCOUNT = "discount"
    CATEGORY = "category"
    STORE = "store"
    QUALITY = "quality"
    TIME = "time"
    CUSTOM = "custom"


class FilterOperator(Enum):
    """Operadores de comparação para filtros"""
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    GREATER_EQUAL = "greater_equal"
    LESS_EQUAL = "less_equal"
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    IN = "in"
    NOT_IN = "not_in"
    BETWEEN = "between"


@dataclass
class AutoFilter:
    """Definição de um filtro automático"""
    name: str
    filter_type: FilterType
    operator: FilterOperator
    value: Any
    secondary_value: Optional[Any] = None  # Para operadores BETWEEN
    enabled: bool = True
    priority: int = 1
    description: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Validação pós-inicialização"""
        if hasattr(self.filter_type, 'value') and self.filter_type.value == "between" and self.secondary_value is None:
            raise ValueError("Filtro BETWEEN requer secondary_value")


@dataclass
class FilterRule:
    """Regra de filtro com condições múltiplas"""
    name: str
    filters: List[AutoFilter]
    logic: str = "AND"  # AND, OR, XOR
    enabled: bool = True
    priority: int = 1
    description: str = ""
    
    def __post_init__(self):
        """Validação pós-inicialização"""
        if not self.filters:
            raise ValueError("Regra deve ter pelo menos um filtro")
        
        if self.logic not in ["AND", "OR", "XOR"]:
            raise ValueError("Logic deve ser AND, OR ou XOR")


@dataclass
class FilterProfile:
    """Perfil de filtros para diferentes cenários"""
    name: str
    description: str
    rules: List[FilterRule]
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Validação pós-inicialização"""
        if not self.rules:
            raise ValueError("Perfil deve ter pelo menos uma regra")


class AutoFilterEngine:
    """Motor de filtros automáticos inteligentes"""
    
    def __init__(self):
        """Inicializa o motor de filtros"""
        self.logger = logging.getLogger(__name__)
        
        # Filtros e regras carregados
        self.filters: Dict[str, AutoFilter] = {}
        self.rules: Dict[str, FilterRule] = {}
        self.profiles: Dict[str, FilterProfile] = {}
        
        # Estatísticas
        self.stats = {
            "total_filters_applied": 0,
            "offers_filtered": 0,
            "offers_passed": 0,
            "last_filter_run": None,
            "filter_performance": {}
        }
        
        # Cache de resultados
        self.filter_cache: Dict[str, List[Offer]] = {}
        
        # Carregar filtros padrão
        self._load_default_filters()
    
    def _load_default_filters(self):
        """Carrega filtros padrão do sistema"""
        try:
            # Filtros de preço
            self.add_filter(AutoFilter(
                name="min_discount_15",
                filter_type=FilterType.DISCOUNT,
                operator=FilterOperator.GREATER_EQUAL,
                value=15,
                description="Desconto mínimo de 15%"
            ))
            
            self.add_filter(AutoFilter(
                name="max_price_1500",
                filter_type=FilterType.PRICE,
                operator=FilterOperator.LESS_EQUAL,
                value=1500.0,
                description="Preço máximo de R$ 1.500"
            ))
            
            # Filtros de categoria
            self.add_filter(AutoFilter(
                name="allowed_categories",
                filter_type=FilterType.CATEGORY,
                operator=FilterOperator.IN,
                value=["eletronicos", "informatica", "games", "casa", "moda"],
                description="Categorias permitidas"
            ))
            
            # Filtros de loja
            self.add_filter(AutoFilter(
                name="excluded_stores",
                filter_type=FilterType.STORE,
                operator=FilterOperator.NOT_IN,
                value=["loja_suspeita", "loja_inativa"],
                description="Lojas excluídas"
            ))
            
            # Filtros de qualidade
            self.add_filter(AutoFilter(
                name="min_quality_score",
                filter_type=FilterType.QUALITY,
                operator=FilterOperator.GREATER_EQUAL,
                value=0.7,
                description="Score de qualidade mínimo"
            ))
            
            self.logger.info("✅ Filtros padrão carregados")
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao carregar filtros padrão: {e}")
    
    def add_filter(self, filter_obj: AutoFilter) -> bool:
        """Adiciona um filtro ao motor"""
        try:
            self.filters[filter_obj.name] = filter_obj
            self.logger.info(f"✅ Filtro adicionado: {filter_obj.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao adicionar filtro: {e}")
            return False
    
    def remove_filter(self, filter_name: str) -> bool:
        """Remove um filtro do motor"""
        try:
            if filter_name in self.filters:
                del self.filters[filter_name]
                self.logger.info(f"✅ Filtro removido: {filter_name}")
                return True
            else:
                self.logger.warning(f"⚠️ Filtro não encontrado: {filter_name}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Erro ao remover filtro: {e}")
            return False
    
    def add_rule(self, rule: FilterRule) -> bool:
        """Adiciona uma regra de filtro"""
        try:
            self.rules[rule.name] = rule
            self.logger.info(f"✅ Regra adicionada: {rule.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao adicionar regra: {e}")
            return False
    
    def add_profile(self, profile: FilterProfile) -> bool:
        """Adiciona um perfil de filtros"""
        try:
            self.profiles[profile.name] = profile
            self.logger.info(f"✅ Perfil adicionado: {profile.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao adicionar perfil: {e}")
            return False
    
    async def apply_filters(self, offers: List[Offer], profile_name: Optional[str] = None) -> List[Offer]:
        """
        Aplica filtros automáticos às ofertas
        
        Args:
            offers: Lista de ofertas para filtrar
            profile_name: Nome do perfil de filtros a usar
            
        Returns:
            Lista de ofertas que passaram nos filtros
        """
        try:
            start_time = datetime.now()
            self.logger.info(f"🔍 Aplicando filtros automáticos a {len(offers)} ofertas")
            
            if profile_name and profile_name in self.profiles:
                # Usar perfil específico
                profile = self.profiles[profile_name]
                filtered_offers = await self._apply_profile(offers, profile)
            else:
                # Usar filtros individuais
                filtered_offers = await self._apply_individual_filters(offers)
            
            # Atualizar estatísticas
            run_time = (datetime.now() - start_time).total_seconds()
            self._update_stats(len(offers), len(filtered_offers), run_time)
            
            self.logger.info(f"✅ Filtros aplicados: {len(filtered_offers)}/{len(offers)} ofertas passaram")
            return filtered_offers
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao aplicar filtros: {e}")
            return offers
    
    async def _apply_profile(self, offers: List[Offer], profile: FilterProfile) -> List[Offer]:
        """Aplica um perfil de filtros específico"""
        try:
            if not profile.enabled:
                self.logger.info(f"⚠️ Perfil {profile.name} está desabilitado")
                return offers
            
            filtered_offers = offers
            
            # Ordenar regras por prioridade
            sorted_rules = sorted(profile.rules, key=lambda r: r.priority, reverse=True)
            
            for rule in sorted_rules:
                if not rule.enabled:
                    continue
                
                self.logger.debug(f"🔧 Aplicando regra: {rule.name}")
                filtered_offers = await self._apply_rule(filtered_offers, rule)
                
                if not filtered_offers:
                    self.logger.info(f"⚠️ Regra {rule.name} removeu todas as ofertas")
                    break
            
            return filtered_offers
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao aplicar perfil {profile.name}: {e}")
            return offers
    
    async def _apply_rule(self, offers: List[Offer], rule: FilterRule) -> List[Offer]:
        """Aplica uma regra de filtro específica"""
        try:
            if rule.logic == "AND":
                # Todas as condições devem ser verdadeiras
                for filter_obj in rule.filters:
                    if not filter_obj.enabled:
                        continue
                    offers = await self._apply_single_filter(offers, filter_obj)
                    if not offers:
                        break
                        
            elif rule.logic == "OR":
                # Pelo menos uma condição deve ser verdadeira
                passed_offers = set()
                for filter_obj in rule.filters:
                    if not filter_obj.enabled:
                        continue
                    filtered = await self._apply_single_filter(offers, filter_obj)
                    passed_offers.update(filtered)
                offers = list(passed_offers)
                
            elif rule.logic == "XOR":
                # Exatamente uma condição deve ser verdadeira
                passed_offers = []
                for filter_obj in rule.filters:
                    if not filter_obj.enabled:
                        continue
                    filtered = await self._apply_single_filter(offers, filter_obj)
                    passed_offers.append(filtered)
                
                # XOR: apenas ofertas que passaram em exatamente um filtro
                if passed_offers:
                    offers = set(passed_offers[0])
                    for other_passed in passed_offers[1:]:
                        offers = offers.symmetric_difference(set(other_passed))
                    offers = list(offers)
            
            return offers
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao aplicar regra {rule.name}: {e}")
            return offers
    
    async def _apply_individual_filters(self, offers: List[Offer]) -> List[Offer]:
        """Aplica filtros individuais às ofertas"""
        try:
            filtered_offers = offers
            
            # Ordenar filtros por prioridade
            sorted_filters = sorted(self.filters.values(), key=lambda f: f.priority, reverse=True)
            
            for filter_obj in sorted_filters:
                if not filter_obj.enabled:
                    continue
                
                filtered_offers = await self._apply_single_filter(filtered_offers, filter_obj)
                
                if not filtered_offers:
                    self.logger.info(f"⚠️ Filtro {filter_obj.name} removeu todas as ofertas")
                    break
            
            return filtered_offers
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao aplicar filtros individuais: {e}")
            return offers
    
    async def _apply_single_filter(self, offers: List[Offer], filter_obj: AutoFilter) -> List[Offer]:
        """Aplica um filtro individual a uma lista de ofertas"""
        try:
            filtered_offers = []
            
            for offer in offers:
                if await self._evaluate_filter(offer, filter_obj):
                    filtered_offers.append(offer)
            
            return filtered_offers
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao aplicar filtro {filter_obj.name}: {e}")
            return offers
    
    async def _evaluate_filter(self, offer: Offer, filter_obj: AutoFilter) -> bool:
        """Avalia se uma oferta passa em um filtro específico"""
        try:
            # Obter valor da oferta para o tipo de filtro
            offer_value = self._get_offer_value(offer, filter_obj.filter_type)
            
            if offer_value is None:
                return False
            
            # Aplicar operador de comparação
            return self._apply_operator(offer_value, filter_obj.operator, 
                                      filter_obj.value, filter_obj.secondary_value)
            
        except Exception as e:
            self.logger.debug(f"⚠️ Erro ao avaliar filtro {filter_obj.name}: {e}")
            return False
    
    def _get_offer_value(self, offer: Offer, filter_type: FilterType) -> Any:
        """Obtém o valor da oferta para o tipo de filtro"""
        try:
            if filter_type == FilterType.PRICE:
                return offer.price
            elif filter_type == FilterType.DISCOUNT:
                return offer.discount_percentage
            elif filter_type == FilterType.CATEGORY:
                return offer.category.lower()
            elif filter_type == FilterType.STORE:
                return offer.store.lower()
            elif filter_type == FilterType.QUALITY:
                # Implementar cálculo de qualidade se necessário
                return 0.8  # Valor padrão
            elif filter_type == FilterType.TIME:
                return offer.collected_at
            else:
                return None
                
        except Exception as e:
            self.logger.debug(f"⚠️ Erro ao obter valor da oferta: {e}")
            return None
    
    def _apply_operator(self, offer_value: Any, operator: FilterOperator, 
                       filter_value: Any, secondary_value: Any = None) -> bool:
        """Aplica operador de comparação"""
        try:
            if operator == FilterOperator.EQUALS:
                return offer_value == filter_value
            elif operator == FilterOperator.NOT_EQUALS:
                return offer_value != filter_value
            elif operator == FilterOperator.GREATER_THAN:
                return offer_value > filter_value
            elif operator == FilterOperator.LESS_THAN:
                return offer_value < filter_value
            elif operator == FilterOperator.GREATER_EQUAL:
                return offer_value >= filter_value
            elif operator == FilterOperator.LESS_EQUAL:
                return offer_value <= filter_value
            elif operator == FilterOperator.CONTAINS:
                return filter_value in offer_value if isinstance(offer_value, str) else False
            elif operator == FilterOperator.NOT_CONTAINS:
                return filter_value not in offer_value if isinstance(offer_value, str) else False
            elif operator == FilterOperator.IN:
                return offer_value in filter_value
            elif operator == FilterOperator.NOT_IN:
                return offer_value not in filter_value
            elif operator == FilterOperator.BETWEEN:
                if secondary_value is None:
                    return False
                return filter_value <= offer_value <= secondary_value
            else:
                return False
                
        except Exception as e:
            self.logger.debug(f"⚠️ Erro ao aplicar operador {operator}: {e}")
            return False
    
    def _update_stats(self, total_offers: int, filtered_offers: int, run_time: float):
        """Atualiza estatísticas do motor de filtros"""
        try:
            self.stats["total_filters_applied"] += 1
            self.stats["offers_filtered"] += (total_offers - filtered_offers)
            self.stats["offers_passed"] += filtered_offers
            self.stats["last_filter_run"] = datetime.now()
            
            # Performance média
            if self.stats["total_filters_applied"] > 0:
                avg_time = (self.stats["filter_performance"].get("avg_time", 0) * 
                           (self.stats["total_filters_applied"] - 1) + run_time) / self.stats["total_filters_applied"]
                self.stats["filter_performance"]["avg_time"] = avg_time
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao atualizar estatísticas: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do motor de filtros"""
        return {
            **self.stats,
            "total_filters": len(self.filters),
            "total_rules": len(self.rules),
            "total_profiles": len(self.profiles),
            "enabled_filters": len([f for f in self.filters.values() if f.enabled]),
            "enabled_rules": len([r for r in self.rules.values() if r.enabled]),
            "enabled_profiles": len([p for p in self.profiles.values() if p.enabled])
        }
    
    def export_config(self, file_path: str) -> bool:
        """Exporta configuração dos filtros para arquivo JSON"""
        try:
            config = {
                "filters": {name: filter_obj.__dict__ for name, filter_obj in self.filters.items()},
                "rules": {name: rule.__dict__ for name, rule in self.rules.items()},
                "profiles": {name: profile.__dict__ for name, profile in self.profiles.items()}
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, default=str)
            
            self.logger.info(f"✅ Configuração exportada para: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao exportar configuração: {e}")
            return False
    
    def import_config(self, file_path: str) -> bool:
        """Importa configuração dos filtros de arquivo JSON"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Limpar configuração atual
            self.filters.clear()
            self.rules.clear()
            self.profiles.clear()
            
            # Importar filtros
            for name, filter_data in config.get("filters", {}).items():
                filter_obj = AutoFilter(**filter_data)
                self.filters[name] = filter_obj
            
            # Importar regras
            for name, rule_data in config.get("rules", {}).items():
                rule = FilterRule(**rule_data)
                self.rules[name] = rule
            
            # Importar perfis
            for name, profile_data in config.get("profiles", {}).items():
                profile = FilterProfile(**profile_data)
                self.profiles[name] = profile
            
            self.logger.info(f"✅ Configuração importada de: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao importar configuração: {e}")
            return False


# Instância global do motor de filtros
auto_filter_engine = AutoFilterEngine()


# Funções de conveniência
async def apply_auto_filters(offers: List[Offer], profile_name: Optional[str] = None) -> List[Offer]:
    """Aplica filtros automáticos às ofertas"""
    return await auto_filter_engine.apply_filters(offers, profile_name)


def get_filter_engine() -> AutoFilterEngine:
    """Retorna instância do motor de filtros"""
    return auto_filter_engine


if __name__ == "__main__":
    # Teste do sistema de filtros
    async def test_filters():
        from core.models import Offer
        
        # Criar ofertas de teste
        test_offers = [
            Offer(title="Produto 1", price=100, discount_percentage=20, store="Loja A", category="eletronicos"),
            Offer(title="Produto 2", price=2000, discount_percentage=10, store="Loja B", category="informatica"),
            Offer(title="Produto 3", price=500, discount_percentage=30, store="Loja C", category="games")
        ]
        
        print(f"📊 Ofertas de teste: {len(test_offers)}")
        
        # Aplicar filtros
        filtered = await apply_auto_filters(test_offers)
        
        print(f"✅ Ofertas filtradas: {len(filtered)}")
        print(f"📊 Estatísticas: {get_filter_engine().get_stats()}")
    
    asyncio.run(test_filters())
