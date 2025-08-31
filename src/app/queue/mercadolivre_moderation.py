#!/usr/bin/env python3
"""
Sistema de Moderação Manual do Mercado Livre
Gerencia o workflow de conversão de links para afiliados
"""

import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Callable

from src.core.models import Offer
from src.app.queue.offer_queue import QueuedOffer, QueueStatus, QueuePriority
from src.affiliate.mercadolivre import validate_ml_url


class ModerationStatus(Enum):
    """Status de moderação do Mercado Livre"""
    PENDING_CONVERSION = "pending_conversion"  # Aguardando conversão manual
    CONVERSION_SUBMITTED = "conversion_submitted"  # Conversão enviada pelo usuário
    CONVERSION_APPROVED = "conversion_approved"  # Conversão aprovada
    CONVERSION_REJECTED = "conversion_rejected"  # Conversão rejeitada
    READY_FOR_POSTING = "ready_for_posting"  # Pronto para postagem
    POSTED = "posted"  # Já postado


@dataclass
class MercadoLivreModerationTask:
    """Tarefa de moderação do Mercado Livre"""
    
    id: str
    offer: Offer
    status: ModerationStatus = ModerationStatus.PENDING_CONVERSION
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    # Dados de conversão
    original_url: str = ""
    converted_affiliate_url: Optional[str] = None
    conversion_notes: str = ""
    conversion_submitted_at: Optional[datetime] = None
    conversion_submitted_by: Optional[str] = None
    
    # Validação
    is_valid_affiliate_url: bool = False
    validation_errors: List[str] = field(default_factory=list)
    
    # Metadados
    priority: QueuePriority = QueuePriority.NORMAL
    tags: List[str] = field(default_factory=list)
    flags: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        if self.original_url == "":
            self.original_url = self.offer.url

    def update_status(self, new_status: ModerationStatus):
        """Atualiza o status da tarefa"""
        self.status = new_status
        self.updated_at = datetime.now()

    def submit_conversion(self, affiliate_url: str, submitted_by: str, notes: str = ""):
        """Submete uma conversão de link"""
        self.converted_affiliate_url = affiliate_url
        self.conversion_submitted_at = datetime.now()
        self.conversion_submitted_by = submitted_by
        self.conversion_notes = notes
        self.update_status(ModerationStatus.CONVERSION_SUBMITTED)

    def validate_conversion(self) -> bool:
        """Valida a conversão submetida"""
        if not self.converted_affiliate_url:
            self.validation_errors.append("URL de afiliado não fornecida")
            return False
        
        # Validar formato da URL
        try:
            is_valid, _ = validate_ml_url(self.converted_affiliate_url)
            self.is_valid_affiliate_url = is_valid
            
            if not is_valid:
                self.validation_errors.append("URL de afiliado inválida")
                return False
                
        except Exception as e:
            self.validation_errors.append(f"Erro na validação: {str(e)}")
            return False
        
        return True

    def approve_conversion(self):
        """Aprova a conversão"""
        if self.validate_conversion():
            self.update_status(ModerationStatus.CONVERSION_APPROVED)
            return True
        return False

    def reject_conversion(self, reason: str):
        """Rejeita a conversão"""
        self.conversion_notes += f"\nREJEITADO: {reason}"
        self.update_status(ModerationStatus.CONVERSION_REJECTED)

    def mark_ready_for_posting(self):
        """Marca como pronto para postagem"""
        if self.status == ModerationStatus.CONVERSION_APPROVED:
            self.update_status(ModerationStatus.READY_FOR_POSTING)
            return True
        return False

    def is_overdue(self, max_hours: int = 24) -> bool:
        """Verifica se a tarefa está atrasada"""
        return datetime.now() - self.updated_at > timedelta(hours=max_hours)


