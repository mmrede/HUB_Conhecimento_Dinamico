# Backup Hub Aura - Versão 3.0

**Data do Backup:** 30 de outubro de 2025  
**Hora:** 17:55:28  
**Versão:** 3.0 (Plano de Trabalho + Embeddings V3)

## Arquivos de Backup Criados

### 1. Banco de Dados PostgreSQL
**Arquivo:** `hub_aura_db_v3_20251030_175528.dump`  
**Tamanho:** 1.94 MB (1,942,379 bytes)  
**Formato:** Custom (pg_dump -F c)  
**Conteúdo:**
- Tabela `instrumentos_parceria` (276 registros) com campo `plano_de_trabalho`
- Tabela `documento_vetores` (276 registros) com `objeto_vetor_v2` e `objeto_vetor_v3`
- Tabela `similaridades`
- Tabela `alembic_version`
- Todas as sequences, índices, constraints e triggers

**Como restaurar:**
```powershell
$env:PGPASSWORD = "rx1800"
& "C:\Program Files\PostgreSQL\15\bin\pg_restore.exe" `
  -h localhost -p 5433 -U postgres `
  -d hub_aura_db_restore `
  -v --clean --if-exists `
  "backups/hub_aura_db_v3_20251030_175528.dump"
```

### 2. Código Backend
**Arquivo:** `hub_aura_code_v3_20251030_175603.zip`  
**Tamanho:** 50.9 KB (50,954 bytes)  
**Conteúdo:**
- `main.py` - Backend FastAPI com endpoints v3
- `requirements.txt` - Dependências Python
- `DOCUMENTATION.md` - Documentação completa do projeto
- `migrations/` - Todas as migrations Alembic incluindo:
  - `20251030_add_plano_de_trabalho.py`
  - `20251030_add_objeto_vetor_v3.py`
  - `60788c255086_add_vector_v2.py`
- `scripts/` - Scripts Python incluindo:
  - `generate_embeddings_v3.py`
  - `generate_embeddings_v2.py`
  - `populate_plano_trabalho.py`
  - `compare_v2_v3.py`
  - `quality_dashboard.py`
  - `test_planos.py`
  - `import_csv.py`

### 3. Código Frontend
**Arquivo:** `hub_aura_frontend_v3_20251030_175618.zip`  
**Tamanho:** 14.1 KB (14,134 bytes)  
**Conteúdo:**
- `src/App.tsx` - Aplicação principal
- `src/PaginaBusca.tsx` - Página de busca
- `src/components/Busca.tsx` - Componente de busca com toggle V3
- `src/components/DetalheParceria.tsx` - Detalhes da parceria
- `src/components/ListaResultados.tsx` - Lista com chips de similaridade
- `src/components/PlanoTrabalho.tsx` - Componente expansível (NOVO)
- `src/components/PaginaUpload.tsx` - Formulário com plano_de_trabalho (NOVO)

## Estado do Sistema no Momento do Backup

### Banco de Dados
- **Host:** localhost
- **Porta:** 5433
- **Database:** hub_aura_db
- **PostgreSQL:** 15.x
- **Extensões:** unaccent

### Dados
- **Parcerias:** 276 registros
- **Planos de Trabalho:** 276 registros (100% preenchidos)
- **Embeddings V2:** 276 vetores (384 dimensões cada)
- **Embeddings V3:** 276 vetores (384 dimensões cada)

### Embeddings
- **Modelo:** sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
- **Dimensões:** 384
- **V2:** Apenas campo `objeto`
- **V3:** Campos `objeto` + `plano_de_trabalho` combinados
- **Melhoria V3 vs V2:** ~4% aumento em similaridade

### Servidores
- **Backend:** http://127.0.0.1:8001 (FastAPI + Uvicorn)
- **Frontend:** http://localhost:5173 (Vite dev server)

### Qualidade
- **Taxa de Sucesso:** 100% (5/5 queries)
- **Relevância Média:** 49%
- **Status:** Todos os testes passando ✅

## Features Implementadas na V3.0

### Backend
- ✅ Campo `plano_de_trabalho` na tabela `instrumentos_parceria`
- ✅ Coluna `objeto_vetor_v3` na tabela `documento_vetores`
- ✅ Endpoint `/api/v1/parcerias/semantic-busca` com parâmetro `version`
- ✅ Modelo `Parceria` com campos `plano_de_trabalho` e `similarity_score`
- ✅ Modelo `ParceriaCreate` aceita `plano_de_trabalho` opcional
- ✅ COALESCE fallback (v3 → v2) na query SQL

### Frontend
- ✅ Componente `PlanoTrabalho` expansível (preview 200 chars)
- ✅ Chips coloridos de similaridade nos resultados
- ✅ Interface `Parceria` com campos opcionais novos
- ✅ Formulário de upload com campo `plano_de_trabalho` multiline
- ✅ Label "Busca Semântica V3" no toggle
- ✅ HMR funcionando com todas as atualizações

