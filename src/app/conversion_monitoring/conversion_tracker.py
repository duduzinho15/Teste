"""
Sistema de Rastreamento de Conversões Geek vs Geral
Monitora e registra métricas de conversão em tempo real
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import statistics
from decimal import Decimal

from src.core.models import Offer
from src.core.geek_prioritizer import GeekPrioritizer


@dataclass
class ConversionEvent:
    """Evento de conversão individual"""
    timestamp: str
    offer_id: str
    offer_title: str
    category: str
    geek_level: str
    geek_score: float
    price: Decimal
    discount_percentage: float
    store: str
    conversion_type: str  # "click", "purchase", "view"
    user_segment: str  # "geek", "general", "mixed"
    revenue: Optional[Decimal] = None
    commission: Optional[Decimal] = None


@dataclass
class ConversionMetrics:
    """Métricas de conversão agregadas"""
    timestamp: str
    period: str  # "hour", "day", "week", "month"
    
    # Métricas gerais
    total_conversions: int
    total_revenue: Decimal
    total_commission: Decimal
    average_order_value: Decimal
    
    # Métricas geek vs geral
    geek_conversions: int
    general_conversions: int
    geek_revenue: Decimal
    general_revenue: Decimal
    geek_commission: Decimal
    general_commission: Decimal
    
    # Taxas de conversão
    geek_conversion_rate: float
    general_conversion_rate: float
    overall_conversion_rate: float
    
    # Performance por categoria
    category_performance: Dict[str, Dict[str, Any]]
    
    # Tendências
    geek_trend: str  # "up", "down", "stable"
    general_trend: str
    overall_trend: str


class ConversionTracker:
    """
    Sistema de rastreamento de conversões geek vs geral
    """
    
    def __init__(self, data_file: str = "conversion_data.json"):
        self.logger = logging.getLogger(__name__)
        self.data_file = data_file
        self.geek_prioritizer = GeekPrioritizer()
        
        # Armazenamento de eventos
        self.conversion_events: List[ConversionEvent] = []
        self.metrics_history: List[ConversionMetrics] = []
        
        # Configurações
        self.tracking_enabled = True
        self.auto_save_interval = 300  # 5 minutos
        self.max_events_in_memory = 10000
        
        # Métricas em tempo real
        self.real_time_metrics = {
            "total_conversions_today": 0,
            "geek_conversions_today": 0,
            "general_conversions_today": 0,
            "total_revenue_today": Decimal("0"),
            "geek_revenue_today": Decimal("0"),
            "general_revenue_today": Decimal("0"),
            "last_conversion_time": None,
            "conversion_rate_24h": 0.0
        }
        
        # Carregar dados existentes
        self._load_existing_data()
        
    def _load_existing_data(self):
        """Carrega dados de conversão existentes"""
        try:
            if Path(self.data_file).exists():
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                # Carregar eventos
                for event_data in data.get("events", []):
                    event = ConversionEvent(
                        timestamp=event_data["timestamp"],
                        offer_id=event_data["offer_id"],
                        offer_title=event_data["offer_title"],
                        category=event_data["category"],
                        geek_level=event_data["geek_level"],
                        geek_score=event_data["geek_score"],
                        price=Decimal(str(event_data["price"])),
                        discount_percentage=event_data["discount_percentage"],
                        store=event_data["store"],
                        conversion_type=event_data["conversion_type"],
                        user_segment=event_data["user_segment"],
                        revenue=Decimal(str(event_data["revenue"])) if event_data.get("revenue") else None,
                        commission=Decimal(str(event_data["commission"])) if event_data.get("commission") else None
                    )
                    self.conversion_events.append(event)
                
                # Carregar métricas
                for metrics_data in data.get("metrics", []):
                    metrics = ConversionMetrics(
                        timestamp=metrics_data["timestamp"],
                        period=metrics_data["period"],
                        total_conversions=metrics_data["total_conversions"],
                        total_revenue=Decimal(str(metrics_data["total_revenue"])),
                        total_commission=Decimal(str(metrics_data["total_commission"])),
                        average_order_value=Decimal(str(metrics_data["average_order_value"])),
                        geek_conversions=metrics_data["geek_conversions"],
                        general_conversions=metrics_data["general_conversions"],
                        geek_revenue=Decimal(str(metrics_data["geek_revenue"])),
                        general_revenue=Decimal(str(metrics_data["general_revenue"])),
                        geek_commission=Decimal(str(metrics_data["geek_commission"])),
                        general_commission=Decimal(str(metrics_data["general_commission"])),
                        geek_conversion_rate=metrics_data["geek_conversion_rate"],
                        general_conversion_rate=metrics_data["general_conversion_rate"],
                        overall_conversion_rate=metrics_data["overall_conversion_rate"],
                        category_performance=metrics_data["category_performance"],
                        geek_trend=metrics_data["geek_trend"],
                        general_trend=metrics_data["general_trend"],
                        overall_trend=metrics_data["overall_trend"]
                    )
                    self.metrics_history.append(metrics)
                
                self.logger.info(f"Carregados {len(self.conversion_events)} eventos e {len(self.metrics_history)} métricas")
                
        except Exception as e:
            self.logger.error(f"Erro ao carregar dados de conversão: {e}")
    
    async def track_conversion(self, offer: Offer, conversion_type: str, 
                             user_segment: str = "general", 
                             revenue: Optional[Decimal] = None,
                             commission: Optional[Decimal] = None) -> ConversionEvent:
        """
        Rastreia uma conversão
        """
        if not self.tracking_enabled:
            return None
        
        try:
            # Calcular score geek
            geek_score_result = self.geek_prioritizer.calculate_geek_score(offer)
            
            # Criar evento de conversão
            event = ConversionEvent(
                timestamp=datetime.now().isoformat(),
                offer_id=getattr(offer, 'id', f"offer_{len(self.conversion_events)}"),
                offer_title=getattr(offer, 'title', 'Sem título'),
                category=getattr(offer, 'category', 'general'),
                geek_level=geek_score_result.geek_level,
                geek_score=geek_score_result.overall_score,
                price=getattr(offer, 'price', Decimal("0")),
                discount_percentage=getattr(offer, 'discount_percentage', 0.0),
                store=getattr(offer, 'store', 'Desconhecida'),
                conversion_type=conversion_type,
                user_segment=user_segment,
                revenue=revenue,
                commission=commission
            )
            
            # Adicionar à lista
            self.conversion_events.append(event)
            
            # Atualizar métricas em tempo real
            await self._update_real_time_metrics(event)
            
            # Limitar eventos em memória
            if len(self.conversion_events) > self.max_events_in_memory:
                self.conversion_events = self.conversion_events[-self.max_events_in_memory:]
            
            self.logger.info(f"Conversão rastreada: {event.conversion_type} - {event.offer_title} ({event.geek_level})")
            
            return event
            
        except Exception as e:
            self.logger.error(f"Erro ao rastrear conversão: {e}")
            return None
    
    async def _update_real_time_metrics(self, event: ConversionEvent):
        """Atualiza métricas em tempo real"""
        today = datetime.now().date()
        
        # Verificar se é do dia atual
        event_date = datetime.fromisoformat(event.timestamp).date()
        if event_date != today:
            return
        
        # Atualizar contadores
        self.real_time_metrics["total_conversions_today"] += 1
        self.real_time_metrics["last_conversion_time"] = event.timestamp
        
        if event.geek_level in ["primary", "secondary"]:
            self.real_time_metrics["geek_conversions_today"] += 1
            if event.revenue:
                self.real_time_metrics["geek_revenue_today"] += event.revenue
        else:
            self.real_time_metrics["general_conversions_today"] += 1
            if event.revenue:
                self.real_time_metrics["general_revenue_today"] += event.revenue
        
        if event.revenue:
            self.real_time_metrics["total_revenue_today"] += event.revenue
    
    async def calculate_conversion_metrics(self, period: str = "day") -> ConversionMetrics:
        """
        Calcula métricas de conversão para um período
        """
        try:
            now = datetime.now()
            
            # Determinar período
            if period == "hour":
                start_time = now - timedelta(hours=1)
            elif period == "day":
                start_time = now - timedelta(days=1)
            elif period == "week":
                start_time = now - timedelta(weeks=1)
            elif period == "month":
                start_time = now - timedelta(days=30)
            else:
                start_time = now - timedelta(days=1)
            
            # Filtrar eventos do período
            period_events = [
                event for event in self.conversion_events
                if datetime.fromisoformat(event.timestamp) >= start_time
            ]
            
            if not period_events:
                return self._create_empty_metrics(period)
            
            # Calcular métricas básicas
            total_conversions = len(period_events)
            total_revenue = sum(event.revenue for event in period_events if event.revenue)
            total_commission = sum(event.commission for event in period_events if event.commission)
            average_order_value = total_revenue / total_conversions if total_conversions > 0 else Decimal("0")
            
            # Separar conversões geek vs geral
            geek_events = [e for e in period_events if e.geek_level in ["primary", "secondary"]]
            general_events = [e for e in period_events if e.geek_level == "general"]
            
            geek_conversions = len(geek_events)
            general_conversions = len(general_events)
            
            geek_revenue = sum(e.revenue for e in geek_events if e.revenue)
            general_revenue = sum(e.revenue for e in general_events if e.revenue)
            
            geek_commission = sum(e.commission for e in geek_events if e.commission)
            general_commission = sum(e.commission for e in general_events if e.commission)
            
            # Calcular taxas de conversão (simulado - em produção viria de dados reais)
            total_views = total_conversions * 100  # Simulado
            geek_views = geek_conversions * 100
            general_views = general_conversions * 100
            
            geek_conversion_rate = (geek_conversions / geek_views) if geek_views > 0 else 0.0
            general_conversion_rate = (general_conversions / general_views) if general_views > 0 else 0.0
            overall_conversion_rate = (total_conversions / total_views) if total_views > 0 else 0.0
            
            # Performance por categoria
            category_performance = self._calculate_category_performance(period_events)
            
            # Calcular tendências
            geek_trend = self._calculate_trend("geek", period)
            general_trend = self._calculate_trend("general", period)
            overall_trend = self._calculate_trend("overall", period)
            
            metrics = ConversionMetrics(
                timestamp=now.isoformat(),
                period=period,
                total_conversions=total_conversions,
                total_revenue=total_revenue,
                total_commission=total_commission,
                average_order_value=average_order_value,
                geek_conversions=geek_conversions,
                general_conversions=general_conversions,
                geek_revenue=geek_revenue,
                general_revenue=general_revenue,
                geek_commission=geek_commission,
                general_commission=general_commission,
                geek_conversion_rate=geek_conversion_rate,
                general_conversion_rate=general_conversion_rate,
                overall_conversion_rate=overall_conversion_rate,
                category_performance=category_performance,
                geek_trend=geek_trend,
                general_trend=general_trend,
                overall_trend=overall_trend
            )
            
            # Adicionar ao histórico
            self.metrics_history.append(metrics)
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Erro ao calcular métricas de conversão: {e}")
            return self._create_empty_metrics(period)
    
    def _create_empty_metrics(self, period: str) -> ConversionMetrics:
        """Cria métricas vazias"""
        return ConversionMetrics(
            timestamp=datetime.now().isoformat(),
            period=period,
            total_conversions=0,
            total_revenue=Decimal("0"),
            total_commission=Decimal("0"),
            average_order_value=Decimal("0"),
            geek_conversions=0,
            general_conversions=0,
            geek_revenue=Decimal("0"),
            general_revenue=Decimal("0"),
            geek_commission=Decimal("0"),
            general_commission=Decimal("0"),
            geek_conversion_rate=0.0,
            general_conversion_rate=0.0,
            overall_conversion_rate=0.0,
            category_performance={},
            geek_trend="stable",
            general_trend="stable",
            overall_trend="stable"
        )
    
    def _calculate_category_performance(self, events: List[ConversionEvent]) -> Dict[str, Dict[str, Any]]:
        """Calcula performance por categoria"""
        category_stats = {}
        
        for event in events:
            category = event.category
            if category not in category_stats:
                category_stats[category] = {
                    "conversions": 0,
                    "revenue": Decimal("0"),
                    "commission": Decimal("0"),
                    "geek_conversions": 0,
                    "general_conversions": 0
                }
            
            category_stats[category]["conversions"] += 1
            if event.revenue:
                category_stats[category]["revenue"] += event.revenue
            if event.commission:
                category_stats[category]["commission"] += event.commission
            
            if event.geek_level in ["primary", "secondary"]:
                category_stats[category]["geek_conversions"] += 1
            else:
                category_stats[category]["general_conversions"] += 1
        
        return category_stats
    
    def _calculate_trend(self, segment: str, period: str) -> str:
        """Calcula tendência para um segmento"""
        # Implementação simplificada - em produção seria mais complexa
        if len(self.metrics_history) < 2:
            return "stable"
        
        # Comparar com período anterior
        current_metrics = self.metrics_history[-1]
        previous_metrics = self.metrics_history[-2] if len(self.metrics_history) > 1 else current_metrics
        
        if segment == "geek":
            current_value = current_metrics.geek_conversions
            previous_value = previous_metrics.geek_conversions
        elif segment == "general":
            current_value = current_metrics.general_conversions
            previous_value = previous_metrics.general_conversions
        else:  # overall
            current_value = current_metrics.total_conversions
            previous_value = previous_metrics.total_conversions
        
        if current_value > previous_value * 1.1:
            return "up"
        elif current_value < previous_value * 0.9:
            return "down"
        else:
            return "stable"
    
    def get_real_time_metrics(self) -> Dict[str, Any]:
        """Retorna métricas em tempo real"""
        return {
            "current_metrics": self.real_time_metrics,
            "last_update": datetime.now().isoformat(),
            "tracking_enabled": self.tracking_enabled,
            "total_events_tracked": len(self.conversion_events)
        }
    
    async def save_data(self):
        """Salva dados de conversão"""
        try:
            # Função auxiliar para converter Decimal para string
            def decimal_to_str(obj):
                if isinstance(obj, Decimal):
                    return str(obj)
                elif isinstance(obj, dict):
                    return {k: decimal_to_str(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [decimal_to_str(item) for item in obj]
                else:
                    return obj
            
            data = {
                "events": [decimal_to_str(asdict(event)) for event in self.conversion_events[-1000:]],  # Últimos 1000
                "metrics": [decimal_to_str(asdict(metric)) for metric in self.metrics_history[-100:]],  # Últimas 100
                "real_time_metrics": decimal_to_str(self.real_time_metrics),
                "last_save": datetime.now().isoformat()
            }
            
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Dados de conversão salvos: {len(data['events'])} eventos, {len(data['metrics'])} métricas")
            
        except Exception as e:
            self.logger.error(f"Erro ao salvar dados de conversão: {e}")
    
    async def start_auto_save(self):
        """Inicia salvamento automático"""
        while self.tracking_enabled:
            await asyncio.sleep(self.auto_save_interval)
            await self.save_data()
    
    def enable_tracking(self):
        """Habilita rastreamento"""
        self.tracking_enabled = True
        self.logger.info("Rastreamento de conversão habilitado")
    
    def disable_tracking(self):
        """Desabilita rastreamento"""
        self.tracking_enabled = False
        self.logger.info("Rastreamento de conversão desabilitado")
