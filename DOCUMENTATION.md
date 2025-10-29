## Documentação do projeto Hub Aura

Data: 2025-10-28

Resumo
-------
Este repositório implementa um pequeno "hub de conhecimento" com:
- Backend em Python (FastAPI) que expõe endpoints para busca por texto e similaridade vetorial;
- Banco PostgreSQL com extensão `pgvector` para armazenamento nativo de vetores e busca vetorial (HNSW index);
- Frontend em React + Vite + TypeScript que consome a API e exibe resultados;
- Scripts de migração, seed e utilitários para administrar o banco e importar dados.

Objetivo técnico
-----------------
Migrar armazenamento de vetores de JSONB para o tipo nativo `vector` (pgvector), criar índices HNSW para busca por similaridade, automatizar o ambiente com Docker, e garantir que o frontend consuma corretamente a nova API.

Tecnologias principais
---------------------
- PostgreSQL (container Docker) com extensão `pgvector` (imagem usada: ankane/pgvector ou equivalente).
- FastAPI (backend) + Uvicorn.
- spaCy (modelo pt_core_news_lg) para gerar embeddings locais de teste.
- React + Vite + TypeScript (frontend).
- Node / npm para dev frontend.
- Ferramentas auxiliares: psycopg2 (ou similar), curl, pg_dump/pg_restore, PowerShell scripts para automação no Windows.

Conexões / Credenciais (padrões usados nos scripts locais)
-------------------------------------------------------
- host: localhost
- port: 5432
- user: postgres
- database: hub_aura_db
- password: rx1800

Importante: não colocar credenciais sensíveis em produção. Aqui aparecem porque foram usados em scripts locais e automações.

Estrutura e arquivos importantes
-------------------------------
Resumo dos arquivos e diretórios mais relevantes (local):

- migrations/
  - `create_instrumentos_parceria.sql` — cria tabela `instrumentos_parceria`.
  - `create_similarity_tables.sql` — (legado) tabelas de vetor/similaridade (JSONB-based originalmente).
  - `zz_create_pgvector_hnsw_index.sql` — criação de índice HNSW (pode ter sido ajustado para remover parâmetros não suportados).
  - `zz_enable_pgvector_and_recreate_vectors.sql` — arquivo original destrutivo (foi arquivado como `.orig.sql`) e substituído por uma versão segura que apenas cria extensões/objetos se não existirem.
  - `zz_safe_enable_pgvector.sql` — migration adicionada para habilitar `pgvector` e `unaccent` de forma segura.
  - `zz_enable_unaccent.sql` — habilita a extensão `unaccent` para busca sem acento.

- backend/
  - `main.py` — endpoints FastAPI (ex.: `/api/v1/parcerias/busca`, `/api/v1/parcerias/{id}/similares`, criação de parcerias), atualizados para usar `vector` e operador de similaridade `<=>`/`<->`.
  - `run_migration.py` — script Python simples para aplicar todas as migrations SQL presentes em `migrations/`.

- scripts/
  - `seed_test.py` — carrega spaCy e gera vetores para algumas parcerias de teste, insere em `documento_vetores` e popula `similaridades`.
  - `import_csv.py` (ou `scripts/import_csv.py`) — importador que lê `Instrumento_Parceria_XLSX_csv.csv` com codificação CP1252 (Windows-1252) e insere em `instrumentos_parceria` (faz deduplicação básica).
  - Vários scripts de diagnóstico: `check_index.py`, `check_indexes_verbose.py`, `list_tables.py`, `test_vector_search.py` — ajudam a verificar status de extensões, índices e funcionamento da busca vetorial.

- infra / automação
  - `setup_docker.ps1` — PowerShell para iniciar containers Docker (compose), aguardar serviços e executar migrations + seed automaticamente (gerencia ambiente Windows).
  - Backups: `backups/hub_aura_db_prepatch.dump` — dump gerado antes de alterações destrutivas.

- frontend/hub-aura-frontend/
  - `package.json` — script `dev` foi alterado para `vite --host` (garante binding em 0.0.0.0/localhost/IPv6).
  - `README.md` — atualizado com instruções de execução e debug do dev server.
  - `src/` — componentes React: `App.tsx`, `PaginaBusca.tsx`, `components/ListaResultados.tsx`, `DetalheParceria.tsx`, `Busca.tsx` — ajustados para consumir a nova API que retorna { items, total_items } e para aplicar heurística temporária de correção de encoding (fixEncoding) para strings com mojibake.

Banco de dados — tabelas principais
----------------------------------
- `instrumentos_parceria`
  - Armazena os metadados das parcerias/instrumentos (razão social, objeto, cnpj, etc.).
  - Dados importados do CSV `Instrumento_Parceria_XLSX_csv.csv` (codificação CP1252). Alguns registros apresentavam duplicatas e problemas de encoding.

- `documento_vetores`
  - Colunas principais: `id`, `parceria_id` (FK para `instrumentos_parceria`), `objeto_vetor` (`vector(300)`), `created_at`, `updated_at`.
  - Armazena o embedding/vetor nativo (pgvector) em vez de JSONB.

- `similaridades`
  - Tabela que armazena resultados pré-calculados ou cache de similaridade entre documentos/parcerias. Contém: `id`, `parceria_origem_id`, `parceria_similar_id`, `pontuacao`, timestamps.

Índices e performance
----------------------
- HNSW index para `documento_vetores.objeto_vetor` foi criado (`idx_documento_vetores_objeto_vetor_hnsw`).
  - Parâmetros usados: `m=16, ef_construction=200` (podem ser ajustados conforme volume e latência desejada).
  - Observação: criação de índices HNSW pode não aceitar todos os parâmetros dependendo da versão do pgvector/Postgres; scripts foram corrigidos para criar o índice sem parâmetros inválidos quando necessário.

