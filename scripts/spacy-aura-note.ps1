<#
spacy-aura-note.ps1

Guia detalhado de instalação e verificação do Hub Aura (Windows + PowerShell),
com detecção automática de versões instaladas e comandos de referência.
Este script NÃO altera o sistema; ele imprime um passo a passo completo e
as versões encontradas para facilitar a instalação.
#>
[CmdletBinding()]
param(
  [string]$ApiUrl = 'http://127.0.0.1:8002',
  [string]$DbUrl  = 'postgresql://postgres@localhost:5433/hub_aura_db'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'SilentlyContinue'

function Exists($cmd) { $null -ne (Get-Command $cmd -ErrorAction SilentlyContinue) }

$repo = Split-Path -Parent $MyInvocation.MyCommand.Path | Split-Path -Parent
$venvPython = Join-Path $repo 'venv\Scripts\python.exe'
$haveVenv = Test-Path $venvPython

# Coleta de versões Python/libs
$versions = [ordered]@{}
$versions['OS'] = (Get-CimInstance Win32_OperatingSystem | Select-Object -ExpandProperty Caption)
$versions['PowerShell'] = $PSVersionTable.PSVersion.ToString()

function PyExec([string]$code) {
  if ($haveVenv) { & $venvPython -c $code }
  elseif (Exists 'python') { & python -c $code }
}

$versions['Python'] = PyExec "import sys; print(sys.version.split()[0])"
$versions['pip']    = PyExec "import pip; print(pip.__version__)"
$versions['spaCy']  = PyExec "import spacy; print(spacy.__version__)"
$versions['FastAPI']= PyExec "import fastapi; print(fastapi.__version__)"
$versions['Uvicorn']= PyExec "import uvicorn; print(uvicorn.__version__)"
$versions['SQLAlchemy']= PyExec "import sqlalchemy; print(sqlalchemy.__version__)"
$versions['Pydantic']= PyExec "import pydantic; print(pydantic.__version__)"
$versions['psycopg2-binary']= PyExec "from importlib.metadata import version; print(version('psycopg2-binary'))"
$versions['sentence-transformers']= PyExec "import sentence_transformers; print(sentence_transformers.__version__)"
$versions['NumPy']  = PyExec "import numpy; print(numpy.__version__)"
$versions['Pandas'] = PyExec "import pandas; print(pandas.__version__)"
$versions['PyPDF2'] = PyExec "import PyPDF2; print(PyPDF2.__version__)"

# Modelo spaCy
$ptModel = ''
try {
  $ptModel = PyExec "import spacy; nlp=spacy.load('pt_core_news_lg'); print(nlp.meta.get('version','?'))"
} catch { $ptModel = '' }
if ([string]::IsNullOrWhiteSpace($ptModel)) { $ptModel = 'não encontrado' }
$versions['pt_core_news_lg'] = $ptModel

# Node/npm
Push-Location $repo
if (Exists 'node') { $versions['Node.js'] = (& node -v).Trim() }
if (Exists 'npm')  { $versions['npm']     = (& npm -v).Trim() }

# Frontend deps (se houver package.json)
$front = Join-Path $repo 'hub-aura-frontend'
if (Test-Path (Join-Path $front 'package.json') -and (Exists 'npm')) {
  Push-Location $front
  $npmList = & npm ls vite react react-dom @mui/material typescript --depth=0 2>$null
  Pop-Location
  if ($npmList) {
    if ($npmList -match 'vite@([\d\.]+)') { $versions['Vite'] = ($matches[0].Split('@')[-1]) }
    if ($npmList -match 'react@([\d\.]+)') { $versions['React'] = ($matches[0].Split('@')[-1]) }
    if ($npmList -match 'react-dom@([\d\.]+)') { $versions['React DOM'] = ($matches[0].Split('@')[-1]) }
    if ($npmList -match '@mui/material@([\d\.]+)') { $versions['@mui/material'] = ($matches[0].Split('@')[-1]) }
    if ($npmList -match 'typescript@([\d\.]+)') { $versions['TypeScript'] = ($matches[0].Split('@')[-1]) }
  }
}

# psql
if (Exists 'psql') {
  $versions['psql'] = (& psql --version).Trim()
} else {
  $versions['psql'] = 'não encontrado (instale PostgreSQL 15 Client)'
}

# Saída estruturada
Write-Host '===================== Hub Aura - Guia de Instalação (Windows) =====================' -ForegroundColor Cyan

Write-Host "Software e Versões Detectadas:" -ForegroundColor Yellow
$versions.GetEnumerator() | ForEach-Object { Write-Host ('- {0}: {1}' -f $_.Key, ($_.Value -replace "\r|\n"," ")) }

Write-Host "`nVersões mínimas recomendadas:" -ForegroundColor Yellow
Write-Host "- Python: 3.10+ (recomendado 3.12.x)"
Write-Host "- Node.js: 18+ (recomendado 20+; detectado: $($versions['Node.js']))"
Write-Host "- PostgreSQL: 15 (cliente psql recomendado)"
Write-Host "- spaCy: 3.5+ (detectado: $($versions['spaCy']))"
Write-Host "- pt_core_news_lg: 3.5+ (detectado: $($versions['pt_core_news_lg']))"

Write-Host "`n1) Pré-requisitos" -ForegroundColor Green
Write-Host "- Instale Python 3.12.x (Windows x64) e marque 'Add Python to PATH'"
Write-Host "- Instale Node.js (LTS) e npm"
Write-Host "- Instale PostgreSQL 15 (ou somente o Client Tools para psql/pg_dump)"
Write-Host "  > psql detectado: $($versions['psql'])"

Write-Host "`n2) Obter o projeto" -ForegroundColor Green
Write-Host "Se tiver o ZIP exportado:" -ForegroundColor DarkCyan
Write-Host "  - Extraia para uma pasta (ex.: C:\\Users\\Voce\\hub_aura)"
Write-Host "  - Abra a pasta no VS Code"
Write-Host "Se estiver clonando do Git, clone e abra no VS Code" -ForegroundColor DarkCyan

Write-Host "`n3) Backend - Ambiente virtual e dependências" -ForegroundColor Green
Write-Host "Abra um PowerShell na raiz do projeto e rode:" -ForegroundColor DarkCyan
Write-Host "```powershell"
Write-Host "python -m venv venv"
Write-Host ".\venv\Scripts\Activate.ps1"
Write-Host "python -m pip install --upgrade pip"
Write-Host "pip install -r requirements.txt"
Write-Host "```"

Write-Host "`n4) Baixar/Validar modelo spaCy (Português)" -ForegroundColor Green
Write-Host "O requirements já inclui o pt_core_news_lg. Para validar manualmente:" -ForegroundColor DarkCyan
Write-Host "```powershell"
Write-Host '.\venv\Scripts\python.exe -c "import spacy; nlp=spacy.load(''pt_core_news_lg''); print(''OK:'', nlp.meta.get(''version''))"'
Write-Host "```"

Write-Host "`n5) Banco de Dados (PostgreSQL)" -ForegroundColor Green
Write-Host "- Crie um banco chamado hub_aura_db na porta 5433 (ou ajuste a URL)"
Write-Host "- Defina a variável de ambiente da sessão (ajuste usuário/senha se houver):" -ForegroundColor DarkCyan
Write-Host "```powershell"
Write-Host "$env:DATABASE_URL = `"$DbUrl`""
Write-Host "```"
Write-Host "- Para aplicar migrações (se configuradas):" -ForegroundColor DarkCyan
Write-Host "```powershell"
Write-Host ".\venv\Scripts\python.exe -m alembic upgrade head"
Write-Host "```"
Write-Host "- Para restaurar um dump existente (pasta backups/):" -ForegroundColor DarkCyan
Write-Host "```powershell"
Write-Host "powershell -ExecutionPolicy Bypass -File .\backups\restore_v3.ps1"
Write-Host "```"

Write-Host "`n6) Frontend (Vite + React)" -ForegroundColor Green
Write-Host "- Crie o arquivo .env.local com a URL da API:" -ForegroundColor DarkCyan
Write-Host "```powershell"
Write-Host "Set-Content -Path .\hub-aura-frontend\.env.local -Value `"VITE_API_URL=$ApiUrl`n`" -Encoding UTF8"
Write-Host "```"
Write-Host "- Instale as dependências e inicie o dev server:" -ForegroundColor DarkCyan
Write-Host "```powershell"
Write-Host "cd hub-aura-frontend"
Write-Host "npm install"
Write-Host "npm run dev"
Write-Host "```"

Write-Host "`n7) Iniciar o Backend (visível)" -ForegroundColor Green
Write-Host "```powershell"
Write-Host ".\venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8002"
Write-Host "```"
Write-Host "Doc da API: http://127.0.0.1:8002/docs"

Write-Host "`n8) Verificações rápidas" -ForegroundColor Green
Write-Host "- spaCy carregando modelo PT: ver passo 4"
Write-Host "- API online: abra /docs ou faça uma requisição de teste"
Write-Host "- Frontend: acesse a URL que o Vite imprimir (geralmente http://127.0.0.1:5173)"

Write-Host "`n9) Problemas comuns e soluções" -ForegroundColor Green
Write-Host "- Erro de conexão ao banco: verifique a porta (5433), usuário/senha e DATABASE_URL"
Write-Host "- psql não encontrado: instale PostgreSQL 15 Client e adicione ao PATH"
Write-Host "- CORS no navegador: garanta que VITE_API_URL aponta para a URL do backend e reinicie o frontend"
Write-Host "- Modelo spaCy demora a carregar na primeira vez: é normal (cache inicial)"

Write-Host "`nFim do guia. Este script apenas imprime instruções e versões detectadas."