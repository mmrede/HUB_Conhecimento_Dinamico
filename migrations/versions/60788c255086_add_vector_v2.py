"""add_vector_v2

Revision ID: 60788c255086
Revises: 
Create Date: 2025-10-29 17:44:07.502438

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '60788c255086'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Cria a tabela documento_vetores se não existir
    # Usando ARRAY ao invés de vector type (fallback sem pgvector)
    op.execute('''
    CREATE TABLE IF NOT EXISTS documento_vetores (
        id SERIAL PRIMARY KEY,
        parceria_id INTEGER REFERENCES instrumentos_parceria(id),
        objeto_vetor_v2 FLOAT[]
    );
    ''')
    
    # Cria índice simples para parceria_id (para joins rápidos)
    op.execute('''
    CREATE INDEX IF NOT EXISTS documento_vetores_parceria_idx 
    ON documento_vetores (parceria_id);
    ''')


def downgrade() -> None:
    """Downgrade schema."""
    # Remove o índice
    op.execute('DROP INDEX IF EXISTS documento_vetores_parceria_idx;')
    
    # Remove a tabela
    op.execute('DROP TABLE IF EXISTS documento_vetores;')
