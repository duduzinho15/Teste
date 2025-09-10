"""
Comandos utilitários do bot (independentes da lib telegram) para DRY_RUN e status.
"""

from typing import Tuple
from src.core.settings import Settings
from src.posting.posting_manager import posting_manager


def _is_admin(user_id: str) -> bool:
    admins = set(Settings.get_admin_ids())
    # Segurança por padrão: se vazio, ninguém é admin
    return str(user_id) in admins if admins else False


def dryrun_on(user_id: str) -> Tuple[bool, str]:
    if not _is_admin(user_id):
        return False, "Sem permissão."
    Settings.DRY_RUN = True
    return True, "DRY_RUN ativado."


def dryrun_off(user_id: str) -> Tuple[bool, str]:
    if not _is_admin(user_id):
        return False, "Sem permissão."
    Settings.DRY_RUN = False
    return True, "DRY_RUN desativado."


def status(user_id: str) -> str:
    if not _is_admin(user_id):
        return "Sem permissão."
    qs = posting_manager.get_queue_status() if posting_manager else {"queue_size": 0}
    reasons = getattr(posting_manager, "last_block_reasons", [])[-3:]
    attempts = getattr(posting_manager, "last_post_attempts", [])[-3:]
    return (
        f"DRY_RUN: {Settings.is_dry_run()}\n"
        f"Fila: {qs.get('queue_size', 0)}\n"
        f"Bloqueios recentes: {reasons}\n"
        f"Tentativas recentes: {attempts}"
    )


async def testpost(user_id: str) -> Tuple[bool, str]:
    if not _is_admin(user_id):
        return False, "Sem permissão."
    res = await posting_manager.dequeue_and_post()
    return res, f"Teste executado. DRY_RUN={Settings.is_dry_run()} resultado={res}"
