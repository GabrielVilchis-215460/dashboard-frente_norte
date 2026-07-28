"""Add descripcion, fecha_fin and horario fields to eventos

Revision ID: a1b2c3d4e5f6
Revises: c9d4b82f7e15
Create Date: 2026-07-16 00:01:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = 'd23dfcf53fbd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('eventos', sa.Column('descripcion', sa.Text(), nullable=True))
    op.add_column('eventos', sa.Column('fecha_fin', sa.Date(), nullable=True))
    op.add_column('eventos', sa.Column('hora_inicio', sa.Time(), nullable=True))
    op.add_column('eventos', sa.Column('hora_fin', sa.Time(), nullable=True))
    # Ampliar enfoque y tipo de String(50) a String(100)
    op.alter_column('eventos', 'enfoque', type_=sa.String(100))
    op.alter_column('eventos', 'tipo', type_=sa.String(100))


def downgrade() -> None:
    op.drop_column('eventos', 'hora_fin')
    op.drop_column('eventos', 'hora_inicio')
    op.drop_column('eventos', 'fecha_fin')
    op.drop_column('eventos', 'descripcion')
    op.alter_column('eventos', 'enfoque', type_=sa.String(50))
    op.alter_column('eventos', 'tipo', type_=sa.String(50))
