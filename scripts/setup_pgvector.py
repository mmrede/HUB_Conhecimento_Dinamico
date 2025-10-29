"""Script para verificar e configurar pgvector."""
import sys
from sqlalchemy import create_engine, text

def main():
    """Função principal."""
    # Configuração do banco
    DB_URL = 'postgresql://postgres:rx1800@localhost:5432/hub_aura_db'
    
    try:
        # Conecta ao banco
        engine = create_engine(DB_URL)
        
        with engine.connect() as conn:
            # Verifica se a extensão vector já existe
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT 1 
                    FROM pg_extension 
                    WHERE extname = 'vector'
                );
            """))
            vector_exists = result.scalar()
            
            if vector_exists:
                print("Extensão pgvector já está instalada!")
            else:
                print("Instalando extensão pgvector...")
                # Tenta criar a extensão
                conn.execute(text('CREATE EXTENSION vector;'))
                conn.commit()
                print("Extensão pgvector instalada com sucesso!")
                
    except Exception as e:
        print(f"Erro: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()