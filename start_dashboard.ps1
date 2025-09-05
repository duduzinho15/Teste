# Dashboard Windows do Garimpeiro Geek
# Script PowerShell para inicialização

Write-Host "🚀 Iniciando Dashboard Windows do Garimpeiro Geek..." -ForegroundColor Green
Write-Host ""
Write-Host "📱 Aplicativo Windows nativo" -ForegroundColor Cyan
Write-Host "🎮 Sistema de Recomendações de Ofertas" -ForegroundColor Yellow
Write-Host ""

# Verificar se Python está instalado
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python encontrado: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python não encontrado! Instale Python primeiro." -ForegroundColor Red
    Read-Host "Pressione Enter para sair"
    exit 1
}

# Verificar se o arquivo do dashboard existe
if (Test-Path "windows_dashboard.py") {
    Write-Host "✅ Dashboard encontrado" -ForegroundColor Green
} else {
    Write-Host "❌ Arquivo windows_dashboard.py não encontrado!" -ForegroundColor Red
    Read-Host "Pressione Enter para sair"
    exit 1
}

Write-Host ""
Write-Host "⏳ Iniciando aplicativo..." -ForegroundColor Yellow
Write-Host ""

# Iniciar o dashboard
try {
    python windows_dashboard_fixed.py
} catch {
    Write-Host "❌ Erro ao iniciar o dashboard: $_" -ForegroundColor Red
    Read-Host "Pressione Enter para sair"
}
