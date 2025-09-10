"""
Cron manager simples para ticks de postagem.
"""

import asyncio
import logging
import random

from src.core.settings import Settings
from src.posting.posting_manager import posting_manager

logger = logging.getLogger("cron_manager")

_consecutive_failures = 0


async def post_queue_tick(timeout_seconds: int = 10) -> str:
    """Executa um tick de postagem com timeout e registra resultado.

    Returns one of: 'posted', 'empty', 'error'
    """
    global _consecutive_failures
    try:
        if not posting_manager.posting_queue:
            logger.info(
                f"event=post_tick result=empty dry_run={Settings.is_dry_run()}"
            )
            return "empty"

        async def _run():
            # em DRY_RUN não consome a fila; dequeue_and_post retorna True
            return await posting_manager.dequeue_and_post()

        res = await asyncio.wait_for(_run(), timeout=timeout_seconds)
        if res:
            logger.info(
                f"event=post_tick result=posted dry_run={Settings.is_dry_run()}"
            )
            _consecutive_failures = 0
            return "posted"
        else:
            logger.info(
                f"event=post_tick result=empty dry_run={Settings.is_dry_run()}"
            )
            _consecutive_failures = 0
            return "empty"
    except Exception as e:
        _consecutive_failures += 1
        logger.error(f"event=post_tick result=error error={e}")
        # backoff simples
        if _consecutive_failures >= 3:
            await asyncio.sleep(2 * _consecutive_failures)
        return "error"


async def run_loop(interval_seconds: int = 45):
    """Loop periódico com jitter ±5s."""
    while True:
        jitter = random.randint(-5, 5)
        await post_queue_tick()
        await asyncio.sleep(max(1, interval_seconds + jitter))

