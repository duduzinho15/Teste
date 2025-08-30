"""
Sistema de Agendamento de Postagem Automática
Gerencia jobs de coleta, enriquecimento e postagem de ofertas
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum

from ..core.models import Offer
from ..core.affiliate_converter import AffiliateConverter
from ..core.affiliate_validator import AffiliateValidator
from .message_formatter import message_formatter


class JobStatus(Enum):
    """Status de um job"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class JobPriority(Enum):
    """Prioridade de um job"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class ScheduledJob:
    """Job agendado"""
    
    id: str
    name: str
    function: Callable
    interval: timedelta
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    status: JobStatus = JobStatus.PENDING
    priority: JobPriority = JobPriority.NORMAL
    max_retries: int = 3
    retry_count: int = 0
    error_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


class JobScheduler:
    """Agendador de jobs de postagem"""
    
    def __init__(self):
        self.logger = logging.getLogger("job_scheduler")
        self.jobs: Dict[str, ScheduledJob] = {}
        self.running = False
        self.task: Optional[asyncio.Task] = None
        
        # Dependências
        self.converter = AffiliateConverter()
        self.validator = AffiliateValidator()
        
        # Estatísticas
        self.stats = {
            "total_jobs": 0,
            "completed_jobs": 0,
            "failed_jobs": 0,
            "total_runtime": 0.0,
            "last_run": None
        }
    
    async def start(self):
        """Inicia o scheduler"""
        if self.running:
            self.logger.warning("Scheduler já está rodando")
            return
        
        self.running = True
        self.logger.info("Iniciando Job Scheduler...")
        
        # Inicializar jobs padrão
        await self._initialize_default_jobs()
        
        # Iniciar loop principal
        self.task = asyncio.create_task(self._main_loop())
        
        self.logger.info("Job Scheduler iniciado com sucesso")
    
    async def stop(self):
        """Para o scheduler"""
        if not self.running:
            return
        
        self.logger.info("Parando Job Scheduler...")
        self.running = False
        
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        
        self.logger.info("Job Scheduler parado")
    
    async def _initialize_default_jobs(self):
        """Inicializa jobs padrão do sistema"""
        # Job: Coleta de ofertas (90 segundos)
        await self.add_job(
            "collect_offers",
            self._collect_offers_job,
            timedelta(seconds=90),
            priority=JobPriority.HIGH,
            metadata={"description": "Coleta ofertas das plataformas"}
        )
        
        # Job: Enriquecimento de preços (15 minutos)
        await self.add_job(
            "enrich_prices",
            self._enrich_prices_job,
            timedelta(minutes=15),
            priority=JobPriority.NORMAL,
            metadata={"description": "Atualiza preços e descontos"}
        )
        
        # Job: Postagem na fila (45 segundos)
        await self.add_job(
            "post_queue",
            self._post_queue_job,
            timedelta(seconds=45),
            priority=JobPriority.HIGH,
            metadata={"description": "Processa fila de postagem"}
        )
        
        # Job: Agregação de preços (30 minutos)
        await self.add_job(
            "price_aggregate",
            self._price_aggregate_job,
            timedelta(minutes=30),
            priority=JobPriority.LOW,
            metadata={"description": "Agrega dados de preços"}
        )
    
    async def add_job(
        self,
        name: str,
        function: Callable,
        interval: timedelta,
        priority: JobPriority = JobPriority.NORMAL,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Adiciona um novo job
        
        Args:
            name: Nome do job
            function: Função a ser executada
            interval: Intervalo entre execuções
            priority: Prioridade do job
            metadata: Metadados adicionais
            
        Returns:
            ID do job criado
        """
        job_id = f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        job = ScheduledJob(
            id=job_id,
            name=name,
            function=function,
            interval=interval,
            next_run=datetime.now() + interval,
            priority=priority,
            metadata=metadata or {}
        )
        
        self.jobs[job_id] = job
        self.stats["total_jobs"] += 1
        
        self.logger.info(f"Job adicionado: {name} (ID: {job_id})")
        return job_id
    
    async def remove_job(self, job_id: str) -> bool:
        """Remove um job"""
        if job_id in self.jobs:
            del self.jobs[job_id]
            self.logger.info(f"Job removido: {job_id}")
            return True
        return False
    
    async def _main_loop(self):
        """Loop principal do scheduler"""
        while self.running:
            try:
                # Verificar jobs pendentes
                await self._check_pending_jobs()
                
                # Aguardar próximo ciclo
                await asyncio.sleep(1)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Erro no loop principal: {e}")
                await asyncio.sleep(5)  # Aguardar antes de tentar novamente
    
    async def _check_pending_jobs(self):
        """Verifica e executa jobs pendentes"""
        now = datetime.now()
        jobs_to_run = []
        
        # Identificar jobs que devem ser executados
        for job in self.jobs.values():
            if (job.status == JobStatus.PENDING and 
                job.next_run and 
                job.next_run <= now):
                jobs_to_run.append(job)
        
        # Executar jobs em ordem de prioridade
        jobs_to_run.sort(key=lambda j: j.priority.value, reverse=True)
        
        for job in jobs_to_run:
            await self._execute_job(job)
    
    async def _execute_job(self, job: ScheduledJob):
        """Executa um job específico"""
        job.status = JobStatus.RUNNING
        job.last_run = datetime.now()
        
        self.logger.info(f"Executando job: {job.name}")
        
        start_time = datetime.now()
        
        try:
            # Executar função do job
            if asyncio.iscoroutinefunction(job.function):
                await job.function()
            else:
                job.function()
            
            # Job executado com sucesso
            job.status = JobStatus.COMPLETED
            job.retry_count = 0
            job.error_count = 0
            
            runtime = (datetime.now() - start_time).total_seconds()
            self.stats["completed_jobs"] += 1
            self.stats["total_runtime"] += runtime
            self.stats["last_run"] = datetime.now()
            
            self.logger.info(f"Job {job.name} executado com sucesso em {runtime:.2f}s")
            
        except Exception as e:
            # Job falhou
            job.status = JobStatus.FAILED
            job.error_count += 1
            job.retry_count += 1
            
            self.stats["failed_jobs"] += 1
            
            self.logger.error(f"Job {job.name} falhou: {e}")
            
            # Tentar novamente se não excedeu o limite
            if job.retry_count < job.max_retries:
                retry_delay = min(job.interval.total_seconds() * 2, 300)  # Máximo 5 minutos
                job.next_run = datetime.now() + timedelta(seconds=retry_delay)
                job.status = JobStatus.PENDING
                self.logger.info(f"Job {job.name} será tentado novamente em {retry_delay}s")
        
        # Agendar próxima execução
        if job.status == JobStatus.COMPLETED:
            job.next_run = datetime.now() + job.interval
            job.status = JobStatus.PENDING
    
    # Jobs padrão do sistema
    
    async def _collect_offers_job(self):
        """Job de coleta de ofertas"""
        self.logger.info("🔄 Executando coleta de ofertas...")
        
        try:
            # Simular coleta de ofertas
            offers = await self._collect_offers_from_platforms()
            
            # Validar ofertas
            valid_offers = await self._validate_offers(offers)
            
            # Converter para afiliados
            affiliate_offers = await self._convert_to_affiliate(valid_offers)
            
            # Salvar ofertas coletadas
            await self._save_collected_offers(affiliate_offers)
            
            self.logger.info(f"✅ Coleta concluída: {len(affiliate_offers)} ofertas válidas")
            
        except Exception as e:
            self.logger.error(f"❌ Erro na coleta de ofertas: {e}")
            raise
    
    async def _enrich_prices_job(self):
        """Job de enriquecimento de preços"""
        self.logger.info("💰 Executando enriquecimento de preços...")
        
        try:
            # Simular atualização de preços
            updated_count = await self._update_price_data()
            
            self.logger.info(f"✅ Enriquecimento concluído: {updated_count} preços atualizados")
            
        except Exception as e:
            self.logger.error(f"❌ Erro no enriquecimento de preços: {e}")
            raise
    
    async def _post_queue_job(self):
        """Job de postagem na fila"""
        self.logger.info("📝 Executando postagem na fila...")
        
        try:
            # Simular processamento da fila
            posted_count = await self._process_post_queue()
            
            self.logger.info(f"✅ Postagem concluída: {posted_count} ofertas postadas")
            
        except Exception as e:
            self.logger.error(f"❌ Erro na postagem: {e}")
            raise
    
    async def _price_aggregate_job(self):
        """Job de agregação de preços"""
        self.logger.info("📊 Executando agregação de preços...")
        
        try:
            # Simular agregação de dados
            aggregated_data = await self._aggregate_price_data()
            
            self.logger.info(f"✅ Agregação concluída: {len(aggregated_data)} datasets processados")
            
        except Exception as e:
            self.logger.error(f"❌ Erro na agregação: {e}")
            raise
    
    # Métodos auxiliares dos jobs
    
    async def _collect_offers_from_platforms(self) -> List[Offer]:
        """Coleta ofertas das plataformas (simulado)"""
        # Simular coleta
        await asyncio.sleep(2)
        
        offers = [
            Offer(
                title="Smartphone Samsung Galaxy S23",
                price=2999.99,
                original_price=3999.99,
                discount_percentage=25,
                store="Amazon",
                category="Eletrônicos",
                url="https://amzn.to/test123"
            ),
            Offer(
                title="Notebook Dell Inspiron 15",
                price=2499.99,
                original_price=2999.99,
                discount_percentage=17,
                store="Magazine Luiza",
                category="Informática",
                url="https://magazinevoce.com.br/test123"
            )
        ]
        
        return offers
    
    async def _validate_offers(self, offers: List[Offer]) -> List[Offer]:
        """Valida ofertas coletadas"""
        valid_offers = []
        
        for offer in offers:
            try:
                # Validar URL
                validation = self.validator.validate_url(offer.url)
                
                if validation.status.value in ["valid", "warning"]:
                    valid_offers.append(offer)
                else:
                    self.logger.warning(f"Oferta rejeitada: {offer.title} - {validation.message}")
                    
            except Exception as e:
                self.logger.error(f"Erro ao validar oferta {offer.title}: {e}")
        
        return valid_offers
    
    async def _convert_to_affiliate(self, offers: List[Offer]) -> List[Offer]:
        """Converte ofertas para links de afiliado"""
        converted_offers = []
        
        for offer in offers:
            try:
                # Converter URL para afiliado
                affiliate_url = await self.converter.convert_to_affiliate(offer.url)
                
                # Atualizar URL da oferta
                offer.url = affiliate_url
                converted_offers.append(offer)
                
            except Exception as e:
                self.logger.error(f"Erro ao converter oferta {offer.title}: {e}")
        
        return converted_offers
    
    async def _save_collected_offers(self, offers: List[Offer]):
        """Salva ofertas coletadas (simulado)"""
        # Simular salvamento
        await asyncio.sleep(1)
        self.logger.info(f"💾 {len(offers)} ofertas salvas no banco de dados")
    
    async def _update_price_data(self) -> int:
        """Atualiza dados de preços (simulado)"""
        # Simular atualização
        await asyncio.sleep(3)
        return 42  # Número de preços atualizados
    
    async def _process_post_queue(self) -> int:
        """Processa fila de postagem (simulado)"""
        # Simular processamento
        await asyncio.sleep(2)
        return 15  # Número de ofertas postadas
    
    async def _aggregate_price_data(self) -> List[Dict[str, Any]]:
        """Agrega dados de preços (simulado)"""
        # Simular agregação
        await asyncio.sleep(5)
        return [
            {"platform": "amazon", "avg_price": 1500.0, "total_offers": 100},
            {"platform": "mercadolivre", "avg_price": 1200.0, "total_offers": 80}
        ]
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Retorna status de um job específico"""
        if job_id not in self.jobs:
            return None
        
        job = self.jobs[job_id]
        return {
            "id": job.id,
            "name": job.name,
            "status": job.status.value,
            "priority": job.priority.value,
            "last_run": job.last_run.isoformat() if job.last_run else None,
            "next_run": job.next_run.isoformat() if job.next_run else None,
            "retry_count": job.retry_count,
            "error_count": job.error_count,
            "metadata": job.metadata
        }
    
    def get_all_jobs_status(self) -> List[Dict[str, Any]]:
        """Retorna status de todos os jobs"""
        return [self.get_job_status(job_id) for job_id in self.jobs.keys()]
    
    def get_scheduler_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do scheduler"""
        return {
            **self.stats,
            "running": self.running,
            "active_jobs": len([j for j in self.jobs.values() if j.status == JobStatus.PENDING]),
            "total_jobs_registered": len(self.jobs)
        }


# Instância global para uso em outros módulos
job_scheduler = JobScheduler()
