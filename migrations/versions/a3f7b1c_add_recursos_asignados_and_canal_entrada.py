"""add recursos_asignados and canal_entrada to incidents

Revision ID: a3f7b1c
Revises: f84c9e8
Create Date: 2026-11-06 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a3f7b1c'
down_revision = 'f84c9e8'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('incidents', schema=None) as batch_op:
        batch_op.add_column(sa.Column('recursos_asignados', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('canal_entrada', sa.String(length=100), nullable=True))


def downgrade():
    with op.batch_alter_table('incidents', schema=None) as batch_op:
        batch_op.drop_column('canal_entrada')
        batch_op.drop_column('recursos_asignados')
