# Script de Limpeza do Projeto Hub Aura
# Remove arquivos obsoletos, duplicados e temporários
# Data: 30/10/2025

Write-Host "🧹 LIMPEZA DO PROJETO HUB AURA" -ForegroundColor Cyan
Write-Host "================================`n" -ForegroundColor Cyan

$removedFiles = @()
$totalSize = 0

# Função para remover item e registrar
function Remove-ItemSafe {
    param(
        [string]$Path,
        [string]$Description
    )
    
    if (Test-Path $Path) {
        $size = (Get-ChildItem -Path $Path -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
        if ($null -eq $size) { $size = 0 }
        
        Remove-Item -Path $Path -Recurse -Force -ErrorAction SilentlyContinue
        
        if (-not (Test-Path $Path)) {
            $sizeMB = [math]::Round($size / 1MB, 2)
            Write-Host "✅ Removido: $Description ($sizeMB MB)" -ForegroundColor Green
            $script:removedFiles += "$Description ($sizeMB MB)"
            $script:totalSize += $size
        } else {
            Write-Host "⚠️  Falha ao remover: $Description" -ForegroundColor Yellow
        }
    } else {
        Write-Host "⏭️  Não encontrado (já removido): $Description" -ForegroundColor Gray
    }
}

Write-Host "`n📁 REMOVENDO VIRTUAL ENVIRONMENTS DUPLICADOS..." -ForegroundColor Yellow
Remove-ItemSafe -Path "C:\Users\manoe\hub_aura\.venv-1" -Description ".venv-1 (venv duplicado)"

Write-Host "`n📁 REMOVENDO BACKUPS SQL OBSOLETOS DA RAIZ..." -ForegroundColor Yellow
Remove-ItemSafe -Path "C:\Users\manoe\hub_aura\hub_aura_backup.sql" -Description "hub_aura_backup.sql"
Remove-ItemSafe -Path "C:\Users\manoe\hub_aura\hub_aura_backup_clean.sql" -Description "hub_aura_backup_clean.sql"
Remove-ItemSafe -Path "C:\Users\manoe\hub_aura\hub_aura_backup_utf8.sql" -Description "hub_aura_backup_utf8.sql"

Write-Host "`n📁 REMOVENDO SCRIPTS DE DIAGNÓSTICO OBSOLETOS..." -ForegroundColor Yellow
Remove-ItemSafe -Path "C:\Users\manoe\hub_aura\check_index.py" -Description "check_index.py"
Remove-ItemSafe -Path "C:\Users\manoe\hub_aura\check_indexes_verbose.py" -Description "check_indexes_verbose.py"
Remove-ItemSafe -Path "C:\Users\manoe\hub_aura\check_location.py" -Description "check_location.py"
Remove-ItemSafe -Path "C:\Users\manoe\hub_aura\check_tables.py" -Description "check_tables.py"
Remove-ItemSafe -Path "C:\Users\manoe\hub_aura\create_index_test.py" -Description "create_index_test.py"
Remove-ItemSafe -Path "C:\Users\manoe\hub_aura\list_tables.py" -Description "list_tables.py"
Remove-ItemSafe -Path "C:\Users\manoe\hub_aura\print_dataframe.py" -Description "print_dataframe.py"
Remove-ItemSafe -Path "C:\Users\manoe\hub_aura\seed_test.py" -Description "seed_test.py"
Remove-ItemSafe -Path "C:\Users\manoe\hub_aura\show_db.py" -Description "show_db.py"
Remove-ItemSafe -Path "C:\Users\manoe\hub_aura\test_vector_search.py" -Description "test_vector_search.py"
Remove-ItemSafe -Path "C:\Users\manoe\hub_aura\run_migration.py" -Description "run_migration.py"

Write-Host "`n📁 REMOVENDO ARQUIVOS PGVECTOR (NÃO IMPLEMENTADO)..." -ForegroundColor Yellow
Remove-ItemSafe -Path "C:\Users\manoe\hub_aura\pgvector" -Description "pgvector/"
Remove-ItemSafe -Path "C:\Users\manoe\hub_aura\pgvector-0.5.1" -Description "pgvector-0.5.1/"
Remove-ItemSafe -Path "C:\Users\manoe\hub_aura\pgvector.zip" -Description "pgvector.zip"
Remove-ItemSafe -Path "C:\Users\manoe\hub_aura\install_pgvector_pg15.ps1" -Description "install_pgvector_pg15.ps1"
Remove-ItemSafe -Path "C:\Users\manoe\hub_aura\setup_pgvector.ipynb" -Description "setup_pgvector.ipynb"
Remove-ItemSafe -Path "C:\Users\manoe\hub_aura\scripts\setup_pgvector.py" -Description "scripts/setup_pgvector.py"

Write-Host "`n📁 REMOVENDO ARQUIVOS DE PROCESSAMENTO OBSOLETOS..." -ForegroundColor Yellow
Remove-ItemSafe -Path "C:\Users\manoe\hub_aura\processador_ia.py" -Description "processador_ia.py"
Remove-ItemSafe -Path "C:\Users\manoe\hub_aura\carregar_dados" -Description "carregar_dados"

Write-Host "`n📁 REMOVENDO DOCUMENTAÇÃO DUPLICADA/INTERMEDIÁRIA..." -ForegroundColor Yellow
Remove-ItemSafe -Path "C:\Users\manoe\hub_aura\IMPLEMENTATION_SUMMARY.md" -Description "IMPLEMENTATION_SUMMARY.md"
Remove-ItemSafe -Path "C:\Users\manoe\hub_aura\FRONTEND_UPDATE.md" -Description "FRONTEND_UPDATE.md"
Remove-ItemSafe -Path "C:\Users\manoe\hub_aura\PLANO_TRABALHO_IMPLEMENTATION.md" -Description "PLANO_TRABALHO_IMPLEMENTATION.md"
Remove-ItemSafe -Path "C:\Users\manoe\hub_aura\SEMANTIC_SEARCH_ANALYSIS.html" -Description "SEMANTIC_SEARCH_ANALYSIS.html"
Remove-ItemSafe -Path "C:\Users\manoe\hub_aura\SEMANTIC_SEARCH_ANALYSIS.md" -Description "SEMANTIC_SEARCH_ANALYSIS.md"

Write-Host "`n📁 REMOVENDO SCRIPTS AUXILIARES OBSOLETOS..." -ForegroundColor Yellow
Remove-ItemSafe -Path "C:\Users\manoe\hub_aura\setup_docker.ps1" -Description "setup_docker.ps1"
Remove-ItemSafe -Path "C:\Users\manoe\hub_aura\docker-compose.yml" -Description "docker-compose.yml"

Write-Host "`n📁 REMOVENDO __pycache__ DA RAIZ..." -ForegroundColor Yellow
Remove-ItemSafe -Path "C:\Users\manoe\hub_aura\__pycache__" -Description "__pycache__/"

Write-Host "`n📁 REMOVENDO ARQUIVOS HTML TEMPORÁRIOS..." -ForegroundColor Yellow
Remove-ItemSafe -Path "C:\Users\manoe\hub_aura\quality_dashboard.html" -Description "quality_dashboard.html (será regenerado quando necessário)"

Write-Host "`n" + ("="*50) -ForegroundColor Cyan
Write-Host "📊 RESUMO DA LIMPEZA" -ForegroundColor Cyan
Write-Host ("="*50) -ForegroundColor Cyan

$totalSizeMB = [math]::Round($totalSize / 1MB, 2)
Write-Host "`nTotal de itens removidos: $($removedFiles.Count)" -ForegroundColor Green
Write-Host "Espaço liberado: $totalSizeMB MB`n" -ForegroundColor Green

if ($removedFiles.Count -gt 0) {
    Write-Host "Arquivos removidos:" -ForegroundColor Yellow
    foreach ($file in $removedFiles) {
        Write-Host "  - $file" -ForegroundColor Gray
    }
}

Write-Host "`n✅ LIMPEZA CONCLUÍDA!" -ForegroundColor Green
Write-Host "`nArquivos MANTIDOS (essenciais):" -ForegroundColor Cyan
Write-Host "  ✓ venv/ (virtual environment ativo)" -ForegroundColor Gray
Write-Host "  ✓ backups/ (backups organizados da V3.0)" -ForegroundColor Gray
Write-Host "  ✓ migrations/ (migrations Alembic)" -ForegroundColor Gray
Write-Host "  ✓ scripts/ (scripts ativos: populate, generate_embeddings, etc.)" -ForegroundColor Gray
Write-Host "  ✓ DOCUMENTATION.md, CHANGELOG_V3.1.md (docs principais)" -ForegroundColor Gray
Write-Host "  ✓ main.py, requirements.txt (código fonte)" -ForegroundColor Gray
Write-Host "  ✓ hub-aura-frontend/ (código React)" -ForegroundColor Gray
Write-Host "`n"
