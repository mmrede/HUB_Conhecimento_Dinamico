# Script para iniciar o frontend Vite
# Executa o servidor de desenvolvimento do React/Vite

Write-Host "🎨 Iniciando frontend Vite..." -ForegroundColor Cyan
Write-Host "📂 Pasta: hub-aura-frontend" -ForegroundColor Yellow
Write-Host "🌐 Frontend: http://localhost:5173" -ForegroundColor Green
Write-Host "🔌 API Backend: http://localhost:8001" -ForegroundColor Green
Write-Host ""
Write-Host "Pressione Ctrl+C para parar o servidor" -ForegroundColor Gray
Write-Host ""

Set-Location hub-aura-frontend
npm run dev
