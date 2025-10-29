"""Script para gerar embeddings com SentenceTransformers e popular a coluna
`documento_vetores.objeto_vetor_v2` (FLOAT[]).

Uso:
    python scripts/generate_embeddings_v2.py

Notas:
- Requer o pacote `sentence-transformers` e suas dependências (p.ex. torch).
- Execute as migrations antes (para criar a coluna).
"""
from sqlalchemy import create_engine, text
from math import ceil
import os

# Configuração do banco (ajuste se necessário - porta 5433 para PostgreSQL 15)
DB_URL = os.environ.get('DATABASE_URL', 'postgresql://postgres:rx1800@localhost:5433/hub_aura_db')
engine = create_engine(DB_URL)

def chunked(iterable, size):
    for i in range(0, len(iterable), size):
        yield iterable[i:i+size]

def main():
    try:
        from sentence_transformers import SentenceTransformer
    except Exception as e:
        print("Erro: sentence-transformers não encontrado. Instale com 'pip install sentence-transformers'.")
        raise

    model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
    print("Modelo carregado: paraphrase-multilingual-MiniLM-L12-v2")

    with engine.connect() as conn:
        # Buscar todos os instrumentos com texto no campo objeto
        rows = conn.execute(text("SELECT id, objeto FROM instrumentos_parceria WHERE objeto IS NOT NULL"))
        data = rows.mappings().all()

        print(f"Registros com texto: {len(data)}")

        batch_size = 64
        total_batches = ceil(len(data) / batch_size) if data else 0
        for batch_index, batch in enumerate(chunked(data, batch_size), start=1):
            texts = [r['objeto'] or '' for r in batch]
            ids = [r['id'] for r in batch]
            embeddings = model.encode(texts, show_progress_bar=False)

            for pid, emb in zip(ids, embeddings):
                emb_list = emb.tolist()
                # Tenta atualizar; se não existir linha em documento_vetores para aquele parceria_id, insere
                # Usando ARRAY ao invés de vector type
                update_stmt = text("""
                    UPDATE documento_vetores SET objeto_vetor_v2 = :vetor
                    WHERE parceria_id = :pid
                """)
                res = conn.execute(update_stmt, {"vetor": emb_list, "pid": pid})
                if res.rowcount == 0:
                    insert_stmt = text("""
                        INSERT INTO documento_vetores (parceria_id, objeto_vetor_v2)
                        VALUES (:pid, :vetor)
                    """)
                    conn.execute(insert_stmt, {"pid": pid, "vetor": emb_list})

            conn.commit()
            print(f"Batch {batch_index}/{total_batches} processado")

    print("Embeddings v2 gerados com sucesso.")

if __name__ == '__main__':
    main()
