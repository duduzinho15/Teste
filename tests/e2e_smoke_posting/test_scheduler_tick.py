import pytest
import asyncio
from unittest.mock import AsyncMock

from src.core.settings import Settings
from src.posting.posting_manager import PostingManager, posting_manager
from src.app.scheduler.cron_manager import post_queue_tick


@pytest.mark.asyncio
async def test_scheduler_tick_respects_dry_run(monkeypatch):
    # enqueue válido na fila global (singleton)
    offer = {
        "title": "Oferta Awin",
        "price": 199.90,
        "url": "https://www.comfy.com.br/p/123",
        "store": "Awin",
        "affiliate_url": (
            "https://www.awin1.com/cread.php?awinmid=23377&awinaffid=2370719"
            "&ued=https%3A%2F%2Fwww.comfy.com.br%2Fp%2F123"
        ),
    }
    posting_manager.posting_queue.clear()
    assert posting_manager.enqueue(offer)

    # DRY_RUN on: dequeue_and_post should not call _post_to_telegram
    Settings.DRY_RUN = True
    called = {"n": 0}

    async def fake_post(*args, **kwargs):
        called["n"] += 1
        return True

    monkeypatch.setattr(PostingManager, "_post_to_telegram", AsyncMock(side_effect=fake_post))

    res1 = await post_queue_tick()
    assert res1 in ("posted", "empty")  # dry-run returns True; tick reports posted/empty
    assert called["n"] == 0, "_post_to_telegram should not be called in DRY_RUN"

    # enqueue again and DRY_RUN off
    assert posting_manager.enqueue(offer)
    Settings.DRY_RUN = False
    called["n"] = 0
    res2 = await post_queue_tick()
    assert res2 in ("posted", "empty")
    assert called["n"] == 1, "_post_to_telegram should be called once when DRY_RUN off"
