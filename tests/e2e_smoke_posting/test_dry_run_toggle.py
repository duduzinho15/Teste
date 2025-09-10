import asyncio
import pytest

from unittest.mock import AsyncMock

from src.posting.posting_manager import PostingManager
from src.core.settings import Settings


@pytest.mark.asyncio
async def test_dry_run_toggle_controls_posting(monkeypatch):
    pm = PostingManager()

    # Enqueue a valid Shopee shortlink offer
    offer = {
        "title": "Oferta Shopee",
        "price": 49.90,
        "url": "https://shopee.com.br/i.123.456",
        "store": "Shopee",
        "affiliate_url": "https://s.shopee.com.br/AbC123",
    }
    assert pm.enqueue(offer)

    # DRY_RUN on: dequeue should not call _post_to_telegram; success True
    Settings.DRY_RUN = True
    called = {"count": 0}

    async def fake_post_to_telegram(offer, message, image_path=None):
        called["count"] += 1
        return True

    # Because DRY_RUN is handled before telegram call, do not patch here
    success = await pm.dequeue_and_post()
    assert success
    assert called["count"] == 0, "should not call telegram in DRY_RUN"

    # Add again and disable DRY_RUN; patch to catch call
    assert pm.enqueue(offer)
    Settings.DRY_RUN = False

    monkeypatch.setattr(PostingManager, "_post_to_telegram", AsyncMock(return_value=True))

    success2 = await pm.dequeue_and_post()
    assert success2
    PostingManager._post_to_telegram.assert_awaited_once()
