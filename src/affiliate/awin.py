"""
Conversor de afiliados Awin para Garimpeiro Geek.

Implementa geração de deeplinks Awin com validações rígidas
baseadas nos exemplos dos arquivos de referência.
"""

import logging
import os
from typing import Dict, List, Optional, Tuple
from urllib.parse import quote, urlparse

logger = logging.getLogger(__name__)


def get_setting(key: str, default: str = "") -> str:
    """Função simples para obter configurações do .env"""
    return os.getenv(key, default)


logger = logging.getLogger(__name__)

# MIDs permitidos por loja (baseados nos exemplos)
ALLOWED_MIDS = {
    "comfy": 23377,
    "trocafy": 51277,
    "lg": 33061,
    "kabum": 17729,
    "ninja": 106765,
    "samsung": 25539,
    "gigantec": 115463,
}

# AFFIDs permitidos (configuráveis via .env)
DEFAULT_AFFIDS = [2370719, 2510157]


def get_allowed_affids() -> List[int]:
    """Retorna lista de AFFIDs permitidos do .env"""
    affids_str = get_setting("AWIN_AFFIDS", "2370719,2510157")
    try:
        return [int(aid.strip()) for aid in affids_str.split(",")]
    except (ValueError, AttributeError):
        logger.warning(f"AFFIDs inválidos no .env: {affids_str}, usando padrão")
        return DEFAULT_AFFIDS


def get_mid_for_store(store_name: str) -> Optional[int]:
    """Retorna MID para uma loja específica"""
    store_lower = store_name.lower()

    # Mapeamento direto
    if store_lower in ALLOWED_MIDS:
        return ALLOWED_MIDS[store_lower]

    # Mapeamento por domínio
    store_domain_map = {
        "comfy.com.br": 23377,
        "trocafy.com.br": 51277,
        "lg.com": 33061,
        "lg.com.br": 33061,
        "kabum.com.br": 17729,
        "ninja.com.br": 106765,
        "samsung.com": 25539,
        "samsung.com.br": 25539,
        "gigantec.com.br": 115463,
    }

    for domain, mid in store_domain_map.items():
        if domain in store_lower:
            return mid

    return None


def validate_store_domain(url: str) -> Tuple[bool, str, str]:
    """
    Valida se o domínio da loja é permitido para Awin.

    Args:
        url: URL da loja para validar

    Returns:
        Tuple (is_valid, store_name, error_message)
    """
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()

        # Domínios permitidos
        allowed_domains = [
            "comfy.com.br",
            "trocafy.com.br",
            "lg.com",
            "lg.com.br",
            "kabum.com.br",
            "ninja.com.br",
            "samsung.com",
            "samsung.com.br",
            "gigantec.com.br",
        ]

        for allowed_domain in allowed_domains:
            if allowed_domain in domain:
                # Extrair nome da loja
                store_name = allowed_domain.split(".")[0]
                return True, store_name, ""

        # Log detalhado para debugging
        logger.warning(f"Domínio não permitido para Awin: {domain}")
        logger.info(f"Domínios permitidos: {allowed_domains}")

        return (
            False,
            "unknown",
            f"Domínio não permitido: {domain}. Domínios permitidos: {', '.join(allowed_domains)}",
        )

    except Exception as e:
        logger.error(f"Erro ao validar domínio: {e}")
        return False, "unknown", f"Erro ao validar domínio: {str(e)}"


def build_awin_deeplink(
    url: str, awinmid: Optional[int] = None, awinaffid: Optional[int] = None
) -> Tuple[bool, str, str]:
    """
    Constrói deeplink Awin válido baseado nos exemplos.

    Args:
        url: URL da loja para converter
        awinmid: MID específico (opcional, será detectado automaticamente)
        awinaffid: AFFID específico (opcional, será usado o primeiro do .env)

    Returns:
        Tuple (success, deeplink, error_message)
    """
    try:
        # 1. Validar domínio da loja
        is_valid_domain, store_name, domain_error = validate_store_domain(url)
        if not is_valid_domain:
            return False, "", domain_error

        # 2. Determinar MID
        if awinmid is None:
            awinmid = get_mid_for_store(store_name)
            if awinmid is None:
                return False, "", f"MID não encontrado para loja: {store_name}"

        # Validar se MID está na lista permitida
        if awinmid not in ALLOWED_MIDS.values():
            return (
                False,
                "",
                f"MID {awinmid} não está na lista permitida: {list(ALLOWED_MIDS.values())}",
            )

        # 3. Determinar AFFID
        if awinaffid is None:
            allowed_affids = get_allowed_affids()
            if not allowed_affids:
                return False, "", "Nenhum AFFID configurado no .env"
            awinaffid = allowed_affids[0]

        # Validar se AFFID está na lista permitida
        if awinaffid not in get_allowed_affids():
            return False, "", f"AFFID {awinaffid} não está na lista permitida"

        # 4. URL-encode o parâmetro UED
        ued_encoded = quote(url, safe="")

        # 5. Construir deeplink no formato exato dos exemplos
        deeplink = f"https://www.awin1.com/cread.php?awinmid={awinmid}&awinaffid={awinaffid}&ued={ued_encoded}"

        logger.info(
            f"Deeplink Awin gerado: {store_name} -> MID:{awinmid}, AFFID:{awinaffid}"
        )
        return True, deeplink, ""

    except Exception as e:
        error_msg = f"Erro ao gerar deeplink Awin: {e}"
        logger.error(error_msg)
        return False, "", error_msg


