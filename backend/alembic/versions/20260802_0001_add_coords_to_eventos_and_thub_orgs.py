"""add coords to eventos and update thub org locations

Revision ID: c4d5e6f7a8b9
Revises: 943510da531b
Create Date: 2026-08-02
"""
from typing import Union
from alembic import op
import sqlalchemy as sa


revision: str = 'c4d5e6f7a8b9'
down_revision: Union[str, None] = '943510da531b'
branch_labels = None
depends_on = None

# Coordenadas del T-Hub (Av. Tecnológico 11501, Cd. Juárez)
THUB_LAT = 31.6681
THUB_LNG = -106.4235

# Nombres exactos (o parciales) de las orgs con sede en T-Hub
THUB_ORG_KEYWORDS = ['Frente Norte', 'Startup Juárez', 'Fab Lab Juárez']


def upgrade() -> None:
    # ── Columnas de coordenadas en eventos ────────────────────────────────────
    op.add_column('eventos', sa.Column('latitud', sa.Float(), nullable=True))
    op.add_column('eventos', sa.Column('longitud', sa.Float(), nullable=True))

    # ── Actualizar coordenadas de orgs en T-Hub ───────────────────────────────
    conn = op.get_bind()
    for keyword in THUB_ORG_KEYWORDS:
        conn.execute(
            sa.text(
                "UPDATE organizaciones "
                "SET latitud = :lat, longitud = :lng "
                "WHERE nombre ILIKE :nombre AND (latitud IS NULL OR longitud IS NULL)"
            ),
            {"lat": THUB_LAT, "lng": THUB_LNG, "nombre": f"%{keyword}%"},
        )


def downgrade() -> None:
    op.drop_column('eventos', 'longitud')
    op.drop_column('eventos', 'latitud')
