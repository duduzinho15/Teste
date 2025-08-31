"""
Sistema de Alertas Geek para o Garimpeiro Geek
Monitora e alerta sobre produtos geek/gamer de alta prioridade
"""

import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path
import sys

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.models import Offer
from src.core.geek_prioritizer import GeekPrioritizer, GeekScore

logger = logging.getLogger(__name__)

@dataclass
class GeekAlert:
    """Alerta para produto geek de alta prioridade"""
    offer: Offer
    geek_score: GeekScore
    alert_type: str  # "high_priority", "new_release", "price_drop", "limited_stock"
    priority: str    # "critical", "high", "medium", "low"
    message: str
    created_at: datetime
    sent: bool = False
    sent_at: Optional[datetime] = None

class GeekAlertManager:
    """Gerenciador de alertas para produtos geek"""
    
    def __init__(self):
        """Inicializa o gerenciador de alertas"""
        self.logger = logging.getLogger(__name__)
        self.prioritizer = GeekPrioritizer()
        
        # Configurações de alertas
        self.alert_config = {
            "high_priority_threshold": 0.8,  # Score mínimo para alerta de alta prioridade
            "critical_threshold": 0.9,       # Score mínimo para alerta crítico
            "price_drop_threshold": 0.15,    # Desconto mínimo para alerta de preço
            "limited_stock_threshold": 5,    # Estoque mínimo para alerta de estoque
            "check_interval": 300,           # Intervalo de verificação em segundos
            "max_alerts_per_hour": 10,       # Máximo de alertas por hora
            "max_alerts_per_day": 50         # Máximo de alertas por dia
        }
        
        # Histórico de alertas
        self.alert_history: List[GeekAlert] = []
        self.sent_alerts_count = {"hour": 0, "day": 0, "total": 0}
        self.last_reset = datetime.now()
        
        self.logger.info("GeekAlertManager inicializado")
    
    async def check_offer_for_alerts(self, offer: Offer) -> Optional[GeekAlert]:
        """
        Verifica se uma oferta deve gerar alerta geek
        
        Args:
            offer: Oferta a ser verificada
            
        Returns:
            GeekAlert se deve gerar alerta, None caso contrário
        """
        try:
            # Calcular score geek
            geek_score = self.prioritizer.calculate_geek_score(offer)
            
            # Verificar se deve gerar alerta
            if geek_score.overall_score >= self.alert_config["high_priority_threshold"]:
                alert = await self._create_geek_alert(offer, geek_score)
                if alert:
                    self.alert_history.append(alert)
                    self.logger.info(f"Alerta geek criado para: {offer.title[:50]}...")
                    return alert
            
            return None
            
        except Exception as e:
            self.logger.error(f"Erro ao verificar oferta para alertas: {e}")
            return None
    
    async def _create_geek_alert(self, offer: Offer, geek_score: GeekScore) -> Optional[GeekAlert]:
        """Cria um alerta geek baseado na oferta e score"""
        try:
            # Determinar tipo e prioridade do alerta
            alert_type, priority, message = self._determine_alert_details(offer, geek_score)
            
            # Verificar limites de alertas
            if not self._can_send_alert(priority):
                return None
            
            alert = GeekAlert(
                offer=offer,
                geek_score=geek_score,
                alert_type=alert_type,
                priority=priority,
                message=message,
                created_at=datetime.now()
            )
            
            # Adicionar ao histórico automaticamente
            self.alert_history.append(alert)
            
            return alert
            
        except Exception as e:
            self.logger.error(f"Erro ao criar alerta geek: {e}")
            return None
    
    def _determine_alert_details(self, offer: Offer, geek_score: GeekScore) -> tuple[str, str, str]:
        """Determina detalhes do alerta baseado na oferta"""
        
        # Prioridade baseada no score
        if geek_score.overall_score >= self.alert_config["critical_threshold"]:
            priority = "critical"
        elif geek_score.overall_score >= self.alert_config["high_priority_threshold"]:
            priority = "high"
        else:
            priority = "medium"
        
        # Tipo de alerta baseado nas características
        alert_type = "high_priority"
        message_parts = []
        
        # Verificar desconto
        if offer.discount_percentage and offer.discount_percentage >= self.alert_config["price_drop_threshold"]:
            alert_type = "price_drop"
            message_parts.append(f"🔥 DESCONTO DE {offer.discount_percentage}%!")
        
        # Verificar estoque limitado
        if offer.stock_quantity and offer.stock_quantity <= self.alert_config["limited_stock_threshold"]:
            alert_type = "limited_stock"
            message_parts.append(f"⚠️ ESTOQUE LIMITADO: {offer.stock_quantity} unidades!")
        
        # Verificar categoria geek
        if geek_score.matched_categories:
            categories = ", ".join(geek_score.matched_categories)
            message_parts.append(f"🎯 CATEGORIA GEEK: {categories}")
        
        # Verificar palavras-chave
        if geek_score.matched_keywords:
            keywords = ", ".join(geek_score.matched_keywords[:3])  # Máximo 3 keywords
            message_parts.append(f"🔍 KEYWORDS: {keywords}")
        
        # Score geek
        message_parts.append(f"⭐ SCORE GEEK: {geek_score.overall_score:.2f}")
        
        # Preço
        message_parts.append(f"💰 PREÇO: R$ {offer.price}")
        
        # Mensagem final
        message = f"🚨 ALERTA GEEK {priority.upper()}!\n\n" + "\n".join(message_parts)
        
        return alert_type, priority, message
    
    def _can_send_alert(self, priority: str) -> bool:
        """Verifica se pode enviar alerta baseado nos limites"""
        
        # Resetar contadores se necessário
        now = datetime.now()
        if now - self.last_reset >= timedelta(hours=1):
            self.sent_alerts_count["hour"] = 0
            self.last_reset = now
        
        if now - self.last_reset >= timedelta(days=1):
            self.sent_alerts_count["day"] = 0
        
        # Verificar limites
        if self.sent_alerts_count["hour"] >= self.alert_config["max_alerts_per_hour"]:
            return False
        
        if self.sent_alerts_count["day"] >= self.alert_config["max_alerts_per_day"]:
            return False
        
        # Alertas críticos sempre passam
        if priority == "critical":
            return True
        
        return True
    
    async def get_pending_alerts(self, priority_filter: Optional[str] = None) -> List[GeekAlert]:
        """Retorna alertas pendentes de envio"""
        alerts = [alert for alert in self.alert_history if not alert.sent]
        
        if priority_filter:
            alerts = [alert for alert in alerts if alert.priority == priority_filter]
        
        # Ordenar por prioridade e data
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        alerts.sort(key=lambda x: (priority_order[x.priority], x.created_at))
        
        return alerts
    
    async def mark_alert_sent(self, alert: GeekAlert) -> bool:
        """Marca um alerta como enviado"""
        try:
            alert.sent = True
            alert.sent_at = datetime.now()
            
            # Atualizar contadores
            self.sent_alerts_count["hour"] += 1
            self.sent_alerts_count["day"] += 1
            self.sent_alerts_count["total"] += 1
            
            self.logger.info(f"Alerta marcado como enviado: {alert.offer.title[:50]}...")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao marcar alerta como enviado: {e}")
            return False
    
    async def get_alert_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas dos alertas"""
        total_alerts = len(self.alert_history)
        pending_alerts = len([a for a in self.alert_history if not a.sent])
        sent_alerts = total_alerts - pending_alerts
        
        # Contar por prioridade
        priority_counts = {}
        for alert in self.alert_history:
            priority_counts[alert.priority] = priority_counts.get(alert.priority, 0) + 1
        
        # Contar por tipo
        type_counts = {}
        for alert in self.alert_history:
            type_counts[alert.alert_type] = type_counts.get(alert.alert_type, 0) + 1
        
        return {
            "total_alerts": total_alerts,
            "pending_alerts": pending_alerts,
            "sent_alerts": sent_alerts,
            "priority_counts": priority_counts,
            "type_counts": type_counts,
            "sent_alerts_count": self.sent_alerts_count,
            "alert_config": self.alert_config
        }
    
    async def clear_old_alerts(self, days: int = 7) -> int:
        """Remove alertas antigos do histórico"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            initial_count = len(self.alert_history)
            
            self.alert_history = [
                alert for alert in self.alert_history 
                if alert.created_at >= cutoff_date
            ]
            
            removed_count = initial_count - len(self.alert_history)
            self.logger.info(f"Removidos {removed_count} alertas antigos")
            
            return removed_count
            
        except Exception as e:
            self.logger.error(f"Erro ao limpar alertas antigos: {e}")
            return 0
    
    async def get_top_geek_offers(self, limit: int = 10) -> List[tuple[Offer, GeekScore]]:
        """Retorna as melhores ofertas geek baseado no score"""
        try:
            # Usar o prioritizador para ordenar ofertas
            # Esta função seria chamada com uma lista de ofertas
            # Por enquanto, retorna as ofertas com maior score do histórico
            scored_offers = [
                (alert.offer, alert.geek_score) 
                for alert in self.alert_history
            ]
            
            # Ordenar por score
            scored_offers.sort(key=lambda x: x[1].overall_score, reverse=True)
            
            return scored_offers[:limit]
            
        except Exception as e:
            self.logger.error(f"Erro ao obter top ofertas geek: {e}")
            return []
    
    async def start_monitoring(self):
        """Inicia o monitoramento contínuo de alertas"""
        self.logger.info("Iniciando monitoramento de alertas geek...")
        
        try:
            while True:
                # Verificar alertas pendentes
                pending_alerts = await self.get_pending_alerts()
                
                if pending_alerts:
                    self.logger.info(f"Encontrados {len(pending_alerts)} alertas pendentes")
                    
                    # Processar alertas por prioridade
                    for alert in pending_alerts:
                        if await self._process_alert(alert):
                            await self.mark_alert_sent(alert)
                
                # Aguardar próximo ciclo
                await asyncio.sleep(self.alert_config["check_interval"])
                
        except asyncio.CancelledError:
            self.logger.info("Monitoramento de alertas cancelado")
        except Exception as e:
            self.logger.error(f"Erro no monitoramento de alertas: {e}")
    
    async def _process_alert(self, alert: GeekAlert) -> bool:
        """Processa um alerta individual"""
        try:
            # Aqui você implementaria a lógica de envio
            # Por exemplo, enviar para Telegram, email, etc.
            self.logger.info(f"Processando alerta: {alert.message[:100]}...")
            
            # Simular processamento
            await asyncio.sleep(0.1)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao processar alerta: {e}")
            return False