### Scripts
- ✅ `populate_plano_trabalho.py` - Geração automática de planos
- ✅ `generate_embeddings_v3.py` - Criação de embeddings V3
- ✅ `compare_v2_v3.py` - Ferramenta de comparação
- ✅ `quality_dashboard.py` - Dashboard de métricas

### Migrations
- ✅ `20251030_add_plano_de_trabalho.py` - Adiciona coluna TEXT
- ✅ `20251030_add_objeto_vetor_v3.py` - Adiciona coluna FLOAT[]

## Procedimento de Recuperação Completa

### 1. Restaurar Banco de Dados
```powershell
# Criar novo banco (se necessário)
$env:PGPASSWORD = "rx1800"
& "C:\Program Files\PostgreSQL\15\bin\psql.exe" `
  -h localhost -p 5433 -U postgres `
  -c "DROP DATABASE IF EXISTS hub_aura_db;"
  
& "C:\Program Files\PostgreSQL\15\bin\psql.exe" `
  -h localhost -p 5433 -U postgres `
  -c "CREATE DATABASE hub_aura_db;"

# Restaurar backup
& "C:\Program Files\PostgreSQL\15\bin\pg_restore.exe" `
  -h localhost -p 5433 -U postgres `
  -d hub_aura_db -v `
  "backups/hub_aura_db_v3_20251030_175528.dump"
```

### 2. Restaurar Código Backend
```powershell
# Extrair arquivos
Expand-Archive -Path "backups/hub_aura_code_v3_20251030_175603.zip" `
  -DestinationPath "." -Force

# Instalar dependências
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 3. Restaurar Código Frontend
```powershell
# Extrair arquivos
Expand-Archive -Path "backups/hub_aura_frontend_v3_20251030_175618.zip" `
  -DestinationPath "hub-aura-frontend/" -Force

# Instalar dependências
cd hub-aura-frontend
npm install
```

### 4. Iniciar Servidores
```powershell
# Terminal 1 - Backend
cd C:\Users\manoe\hub_aura
.\venv\Scripts\Activate.ps1
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8001

# Terminal 2 - Frontend
cd C:\Users\manoe\hub_aura\hub-aura-frontend
npm run dev
```

## Verificação Pós-Restauração

### 1. Verificar Banco de Dados
```powershell
$env:PGPASSWORD = "rx1800"
& "C:\Program Files\PostgreSQL\15\bin\psql.exe" `
  -h localhost -p 5433 -U postgres -d hub_aura_db `
  -c "SELECT COUNT(*) FROM instrumentos_parceria WHERE plano_de_trabalho IS NOT NULL;"
# Deve retornar: 276

& "C:\Program Files\PostgreSQL\15\bin\psql.exe" `
  -h localhost -p 5433 -U postgres -d hub_aura_db `
  -c "SELECT COUNT(*) FROM documento_vetores WHERE objeto_vetor_v3 IS NOT NULL;"
# Deve retornar: 276
```

### 2. Testar Backend
```powershell
# Health check
curl.exe http://127.0.0.1:8001/docs

# Busca semântica V3
curl.exe "http://127.0.0.1:8001/api/v1/parcerias/semantic-busca?termo=educacao&version=v3"
```

### 3. Testar Frontend
- Acessar http://localhost:5173
- Verificar toggle "Busca Semântica V3 (IA)"
- Fazer busca e verificar chips de similaridade
- Expandir detalhes e verificar componente PlanoTrabalho
- Testar formulário de upload

## Notas Importantes

### Dependências Críticas
- PostgreSQL 15 na porta 5433
- Python 3.10+ com venv
- Node.js + npm
- Modelo sentence-transformers (download automático ~90MB na primeira execução)

### Credenciais (DESENVOLVIMENTO)
- **Database User:** postgres
- **Database Password:** rx1800
- ⚠️ **ATENÇÃO:** Não usar em produção!

### Performance
- Geração de embeddings v3: ~2-3 minutos para 276 registros
- Busca semântica: <200ms por query
- Frontend HMR: <100ms

### Backups Anteriores
- `hub_aura_db_prepatch.dump` - Backup pré-v2 (28/10/2025)
- `hub_aura_semantic_2025-10-29_20-21-49.backup` - Backup v2 (29/10/2025)

## Checklist de Validação

- [ ] Banco restaurado com 276 registros
- [ ] Campo plano_de_trabalho presente e preenchido (276/276)
- [ ] Embeddings v3 gerados (276/276)
- [ ] Backend iniciando sem erros
- [ ] Frontend compilando sem erros
- [ ] Endpoint /semantic-busca retornando resultados
- [ ] Toggle V3 funcionando
- [ ] Componente PlanoTrabalho expandindo corretamente
- [ ] Chips de similaridade exibidos
- [ ] Formulário de upload com campo plano_de_trabalho

---

**Backup criado com sucesso!** ✅  
**Versão:** Hub Aura 3.0  
**Timestamp:** 2025-10-30 17:55:28
