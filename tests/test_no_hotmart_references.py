"""
Teste para garantir que não há mais referências à Hotmart no código.
"""
import os
import re
import unittest
from pathlib import Path

class TestNoHotmartReferences(unittest.TestCase):
    """Testa a ausência de referências à Hotmart no código."""
    
    def setUp(self):
        """Configura os diretórios a serem verificados."""
        self.base_dir = Path(__file__).parent.parent
        self.exclude_dirs = [
            '.git',
            '__pycache__',
            '.pytest_cache',
            '.venv',
            'venv',
            'node_modules',
            '.mypy_cache',
            '.ruff_cache',
            '.github',
            '.vscode',
            '.idea',
            'dist',
            'build',
            'docs',  # Já processado separadamente
            'logs',
            'temp',
            'tmp'
        ]
        
        self.patterns = [
            r'hotmart',
            r'hotm\.art',
            r'pay\.hotmart\.com'
        ]
    
    def test_no_hotmart_references(self):
        """Verifica se existem referências à Hotmart no código."""
        found = []
        
        for root, dirs, files in os.walk(self.base_dir):
            # Pular diretórios excluídos
            dirs[:] = [d for d in dirs if d not in self.exclude_dirs]
            
            for file in files:
                # Verificar apenas arquivos de código e configuração
                if not file.endswith(('.py', '.md', '.txt', '.json', '.yaml', '.yml', '.conf', '.ini')):
                    continue
                
                file_path = Path(root) / file
                
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    for pattern in self.patterns:
                        if re.search(pattern, content, re.IGNORECASE):
                            found.append(str(file_path.relative_to(self.base_dir)))
                            break
                            
                except Exception as e:
                    print(f"⚠️ Erro ao processar {file_path}: {e}")
        
        # Se encontrou referências, falhar o teste
        self.assertEqual(len(found), 0, 
                        f"Foram encontradas referências à Hotmart nos seguintes arquivos:\n" + 
                        "\n".join(f"- {f}" for f in found))

if __name__ == "__main__":
    unittest.main()
