# Scripts do Projeto Hub Aura

Este diretório contém scripts essenciais e utilitários para o projeto.

## 📁 Estrutura

### Scripts Principais (Produção/Desenvolvimento)

- **`import_csv.py`** - Importa dados do CSV (Instrumento_Parceria_XLSX_csv.csv) para o banco PostgreSQL
  - Codificação: CP1252
  - Cria registros em `instrumentos_parceria`
  - Uso: `python scripts/import_csv.py`

- **`populate_plano_trabalho.py`** - Gera planos de trabalho sintéticos para todos os instrumentos
  - 5 templates diferentes
  - Popula campo `plano_de_trabalho` (TEXT)
  - ~276 registros
  - Uso: `python scripts/populate_plano_trabalho.py`

- **`generate_embeddings_v2.py`** - Gera embeddings V2 (apenas campo `objeto`)
  - Modelo: sentence-transformers (paraphrase-multilingual-MiniLM-L12-v2)
  - Dimensões: 384
  - Popula: `objeto_vetor_v2` (FLOAT[])
  - Uso: `python scripts/generate_embeddings_v2.py`

- **`generate_embeddings_v3.py`** - Gera embeddings V3 (objeto + plano_de_trabalho)
  - **VERSÃO RECOMENDADA** para produção
  - Combina objeto + plano (máx 3000 chars)
  - Dimensões: 384
  - Popula: `objeto_vetor_v3` (FLOAT[])
  - ~4% melhor que V2 em qualidade
  - Uso: `python scripts/generate_embeddings_v3.py`

- **`compare_v2_v3.py`** - Ferramenta de comparação entre embeddings V2 e V3
  - Testa mesmas queries em ambas versões
  - Exibe diferenças de similaridade
  - Uso: `python scripts/compare_v2_v3.py`

- **`quality_dashboard.py`** - Gera dashboard HTML com métricas de qualidade
  - Executa suite de queries de teste
  - Calcula métricas: relevância, cobertura, performance
  - Gera `quality_dashboard.html`
  - Uso: `python scripts/quality_dashboard.py` (abre browser automaticamente)

### Utilitários (scripts/)utilities/

Scripts auxiliares para diagnóstico e manutenção:

- **`analyze_search_quality.py`** - Análise detalhada de qualidade de buscas
- **`deduplicate_instrumentos.py`** - Remove duplicatas na tabela instrumentos_parceria
- **`detect_mojibake.py`** - Detecta problemas de encoding (mojibake)
- **`fix_mojibake.py`** - Corrige problemas de encoding
- **`generate_pdf_report.py`** - Gera relatórios em PDF
- **`report_analyzer.py`** - Analisa relatórios gerados
- **`test_planos.py`** - Valida conteúdo dos planos de trabalho gerados

## 🚀 Workflow Típico

### 1. Primeiro Setup (uma vez)

```powershell
# Ativar venv
.\venv\Scripts\Activate.ps1

# Importar dados do CSV
python scripts/import_csv.py

# Gerar planos de trabalho
python scripts/populate_plano_trabalho.py

# Gerar embeddings V3
python scripts/generate_embeddings_v3.py
```

### 2. Validação de Qualidade

```powershell
# Gerar dashboard de qualidade
python scripts/quality_dashboard.py

# Comparar V2 vs V3 (opcional)
python scripts/compare_v2_v3.py
```

### 3. Regeneração (se necessário)

```powershell
# Apenas planos de trabalho
python scripts/populate_plano_trabalho.py

# Apenas embeddings V3
python scripts/generate_embeddings_v3.py

# Ambos
python scripts/populate_plano_trabalho.py && python scripts/generate_embeddings_v3.py
```

## 📊 Métricas de Performance

- **Import CSV:** ~2-5s (276 registros)
- **Populate planos:** ~1-2s (276 registros)
- **Generate embeddings V2:** ~2-3 min (276 embeddings @ ~0.5s cada)
- **Generate embeddings V3:** ~2-3 min (276 embeddings @ ~0.5s cada)
- **Quality dashboard:** ~5-10s (5 queries de teste)

## ⚠️ Importante

- **Sempre use V3 para novas implementações** (melhor qualidade)
- **V2 mantido para compatibilidade** com análises históricas
- Scripts de utilities/ **não são necessários** para operação normal
- **Backup do banco** antes de regenerar embeddings em produção

## 🔗 Referências

- Documentação principal: `DOCUMENTATION.md`
- Changelog V3.1: `CHANGELOG_V3.1.md`
- Relatório embeddings V2: `EMBEDDINGS_V2_REPORT.md`
