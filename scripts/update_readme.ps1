# Script PowerShell para atualizacao automatica do README.md

param(
    [switch]$Force,
    [switch]$Help
)

if ($Help) {
    Write-Host "Script de Atualizacao do README.md" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Uso:" -ForegroundColor Yellow
    Write-Host "  .\update_readme.ps1              # Verifica e atualiza se necessario"
    Write-Host "  .\update_readme.ps1 -Force       # Forca atualizacao"
    Write-Host "  .\update_readme.ps1 -Help        # Mostra esta ajuda"
    Write-Host ""
    exit 0
}

Write-Host "Verificando mudancas na estrutura do projeto..." -ForegroundColor Cyan

if ($Force) {
    Write-Host "Forcando atualizacao do README..." -ForegroundColor Yellow
    $cacheFile = ".readme_structure_cache.json"
    if (Test-Path $cacheFile) {
        Remove-Item $cacheFile
        Write-Host "Cache removido para forcar atualizacao" -ForegroundColor Yellow
    }
}

try {
    $result = python scripts/update_readme.py
    if ($LASTEXITCODE -eq 0) {
        Write-Host "README.md atualizado com sucesso!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Proximos passos:" -ForegroundColor Cyan
        Write-Host "  1. Verifique as mudancas: git diff README.md"
        Write-Host "  2. Adicione ao commit: git add README.md"
        Write-Host "  3. Faca o commit: git commit -m 'docs: Atualizar README'"
    } else {
        Write-Host "Erro ao atualizar README.md" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "Erro ao executar script Python: $_" -ForegroundColor Red
    exit 1
}

Write-Host "Script concluido!" -ForegroundColor Green
