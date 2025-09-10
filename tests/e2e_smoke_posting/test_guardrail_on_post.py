import asyncio
import pytest

from src.posting.posting_manager import PostingManager


@pytest.mark.asyncio
async def test_enqueue_rejects_invalid_awin():
    pm = PostingManager()
    invalid_offer = {
        "title": "Cadeira Comfy",
        "price": 999.90,
        "url": "https://www.comfy.com.br/p/123",
        "store": "Awin",
        # missing ued
        "affiliate_url": "https://www.awin1.com/cread.php?awinmid=23377&awinaffid=2370719",
    }

    ok = pm.enqueue(invalid_offer)
    assert not ok
    assert pm.get_queue_status()["queue_size"] == 0


@pytest.mark.asyncio
async def test_enqueue_and_dequeue_dry_run_valid_awin():
    pm = PostingManager()
    valid_offer = {
        "title": "Cadeira Comfy",
        "price": 999.90,
        "url": "https://www.comfy.com.br/p/123",
        "store": "Awin",
        "affiliate_url": (
            "https://www.awin1.com/cread.php?awinmid=23377&awinaffid=2370719"
            "&ued=https%3A%2F%2Fwww.comfy.com.br%2Fp%2F123"
        ),
    }

    ok = pm.enqueue(valid_offer)
    assert ok

    # DRY_RUN default is True in Settings; just run dequeue
    success = await pm.dequeue_and_post()
    assert success, "dry run should logically succeed without posting"
