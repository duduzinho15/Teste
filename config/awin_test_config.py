#!/usr/bin/env python3
"""
Configuração de Teste para Sistema Awin
Arquivo temporário para testes locais
"""

import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurações Awin para teste
AWIN_TEST_CONFIG = {
    "publisher_id": "2370719",
    "oauth2_token": "f647c7b9-e8de-44a4-80fe-e9572ef35c10",
    "enabled": True
}

# Configurações dos anunciantes
AWIN_ADVERTISERS = {
    "comfy": {"mid": "23377", "name": "COMFY", "category": "eletronicos"},
    "trocafy": {"mid": "51277", "name": "Trocafy", "category": "informatica"},
    "lg": {"mid": "33061", "name": "LG", "category": "eletronicos"},
    "kabum": {"mid": "17729", "name": "Kabum", "category": "informatica"},
    "samsung": {"mid": "25539", "name": "Samsung", "category": "eletronicos"},
    "gigantec": {"mid": "106765", "name": "Gigantec", "category": "informatica"},
    "ninja": {"mid": "106765", "name": "Ninja", "category": "games"}
}

def get_awin_credentials():
    """Retorna credenciais Awin para teste"""
    return AWIN_TEST_CONFIG

def get_advertisers():
    """Retorna configuração dos anunciantes"""
    return AWIN_ADVERTISERS
