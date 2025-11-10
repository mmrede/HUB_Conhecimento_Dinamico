<#
Exporta o projeto Hub Aura para um ZIP portátil.
- Exclui: .git, .venv/venv, node_modules, __pycache__, *.pytest_cache, .mypy_cache, backups/*.dump
- Mantém: código-fonte, requirements.txt, frontend (sem node_modules), scripts, docs, migrations, dumps .zip existentes
Saída: ..\hub_aura_export_YYYYMMDD_HHMM.zip
#>
[CmdletBinding()]
param(
    [switch]$IncludeBackupsZip
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# Caminhos
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
# $root = <repo>/scripts ; repo é o pai
$repo = Resolve-Path (Join-Path $root '..') | Select-Object -ExpandProperty Path
Set-Location $repo

# Timestamp
$ts = Get-Date -Format 'yyyyMMdd_HHmm'
$zipName = "hub_aura_export_$ts.zip"
$outDir = Resolve-Path (Join-Path $repo '..') | Select-Object -ExpandProperty Path
$outZip = Join-Path $outDir $zipName

Write-Host "Gerando pacote: $outZip" -ForegroundColor Cyan

# Lista de exclusões
$excludeDirs = @(
    '.git', '.github', '.venv', 'venv', '.idea', '.vscode',
    'hub-aura-frontend/node_modules',
    '**/__pycache__',
    '.pytest_cache', '.mypy_cache'
)
$excludeFilesPatterns = @(
    '*.pyc', '*.pyo', '*.pyd',
    'Thumbs.db', '.DS_Store'
)

# Excluir dumps .dump pesados por padrão
$excludeBackups = @('backups/*.dump')
if ($IncludeBackupsZip) {
    $excludeBackups = @()  # mantém tudo se usuário pedir explicitamente
}

# Coleta de arquivos
$all = Get-ChildItem -Recurse -File | Where-Object {
    $p = $_.FullName.Replace($repo + [IO.Path]::DirectorySeparatorChar, '')
    # Excluir diretórios
    -not ($excludeDirs | ForEach-Object { $p -like (Join-Path $_ '*') }) -and
    # Excluir padrões de arquivos
    -not ($excludeFilesPatterns | ForEach-Object { $_ -and ($_.Length -gt 0) -and ($p -like $_) }) -and
    # Excluir dumps pesados
    -not ($excludeBackups | ForEach-Object { $p -like $_ })
}

# Cria zip
if (Test-Path $outZip) { Remove-Item $outZip -Force }
# Carrega as assemblies necessárias para zip
Add-Type -AssemblyName System.IO.Compression
Add-Type -AssemblyName System.IO.Compression.FileSystem
$zip = [System.IO.Compression.ZipFile]::Open($outZip, [System.IO.Compression.ZipArchiveMode]::Create)
try {
    foreach ($f in $all) {
        $rel = $f.FullName.Substring($repo.Length).TrimStart([IO.Path]::DirectorySeparatorChar)
        [System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile($zip, $f.FullName, $rel, [System.IO.Compression.CompressionLevel]::Optimal) | Out-Null
    }
}
finally {
    $zip.Dispose()
}

Write-Host "Pacote criado com sucesso:" -ForegroundColor Green
Write-Host "  $outZip"

# Dicas
Write-Host "\nComo usar no outro notebook:" -ForegroundColor Yellow
Write-Host "1) Copie o ZIP para o outro computador e extraia."
Write-Host "2) Abra no VS Code."
Write-Host "3) Execute scripts/bootstrap_new_machine.ps1 (PowerShell) para configurar ambiente."