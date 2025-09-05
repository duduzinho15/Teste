#!/usr/bin/env python3
"""Teste simples do dashboard Flet"""

import sys
from pathlib import Path

# Adicionar o diretório raiz ao Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    print("🔍 Testando imports do dashboard...")
    
    # Testar imports básicos
    import flet as ft
    print("✅ Flet importado com sucesso")
    
    # Testar import do dashboard
    from apps.flet_dashboard.main import GarimpeiroDashboard
    print("✅ Dashboard importado com sucesso")
    
    # Testar criação do dashboard
    dashboard = GarimpeiroDashboard()
    print("✅ Dashboard criado com sucesso")
    
    print("\n🎉 Todos os testes passaram! O dashboard pode ser iniciado.")
    
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
