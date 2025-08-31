#!/usr/bin/env python3
"""
Script de Análise de Implementação
Verifica o estado atual dos arquivos para implementação inteligente
"""

import os
from pathlib import Path

def analyze_files():
    """Analisa o estado atual dos arquivos de implementação"""
    
    files = [
        'src/affiliate/awin_api.py',
        'src/pipelines/ingest_awin_offers.py', 
        'src/scrapers/comunidades/promobit.py',
        'src/scrapers/comunidades/pelando.py',
        'src/scrapers/comunidades/meupc.py'
    ]
    
    print('=== ANÁLISE DE IMPLEMENTAÇÃO ===')
    print('Verificando arquivos para implementação inteligente...\n')
    
    results = []
    
    for file in files:
        if os.path.exists(file):
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    lines = len(f.readlines())
                    if lines > 50:
                        status = '✅ EXISTE'
                        action = 'Melhorar código existente'
                    elif lines > 0:
                        status = '⚠️ COMPLETAR'
                        action = 'Completar implementação'
                    else:
                        status = '❌ VAZIO'
                        action = 'Implementar do zero'
                    
                    print(f'{status}: {file} ({lines} linhas)')
                    print(f'   Ação: {action}')
                    results.append((file, lines, status))
                print()
            except Exception as e:
                print(f'❌ ERRO: {file} - {e}')
                results.append((file, 0, 'ERRO'))
        else:
            print(f'❌ CRIAR: {file} (não existe)')
            print(f'   Ação: Criar arquivo do zero')
            results.append((file, 0, 'CRIAR'))
            print()
    
    # Resumo
    print('=== RESUMO ===')
    total_files = len(files)
    existem = len([r for r in results if r[2] == '✅ EXISTE'])
    completar = len([r for r in results if r[2] == '⚠️ COMPLETAR'])
    criar = len([r for r in results if r[2] == '❌ CRIAR'])
    
    print(f'Total de arquivos: {total_files}')
    print(f'✅ Existem (>50 linhas): {existem}')
    print(f'⚠️ Completar (<50 linhas): {completar}')
    print(f'❌ Criar (não existem): {criar}')
    
    if existem > 0:
        print(f'\n📁 Arquivos para melhorar:')
        for file, lines, status in results:
            if status == '✅ EXISTE':
                print(f'   - {file} ({lines} linhas)')
    
    if completar > 0:
        print(f'\n🔧 Arquivos para completar:')
        for file, lines, status in results:
            if status == '⚠️ COMPLETAR':
                print(f'   - {file} ({lines} linhas)')
    
    if criar > 0:
        print(f'\n🆕 Arquivos para criar:')
        for file, lines, status in results:
            if status == '❌ CRIAR':
                print(f'   - {file}')

if __name__ == "__main__":
    analyze_files()
