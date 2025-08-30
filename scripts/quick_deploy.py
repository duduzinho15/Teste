#!/usr/bin/env python3
"""
⚡ DEPLOY RÁPIDO PARA GITHUB
============================

Script simplificado para deploy rápido quando implementações estiverem prontas.
Executa automaticamente: add, commit e push.

USO:
    python scripts/quick_deploy.py
    python scripts/quick_deploy.py "Mensagem customizada"
"""

import subprocess
import sys
from datetime import datetime
from pathlib import Path

def run_command(command: str) -> bool:
    """Executa um comando e retorna True se sucesso"""
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro: {e}")
        return False

def quick_deploy(message: str = None):
    """Executa deploy rápido"""
    print("⚡ DEPLOY RÁPIDO INICIADO")
    print("=" * 30)
    
    # 1. Verificar se há mudanças
    print("🔍 Verificando mudanças...")
    if not run_command("git status --porcelain"):
        print("❌ Erro ao verificar status")
        return False
    
    # 2. Adicionar todos os arquivos
    print("📁 Adicionando arquivos...")
    if not run_command("git add ."):
        print("❌ Erro ao adicionar arquivos")
        return False
    
    # 3. Criar commit
    if not message:
        timestamp = datetime.now().strftime("%H:%M:%S")
        message = f"🚀 Deploy automático - {timestamp}"
    
    print(f"💾 Commit: {message}")
    if not run_command(f'git commit -m "{message}"'):
        print("❌ Erro ao criar commit")
        return False
    
    # 4. Push para GitHub
    print("🚀 Enviando para GitHub...")
    if not run_command("git push origin master"):
        print("❌ Erro ao fazer push")
        return False
    
    print("\n✅ DEPLOY RÁPIDO CONCLUÍDO!")
    return True

if __name__ == "__main__":
    message = sys.argv[1] if len(sys.argv) > 1 else None
    success = quick_deploy(message)
    sys.exit(0 if success else 1)
