# 🚀 Hub de Conhecimento Dinâmico (HCD) - Guia de Inicialização

## 📋 Configuração Atual

### Backend (FastAPI)
- **Porta**: 8001
- **Database**: PostgreSQL 15 (porta 5433)
- **Embeddings**: 276 vetores de 384 dimensões
- **Modelo**: paraphrase-multilingual-MiniLM-L12-v2

### Frontend (React + Vite)
- **Porta**: 5173
- **API**: http://localhost:8001

## 🎯 Iniciar a Aplicação

### Opção 1: Scripts PowerShell

#### Backend
```powershell
.\start_server.ps1
```

#### Frontend
```powershell
.\start_frontend.ps1
```

### Opção 2: Comandos Manuais

#### Backend
```powershell
C:/Users/manoe/hub_aura/venv/Scripts/python.exe -m uvicorn main:app --reload --host 127.0.0.1 --port 8001
```

#### Frontend
```powershell
cd hub-aura-frontend
npm run dev
```

## 🔗 URLs Importantes

- **Frontend**: http://localhost:5173
- **API Docs**: http://localhost:8001/docs
- **API Base**: http://localhost:8001/api/v1

## 📊 Endpoints Disponíveis

### Parcerias
- `GET /api/v1/parcerias` - Listar todas
- `GET /api/v1/parcerias/busca?termo=X` - Busca por texto
- `GET /api/v1/parcerias/{id}` - Detalhes
- `POST /api/v1/parcerias` - Criar nova
- `GET /api/v1/parcerias/{id}/similares` - Documentos similares
- `GET /api/v1/parcerias/semantic-busca` - Busca semântica v2

### Documentos
- `POST /api/v1/processar-documento` - Upload e processamento de PDF

## 🗄️ Banco de Dados

### PostgreSQL 15 (Porta 5433)
```powershell
# Conectar ao banco
$env:PGPASSWORD = "rx1800"
& "C:\Program Files\PostgreSQL\15\bin\psql.exe" -h localhost -p 5433 -U postgres -d hub_aura_db
```

### Verificar Embeddings
```sql
SELECT COUNT(*) FROM documento_vetores WHERE objeto_vetor_v2 IS NOT NULL;
-- Resultado esperado: 276
```

## 🔧 Manutenção

### Gerar Novos Embeddings
```powershell
C:/Users/manoe/hub_aura/venv/Scripts/python.exe scripts/generate_embeddings_v2.py
```

### Executar Migrations
```powershell
C:/Users/manoe/hub_aura/venv/Scripts/python.exe -m alembic upgrade head
```

### Backup do Banco
```powershell
$env:PGPASSWORD = "rx1800"
& "C:\Program Files\PostgreSQL\15\bin\pg_dump.exe" -h localhost -p 5433 -U postgres -d hub_aura_db -f backup_$(Get-Date -Format 'yyyyMMdd_HHmmss').sql
```

## 📁 Estrutura do Projeto

```
hub_aura/
├── main.py                    # FastAPI app principal
├── requirements.txt           # Dependências Python
├── alembic.ini               # Configuração de migrations
├── start_server.ps1          # Script para iniciar backend
├── start_frontend.ps1        # Script para iniciar frontend
├── migrations/               # Migrations do banco
│   └── versions/
│       └── 60788c255086_add_vector_v2.py
├── scripts/
│   ├── generate_embeddings_v2.py   # Gerar embeddings
│   ├── import_csv.py              # Importar dados
│   └── report_analyzer.py         # Análises
├── hub-aura-frontend/        # Frontend React
│   ├── src/
│   │   ├── config/
│   │   │   └── api.ts        # Configuração da API
│   │   ├── components/
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── .env                  # Variáveis de ambiente
│   └── vite.config.ts
└── venv/                     # Ambiente virtual Python
```

## 🐛 Troubleshooting

### Backend não inicia
1. Verificar se porta 8001 está livre: `netstat -ano | findstr :8001`
2. Verificar conexão com PostgreSQL 15: `psql -h localhost -p 5433 -U postgres`
3. Verificar logs de erro no terminal

### Frontend não conecta
1. Verificar se backend está rodando em http://localhost:8001
2. Verificar arquivo `.env` em `hub-aura-frontend/`
3. Limpar cache: `npm run build` e reiniciar

### Embeddings não funcionam
1. Verificar se sentence-transformers está instalado: `pip list | findstr sentence`
2. Verificar tabela documento_vetores: `\d documento_vetores` no psql
3. Reprocessar embeddings: executar `generate_embeddings_v2.py`

## 📚 Documentação Adicional

- `EMBEDDINGS_V2_REPORT.md` - Relatório completo de embeddings
- `MIGRATION_PG15.md` - Guia de migração PostgreSQL
- `FRONTEND_CHANGES.md` - Mudanças no frontend

## 🎉 Tudo Pronto!

1. Inicie o backend: `.\start_server.ps1`
2. Inicie o frontend: `.\start_frontend.ps1`
3. Acesse: http://localhost:5173
4. Explore a API: http://localhost:8001/docs

---
**Versão**: 2.0  
**Data**: 29/10/2025  
**Status**: ✅ Produção