class MercadoLivreModerationSystem:
    """Sistema de moderação manual do Mercado Livre"""
    
    def __init__(self, offer_queue=None):
        self.logger = logging.getLogger("moderation.mercadolivre")
        self.offer_queue = offer_queue
        
        # Tarefas de moderação
        self.moderation_tasks: Dict[str, MercadoLivreModerationTask] = {}
        
        # Callbacks
        self.on_conversion_submitted: Optional[Callable[[MercadoLivreModerationTask], None]] = None
        self.on_conversion_approved: Optional[Callable[[MercadoLivreModerationTask], None]] = None
        self.on_ready_for_posting: Optional[Callable[[MercadoLivreModerationTask], None]] = None
        
        # Estatísticas
        self.stats = {
            "total_tasks": 0,
            "pending_conversion": 0,
            "conversion_submitted": 0,
            "conversion_approved": 0,
            "conversion_rejected": 0,
            "ready_for_posting": 0,
            "posted": 0,
            "overdue_tasks": 0
        }
        
        self.logger.info("Sistema de moderação Mercado Livre inicializado")

    def create_moderation_task(self, offer: Offer) -> str:
        """Cria uma nova tarefa de moderação"""
        task_id = str(uuid.uuid4())
        
        task = MercadoLivreModerationTask(
            id=task_id,
            offer=offer
        )
        
        self.moderation_tasks[task_id] = task
        self.stats["total_tasks"] += 1
        self.stats["pending_conversion"] += 1
        
        self.logger.info(f"Nova tarefa de moderação criada: {task_id}")
        return task_id

    def submit_conversion(self, task_id: str, affiliate_url: str, submitted_by: str, notes: str = "") -> bool:
        """Submete uma conversão de link"""
        if task_id not in self.moderation_tasks:
            self.logger.error(f"Tarefa não encontrada: {task_id}")
            return False
        
        task = self.moderation_tasks[task_id]
        
        # Atualizar estatísticas
        if task.status == ModerationStatus.PENDING_CONVERSION:
            self.stats["pending_conversion"] -= 1
        self.stats["conversion_submitted"] += 1
        
        # Submeter conversão
        task.submit_conversion(affiliate_url, submitted_by, notes)
        
        # Validar automaticamente
        if task.validate_conversion():
            task.approve_conversion()
            self.stats["conversion_approved"] += 1
            self.stats["conversion_submitted"] -= 1
            
            # Marcar como pronto para postagem
            if task.mark_ready_for_posting():
                self.stats["ready_for_posting"] += 1
                
                # Callback
                if self.on_ready_for_posting:
                    self.on_ready_for_posting(task)
        else:
            self.logger.warning(f"Conversão rejeitada para tarefa {task_id}: {task.validation_errors}")
        
        # Callback
        if self.on_conversion_submitted:
            self.on_conversion_submitted(task)
        
        return True

    def approve_conversion(self, task_id: str) -> bool:
        """Aprova uma conversão manualmente"""
        if task_id not in self.moderation_tasks:
            return False
        
        task = self.moderation_tasks[task_id]
        
        if task.approve_conversion():
            self.stats["conversion_submitted"] -= 1
            self.stats["conversion_approved"] += 1
            
            if task.mark_ready_for_posting():
                self.stats["ready_for_posting"] += 1
                
                # Callback
                if self.on_ready_for_posting:
                    self.on_ready_for_posting(task)
            
            return True
        
        return False

    def reject_conversion(self, task_id: str, reason: str) -> bool:
        """Rejeita uma conversão"""
        if task_id not in self.moderation_tasks:
            return False
        
        task = self.moderation_tasks[task_id]
        
        # Atualizar estatísticas
        if task.status == ModerationStatus.CONVERSION_SUBMITTED:
            self.stats["conversion_submitted"] -= 1
        elif task.status == ModerationStatus.CONVERSION_APPROVED:
            self.stats["conversion_approved"] -= 1
        
        self.stats["conversion_rejected"] += 1
        
        task.reject_conversion(reason)
        return True

    def mark_as_posted(self, task_id: str) -> bool:
        """Marca uma tarefa como postada"""
        if task_id not in self.moderation_tasks:
            return False
        
        task = self.moderation_tasks[task_id]
        
        if task.status == ModerationStatus.READY_FOR_POSTING:
            task.update_status(ModerationStatus.POSTED)
            self.stats["ready_for_posting"] -= 1
            self.stats["posted"] += 1
            return True
        
        return False

    def get_pending_tasks(self, limit: int = 50) -> List[MercadoLivreModerationTask]:
        """Obtém tarefas pendentes de conversão"""
        pending = [
            task for task in self.moderation_tasks.values()
            if task.status == ModerationStatus.PENDING_CONVERSION
        ]
        
        # Ordenar por prioridade e data de criação
        pending.sort(key=lambda x: (x.priority.value, x.created_at))
        
        return pending[:limit]

    def get_ready_for_posting_tasks(self, limit: int = 50) -> List[MercadoLivreModerationTask]:
        """Obtém tarefas prontas para postagem"""
        ready = [
            task for task in self.moderation_tasks.values()
            if task.status == ModerationStatus.READY_FOR_POSTING
        ]
        
        # Ordenar por prioridade e data de aprovação
        ready.sort(key=lambda x: (x.priority.value, x.conversion_submitted_at or x.created_at))
        
        return ready[:limit]

    def get_task_by_id(self, task_id: str) -> Optional[MercadoLivreModerationTask]:
        """Obtém uma tarefa por ID"""
        return self.moderation_tasks.get(task_id)

    def get_overdue_tasks(self, max_hours: int = 24) -> List[MercadoLivreModerationTask]:
        """Obtém tarefas atrasadas"""
        overdue = [
            task for task in self.moderation_tasks.values()
            if task.is_overdue(max_hours)
        ]
        
        self.stats["overdue_tasks"] = len(overdue)
        return overdue

    def cleanup_old_tasks(self, days: int = 30):
        """Remove tarefas antigas"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        to_remove = [
            task_id for task_id, task in self.moderation_tasks.items()
            if task.updated_at < cutoff_date and task.status == ModerationStatus.POSTED
        ]
        
        for task_id in to_remove:
            del self.moderation_tasks[task_id]
        
        self.logger.info(f"Removidas {len(to_remove)} tarefas antigas")

    def get_stats(self) -> Dict[str, Any]:
        """Obtém estatísticas do sistema"""
        return {
            **self.stats,
            "total_active_tasks": len(self.moderation_tasks),
            "last_updated": datetime.now().isoformat()
        }

    def export_ready_offers(self) -> List[Offer]:
        """Exporta ofertas prontas para postagem"""
        ready_tasks = self.get_ready_for_posting_tasks()
        offers = []
        
        for task in ready_tasks:
            # Criar nova oferta com URL de afiliado
            offer = Offer(
                title=task.offer.title,
                price=task.offer.price,
                original_price=task.offer.original_price,
                url=task.converted_affiliate_url,  # URL convertida
                store=task.offer.store,
                image_url=task.offer.image_url,
                source=task.offer.source,
                store_data={
                    **task.offer.store_data,
                    "affiliate_url": task.converted_affiliate_url,
                    "conversion_task_id": task.id,
                    "conversion_approved_at": task.updated_at.isoformat(),
                    "needs_conversion": False  # Já convertida
                }
            )
            offers.append(offer)
        
        return offers


# Função de conveniência para uso externo
def get_mercadolivre_moderation_system(offer_queue=None) -> MercadoLivreModerationSystem:
    """Retorna instância do sistema de moderação do Mercado Livre"""
    return MercadoLivreModerationSystem(offer_queue)


if __name__ == "__main__":
    # Teste do sistema
    from src.core.models import Offer
    from decimal import Decimal
    
    # Criar oferta de teste
    test_offer = Offer(
        title="Smartphone Teste",
        price=Decimal("999.99"),
        url="https://www.mercadolivre.com.br/teste",
        store="Mercado Livre",
        source="test"
    )
    
    # Testar sistema
    moderation_system = get_mercadolivre_moderation_system()
    
    # Criar tarefa
    task_id = moderation_system.create_moderation_task(test_offer)
    print(f"Tarefa criada: {task_id}")
    
    # Submeter conversão
    success = moderation_system.submit_conversion(
        task_id, 
        "https://mercadolivre.com/sec/abc123", 
        "usuario_teste"
    )
    print(f"Conversão submetida: {success}")
    
    # Estatísticas
    stats = moderation_system.get_stats()
    print(f"Estatísticas: {stats}")
