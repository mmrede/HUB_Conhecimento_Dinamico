## Documentação do projeto Hub Aura

Data: 2025-10-31 (atualizado)

Resumo
-------
Este repositório implementa um "hub de conhecimento" com busca semântica usando IA:
- Backend em Python (FastAPI) com endpoints para busca textual e **busca semântica por similaridade vetorial**;
- Banco PostgreSQL 15 (porta 5433) com extensão `unaccent` para armazenamento de vetores como FLOAT[];
- **Modelo sentence-transformers** (paraphrase-multilingual-MiniLM-L12-v2) para embeddings contextuais de 384 dimensões;
- Frontend em React + Vite + TypeScript com **toggle de busca semântica** e exibição de resultados;
- Scripts de migração (Alembic), geração de embeddings v2 e utilitários para administrar o banco e importar dados.

Objetivo técnico
-----------------
Implementar busca semântica usando **sentence-transformers** para queries contextuais (frases completas funcionam melhor que palavras isoladas), com armazenamento de vetores FLOAT[] (384 dimensões) e cálculo de similaridade cosseno via SQL (sem pgvector operators). O frontend permite alternar entre busca textual tradicional e busca semântica com IA.

Tecnologias principais
---------------------
- PostgreSQL 15 (porta 5433, banco `hub_aura`) com extensão `unaccent` para busca sem acentos.
- FastAPI (backend) + Uvicorn no port 8002.
- **sentence-transformers** (modelo: paraphrase-multilingual-MiniLM-L12-v2) para embeddings contextuais.
- spaCy (modelo pt_core_news_lg) — legado, usado para embeddings v1 de 96 dimensões (substituído por sentence-transformers).
- React + Vite + TypeScript (frontend em http://localhost:5173).
- Alembic para migrations do banco de dados.
- Node / npm para dev frontend.
- Ferramentas auxiliares: psycopg2, curl, PowerShell scripts para automação no Windows.

Conexões / Credenciais (padrões usados nos scripts locais)
-------------------------------------------------------
- host: localhost
- port: **5433** (PostgreSQL 15)
- user: postgres
- database: hub_aura
- autenticação via variável de ambiente (DATABASE_URL)

Backend API:
- host: 127.0.0.1
- port: **8002**

Frontend (Vite):
- host: localhost / 0.0.0.0
- port: 5173

Importante: **Credenciais não devem estar hardcoded em produção.** O projeto foi atualizado para usar variáveis de ambiente (DATABASE_URL, PGHOST, PGPORT, PGUSER, PGPASSWORD). Scripts legados ainda contêm valores de fallback para desenvolvimento local.

Estrutura e arquivos importantes
-------------------------------
Resumo dos arquivos e diretórios mais relevantes (local):

- **migrations/** (Alembic)
  - `env.py` — configuração do Alembic
  - `versions/20251030_add_plano_de_trabalho.py` — migration que adiciona coluna `plano_de_trabalho` (TEXT) à tabela `instrumentos_parceria`
  - `versions/20251030_add_objeto_vetor_v3.py` — migration que adiciona coluna `objeto_vetor_v3` (FLOAT[]) à tabela `documento_vetores`
  - `versions/60788c255086_add_vector_v2.py` — migration que adiciona coluna `objeto_vetor_v2` (FLOAT[]) à tabela `documento_vetores`
  - Migrations legadas SQL arquivadas (zz_*.sql) — referências históricas, não são mais usadas

- **main.py** (backend FastAPI)
  - **Segurança:** Lê conexão do banco via variável de ambiente DATABASE_URL (fallback local para dev)
  - **Validação de uploads:** Endpoint `/api/v1/processar-documento` valida tipo MIME (PDF) e tamanho máximo (10MB)
  - Endpoint `/api/v1/parcerias/semantic-busca?termo=<termo>` — busca semântica usando sentence-transformers
  - Endpoint `/api/v1/parcerias/busca?termo=<termo>` — busca textual tradicional com unaccent
  - Endpoint `/api/v1/parcerias/{id}` — detalhes de uma parceria
  - **Endpoint POST `/api/v1/parcerias`** — criação de nova parceria com validação
  - Modelo sentence-transformers carregado globalmente no startup para performance
  - SQL query com CTE para calcular similaridade cosseno via unnest (dot product / normas)

- **scripts/**
  - `generate_embeddings_v3.py` — gera embeddings de 384 dimensões combinando objeto + plano_de_trabalho, popula `objeto_vetor_v3` (**usa DATABASE_URL**)
  - `generate_embeddings_v2.py` — gera embeddings de 384 dimensões usando sentence-transformers para todas as parcerias, popula `objeto_vetor_v2` (**usa DATABASE_URL**)
  - `populate_plano_trabalho.py` — gera conteúdo sintético estruturado para o campo plano_de_trabalho (276 registros) (**usa DATABASE_URL**)
  - `compare_v2_v3.py` — ferramenta de comparação entre buscas usando v2 vs v3 embeddings
  - `quality_dashboard.py` — gera dashboard HTML com métricas de qualidade das buscas
  - `test_planos.py` — script de validação do conteúdo gerado para planos de trabalho
  - `import_csv.py` — importador que lê CSV com codificação CP1252 e insere em `instrumentos_parceria`
  - **Utilitários** (`scripts/utilities/`): deduplicate_instrumentos.py, detect_mojibake.py, fix_mojibake.py — **usam variáveis de ambiente PGHOST/PGPORT/PGUSER/PGPASSWORD**

- **hub-aura-frontend/**
  - **Proxy config:** `vite.config.ts` configurado para proxy `/api` → `http://localhost:8002`
  - `src/config/api.ts` — configuração central da API (API_BASE_URL usa `http://localhost:8002`)
  - `src/App.tsx` — componente principal com lógica de busca (textual vs semântica)
  - `src/components/Busca.tsx` — campo de busca com toggle "Busca Semântica (IA)" usando V3 (padrão: ativado)
  - `src/PaginaBusca.tsx` — página de busca com fallback automático, interface Parceria inclui plano_de_trabalho e similarity_score
  - `src/components/DetalheParceria.tsx` — exibe detalhes completos incluindo componente PlanoTrabalho
  - `src/components/PlanoTrabalho.tsx` — componente expansível para exibir plano de trabalho (preview 200 chars)
  - `src/components/ListaResultados.tsx` — exibe chips de similarity_score nos resultados
  - `src/components/PaginaUpload.tsx` — formulário para adicionar nova parceria com campo plano_de_trabalho
  - `package.json` — script `dev` configurado como `vite --host` para bind em todas interfaces
  - Estado `usarBuscaSemantica` preservado entre paginações

- **Documentação:**
  - `START_HERE.md` — guia rápido de início
  - `EMBEDDINGS_V2_REPORT.md` — relatório técnico da implementação de embeddings v2
  - `MIGRATION_PG15.md` — guia de migração para PostgreSQL 15
  - `REPAIR_REPORT.md` — histórico de correções aplicadas

Banco de dados — tabelas principais
----------------------------------
- `instrumentos_parceria`
  - Armazena os metadados das parcerias/instrumentos (razão social, objeto, cnpj, etc.).
  - Dados importados do CSV (codificação CP1252).
  - **276 registros** atualmente no banco.
  - **Novo campo v3.0:** `plano_de_trabalho` (TEXT) - contém estrutura detalhada do plano (justificativa, objetivos, público-alvo, metas, cronograma)

- `documento_vetores`
  - Colunas principais: `id`, `parceria_id` (FK para `instrumentos_parceria`), `objeto_vetor_v2` (**FLOAT[]**, 384 dimensões), `objeto_vetor_v3` (**FLOAT[]**, 384 dimensões), `created_at`, `updated_at`.
  - **V3 (atual):** `objeto_vetor_v3` - embeddings combinando `objeto` + `plano_de_trabalho` (276 embeddings)
  - **V2:** `objeto_vetor_v2` - embeddings apenas do campo `objeto` (276 embeddings)
  - **Legado:** `objeto_vetor` (96 dimensões, spaCy) - descontinuado
  - Armazena embeddings gerados por sentence-transformers.
  - **276 embeddings v3** gerados com sucesso.

- `similaridades`
  - Tabela que armazena resultados pré-calculados ou cache de similaridade entre documentos/parcerias. 
  - Contém: `id`, `parceria_origem_id`, `parceria_similar_id`, `pontuacao`, timestamps.
  - **Observação:** não é mais usada ativamente; busca semântica calcula similaridade em tempo real.

Índices e performance
----------------------
**Busca semântica atual:**
- Não usa índice HNSW (removido do projeto)
- Similaridade cosseno calculada via SQL com CTE:
  ```sql
  WITH cosine_similarity AS (
      SELECT 
          dv.parceria_id,
          (SELECT SUM(a*b) FROM unnest(dv.objeto_vetor_v2, query_vec) AS t(a,b)) /
          ((SELECT sqrt(SUM(a*a)) FROM unnest(dv.objeto_vetor_v2) AS a) *
           (SELECT sqrt(SUM(b*b)) FROM unnest(query_vec) AS b)) AS similarity
      FROM documento_vetores dv
      WHERE dv.objeto_vetor_v2 IS NOT NULL
  )
  ```
- Performance: adequada para 276 registros (scan completo tolerável)
- **Recomendação futura:** Para datasets maiores (>10k), considerar:
  - Índice GiST/GIN sobre FLOAT[] se disponível
  - Migrar para pgvector com HNSW se necessário
  - Implementar cache de resultados frequentes

API — endpoints principais
-------------------------
**Backend rodando em http://127.0.0.1:8002**

- **GET /api/v1/parcerias/semantic-busca?termo=<termo>&limit=10&offset=0&version=v3**
  - **Busca semântica V3 (padrão)** usando sentence-transformers
  - Gera embedding do termo de busca (384 dimensões)
  - Calcula similaridade cosseno com vetores em `objeto_vetor_v3` (objeto + plano_de_trabalho)
  - Fallback para `objeto_vetor_v2` se v3 não estiver disponível
  - Ordena por similaridade (maior = mais relevante)
  - **Funciona melhor com frases contextuais** do que palavras isoladas
  - Parâmetro `version`: "v2" (só objeto) ou "v3" (objeto + plano, padrão)
  - Exemplo: `termo=melhor parceria na educação&version=v3`
  - Resposta: `{ items: [{id, razao_social, objeto, plano_de_trabalho, similarity_score}], total_items: N }`
  - **Melhoria V3:** ~4% aumento na similaridade vs V2 para queries contextuais

- **GET /api/v1/parcerias/busca?termo=<termo>&limit=10&offset=0**
  - Busca textual tradicional com `unaccent(lower(...)) ILIKE unaccent(lower(:termo))`
  - Busca em múltiplos campos: razao_social, objeto, cnpj, etc.
  - Resposta paginada: `{ items: [...], total_items: N }`

- **GET /api/v1/parcerias/{id}**
  - Retorna detalhes de uma parceria específica
  - Resposta: objeto JSON com todos os campos da parceria

- **POST /api/v1/parcerias**
  - Criação de nova parceria
  - Campos aceitos: razao_social, objeto, cnpj, plano_de_trabalho (opcional), etc.
  - Gera embeddings v2 e v3 automaticamente ao inserir
  - Resposta: objeto parceria criado com ID

Frontend — Busca Semântica V3
-----------------------------
**Interface disponível em http://localhost:5173**

- **Toggle "Busca Semântica V3 (IA)"** no componente Busca.tsx
  - Padrão: ATIVADO (recomendado para queries contextuais)
  - Quando ativado: usa endpoint `/api/v1/parcerias/semantic-busca?version=v3`
  - Quando desativado: usa endpoint `/api/v1/parcerias/busca` (textual)

- **Dica exibida:** "Dica: frases funcionam melhor com a Busca Semântica (IA)"

- **Fallback inteligente** (PaginaBusca.tsx):
  - Se busca textual retorna 0 resultados, tenta automaticamente busca semântica
  - Exibe mensagem informando o fallback ao usuário

- **Preservação de estado:**
  - Escolha de busca (semântica/textual) é preservada durante paginação
  - Estado `usarBuscaSemantica` mantido em App.tsx

- **Exibição de resultados (ListaResultados.tsx):**
  - Lista mostra: razão social, objeto da parceria
  - **Chips coloridos de similaridade** quando disponível (verde: >0.6, laranja: 0.4-0.6, cinza: <0.4)
  - Link para detalhes da parceria

- **Detalhes da parceria (DetalheParceria.tsx):**
  - Exibe todos os campos incluindo plano_de_trabalho
  - **Componente PlanoTrabalho expansível** (preview 200 chars, expandir para ver completo)
  - Botões de ação e navegação

- **Adicionar nova parceria (PaginaUpload.tsx):**
  - Formulário completo com todos os campos
  - Campo **plano_de_trabalho** multiline (8 linhas)
  - Placeholder com exemplo de estrutura esperada
  - Validação e feedback de envio

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
- PostgreSQL 15 rodando na porta 5433 (banco `hub_aura`, senha: rx1800)
- Python 3.10+ com venv (`venv/` ou `.venv/`)
- Node.js + npm para o frontend

**Passos para subir ambiente de dev:**

```powershell
# 1) Ativar virtual environment Python
cd c:\Users\manoe\hub_aura
.\venv\Scripts\Activate.ps1

# 2) Instalar dependências Python (se necessário)
pip install -r requirements.txt

# 3) Configurar variável de ambiente do banco (OPCIONAL - usa fallback local se não definida)
$env:DATABASE_URL = "postgresql://postgres:SUA_SENHA@localhost:5433/hub_aura_db"

# 4) Executar migrations (Alembic) - lê DATABASE_URL ou usa alembic.ini
alembic upgrade head

# 5) Gerar planos de trabalho (opcional, se ainda não existirem)
python scripts/populate_plano_trabalho.py

# 6) Gerar embeddings v3 (sentence-transformers) - demora ~2-3 min
python scripts/generate_embeddings_v3.py

# 7) Rodar backend FastAPI
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8002
# Backend estará em http://127.0.0.1:8002

# 8) Rodar frontend (em outro terminal)
cd hub-aura-frontend
npm install  # primeira vez
npm run dev  # inicia Vite em http://localhost:5173
```

**Verificação rápida:**

```powershell
# Backend health check
curl.exe http://127.0.0.1:8002/docs

# Teste busca semântica
curl.exe "http://127.0.0.1:8002/api/v1/parcerias/semantic-busca?termo=educacao"

# Frontend
curl.exe -I http://localhost:5173
```

Testes e validação
------------------
**Teste de busca semântica V3 validado:**

✅ Query: "educação" → Retorna 10 resultados ordenados por similaridade
✅ Query contextual: "melhor parceria na educação" → Funciona corretamente
✅ Frontend: Toggle de busca semântica V3 operacional
✅ Fallback automático: Busca textual vazia → retry semântica
✅ Componente PlanoTrabalho: expansão/collapse funcionando
✅ Chips de similaridade: cores corretas baseadas em threshold
✅ Formulário upload: campo plano_de_trabalho aceita entrada

**Quality Dashboard (quality_dashboard.html):**
- ✅ 5/5 queries executadas com sucesso (100%)
- ✅ Relevância média: 49%
- ✅ V3 mostra ~4% melhoria vs V2
- ✅ Todas as queries retornam resultados

**Comandos de teste:**

```powershell
# Teste backend direto (V3)
curl.exe "http://127.0.0.1:8002/api/v1/parcerias/semantic-busca?termo=educacao&version=v3" | ConvertFrom-Json

# Comparar V2 vs V3
python scripts/compare_v2_v3.py

# Verificar quantidade de embeddings v3 gerados
# Conectar ao banco e executar:
# SELECT COUNT(*) FROM documento_vetores WHERE objeto_vetor_v3 IS NOT NULL;
# Resultado esperado: 276

# Verificar planos de trabalho
# SELECT COUNT(*) FROM instrumentos_parceria WHERE plano_de_trabalho IS NOT NULL;
# Resultado esperado: 276

# Gerar quality dashboard
python scripts/quality_dashboard.py
# Abre quality_dashboard.html no browser
```

**Métricas de performance:**
- Geração de planos de trabalho: ~1-2s total (276 registros)
- Geração de embeddings v3: ~0.5-1s por parceria (batch de 276 em ~2-3 min)
- Busca semântica V3: <200ms para 276 registros (scan completo)
- Caching do modelo: modelo carregado 1x no startup (não recarrega por request)
- Tamanho médio plano_de_trabalho: ~500-1000 caracteres

Problemas conhecidos e soluções aplicadas
---------------------------------------
### ✅ Resolvidos:

1. **Busca semântica só funcionava com palavras isoladas**
   - **Causa:** Endpoint usava `objeto_vetor` (spaCy 96d) em vez de `objeto_vetor_v2` (sentence-transformers 384d)
   - **Solução:** Atualizado `main.py` para usar coluna correta e modelo sentence-transformers

2. **Erro de sintaxe SQL com operador `<=>`**
   - **Causa:** Tentativa de usar operador pgvector em FLOAT[]
   - **Solução:** Implementado cálculo de similaridade cosseno com CTE e unnest

3. **Endpoint /semantic-busca retornava 422**
   - **Causa:** Rota capturada por `/{parceria_id}` (ordem de definição)
   - **Solução:** Movido endpoint semântico ANTES da rota parametrizada

4. **"Campos sumiram" no frontend**
   - **Causa:** Import faltante de `Typography` em Busca.tsx
   - **Solução:** Adicionado import correto do MUI

5. **"Nenhum resultado" mesmo com dados no banco**
   - **Causa:** App.tsx não passava parâmetro `semantica` para função de busca
   - **Solução:** Implementado estado `usarBuscaSemantica` e propagação correta

### ⚠️ Observações:

- **Encoding:** CSV original em CP1252; dados importados corretamente mas alguns caracteres especiais podem aparecer com mojibake visual (não afeta busca)
- **Performance:** Scan completo tolerável para 276 registros; considerar índice para >10k
- **Modelo AI:** Download automático do modelo sentence-transformers na primeira execução (~90MB)

Próximos passos recomendados
---------------------------
### Curto prazo:
1. **Otimização de performance** (quando dataset crescer)
   - Implementar cache de resultados frequentes
   - Considerar índice sobre FLOAT[] ou migrar para pgvector com HNSW
   - Batch processing para geração de embeddings

2. **Melhorias de UX**
   - ✅ Adicionar indicador de loading durante busca semântica
   - ✅ Exibir score de similaridade de forma mais visual (chips coloridos)
   - ✅ Adicionar preview de plano_de_trabalho nos cards de resultado (box destacado com ícone)
   - ✅ Indicador de loading visual no campo de busca e botão
   - Implementar highlight de termos relevantes nos resultados (futuro)

3. **Qualidade de dados**
   - Normalizar encoding de caracteres especiais (reimportar CSV como UTF-8)
   - Implementar deduplicação automática de parcerias
   - ✅ Adicionar validação de campos obrigatórios (FormData)
   - Permitir edição de planos de trabalho existentes via UI

### Médio prazo:
4. **Testes automatizados**
   - Testes de integração para endpoints de busca
   - Testes unitários para cálculo de similaridade
   - CI/CD pipeline com GitHub Actions

5. **Monitoramento e observabilidade**
   - Logging estruturado (JSON logs)
   - Métricas de latência de busca
   - Dashboard com estatísticas de uso

6. **Features avançadas**
   - Filtros combinados (busca semântica + filtros por data, tipo, etc.)
   - Busca multi-campo (não só `objeto`, mas também `razao_social`)
   - Recomendação de parcerias similares (relacionados)

### Longo prazo:
7. **Produção**
   - Containerização com Docker (backend + frontend)
   - Deploy em cloud (AWS, Azure, GCP)
   - Backup automático do banco
   - Estratégia de rollback e versionamento

Histórico de versões
-------------------
### v3.1 - Correções de Segurança e Infraestrutura (2025-10-31)
- ✅ **Segurança:** Removidas credenciais hardcoded do código-fonte
- ✅ main.py, migrations/env.py, scripts/* agora leem DATABASE_URL do ambiente
- ✅ alembic.ini sem senha (usa env.py override via DATABASE_URL)
- ✅ Scripts utilitários (utilities/) usam PGHOST/PGPORT/PGUSER/PGPASSWORD
- ✅ **Backend:** Porta atualizada de 8001 → 8002 (conflitos resolvidos)
- ✅ **Endpoint POST /api/v1/parcerias** registrado com decorator @app.post
- ✅ **Validação de uploads:** PDF verificado por content-type + limite 10MB
- ✅ **Proxy Vite:** Corrigido de 8001 → 8002 em vite.config.ts
- ✅ Frontend config (api.ts) usa localhost:8002
- ✅ Referências a ngrok removidas do código
- ⚠️ Fallback local para dev preservado nos scripts (não usar em produção)

### v3.0 - Plano de Trabalho + Embeddings V3 (2025-10-30)
- ✅ Adicionado campo `plano_de_trabalho` (TEXT) na tabela `instrumentos_parceria`
- ✅ Migration Alembic para adicionar coluna plano_de_trabalho
- ✅ 276 planos de trabalho gerados automaticamente com conteúdo sintético
- ✅ Implementação de embeddings V3 (objeto + plano_de_trabalho combinados)
- ✅ Migration Alembic para `objeto_vetor_v3` (FLOAT[], 384 dimensões)
- ✅ 276 embeddings v3 gerados com sucesso
- ✅ Endpoint `/api/v1/parcerias/semantic-busca` com parâmetro `version` (v2/v3)
- ✅ Frontend atualizado com componente `PlanoTrabalho` (expansível)
- ✅ Campo `similarity_score` adicionado à interface Parceria
- ✅ Chips de similaridade nos resultados de busca
- ✅ Formulário "Adicionar Novo Acordo" com campo plano_de_trabalho
- ✅ Quality dashboard com métricas de performance (5/5 queries, 49% relevância)
- ✅ V3 mostra ~4% melhoria vs V2 em similaridade

### v2.0 - Busca Semântica com IA (2025-10-29)
- ✅ Implementação de busca semântica usando sentence-transformers
- ✅ Modelo: paraphrase-multilingual-MiniLM-L12-v2 (384 dimensões)
- ✅ 276 embeddings gerados com sucesso
- ✅ Frontend com toggle de busca semântica
- ✅ Cálculo de similaridade cosseno via SQL (CTE + unnest)
- ✅ Fallback inteligente (textual → semântica)
- ✅ Migration Alembic para objeto_vetor_v2 (FLOAT[])

### v1.0 - Base inicial (2025-10-28)
- Backend FastAPI com busca textual
- PostgreSQL com extensão unaccent
- Frontend React + Vite + TypeScript
- spaCy para embeddings v1 (96 dimensões - descontinuado)

Anexos e referências rápidas
----------------------------
### Onde encontrar:
- **Migrations:** `migrations/versions/`
- **Scripts:** `scripts/` (generate_embeddings_v2.py, import_csv.py)
- **Backend:** `main.py` (raiz do projeto)
- **Frontend:** `hub-aura-frontend/src/` (App.tsx, components/)
- **Documentação:** `*.md` na raiz (START_HERE.md, EMBEDDINGS_V2_REPORT.md, etc.)

### Comandos úteis:

```powershell
# Verificar status do banco
psql -h localhost -p 5433 -U postgres -d hub_aura -c "SELECT COUNT(*) FROM documento_vetores WHERE objeto_vetor_v3 IS NOT NULL;"

# Regenerar planos de trabalho
python scripts/populate_plano_trabalho.py

# Regenerar embeddings v3 (se necessário)
python scripts/generate_embeddings_v3.py

# Comparar performance V2 vs V3
python scripts/compare_v2_v3.py

# Ver logs do backend
# (backend roda em foreground, logs aparecem no terminal)

# Rebuild frontend
cd hub-aura-frontend
npm run build

# Ver git log
git log --oneline -10
```

### Links importantes:
- **FastAPI Docs:** http://127.0.0.1:8002/docs (Swagger UI automático)
- **Frontend:** http://localhost:5173
- **Modelo AI:** https://huggingface.co/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2

Contato/suporte
--------------
Para dúvidas ou suporte, consulte:
- `START_HERE.md` — guia de início rápido
- `EMBEDDINGS_V2_REPORT.md` — detalhes técnicos da implementação
- Swagger UI (http://127.0.0.1:8002/docs) — documentação interativa da API

**Status atual:** Sistema funcionando, testado e validado ✅
**Versão:** v3.1 (2025-10-31) — Segurança e infraestrutura aprimoradas

Fim do documento.
