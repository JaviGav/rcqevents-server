from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from config import config
from app.socket import socketio
from app.extensions import db, migrate
import logging

def create_app(config_name='default'):
    app = Flask(__name__)
    
    # Cargar configuración
    app.config.from_object(config[config_name])
    
    # Configurar logging
    if not app.debug:
        # En producción, configurar logging para mostrar INFO y superiores
        logging.basicConfig(level=logging.INFO)
        app.logger.setLevel(logging.INFO)
    else:
        # En desarrollo, mostrar DEBUG y superiores
        logging.basicConfig(level=logging.DEBUG)
        app.logger.setLevel(logging.DEBUG)
    
    # Inicializar extensiones con la app
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app, resources={r"/*": {"origins": app.config['CORS_ORIGINS']}})
    socketio.init_app(app, cors_allowed_origins="*")

    # Importar modelos para que Alembic los vea y crear tablas si no existen
    with app.app_context():
        from .models import user, event, indicativo, incident, incident_assignment, message
        db.create_all()
    
    # Registrar blueprints
    from app.routes import main, auth, events
    app.register_blueprint(main.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(events.bp)
    
    return app 