# Script para executar teste de busca semântica
Write-Host "Aguardando servidor inicializar..." -ForegroundColor Yellow
Start-Sleep -Seconds 12

Write-Host "`nExecutando busca semântica..." -ForegroundColor Green
cd C:\Users\manoe\hub_aura
C:/Users/manoe/hub_aura/venv/Scripts/python.exe test_semantic_search.py

Write-Host "`nTeste concluído!" -ForegroundColor Green
