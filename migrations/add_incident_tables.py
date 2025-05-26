import os
import sys

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)

from app import db, create_app
from sqlalchemy import text

def upgrade():
    app = create_app()
    with app.app_context():
        db.session.execute(text('''
            CREATE TABLE IF NOT EXISTS incidents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id INTEGER NOT NULL,
                incident_number INTEGER NOT NULL,
                estado VARCHAR(32) DEFAULT 'activo',
                reportado_por VARCHAR(64),
                tipo VARCHAR(64),
                descripcion TEXT,
                lat FLOAT,
                lng FLOAT,
                dorsal VARCHAR(32),
                patologia VARCHAR(128),
                fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(event_id, incident_number),
                FOREIGN KEY (event_id) REFERENCES events(id)
            )
        '''))
        db.session.execute(text('''
            CREATE TABLE IF NOT EXISTS incident_assignments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                incident_id INTEGER NOT NULL,
                asignado_a VARCHAR(64) NOT NULL,
                estado VARCHAR(32) DEFAULT 'pre-avisado',
                hora_preavisado DATETIME DEFAULT CURRENT_TIMESTAMP,
                hora_avisado DATETIME,
                hora_en_camino DATETIME,
                hora_en_lugar DATETIME,
                hora_desasignado DATETIME,
                FOREIGN KEY (incident_id) REFERENCES incidents(id)
            )
        '''))
        db.session.commit()

def downgrade():
    app = create_app()
    with app.app_context():
        db.session.execute(text('DROP TABLE IF EXISTS incident_assignments'))
        db.session.execute(text('DROP TABLE IF EXISTS incidents'))
        db.session.commit()

if __name__ == '__main__':
    upgrade() 