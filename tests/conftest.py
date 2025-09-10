"""Global test configuration and fixtures."""
import pytest
import socket
import urllib.request
from unittest.mock import patch

# Bloqueia todas as requisições de rede
def block_network():
    """Block network access for tests."""
    def guarded(*args, **kwargs):
        pytest.fail("Network access not allowed during testing")
    
    # Patch de bibliotecas comuns de rede
    patches = [
        patch('socket.socket', side_effect=Exception("Network access blocked")),
        patch('urllib.request.urlopen', side_effect=Exception("Network access blocked")),
        patch('aiohttp.ClientSession', side_effect=Exception("Network access blocked")),
        patch('requests.get', side_effect=Exception("Network access blocked")),
        patch('requests.post', side_effect=Exception("Network access blocked")),
    ]
    # Playwright pode não estar instalado no ambiente de testes
    try:
        import importlib
        importlib.import_module('playwright')
        patches.append(
            patch('playwright.async_api.Playwright', side_effect=Exception("Playwright access blocked"))
        )
    except Exception:
        pass
    
    return patches

@pytest.fixture(autouse=True)
def no_network_access():
    """Fixture to block network access in all tests."""
    patches = block_network()
    for p in patches:
        p.start()
    
    yield
    
    # Limpeza após o teste
    for p in patches:
        p.stop()
