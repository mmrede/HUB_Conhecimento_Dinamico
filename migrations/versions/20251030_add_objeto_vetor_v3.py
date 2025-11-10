"""add objeto_vetor_v3 for enriched embeddings

Revision ID: 20251030_add_v3
Revises: 20251030_add_plano
Create Date: 2025-10-30 01:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20251030_add_v3'
down_revision: Union[str, Sequence[str], None] = '20251030_add_plano'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add objeto_vetor_v3 column (FLOAT[], nullable) for enriched embeddings (objeto + plano_de_trabalho)"""
    try:
        op.add_column('documento_vetores', sa.Column('objeto_vetor_v3', sa.ARRAY(sa.Float()), nullable=True))
    except Exception:
        # Fallback idempotente via SQL bruto
        op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name='documento_vetores' AND column_name='objeto_vetor_v3'
            ) THEN
                ALTER TABLE documento_vetores ADD COLUMN objeto_vetor_v3 FLOAT[];
            END IF;
        END$$;
        """)


def downgrade() -> None:
    """Remove objeto_vetor_v3 column"""
    try:
        op.drop_column('documento_vetores', 'objeto_vetor_v3')
    except Exception:
        op.execute('ALTER TABLE IF EXISTS documento_vetores DROP COLUMN IF EXISTS objeto_vetor_v3;')
