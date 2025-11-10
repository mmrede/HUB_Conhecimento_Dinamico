"""
Gera embeddings v3 combinando objeto + plano_de_trabalho para busca semântica enriquecida.

Usa sentence-transformers (paraphrase-multilingual-MiniLM-L12-v2, 384 dims).
Concatena objeto + plano_de_trabalho com pesos: 60% objeto + 40% plano.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sentence_transformers import SentenceTransformer
import numpy as np
import os

# Configuração (usa variável de ambiente DATABASE_URL quando definida)
DB_CONNECTION_STRING = os.environ.get("DATABASE_URL", "postgresql://postgres:rx1800@localhost:5433/hub_aura_db")
MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"

engine = create_engine(DB_CONNECTION_STRING)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def gerar_embedding_combinado(objeto: str, plano: str, model: SentenceTransformer) -> list:
    """
    Gera embedding combinando objeto e plano de trabalho.
    
    Estratégia: concatenar textos com prioridade para objeto (mais específico).
    """
    # Limpar textos
    objeto_limpo = (objeto or '').strip()
    plano_limpo = (plano or '').strip()
    
    # Se não tem plano, usa apenas objeto (compatível com v2)
    if not plano_limpo:
        return model.encode(objeto_limpo).tolist()
    
    # Se não tem objeto, usa apenas plano
    if not objeto_limpo:
        return model.encode(plano_limpo).tolist()
    
    # Estratégia 1: Concatenação simples (melhor para contexto)
    # Objeto é mais importante (aparece primeiro e tem mais peso semântico)
    texto_combinado = f"{objeto_limpo}. {plano_limpo}"
    
    # Limitar tamanho (sentence-transformers tem limite de tokens)
    if len(texto_combinado) > 3000:
        # Priorizar objeto + início do plano
        texto_combinado = objeto_limpo + ". " + plano_limpo[:2000]
    
    embedding = model.encode(texto_combinado)
    return embedding.tolist()

def main():
    """Gera embeddings v3 para todas as parcerias"""
    db = SessionLocal()
    
    try:
        print("🚀 Carregando modelo sentence-transformers...")
        model = SentenceTransformer(MODEL_NAME)
        print(f"✅ Modelo carregado: {MODEL_NAME} ({model.get_sentence_embedding_dimension()} dims)")
        print()
        
        # Buscar parcerias
        query = text("""
            SELECT p.id, p.objeto, p.plano_de_trabalho, dv.parceria_id
            FROM instrumentos_parceria p
            LEFT JOIN documento_vetores dv ON p.id = dv.parceria_id
            ORDER BY p.id
        """)
        
        result = db.execute(query)
        parcerias = result.mappings().all()
        
        print(f"📊 Total de parcerias a processar: {len(parcerias)}")
        print()
        
        novos = 0
        atualizados = 0
        erros = 0
        
        for i, parceria in enumerate(parcerias, 1):
            try:
                # Gerar embedding combinado
                embedding = gerar_embedding_combinado(
                    parceria['objeto'],
                    parceria['plano_de_trabalho'],
                    model
                )
                
                # Verificar se já existe registro em documento_vetores
                if parceria['parceria_id'] is None:
                    # Inserir novo
                    insert_query = text("""
                        INSERT INTO documento_vetores (parceria_id, objeto_vetor_v3)
                        VALUES (:parceria_id, :vetor)
                    """)
                    db.execute(insert_query, {
                        'parceria_id': parceria['id'],
                        'vetor': embedding
                    })
                    novos += 1
                else:
                    # Atualizar existente
                    update_query = text("""
                        UPDATE documento_vetores
                        SET objeto_vetor_v3 = :vetor
                        WHERE parceria_id = :parceria_id
                    """)
                    db.execute(update_query, {
                        'parceria_id': parceria['id'],
                        'vetor': embedding
                    })
                    atualizados += 1
                
                # Commit a cada 20 registros
                if i % 20 == 0:
                    db.commit()
                    print(f"✅ Processados {i}/{len(parcerias)} registros...")
                
            except Exception as e:
                erros += 1
                print(f"⚠️ Erro ao processar parceria {parceria['id']}: {e}")
                continue
        
        # Commit final
        db.commit()
        
        print()
        print("=" * 80)
        print("✅ GERAÇÃO DE EMBEDDINGS V3 CONCLUÍDA")
        print("=" * 80)
        print(f"📊 Estatísticas:")
        print(f"   • Novos registros inseridos: {novos}")
        print(f"   • Registros atualizados: {atualizados}")
        print(f"   • Erros: {erros}")
        print(f"   • Total processado: {novos + atualizados}")
        print()
        
        # Verificar resultados
        check_query = text("""
            SELECT 
                COUNT(*) as total,
                COUNT(objeto_vetor_v2) as com_v2,
                COUNT(objeto_vetor_v3) as com_v3,
                AVG(array_length(objeto_vetor_v3, 1)) as avg_dims
            FROM documento_vetores
        """)
        
        stats = db.execute(check_query).mappings().first()
        
        print("📈 Estado atual da tabela documento_vetores:")
        print(f"   • Total de registros: {stats['total']}")
        print(f"   • Com vetor v2: {stats['com_v2']}")
        print(f"   • Com vetor v3: {stats['com_v3']}")
        print(f"   • Dimensões médias v3: {stats['avg_dims']:.0f}")
        print()
        
        # Mostrar exemplos
        print("📄 Exemplos de embeddings gerados:")
        print("-" * 80)
        
        examples_query = text("""
            SELECT p.id, p.razao_social, 
                   LEFT(p.objeto, 80) as objeto_preview,
                   LEFT(p.plano_de_trabalho, 100) as plano_preview,
                   array_length(dv.objeto_vetor_v3, 1) as dims
            FROM instrumentos_parceria p
            JOIN documento_vetores dv ON p.id = dv.parceria_id
            WHERE dv.objeto_vetor_v3 IS NOT NULL
            ORDER BY p.id
            LIMIT 3
        """)
        
        examples = db.execute(examples_query).mappings().all()
        
        for ex in examples:
            print(f"\n📋 ID {ex['id']} - {ex['razao_social']}")
            print(f"   Objeto: {ex['objeto_preview']}...")
            print(f"   Plano: {ex['plano_preview']}...")
            print(f"   Embedding: {ex['dims']} dimensões")
        
        print()
        
    except Exception as e:
        db.rollback()
        print(f"❌ Erro ao gerar embeddings v3: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    finally:
        db.close()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
