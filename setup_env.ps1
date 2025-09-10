# Script para configurar o ambiente de desenvolvimento
# Uso: .\setup_env.ps1

# Verifica se o arquivo .env já existe
$envFile = ".env"
$envExample = ".env.example"

if (Test-Path $envFile) {
    Write-Host "O arquivo .env já existe. Deseja sobrescrever? (S/N)" -ForegroundColor Yellow
    $response = Read-Host ">"
    if ($response -ne "S" -and $response -ne "s") {
        Write-Host "Configuração cancelada pelo usuário." -ForegroundColor Yellow
        exit 0
    }
}

# Copia o arquivo de exemplo
Copy-Item -Path $envExample -Destination $envFile -Force

# Abre o arquivo para edição
Write-Host "Abrindo o arquivo .env para edição..." -ForegroundColor Green
Write-Host "Por favor, preencha as configurações necessárias e salve o arquivo." -ForegroundColor Yellow

# Tenta abrir no editor padrão do sistema
try {
    Start-Process $envFile
} catch {
    # Fallback para abrir no Notepad
    notepad $envFile
}

Write-Host "Configuração do ambiente concluída!" -ForegroundColor Green
