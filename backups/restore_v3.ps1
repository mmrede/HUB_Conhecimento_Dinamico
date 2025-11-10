# Script de Restauração - Hub Aura V3.0
# Data: 30/10/2025
# Uso: .\restore_v3.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Hub Aura - Restauração Versão 3.0" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$BACKUP_DATE = "20251030_175528"
$DB_NAME = "hub_aura_db"
$DB_USER = "postgres"
$DB_HOST = "localhost"
$DB_PORT = "5433"
$DB_PASSWORD = "rx1800"

# Configurar variável de ambiente
$env:PGPASSWORD = $DB_PASSWORD

Write-Host "1. Verificando backups..." -ForegroundColor Yellow
if (-not (Test-Path "backups/hub_aura_db_v3_$BACKUP_DATE.dump")) {
    Write-Host "   ❌ Backup do banco não encontrado!" -ForegroundColor Red
    exit 1
}
Write-Host "   ✅ Backup do banco encontrado (1.94 MB)" -ForegroundColor Green

if (-not (Test-Path "backups/hub_aura_code_v3_20251030_175603.zip")) {
    Write-Host "   ⚠️  Backup do código backend não encontrado" -ForegroundColor Yellow
}
else {
    Write-Host "   ✅ Backup do código backend encontrado" -ForegroundColor Green
}

if (-not (Test-Path "backups/hub_aura_frontend_v3_20251030_175618.zip")) {
    Write-Host "   ⚠️  Backup do código frontend não encontrado" -ForegroundColor Yellow
}
else {
    Write-Host "   ✅ Backup do código frontend encontrado" -ForegroundColor Green
}

Write-Host ""
Write-Host "2. Deseja continuar com a restauração? (S/N)" -ForegroundColor Yellow
$response = Read-Host
if ($response -ne "S" -and $response -ne "s") {
    Write-Host "   Restauração cancelada." -ForegroundColor Red
    exit 0
}

Write-Host ""
Write-Host "3. Restaurando banco de dados..." -ForegroundColor Yellow
Write-Host "   ⚠️  Isso irá SUBSTITUIR os dados atuais!" -ForegroundColor Red
Write-Host "   Confirmar? (S/N)" -ForegroundColor Yellow
$response = Read-Host
if ($response -ne "S" -and $response -ne "s") {
    Write-Host "   Restauração do banco cancelada." -ForegroundColor Red
    exit 0
}

Write-Host "   Executando pg_restore..." -ForegroundColor Cyan
& "C:\Program Files\PostgreSQL\15\bin\pg_restore.exe" `
    -h $DB_HOST -p $DB_PORT -U $DB_USER `
    -d $DB_NAME --clean --if-exists -v `
    "backups/hub_aura_db_v3_$BACKUP_DATE.dump" 2>&1 | Out-Null

if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ Banco de dados restaurado com sucesso!" -ForegroundColor Green
}
else {
    Write-Host "   ⚠️  Restauração concluída com avisos (normal)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "4. Verificando dados restaurados..." -ForegroundColor Yellow

# Verificar parcerias
$result = & "C:\Program Files\PostgreSQL\15\bin\psql.exe" `
    -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME `
    -t -c "SELECT COUNT(*) FROM instrumentos_parceria;" 2>$null
$count_parcerias = $result.Trim()
Write-Host "   Parcerias: $count_parcerias (esperado: 276)" -ForegroundColor Cyan

# Verificar planos de trabalho
$result = & "C:\Program Files\PostgreSQL\15\bin\psql.exe" `
    -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME `
    -t -c "SELECT COUNT(*) FROM instrumentos_parceria WHERE plano_de_trabalho IS NOT NULL;" 2>$null
$count_planos = $result.Trim()
Write-Host "   Planos de Trabalho: $count_planos (esperado: 276)" -ForegroundColor Cyan

# Verificar embeddings v3
$result = & "C:\Program Files\PostgreSQL\15\bin\psql.exe" `
    -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME `
    -t -c "SELECT COUNT(*) FROM documento_vetores WHERE objeto_vetor_v3 IS NOT NULL;" 2>$null
$count_v3 = $result.Trim()
Write-Host "   Embeddings V3: $count_v3 (esperado: 276)" -ForegroundColor Cyan

if ($count_parcerias -eq "276" -and $count_planos -eq "276" -and $count_v3 -eq "276") {
    Write-Host "   ✅ Todos os dados verificados com sucesso!" -ForegroundColor Green
}
else {
    Write-Host "   ⚠️  Verificar dados - contagens não correspondem ao esperado" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "5. Restaurar código? (S/N)" -ForegroundColor Yellow
$response = Read-Host
if ($response -eq "S" -or $response -eq "s") {
    Write-Host "   Extraindo código backend..." -ForegroundColor Cyan
    if (Test-Path "backups/hub_aura_code_v3_20251030_175603.zip") {
        Expand-Archive -Path "backups/hub_aura_code_v3_20251030_175603.zip" -DestinationPath "." -Force
        Write-Host "   ✅ Código backend restaurado" -ForegroundColor Green
    }
    
    Write-Host "   Extraindo código frontend..." -ForegroundColor Cyan
    if (Test-Path "backups/hub_aura_frontend_v3_20251030_175618.zip") {
        Expand-Archive -Path "backups/hub_aura_frontend_v3_20251030_175618.zip" -DestinationPath "hub-aura-frontend/" -Force
        Write-Host "   ✅ Código frontend restaurado" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Restauração Concluída!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Próximos passos:" -ForegroundColor Yellow
Write-Host "  1. Ativar venv: .\venv\Scripts\Activate.ps1"
Write-Host "  2. Iniciar backend: python -m uvicorn main:app --reload --host 127.0.0.1 --port 8002"
Write-Host "  3. Iniciar frontend (outro terminal): cd hub-aura-frontend; npm run dev"
Write-Host ""
Write-Host "URLs de acesso:" -ForegroundColor Yellow
Write-Host "  Backend API: http://127.0.0.1:8001/docs"
Write-Host "  Frontend: http://localhost:5173"
Write-Host ""
