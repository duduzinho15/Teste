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
from typing import Optional

def run_command(command: str) -> bool:
    """Executa um comando e retorna True se sucesso"""
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro: {e}")
        return False

def get_clean_files() -> bool:
    """Obtém lista de arquivos limpos para adicionar"""
    try:
        # Adiciona apenas arquivos importantes e limpos
        files_to_add = [
            "src/",
            "tests/", 
            "docs/",
            "scripts/",
            "README.md",
            "pytest.ini",
            ".env.example"
        ]
        
        for file_path in files_to_add:
            if Path(file_path).exists():
                if not run_command(f"git add {file_path}"):
                    print(f"⚠️  Aviso: Não foi possível adicionar {file_path}")
        
        return True
    except Exception as e:
        print(f"❌ Erro ao adicionar arquivos: {e}")
        return False

def quick_deploy(message: Optional[str] = None) -> bool:
    """Executa deploy rápido"""
    print("⚡ DEPLOY RÁPIDO INICIADO")
    print("=" * 30)
    
    # 1. Verificar se há mudanças
    print("🔍 Verificando mudanças...")
    if not run_command("git status --porcelain"):
        print("❌ Erro ao verificar status")
        return False
    
    # 2. Adicionar arquivos limpos
    print("📁 Adicionando arquivos...")
    if not get_clean_files():
        print("❌ Erro ao adicionar arquivos")
        return False
    
    # 3. Verificar se há algo para commitar
    print("🔍 Verificando se há mudanças para commitar...")
    if not run_command("git diff --cached --quiet"):
        print("✅ Há mudanças para commitar")
    else:
        print("⚠️  Nenhuma mudança para commitar")
        return True
    
    # 4. Criar commit
    if not message:
        timestamp = datetime.now().strftime("%H:%M:%S")
        message = f"🚀 Deploy automático - {timestamp}"
    
    print(f"💾 Commit: {message}")
    if not run_command(f'git commit -m "{message}"'):
        print("❌ Erro ao criar commit")
        return False
    
    # 5. Push para GitHub
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
