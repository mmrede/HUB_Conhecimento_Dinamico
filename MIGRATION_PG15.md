# Migração para PostgreSQL 15 - Resumo de Alterações

## Data: 29/10/2025

## Arquivos Atualizados

### Porta alterada de 5432 → 5433

1. ✅ `main.py` - Configuração principal do FastAPI
2. ✅ `app/core/config.py` - Settings da aplicação
3. ✅ `alembic.ini` - Configuração de migrations
4. ✅ `scripts/generate_embeddings_v2.py` - Script de embeddings
5. ✅ `scripts/report_analyzer.py` - Análise de dados
6. ✅ `scripts/import_csv.py` - Importação de CSV
7. ✅ `run_migration.py` - Execução de migrations

## Arquivos NÃO Atualizados (scripts de desenvolvimento/teste)

Estes arquivos ainda apontam para porta 5432 caso você precise acessar o PostgreSQL 18:
- `check_index.py`
- `check_location.py`
- `check_indexes_verbose.py`
- `check_tables.py`
- `create_index_test.py`
- `list_tables.py`
- `seed_test.py`
- `show_db.py`
- `test_vector_search.py`
- `scripts/setup_pgvector.py`

## Testando a Migração

### 1. Verificar Conexão
```bash
python -c "from sqlalchemy import create_engine; engine = create_engine('postgresql://postgres:rx1800@localhost:5433/hub_aura_db'); print('Conexão OK!')"
```

### 2. Iniciar o Servidor FastAPI
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Testar Endpoints
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/api/v1/parcerias
- Busca Semântica: http://localhost:8000/api/v1/parcerias/semantic-busca

## Rollback (se necessário)

Para voltar ao PostgreSQL 18, substitua `5433` por `5432` nos arquivos listados acima.

## Observações

- **PostgreSQL 18**: Porta 5432 (ainda ativo, pode ser usado como fallback)
- **PostgreSQL 15**: Porta 5433 (produção com embeddings v2)
- **Embeddings v2**: 276 registros, 384 dimensões, modelo multilíngue

## Próximos Passos

1. Testar todos os endpoints da API
2. Verificar performance das buscas
3. Monitorar logs de erro
4. Considerar desabilitar PostgreSQL 18 se tudo funcionar bem
