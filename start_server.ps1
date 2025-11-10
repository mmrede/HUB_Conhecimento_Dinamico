# Script para iniciar o servidor FastAPI
# Executa o servidor na porta 8001 com reload automático

Write-Host "🚀 Iniciando servidor FastAPI..." -ForegroundColor Cyan
Write-Host "📊 Database: PostgreSQL 15 (porta 5433)" -ForegroundColor Yellow
Write-Host "🌐 Servidor: http://localhost:8001" -ForegroundColor Green
Write-Host "📖 Documentação: http://localhost:8001/docs" -ForegroundColor Green
Write-Host ""
Write-Host "Pressione Ctrl+C para parar o servidor" -ForegroundColor Gray
Write-Host ""

C:/Users/manoe/hub_aura/venv/Scripts/python.exe -m uvicorn main:app --reload --host 127.0.0.1 --port 8001
