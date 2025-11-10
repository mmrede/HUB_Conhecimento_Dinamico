# Plano de Migração: pgvector com HNSW

**Status:** NÃO IMPLEMENTADO (não necessário para 276 registros)  
**Trigger de Implementação:** Dataset > 5.000 registros OU busca > 500ms

## Performance Atual vs Esperada com HNSW

| Dataset Size | Scan Completo (atual) | HNSW (pgvector) | Ganho |
|--------------|----------------------|-----------------|-------|
| 276          | ~150ms ✅            | ~80ms           | 1.9x  |
| 1.000        | ~350ms               | ~60ms           | 5.8x  |
| 10.000       | ~900ms ⚠️            | ~40ms ✅        | 22.5x |
| 100.000      | ~8s ❌               | ~50ms ✅        | 160x  |

## Quando Implementar?

### ✅ Triggers de Migração:
- Dataset ultrapassar 5.000 registros
- Tempo médio de busca > 500ms
- Planos de crescimento rápido (>1.000 registros/mês)

### ❌ Não implementar se:
- Dataset < 5.000 registros
- Performance atual satisfatória (<300ms)
- Precisão de 100% é requisito crítico

## Passo a Passo da Migração

### 1. Instalar extensão pgvector

```powershell
# Baixar e instalar pgvector no PostgreSQL 15
# https://github.com/pgvector/pgvector

# No banco:
$env:PGPASSWORD = "rx1800"
& "C:\Program Files\PostgreSQL\15\bin\psql.exe" `
  -h localhost -p 5433 -U postgres -d hub_aura_db `
  -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

### 2. Criar migration Alembic

```python
# migrations/versions/YYYYMMDD_migrate_to_pgvector.py

