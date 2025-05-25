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
        # Crear tabla de mensajes
        db.session.execute(text('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id INTEGER NOT NULL,
                indicativo_id INTEGER NOT NULL,
                content TEXT NOT NULL,
                timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (event_id) REFERENCES events (id),
                FOREIGN KEY (indicativo_id) REFERENCES indicativos (id)
            )
        '''))
        db.session.commit()

def downgrade():
    app = create_app()
    with app.app_context():
        # Eliminar tabla de mensajes
        db.session.execute(text('DROP TABLE IF EXISTS messages'))
        db.session.commit()

if __name__ == '__main__':
    upgrade() 