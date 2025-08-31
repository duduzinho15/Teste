#!/usr/bin/env python3
"""
Sistema de Produção - Garimpeiro Geek
Ativa o sistema automático de postagem em produção
"""

import asyncio
import sys
import os
import signal
from pathlib import Path
from datetime import datetime
import logging

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from auto_telegram_system import AutoTelegramSystem

# Configurar logging para produção
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/production_system.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class ProductionSystem:
    """Sistema de produção do Garimpeiro Geek"""
    
    def __init__(self):
        self.logger = logging.getLogger("production_system")
        self.auto_system = AutoTelegramSystem()
        self.running = False
        
        # Configurar handlers de sinal
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handler para sinais de interrupção"""
        self.logger.info(f"🛑 Sinal {signum} recebido, parando sistema...")
        asyncio.create_task(self.stop_production())
    
    async def start_production(self):
        """Inicia o sistema de produção"""
        self.logger.info("🚀 INICIANDO SISTEMA DE PRODUÇÃO - GARIMPEIRO GEEK")
        self.logger.info("=" * 60)
        
        try:
            # Verificar configuração
            self.logger.info("🔧 Verificando configuração...")
            
            # Iniciar sistema automático
            success = await self.auto_system.start_auto_system()
            
            if not success:
                self.logger.error("❌ Falha ao iniciar sistema automático")
                return False
            
            self.running = True
            self.logger.info("✅ Sistema de produção iniciado com sucesso!")
            
            # Mostrar status inicial
            await self._show_status()
            
            # Loop principal de produção
            while self.running:
                await asyncio.sleep(300)  # Verificar a cada 5 minutos
                
                # Mostrar status periódico
                await self._show_status()
                
                # Verificar saúde do sistema
                await self._health_check()
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erro no sistema de produção: {e}")
            return False
    
    async def stop_production(self):
        """Para o sistema de produção"""
        self.logger.info("🛑 Parando sistema de produção...")
        
        self.running = False
        
        if self.auto_system:
            await self.auto_system.stop_auto_system()
        
        self.logger.info("✅ Sistema de produção parado")
    
    async def _show_status(self):
        """Mostra status do sistema"""
        try:
            status = self.auto_system.get_system_status()
            
            self.logger.info("📊 STATUS DO SISTEMA:")
            self.logger.info(f"   🟢 Rodando: {status['running']}")
            self.logger.info(f"   📝 Ofertas postadas: {status['posted_count']}")
            self.logger.info(f"   📭 Fila de ofertas: {status['queue_size']}")
            self.logger.info(f"   ⏰ Última postagem: {status['last_post_time']}")
            self.logger.info(f"   ⚙️ Scheduler: {status['scheduler_running']}")
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao obter status: {e}")
    
    async def _health_check(self):
        """Verifica saúde do sistema"""
        try:
            # Verificar se o bot está funcionando
            if not self.auto_system.bot:
                self.logger.warning("⚠️ Bot do Telegram não configurado")
                return False
            
            # Verificar se há ofertas na fila
            if len(self.auto_system.offer_queue) == 0:
                self.logger.info("📭 Fila de ofertas vazia - sistema funcionando normalmente")
            
            # Verificar se o scheduler está rodando
            if not self.auto_system.scheduler.running:
                self.logger.warning("⚠️ Scheduler não está rodando")
                return False
            
            self.logger.info("✅ Health check: Sistema saudável")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erro no health check: {e}")
            return False
    
    async def emergency_stop(self):
        """Para o sistema em emergência"""
        self.logger.warning("🚨 PARADA DE EMERGÊNCIA ATIVADA!")
        
        try:
            await self.stop_production()
            self.logger.info("✅ Sistema parado com sucesso")
        except Exception as e:
            self.logger.error(f"❌ Erro na parada de emergência: {e}")


async def main():
    """Função principal"""
    print("🚀 SISTEMA DE PRODUÇÃO - GARIMPEIRO GEEK")
    print("=" * 60)
    print("💡 Para parar o sistema, pressione Ctrl+C")
    print("=" * 60)
    
    # Criar sistema de produção
    production = ProductionSystem()
    
    try:
        # Iniciar sistema
        await production.start_production()
        
    except KeyboardInterrupt:
        print("\n🛑 Interrupção detectada, parando sistema...")
        await production.stop_production()
        
    except Exception as e:
        print(f"\n❌ Erro no sistema: {e}")
        await production.emergency_stop()


if __name__ == "__main__":
    # Configurar encoding para Windows
    if os.name == 'nt':
        os.system('chcp 65001 > nul')
    
    asyncio.run(main())
