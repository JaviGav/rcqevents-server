from app import create_app, db
from app.models.event import Event

app = create_app()

with app.app_context():
    # Crear todas las tablas
    db.create_all()
    print("Base de datos inicializada correctamente!") 