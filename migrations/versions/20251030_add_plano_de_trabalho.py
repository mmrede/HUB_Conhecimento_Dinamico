"""add plano_de_trabalho to instrumentos_parceria

Revision ID: 20251030_add_plano
Revises: 60788c255086
Create Date: 2025-10-30 00:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20251030_add_plano'
down_revision: Union[str, Sequence[str], None] = '60788c255086'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add column plano_de_trabalho (TEXT, nullable) to instrumentos_parceria"""
    try:
        op.add_column('instrumentos_parceria', sa.Column('plano_de_trabalho', sa.Text(), nullable=True))
    except Exception:
        # Fallback idempotente: tentar via SQL bruto (não falha se já existir)
        op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name='instrumentos_parceria' AND column_name='plano_de_trabalho'
            ) THEN
                ALTER TABLE instrumentos_parceria ADD COLUMN plano_de_trabalho TEXT;
            END IF;
        END$$;
        """)


def downgrade() -> None:
    """Remove column plano_de_trabalho"""
    try:
        op.drop_column('instrumentos_parceria', 'plano_de_trabalho')
    except Exception:
        op.execute('ALTER TABLE IF EXISTS instrumentos_parceria DROP COLUMN IF EXISTS plano_de_trabalho;')
