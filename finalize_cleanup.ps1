# Finalize Hotmart Removal Script
# This script helps finalize the removal of Hotmart/PerfectPay/Kiwify from the project

# Set error action preference
$ErrorActionPreference = "Stop"

# Project root directory
$projectRoot = $PSScriptRoot
$branchName = "chore/remove-digital-affiliates"

# Function to execute a command and check for errors
function Invoke-SafeCommand {
    param (
        [string]$command,
        [string]$errorMessage = "Command failed: $command"
    )
    
    Write-Host "`n> $command" -ForegroundColor Cyan
    try {
        Invoke-Expression $command
        if ($LASTEXITCODE -ne 0 -and $LASTEXITCODE -ne $null) {
            throw "Command failed with exit code $LASTEXITCODE"
        }
    }
    catch {
        Write-Host "ERROR: $errorMessage" -ForegroundColor Red
        Write-Host $_.Exception.Message -ForegroundColor Red
        exit 1
    }
}

# 1. Setup virtual environment and install dependencies
Write-Host "`n=== Setting up environment ===" -ForegroundColor Green
if (-not (Test-Path "$projectRoot\.venv")) {
    Invoke-SafeCommand "python -m venv .venv" "Failed to create virtual environment"
}

# Activate virtual environment
$activatePath = "$projectRoot\.venv\Scripts\Activate.ps1"
if (Test-Path $activatePath) {
    . $activatePath
    
    # Upgrade pip
    Invoke-SafeCommand "python -m pip install --upgrade pip" "Failed to upgrade pip"
    
    # Install dependencies
    $requirementsFiles = @(
        "$projectRoot\requirements.txt",
        "$projectRoot\apps\flet_dashboard\requirements.txt"
    )
    
    foreach ($reqFile in $requirementsFiles) {
        if (Test-Path $reqFile) {
            Invoke-SafeCommand "pip install -r \"$reqFile\"" "Failed to install dependencies from $reqFile"
        }
    }
    
    # Install test dependencies
    Invoke-SafeCommand "pip install pytest ruff" "Failed to install test dependencies"
}
else {
    Write-Host "Virtual environment activation script not found at $activatePath" -ForegroundColor Yellow
    Write-Host "Please activate the virtual environment manually and run the checks." -ForegroundColor Yellow
}

# 2. Run linters and tests
Write-Host "`n=== Running code checks ===" -ForegroundColor Green
Invoke-SafeCommand "ruff check src" "Linting failed"
Invoke-SafeCommand "pytest -q" "Tests failed"

# 3. Check for remaining references
Write-Host "`n=== Checking for remaining references ===" -ForegroundColor Green
$terms = @("hotmart", "perfectpay", "kiwify")
$found = $false

foreach ($term in $terms) {
    $result = git grep -nIi $term
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Found references to $term :" -ForegroundColor Red
        $result
        $found = $true
    }
    else {
        Write-Host "No references found to $term" -ForegroundColor Green
    }
}

if ($found) {
    Write-Host "`nWARNING: Found references to removed terms. Please review and remove them." -ForegroundColor Red
    exit 1
}

# 4. Push changes to GitHub
Write-Host "`n=== Pushing changes to GitHub ===" -ForegroundColor Green

# Check if we're on the right branch
$currentBranch = git rev-parse --abbrev-ref HEAD
if ($currentBranch -ne $branchName) {
    Write-Host "Not on branch $branchName. Current branch: $currentBranch" -ForegroundColor Yellow
    $switchBranch = Read-Host "Switch to branch $branchName? (y/n)"
    if ($switchBranch -eq 'y') {
        Invoke-SafeCommand "git checkout $branchName" "Failed to switch to branch $branchName"
    }
    else {
        Write-Host "Please switch to branch $branchName and run the script again." -ForegroundColor Yellow
        exit 1
    }
}

# Add all changes
Invoke-SafeCommand "git add ." "Failed to add changes to git"

# Commit if there are changes
$status = git status --porcelain
if ($status) {
    $commitMessage = "chore: remove Hotmart/PerfectPay/Kiwify; update docs, dashboard and tests"
    Invoke-SafeCommand "git commit -m \"$commitMessage\"" "Failed to commit changes"
}

# Push to remote
Invoke-SafeCommand "git push -u origin $branchName" "Failed to push changes to GitHub"

# 5. Generate PR link
$repoUrl = git config --get remote.origin.url -replace '\.git$', ''
$prUrl = "$repoUrl/compare/main...$branchName?expand=1"

Write-Host "`n=== Cleanup Complete ===" -ForegroundColor Green
Write-Host "✅ All checks passed successfully!" -ForegroundColor Green
Write-Host "✅ Changes pushed to branch: $branchName" -ForegroundColor Green
Write-Host "`nNext steps:" -ForegroundColor Cyan
Write-Host "1. Open PR: $prUrl"
Write-Host "2. Use the PR template from the original message"
Write-Host "3. After merge, run:"
Write-Host "   git checkout main"
Write-Host "   git pull"
Write-Host "   git branch -d $branchName"
Write-Host "   git push origin --delete $branchName"
