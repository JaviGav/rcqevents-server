"""Final merge of all migration heads

Revision ID: 4bc6a3cfa046
Revises: 4005f40d95e4, d521463f2046, f84c9e8
Create Date: 2025-05-27 18:58:32.794991

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4bc6a3cfa046'
down_revision = ('4005f40d95e4', 'd521463f2046', 'f84c9e8')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