API — endpoints principais
-------------------------
- GET /api/v1/parcerias/busca?termo=<termo>&limit=&offset=
  - Busca textual sobre `instrumentos_parceria` com `unaccent(lower(...)) ILIKE unaccent(lower(:termo))` e retorno paginado.
  - Resposta: { items: [...], total_items: N }

- GET /api/v1/parcerias/{id}/similares?limit=10&ef_search=...
  - Retorna parcerias semelhantes por similaridade vetorial usando operador `<=>` (ou `<->` para distância) ordenado pela pontuação.
  - Pode tentar ajustar `SET pgvector.index_search_type = 'hnsw'` ou `SET pgvector.ef_search = n` se a extensão suportar ajuste por sessão.

- POST /api/v1/parcerias
  - Criação de parceria e inserção do vetor em `documento_vetores` (o backend realiza o cast para `::vector` ao gravar).

Comportamento de encoding e dados
---------------------------------
- O CSV `Instrumento_Parceria_XLSX_csv.csv` foi identificado como Windows-1252 (CP1252). Ao importar sem conversão, alguns campos apresentaram mojibake (e.g., 'CooperaÃ§Ã£o').
- Medidas tomadas:
  - Importador foi escrito para abrir CSV com cp1252 e inserir corretamente.
  - No frontend aplicamos temporariamente uma função `fixEncoding()` para decodificar strings já corrompidas enquanto planejamos uma correção definitiva (reimportar/normalizar dados usando UTF-8).

Backups e recuperação
----------------------
- Antes de alterações destrutivas foi criado dump: `backups/hub_aura_db_prepatch.dump` (pg_dump). Para restaurar:

```powershell
# Exemplo de restauração (no container ou local com pg_restore disponível):
# pg_restore -h localhost -p 5432 -U postgres -d hub_aura_db -v backups/hub_aura_db_prepatch.dump
```

Nota: conferir permissões e senha do usuário `postgres` antes de rodar.

Automação e execução local (desenvolvimento)
--------------------------------------------
Pré-requisitos:
- Docker & Docker Compose (se existir docker-compose.yml usado pelo `setup_docker.ps1`)
- Python 3.10+ (conforme requirements.txt)
- Node.js + npm

Passos para subir ambiente de dev (resumido):

```powershell
# 1) Start Docker + DB (PowerShell script já preparado):
PowerShell -ExecutionPolicy Bypass -File .\setup_docker.ps1

# 2) Executar migrations e seed (o setup_docker.ps1 já chama run_migration.py e seed):
python run_migration.py
python scripts/seed_test.py

# 3) Rodar backend (exemplo):
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 4) Rodar frontend:
cd hub-aura-frontend
npm install
npm run dev   # script já definido como 'vite --host'
```

Verificação rápida (curl):

```powershell
curl.exe -I http://localhost:5173
curl.exe -sS http://localhost:8000/api/v1/parcerias/busca?termo=inteligencia | jq .
```

Observações para Windows: usar `curl.exe`/PowerShell; `Invoke-WebRequest` pode preferir IPv4 e falhar quando Vite está escutando apenas em IPv6 (`::1`). Preferir `curl.exe` para testes.

Testes e validação
------------------
- `test_vector_search.py` — testes de busca vetorial (usa spaCy local para gerar vetores de exemplo e executa buscas comparativas). Rode para validar o pipeline de vetores.

Problemas conhecidos e recomendações
-----------------------------------
- Migrações: havia uma migration destrutiva que realizava DROP TABLE; ela foi arquivada como `zz_enable_pgvector_and_recreate_vectors.orig.sql` e substituída por uma versão segura. Sempre fazer backup antes de aplicar migrations que alterem estruturas.
- Encoding: dados importados originalmente em CP1252 devem ser normalizados para UTF-8; recomendo reimportar o CSV convertendo para UTF-8 e atualizando as linhas corrompidas no banco.
- Index HNSW: quando recriar índices em produção, planejar janela de manutenção; criação pode ser custosa dependendo do volume.
- Acesso frontend: o dev server Vite pode bindar em IPv6 (::1); para acesso externo use `--host` ou `--host 0.0.0.0`.

Próximos passos recomendados
---------------------------
1. Normalizar dados: identificar registros com mojibake (procedimento de detecção heurística) e reimportar/atualizar para UTF-8. Fazer isso em um ambiente de staging e testar frontend.
2. Revisar e consolidar migrations: garantir que cada migration seja idempotente e revisada por code review; remover quaisquer DROP TABLE automatizados.
3. Hardening para produção: criar scripts de backup automáticos, política de rollback, e documentar janela de manutenção para criação/reconstrução de índices vetoriais.
4. Testes automatizados: aumentar a cobertura de testes de integração (endpoints, busca vetorial, seed) e criar CI que rode essas verificações.
5. Monitoramento: adicionar métricas básicas (latência de consultas vetoriais, taxa de erros) e logs estruturados no backend.

Anexos e mapas rápidos (onde olhar)
-----------------------------------
- Migrations: `migrations/`
- Scripts de seed e import: `scripts/` ou no root com nomes `seed_test.py`, `scripts/import_csv.py`
- Automação Docker/Windows: `setup_docker.ps1`
- Frontend: `hub-aura-frontend/` (`package.json`, `README.md`, `src/`)
- Backups: `backups/` (dumps gerados previamente)

Contato/apoio
------------
Se quiser, eu posso:
- Comitar este documento (`DOCUMENTATION.md`) e criar uma branch com o resumo das mudanças.
- Gerar um script de detecção de mojibake para listar linhas afetadas no banco.
- Preparar scripts seguros de deduplicação para `instrumentos_parceria`.

Fim do documento.
