#!/usr/bin/env python3
"""Sistema de Controle Avançado do Bot"""

import asyncio
import logging
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Literal
from dataclasses import dataclass, asdict
from pathlib import Path
import sqlite3
from enum import Enum

class BotStatus(Enum):
    """Status do bot"""
    STOPPED = "stopped"
    RUNNING = "running"
    STARTING = "starting"
    STOPPING = "stopping"
    ERROR = "error"
    MAINTENANCE = "maintenance"

class BotAction(Enum):
    """Ações disponíveis para o bot"""
    START = "start"
    STOP = "stop"
    RESTART = "restart"
    PAUSE = "pause"
    RESUME = "resume"

@dataclass
class BotLog:
    """Log de uma ação do bot"""
    id: str
    action: str
    status: str
    message: str
    timestamp: datetime
    user: str
    details: Optional[Dict] = None

@dataclass
class BotSchedule:
    """Agendamento do bot"""
    id: str
    name: str
    cron_expression: str
    enabled: bool
    action: BotAction
    created_at: datetime
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None

class AdvancedBotController:
    """Controlador avançado do bot com agendamento e logs"""
    
    def __init__(self, db_path: str = "src/db/analytics.sqlite"):
        self.db_path = Path(db_path)
        self.logger = logging.getLogger(__name__)
        
        # Status atual do bot
        self.current_status = BotStatus.STOPPED
        self.start_time: Optional[datetime] = None
        self.uptime_seconds = 0
        
        # Configurações
        self.platforms_enabled = {
            "awin": True,
            "mercadolivre": True,
            "magalu": True,
            "amazon": True,
            "shopee": True,
            "aliexpress": True,
            "rakuten": True
        }
        
        # Inicializar banco
        self._init_database()
    
    def _init_database(self):
        """Inicializa tabelas necessárias"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Tabela de logs do bot
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS bot_logs (
                        id TEXT PRIMARY KEY,
                        action TEXT NOT NULL,
                        status TEXT NOT NULL,
                        message TEXT NOT NULL,
                        timestamp TEXT NOT NULL,
                        user TEXT NOT NULL,
                        details TEXT
                    )
                """)
                
                # Tabela de agendamentos
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS bot_schedules (
                        id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        cron_expression TEXT NOT NULL,
                        enabled INTEGER NOT NULL,
                        action TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        last_run TEXT,
                        next_run TEXT
                    )
                """)
                
                # Tabela de status do bot
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS bot_status (
                        id TEXT PRIMARY KEY,
                        status TEXT NOT NULL,
                        start_time TEXT,
                        uptime_seconds INTEGER DEFAULT 0,
                        last_action TEXT,
                        last_action_time TEXT,
                        updated_at TEXT NOT NULL
                    )
                """)
                
                # Inserir status inicial se não existir
                conn.execute("""
                    INSERT OR IGNORE INTO bot_status (id, status, updated_at)
                    VALUES ('main', 'stopped', ?)
                """, (datetime.now().isoformat(),))
                
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"Erro ao inicializar banco de dados: {e}")
    
    async def start_bot(self, user: str = "system") -> Dict:
        """Inicia o bot"""
        try:
            self.logger.info("Iniciando bot...")
            
            # Verificar se já está rodando
            if self.current_status == BotStatus.RUNNING:
                return {"success": False, "message": "Bot já está rodando"}
            
            # Atualizar status
            self.current_status = BotStatus.STARTING
            self.start_time = datetime.now()
            
            # Log da ação
            await self._log_action(BotAction.START, "success", "Bot iniciado com sucesso", user)
            
            # Simular inicialização (substituir por lógica real)
            await asyncio.sleep(2)
            
            self.current_status = BotStatus.RUNNING
            await self._update_status_in_db()
            
            self.logger.info("Bot iniciado com sucesso")
            return {"success": True, "message": "Bot iniciado com sucesso"}
            
        except Exception as e:
            self.current_status = BotStatus.ERROR
            error_msg = f"Erro ao iniciar bot: {e}"
            self.logger.error(error_msg)
            await self._log_action(BotAction.START, "error", error_msg, user)
            return {"success": False, "message": error_msg}
    
    async def stop_bot(self, user: str = "system") -> Dict:
        """Para o bot"""
        try:
            self.logger.info("Parando bot...")
            
            if self.current_status == BotStatus.STOPPED:
                return {"success": False, "message": "Bot já está parado"}
            
            self.current_status = BotStatus.STOPPING
            
            # Log da ação
            await self._log_action(BotAction.STOP, "success", "Bot parado com sucesso", user)
            
            # Simular parada (substituir por lógica real)
            await asyncio.sleep(1)
            
            # Calcular uptime
            if self.start_time:
                self.uptime_seconds = int((datetime.now() - self.start_time).total_seconds())
            
            self.current_status = BotStatus.STOPPED
            self.start_time = None
            await self._update_status_in_db()
            
            self.logger.info("Bot parado com sucesso")
            return {"success": True, "message": "Bot parado com sucesso"}
            
        except Exception as e:
            self.current_status = BotStatus.ERROR
            error_msg = f"Erro ao parar bot: {e}"
            self.logger.error(error_msg)
            await self._log_action(BotAction.STOP, "error", error_msg, user)
            return {"success": False, "message": error_msg}
    
    async def restart_bot(self, user: str = "system") -> Dict:
        """Reinicia o bot"""
        try:
            self.logger.info("Reiniciando bot...")
            
            # Parar primeiro
            stop_result = await self.stop_bot(user)
            if not stop_result["success"]:
                return stop_result
            
            # Aguardar um pouco
            await asyncio.sleep(2)
            
            # Iniciar novamente
            start_result = await self.start_bot(user)
            if not start_result["success"]:
                return start_result
            
            await self._log_action(BotAction.RESTART, "success", "Bot reiniciado com sucesso", user)
            
            return {"success": True, "message": "Bot reiniciado com sucesso"}
            
        except Exception as e:
            error_msg = f"Erro ao reiniciar bot: {e}"
            self.logger.error(error_msg)
            await self._log_action(BotAction.RESTART, "error", error_msg, user)
            return {"success": False, "message": error_msg}
    
    async def get_bot_status(self) -> Dict:
        """Obtém status atual do bot"""
        try:
            # Calcular uptime atual se estiver rodando
            current_uptime = self.uptime_seconds
            if self.current_status == BotStatus.RUNNING and self.start_time:
                current_uptime = int((datetime.now() - self.start_time).total_seconds())
            
            # Verificar status no banco
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("SELECT * FROM bot_status WHERE id = 'main'")
                row = cursor.fetchone()
                
                db_status = row["status"] if row else "unknown"
                last_action = row["last_action"] if row else None
                last_action_time = row["last_action_time"] if row else None
            
            return {
                "status": self.current_status.value,
                "uptime_seconds": current_uptime,
                "uptime_formatted": self._format_uptime(current_uptime),
                "start_time": self.start_time.isoformat() if self.start_time else None,
                "last_action": last_action,
                "last_action_time": last_action_time,
                "platforms_enabled": self.platforms_enabled,
                "updated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao obter status do bot: {e}")
            return {
                "status": "error",
                "error": str(e),
                "updated_at": datetime.now().isoformat()
            }
    
    async def toggle_platform(self, platform: str, enabled: bool, user: str = "system") -> Dict:
        """Ativa/desativa uma plataforma"""
        try:
            if platform not in self.platforms_enabled:
                return {"success": False, "message": f"Plataforma '{platform}' não reconhecida"}
            
            old_status = self.platforms_enabled[platform]
            self.platforms_enabled[platform] = enabled
            
            action = "ativada" if enabled else "desativada"
            message = f"Plataforma {platform} {action}"
            
            await self._log_action(
                "toggle_platform", 
                "success", 
                message, 
                user, 
                {"platform": platform, "enabled": enabled, "previous": old_status}
            )
            
            return {"success": True, "message": message}
            
        except Exception as e:
            error_msg = f"Erro ao alterar plataforma {platform}: {e}"
            self.logger.error(error_msg)
            return {"success": False, "message": error_msg}
    
    async def get_recent_logs(self, limit: int = 50) -> List[Dict]:
        """Obtém logs recentes do bot"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("""
                    SELECT * FROM bot_logs 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                """, (limit,))
                
                logs = []
                for row in cursor.fetchall():
                    log = {
                        "id": row["id"],
                        "action": row["action"],
                        "status": row["status"],
                        "message": row["message"],
                        "timestamp": row["timestamp"],
                        "user": row["user"],
                        "details": json.loads(row["details"]) if row["details"] else None
                    }
                    logs.append(log)
                
                return logs
                
        except Exception as e:
            self.logger.error(f"Erro ao obter logs: {e}")
            return []
    
    async def create_schedule(self, name: str, cron_expression: str, action: BotAction, user: str = "system") -> Dict:
        """Cria um novo agendamento"""
        try:
            schedule_id = f"schedule_{int(time.time())}"
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO bot_schedules 
                    (id, name, cron_expression, enabled, action, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (schedule_id, name, cron_expression, 1, action.value, datetime.now().isoformat()))
                
                conn.commit()
            
            await self._log_action(
                "create_schedule", 
                "success", 
                f"Agendamento '{name}' criado", 
                user,
                {"schedule_id": schedule_id, "cron": cron_expression, "action": action.value}
            )
            
            return {"success": True, "message": f"Agendamento '{name}' criado com sucesso"}
            
        except Exception as e:
            error_msg = f"Erro ao criar agendamento: {e}"
            self.logger.error(error_msg)
            return {"success": False, "message": error_msg}
    
    async def get_schedules(self) -> List[Dict]:
        """Obtém todos os agendamentos"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("SELECT * FROM bot_schedules ORDER BY created_at DESC")
                
                schedules = []
                for row in cursor.fetchall():
                    schedule = {
                        "id": row["id"],
                        "name": row["name"],
                        "cron_expression": row["cron_expression"],
                        "enabled": bool(row["enabled"]),
                        "action": row["action"],
                        "created_at": row["created_at"],
                        "last_run": row["last_run"],
                        "next_run": row["next_run"]
                    }
                    schedules.append(schedule)
                
                return schedules
                
        except Exception as e:
            self.logger.error(f"Erro ao obter agendamentos: {e}")
            return []
    
    async def _log_action(self, action: str, status: str, message: str, user: str, details: Optional[Dict] = None):
        """Registra uma ação do bot"""
        try:
            log_id = f"log_{int(time.time())}_{action}"
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO bot_logs (id, action, status, message, timestamp, user, details)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    log_id, 
                    action, 
                    status, 
                    message, 
                    datetime.now().isoformat(), 
                    user,
                    json.dumps(details) if details else None
                ))
                
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"Erro ao registrar log: {e}")
    
    async def _update_status_in_db(self):
        """Atualiza status do bot no banco de dados"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    UPDATE bot_status 
                    SET status = ?, start_time = ?, uptime_seconds = ?, updated_at = ?
                    WHERE id = 'main'
                """, (
                    self.current_status.value,
                    self.start_time.isoformat() if self.start_time else None,
                    self.uptime_seconds,
                    datetime.now().isoformat()
                ))
                
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"Erro ao atualizar status no banco: {e}")
    
    def _format_uptime(self, seconds: int) -> str:
        """Formata uptime em formato legível"""
        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            minutes = seconds // 60
            return f"{minutes}m {seconds % 60}s"
        else:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"{hours}h {minutes}m"
    
    async def get_system_health(self) -> Dict:
        """Obtém saúde geral do sistema"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                # Contar views SQL
                cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='view'")
                views = cursor.fetchall()
                total_views = len(views)
                
                # Verificar se views estão funcionando
                working_views = 0
                for view in views:
                    try:
                        conn.execute(f"SELECT COUNT(*) FROM {view['name']} LIMIT 1")
                        working_views += 1
                    except:
                        pass
                
                # Contar eventos recentes (24h)
                yesterday = datetime.now() - timedelta(days=1)
                cursor = conn.execute("""
                    SELECT COUNT(*) as count FROM offers_posted 
                    WHERE created_at >= ?
                """, (yesterday.isoformat(),))
                
                recent_events = cursor.fetchone()["count"] if cursor.fetchone() else 0
                
                return {
                    "sql_views": f"{working_views}/{total_views}",
                    "recent_events_24h": recent_events,
                    "system_status": "Ativo" if working_views == total_views else "Parcial",
                    "bot_status": self.current_status.value,
                    "uptime": self._format_uptime(self.uptime_seconds),
                    "platforms_active": sum(self.platforms_enabled.values()),
                    "last_check": datetime.now().isoformat()
                }
                
        except Exception as e:
            self.logger.error(f"Erro ao verificar saúde do sistema: {e}")
            return {
                "sql_views": "0/0",
                "recent_events_24h": 0,
                "system_status": "Erro",
                "error": str(e),
                "last_check": datetime.now().isoformat()
            }
