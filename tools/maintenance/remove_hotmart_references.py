"""
Script para remover referências à Hotmart de arquivos de documentação.
"""
import os
import re
from pathlib import Path

# Diretórios a serem processados
DOCS_DIR = Path(__file__).parent.parent / 'docs'

# Padrões para remoção
PATTERNS = [
    r'• Hotmart',
    r'Hotmart',
    r'hotmart\.com',
    r'hotm\.art',
    r'pay\.hotmart\.com'
]

def process_file(file_path):
    """Processa um único arquivo, removendo referências à Hotmart."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        original_content = content
        
        # Remover cada padrão
        for pattern in PATTERNS:
            content = re.sub(pattern, '', content, flags=re.IGNORECASE)
        
        # Remover linhas vazias extras
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        # Se o conteúdo mudou, salvar o arquivo
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(content)
            print(f"✅ Atualizado: {file_path}")
            return True
        return False
    except Exception as e:
        print(f"❌ Erro ao processar {file_path}: {e}")
        return False

def main():
    """Função principal que processa todos os arquivos de documentação."""
    updated_files = 0
    
    for root, _, files in os.walk(DOCS_DIR):
        for file in files:
            if file.endswith(('.md', '.txt', '.rst')):
                file_path = Path(root) / file
                if process_file(file_path):
                    updated_files += 1
    
    print(f"\n✅ Processamento concluído. {updated_files} arquivos foram atualizados.")

if __name__ == "__main__":
    main()
