"""add incident_comments table

Revision ID: a1b2c3d
Revises: f84c9e8
Create Date: 2026-11-07 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1b2c3d'
down_revision = 'f84c9e8'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'incident_comments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('incident_id', sa.Integer(), nullable=False),
        sa.Column('texto', sa.Text(), nullable=True),
        sa.Column('imagen_filename', sa.String(length=255), nullable=True),
        sa.Column('autor', sa.String(length=64), nullable=True),
        sa.Column('fecha_creacion', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['incident_id'], ['incidents.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('incident_comments')
