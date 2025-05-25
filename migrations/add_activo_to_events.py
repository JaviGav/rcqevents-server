import os
import sys

# Añadir el directorio raíz al PYTHONPATH
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)

from app import db
from app.models.event import Event

def upgrade():
    # Añadir columna activo con valor por defecto True
    db.session.execute('ALTER TABLE events ADD COLUMN activo BOOLEAN NOT NULL DEFAULT TRUE')
    db.session.commit()

def downgrade():
    # Eliminar columna activo
    db.session.execute('ALTER TABLE events DROP COLUMN activo')
    db.session.commit()

if __name__ == '__main__':
    upgrade() 