from pathlib import Path
import sys

# Adiciona o diretório raiz ao path para importar os módulos
sys.path.append(str(Path(__file__).parent.parent))

from src.core.affiliate_integration import AffiliateNetwork

def test_networks_list():
    """Verifica se a lista de redes de afiliados contém apenas as redes suportadas."""
    redes_esperadas = {
        "AMAZON": "amazon",
        "AWIN": "awin",
        "RAKUTEN": "rakuten",
        "SHOPEE": "shopee",
        "ALIEXPRESS": "aliexpress",
        "MERCADO_LIVRE": "mercado_livre",
        "MAGAZINE_LUIZA": "magazine_luiza"
    }
    
    # Verifica se todas as redes esperadas existem
    for nome, valor in redes_esperadas.items():
        assert hasattr(AffiliateNetwork, nome), f"Rede {nome} não encontrada no enum AffiliateNetwork"
        assert getattr(AffiliateNetwork, nome) == valor, f"Valor da rede {nome} incorreto"
    
    # Verifica se não há redes extras
    redes_atuais = [attr for attr in dir(AffiliateNetwork) 
                   if not attr.startswith('_') and attr.isupper()]
    assert len(redes_atuais) == len(redes_esperadas), \
        f"Número incorreto de redes. Esperado: {len(redes_esperadas)}, Encontrado: {len(redes_atuais)}"
