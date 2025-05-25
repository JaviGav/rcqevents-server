import os
import sys

# Añadir el directorio raíz al PYTHONPATH
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)

from app import create_app
from sqlalchemy import text

def upgrade():
    app = create_app()
    with app.app_context():
        # Añadir columna color
        try:
            from app.extensions import db
            db.session.execute(text('ALTER TABLE indicativos ADD COLUMN color VARCHAR(7)'))
            db.session.commit()
        except Exception as e:
            print(f"Ya existe la columna color o error: {e}")

def downgrade():
    app = create_app()
    with app.app_context():
        try:
            from app.extensions import db
            db.session.execute(text('ALTER TABLE indicativos DROP COLUMN color'))
            db.session.commit()
        except Exception as e:
            print(f"Error al eliminar columna color: {e}")

if __name__ == '__main__':
    upgrade() 