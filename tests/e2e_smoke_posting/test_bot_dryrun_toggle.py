import pytest
from src.core.settings import Settings
from src.telegram_bot.commands import dryrun_on, dryrun_off, status


def test_dryrun_toggle_via_commands(monkeypatch):
    # Admin setup
    Settings.TELEGRAM_ADMIN_IDS = "999"

    ok, msg = dryrun_on("999")
    assert ok and Settings.is_dry_run() is True
    assert "ativado" in msg.lower()

    report = status("999")
    assert "dry_run" in report.lower().replace("-","_") or "DRY_RUN" in report

    ok2, msg2 = dryrun_off("999")
    assert ok2 and Settings.is_dry_run() is False
    assert "desativado" in msg2.lower()

    # Non-admin
    ok3, msg3 = dryrun_on("123")
    assert ok3 is False and "perm" in msg3.lower()

