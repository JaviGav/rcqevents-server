import os
import sys

# Añadir el directorio raíz al PYTHONPATH
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)

from app import db, create_app
from sqlalchemy import text

def upgrade():
    app = create_app()
    with app.app_context():
        # Añadir columna to_indicativo_id a la tabla messages
        db.session.execute(text('''
            ALTER TABLE messages 
            ADD COLUMN to_indicativo_id INTEGER 
            REFERENCES indicativos(id)
        '''))
        db.session.commit()

def downgrade():
    app = create_app()
    with app.app_context():
        # Eliminar columna to_indicativo_id de la tabla messages
        # Nota: SQLite no soporta DROP COLUMN directamente, así que necesitaríamos recrear la tabla
        # Por ahora, simplemente dejamos la columna
        pass

if __name__ == '__main__':
    upgrade() 