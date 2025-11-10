<#
Bootstrap do Hub Aura em um novo notebook (Windows + PowerShell).
Pré-requisitos (instale manualmente se ainda não tiver):
- Python 3.10+ em PATH
- Node.js 18+ (npm) em PATH
- PostgreSQL 15 (porta 5433) instalado (ou acesso a uma instância remota)

Uso:
  # na pasta raiz do projeto
  powershell -ExecutionPolicy Bypass -File .\scripts\bootstrap_new_machine.ps1 -ApiUrl "http://127.0.0.1:8002" -DbUrl "postgresql://postgres:senha@localhost:5433/hub_aura_db"

Após execução:
- venv criado e dependências Python instaladas
- dependências do frontend instaladas
- .env.local no frontend com VITE_API_URL
- DATABASE_URL configurado para a sessão atual
- Dicas para criar DB e rodar migrações/restaurar dump
#>
[CmdletBinding()]
param(
  [string]$ApiUrl = 'http://127.0.0.1:8002',
  [string]$DbUrl = 'postgresql://postgres@localhost:5433/hub_aura_db',
  [switch]$SkipFrontend,
  [switch]$SkipMigrations
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Test-Command($name) {
  $null -ne (Get-Command $name -ErrorAction SilentlyContinue)
}

Write-Host "[1/7] Verificando Python e Node..." -ForegroundColor Cyan
if (-not (Test-Command python)) { throw 'Python não encontrado no PATH. Instale Python 3.10+.' }
if (-not $SkipFrontend -and -not (Test-Command npm)) { throw 'Node/npm não encontrado no PATH. Instale Node 18+.' }

Write-Host "[2/7] Criando venv e instalando dependências Python..." -ForegroundColor Cyan
if (-not (Test-Path './venv')) {
  python -m venv venv
}
$venvPython = Join-Path (Resolve-Path 'venv') 'Scripts/python.exe'
& $venvPython -m pip install --upgrade pip
& $venvPython -m pip install -r requirements.txt

Write-Host "[3/7] Configurando DATABASE_URL na sessão atual..." -ForegroundColor Cyan
$env:DATABASE_URL = $DbUrl
Write-Host "DATABASE_URL=$env:DATABASE_URL" -ForegroundColor DarkGray

if (-not $SkipFrontend) {
  Write-Host "[4/7] Instalando dependências do frontend..." -ForegroundColor Cyan
  Push-Location 'hub-aura-frontend'
  if (Test-Path 'package-lock.json') {
    npm ci
  } else {
    npm install
  }
  # cria .env.local
  $envContent = "VITE_API_URL=$ApiUrl`n"
  Set-Content -Path '.env.local' -Value $envContent -Encoding UTF8
  Pop-Location
}

Write-Host "[5/7] Banco de Dados: verificação básica..." -ForegroundColor Cyan
$hasPsql = Test-Command psql
if ($hasPsql) {
  Write-Host "psql encontrado. Você pode restaurar um dump existente (pasta backups/) ou rodar migrações." -ForegroundColor Green
} else {
  Write-Host "psql NÃO encontrado. Instale PostgreSQL 15 e adicione psql ao PATH, ou use um DB remoto." -ForegroundColor Yellow
}

if (-not $SkipMigrations) {
  try {
    Write-Host "[6/7] Executando migrações Alembic (se configuradas)..." -ForegroundColor Cyan
    & $venvPython -m pip install alembic --quiet
    if (Test-Path '.\\alembic.ini' -and (Test-Path '.\\migrations')) {
      & $venvPython -m alembic upgrade head
    } else {
      Write-Host "Alembic não configurado ou pasta migrations ausente; pulando." -ForegroundColor Yellow
    }
  } catch {
    Write-Host "Falha ao rodar migrações: $($_.Exception.Message)" -ForegroundColor Yellow
  }
}

Write-Host "[7/7] Como iniciar" -ForegroundColor Cyan
Write-Host "- Backend (terminal 1):" -ForegroundColor Yellow
Write-Host "  .\\venv\\Scripts\\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8002" -ForegroundColor DarkGray
if (-not $SkipFrontend) {
  Write-Host "- Frontend (terminal 2):" -ForegroundColor Yellow
  Write-Host "  cd hub-aura-frontend; npm run dev" -ForegroundColor DarkGray
}

Write-Host "\nDicas:" -ForegroundColor Yellow
Write-Host "- Para usar outro DB: rode novamente com -DbUrl 'postgresql://usuario:senha@host:5433/hub_aura_db'"
Write-Host "- Se tiver um dump (.dump) em backups/, restaure com psql antes de iniciar o backend."