def validate_awin_deeplink(deeplink: str) -> Tuple[bool, str]:
    """
    Valida se um deeplink Awin está no formato correto.

    Args:
        deeplink: URL do deeplink para validar

    Returns:
        Tuple (is_valid, error_message)
    """
    try:
        parsed = urlparse(deeplink)

        # Validar domínio
        if parsed.netloc not in ["www.awin1.com", "awin1.com"]:
            return False, "Domínio inválido para Awin"

        # Validar path
        if parsed.path != "/cread.php":
            return False, "Path inválido para Awin"

        # Validar parâmetros obrigatórios
        from urllib.parse import parse_qs

        query_params = parse_qs(parsed.query)

        required_params = ["awinmid", "awinaffid", "ued"]
        for param in required_params:
            if param not in query_params:
                return False, f"Parâmetro obrigatório ausente: {param}"

        # Validar MID
        try:
            mid = int(query_params["awinmid"][0])
            if mid not in ALLOWED_MIDS.values():
                return False, f"MID inválido: {mid}"
        except (ValueError, IndexError):
            return False, "MID deve ser um número inteiro"

        # Validar AFFID
        try:
            affid = int(query_params["awinaffid"][0])
            if affid not in get_allowed_affids():
                return False, f"AFFID inválido: {affid}"
        except (ValueError, IndexError):
            return False, "AFFID deve ser um número inteiro"

        # Validar UED
        ued = query_params["ued"][0]
        if not ued.startswith("http"):
            return False, "Parâmetro UED deve ser uma URL válida"

        return True, ""

    except Exception as e:
        return False, f"Erro ao validar deeplink: {e}"


def get_awin_config_summary() -> Dict:
    """Retorna resumo da configuração Awin para debug"""
    return {
        "allowed_mids": ALLOWED_MIDS,
        "allowed_affids": get_allowed_affids(),
        "store_mapping": dict(ALLOWED_MIDS.items()),
    }


# Funções de conveniência para uso direto
def convert_to_awin(url: str, store: Optional[str] = None) -> str:
    """
    Função de conveniência para converter URL para deeplink Awin.

    Args:
        url: URL da loja
        store: Nome da loja (opcional)

    Returns:
        Deeplink Awin ou string vazia se falhar
    """
    success, deeplink, error = build_awin_deeplink(url)
    if not success:
        logger.error(f"Falha ao converter para Awin: {error}")
        return ""
    return deeplink


def is_valid_awin_url(url: str) -> bool:
    """Verifica se uma URL é válida para conversão Awin"""
    is_valid, _, _ = validate_store_domain(url)
    return is_valid


# Teste dos exemplos do arquivo de referência
if __name__ == "__main__":
    print("🧪 TESTANDO CONVERSOR AWIN COM EXEMPLOS DO ARQUIVO")
    print("=" * 60)

    # Exemplos do arquivo "Informações base de geração de link.txt"
    test_cases = [
        ("https://www.comfy.com.br/", "Comfy"),
        ("https://www.trocafy.com.br/", "Trocafy"),
        ("https://www.lg.com/br/", "LG"),
        ("https://www.kabum.com.br/", "KaBuM"),
        (
            "https://www.comfy.com.br/cadeira-de-escritorio-comfy-ergopro-cinza-tela-mesh-cinza-braco-ajustavel-e-relax-avancado.html",
            "Comfy",
        ),
        (
            "https://www.trocafy.com.br/smartphone-samsung-galaxy-s22-256gb-verde-5g-8gb-ram-tela-6-1-camera-tripla-de-50mp-10mp-12mp-frontal-10mp-sou-como-novo-4607/p",
            "Trocafy",
        ),
    ]

    for url, expected_store in test_cases:
        print(f"\n🔍 Testando: {expected_store}")
        print(f"   URL: {url}")

        success, deeplink, error = build_awin_deeplink(url)

        if success:
            print(f"   ✅ SUCESSO: {deeplink[:80]}...")

            # Validar o deeplink gerado
            is_valid, validation_error = validate_awin_deeplink(deeplink)
            if is_valid:
                print("   ✅ VALIDAÇÃO: Deeplink válido")
            else:
                print(f"   ❌ VALIDAÇÃO: {validation_error}")
        else:
            print(f"   ❌ FALHA: {error}")

    print("\n📊 CONFIGURAÇÃO AWIN:")
    config = get_awin_config_summary()
    print(f"   MIDs permitidos: {config['allowed_mids']}")
    print(f"   AFFIDs permitidos: {config['allowed_affids']}")