"""Migração para pgvector com índice HNSW

Revision ID: migrate_to_pgvector
Revises: 20251030_add_objeto_vetor_v3
Create Date: YYYY-MM-DD

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ARRAY
from pgvector.sqlalchemy import Vector

revision = 'migrate_to_pgvector'
down_revision = '20251030_add_objeto_vetor_v3'

def upgrade():
    # Criar extensão vector
    op.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    
    # Criar novas colunas do tipo vector
    op.execute("""
        ALTER TABLE documento_vetores 
        ADD COLUMN IF NOT EXISTS objeto_vetor_v2_vector vector(384);
    """)
    
    op.execute("""
        ALTER TABLE documento_vetores 
        ADD COLUMN IF NOT EXISTS objeto_vetor_v3_vector vector(384);
    """)
    
    # Copiar dados de FLOAT[] para vector
    op.execute("""
        UPDATE documento_vetores 
        SET objeto_vetor_v2_vector = objeto_vetor_v2::vector
        WHERE objeto_vetor_v2 IS NOT NULL;
    """)
    
    op.execute("""
        UPDATE documento_vetores 
        SET objeto_vetor_v3_vector = objeto_vetor_v3::vector
        WHERE objeto_vetor_v3 IS NOT NULL;
    """)
    
    # Criar índices HNSW
    # m=16: número de conexões por nó (padrão: 16, range: 4-64)
    # ef_construction=64: tamanho da fila durante construção (padrão: 64, range: 10-200)
    op.execute("""
        CREATE INDEX idx_objeto_vetor_v2_hnsw 
        ON documento_vetores 
        USING hnsw (objeto_vetor_v2_vector vector_cosine_ops)
        WITH (m = 16, ef_construction = 64);
    """)
    
    op.execute("""
        CREATE INDEX idx_objeto_vetor_v3_hnsw 
        ON documento_vetores 
        USING hnsw (objeto_vetor_v3_vector vector_cosine_ops)
        WITH (m = 16, ef_construction = 64);
    """)
    
    print("✅ Migração para pgvector concluída!")
    print("⚠️  Colunas antigas (FLOAT[]) mantidas para rollback")
    print("📊 Próximo passo: atualizar main.py para usar vector")

def downgrade():
    # Remover índices
    op.execute("DROP INDEX IF EXISTS idx_objeto_vetor_v3_hnsw;")
    op.execute("DROP INDEX IF EXISTS idx_objeto_vetor_v2_hnsw;")
    
    # Remover colunas vector
    op.execute("ALTER TABLE documento_vetores DROP COLUMN IF EXISTS objeto_vetor_v3_vector;")
    op.execute("ALTER TABLE documento_vetores DROP COLUMN IF EXISTS objeto_vetor_v2_vector;")
    
    # Nota: não removemos a extensão vector para evitar problemas
    print("✅ Rollback para FLOAT[] concluído")
```

### 3. Atualizar main.py

```python
# main.py

from pgvector.sqlalchemy import Vector
from sqlalchemy import text

# Modelo SQLAlchemy
class DocumentoVetores(Base):
    __tablename__ = "documento_vetores"
    
    id = Column(Integer, primary_key=True)
    parceria_id = Column(Integer, ForeignKey("instrumentos_parceria.id"))
    
    # Manter colunas antigas para compatibilidade
    objeto_vetor_v2 = Column(ARRAY(Float))
    objeto_vetor_v3 = Column(ARRAY(Float))
    
    # Novas colunas pgvector
    objeto_vetor_v2_vector = Column(Vector(384))
    objeto_vetor_v3_vector = Column(Vector(384))

# Endpoint de busca atualizado
@app.get("/api/v1/parcerias/semantic-busca")
async def busca_semantica(
    termo: str,
    version: str = "v3",
    limit: int = 10,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    # Gerar embedding da query
    query_embedding = sentence_model.encode(termo)
    
    # Escolher coluna baseado na versão
    vector_column = "objeto_vetor_v3_vector" if version == "v3" else "objeto_vetor_v2_vector"
    
    # Query usando operador pgvector <=>
    sql = text(f"""
        SELECT 
            ip.*,
            1 - (dv.{vector_column} <=> :query_vector) AS similarity_score
        FROM instrumentos_parceria ip
        JOIN documento_vetores dv ON dv.parceria_id = ip.id
        WHERE dv.{vector_column} IS NOT NULL
        ORDER BY dv.{vector_column} <=> :query_vector
        LIMIT :limit OFFSET :offset
    """)
    
    result = db.execute(sql, {
        "query_vector": query_embedding.tolist(),
        "limit": limit,
        "offset": offset
    })
    
    return {"items": result.fetchall(), "total_items": result.rowcount}
```

### 4. Tuning do índice HNSW

Após implementar, ajustar parâmetros baseado em métricas:

```sql
-- Parâmetro de busca (runtime, não requer rebuild)
-- ef_search: quantos vizinhos explorar durante busca
-- Maior = mais preciso, mais lento
SET hnsw.ef_search = 40;  -- padrão: 40, range: 10-200

-- Para rebuild com novos parâmetros:
DROP INDEX idx_objeto_vetor_v3_hnsw;
CREATE INDEX idx_objeto_vetor_v3_hnsw 
ON documento_vetores 
USING hnsw (objeto_vetor_v3_vector vector_cosine_ops)
WITH (
    m = 24,              -- mais conexões = melhor recall, mais espaço
    ef_construction = 100 -- maior = melhor qualidade, construção mais lenta
);
```

### 5. Benchmarking

Script para comparar performance antes/depois:

```python
# scripts/benchmark_pgvector.py

import time
import psycopg2
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

queries = [
    "educação infantil",
    "saúde pública",
    "assistência social",
    "cultura e arte",
    "esporte e lazer"
]

conn = psycopg2.connect(
    "host=localhost port=5433 dbname=hub_aura_db user=postgres password=rx1800"
)

for query in queries:
    embedding = model.encode(query).tolist()
    
    # Testar com scan completo (FLOAT[])
    start = time.time()
    cur = conn.cursor()
    cur.execute("""
        WITH cosine_similarity AS (
            SELECT parceria_id,
                   (SELECT SUM(a*b) FROM unnest(objeto_vetor_v3, %s) AS t(a,b)) /
                   ((SELECT sqrt(SUM(a*a)) FROM unnest(objeto_vetor_v3) AS a) *
                    (SELECT sqrt(SUM(b*b)) FROM unnest(%s) AS b)) AS similarity
            FROM documento_vetores
            WHERE objeto_vetor_v3 IS NOT NULL
        )
        SELECT * FROM cosine_similarity ORDER BY similarity DESC LIMIT 10;
    """, (embedding, embedding))
    results_scan = cur.fetchall()
    time_scan = (time.time() - start) * 1000
    
    # Testar com HNSW (pgvector)
    start = time.time()
    cur.execute("""
        SELECT parceria_id,
               1 - (objeto_vetor_v3_vector <=> %s::vector) AS similarity
        FROM documento_vetores
        WHERE objeto_vetor_v3_vector IS NOT NULL
        ORDER BY objeto_vetor_v3_vector <=> %s::vector
        LIMIT 10;
    """, (embedding, embedding))
    results_hnsw = cur.fetchall()
    time_hnsw = (time.time() - start) * 1000
    
    print(f"\nQuery: '{query}'")
    print(f"  Scan completo: {time_scan:.1f}ms")
    print(f"  HNSW:         {time_hnsw:.1f}ms")
    print(f"  Speedup:      {time_scan/time_hnsw:.1f}x")
    
    # Calcular recall (quantos resultados batem)
    ids_scan = set([r[0] for r in results_scan])
    ids_hnsw = set([r[0] for r in results_hnsw])
    recall = len(ids_scan & ids_hnsw) / len(ids_scan) * 100
    print(f"  Recall:       {recall:.1f}%")

conn.close()
```

## Métricas de Decisão

### Implementar quando:
- ✅ Tempo médio de busca > 500ms consistentemente
- ✅ Dataset > 5.000 registros
- ✅ Recall de 95% é aceitável (vs 100% atual)
- ✅ Equipe tem capacidade de debug/tuning

### Não implementar se:
- ❌ Dataset < 5.000 registros
- ❌ Performance atual < 300ms
- ❌ Precisão de 100% é requisito legal/regulatório
- ❌ Equipe sem experiência com pgvector

## Custos da Migração

### Tempo de implementação:
- Instalação pgvector: 30 min
- Migration + testes: 2-4 horas
- Tuning e otimização: 2-4 horas
- **Total:** ~1 dia de trabalho

### Riscos:
- ⚠️ Perda de 1-5% de recall
- ⚠️ Complexidade adicional (troubleshooting)
- ⚠️ Downtime durante migration (~5-10 min)

### Benefícios:
- ✅ 10-50x speedup em datasets grandes
- ✅ Escalabilidade garantida
- ✅ Uso de tecnologia padrão da indústria

## Alternativas

Se performance se tornar problema ANTES de implementar pgvector:

1. **Cache de resultados frequentes** (Redis/Memcached)
2. **Pré-computar top-K similaridades** (tabela similaridades)
3. **Sharding por categoria** (se dados permitirem)
4. **Filtros pré-busca** (reduzir espaço de busca)

## Conclusão

**Para seu caso atual (276 registros):**
- ❌ **NÃO implementar pgvector/HNSW agora**
- ✅ **Manter scan completo atual**
- 📊 **Monitorar performance conforme dataset cresce**
- 🔄 **Revisar decisão quando atingir 5.000 registros**

---

**Última revisão:** 30/10/2025  
**Próxima revisão:** Quando dataset > 2.500 registros
