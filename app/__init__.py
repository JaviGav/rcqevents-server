from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from config import config

# Inicializar extensiones
db = SQLAlchemy()
migrate = Migrate()

def create_app(config_name='default'):
    app = Flask(__name__)
    
    # Cargar configuración
    app.config.from_object(config[config_name])
    
    # Inicializar extensiones con la app
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app, resources={r"/*": {"origins": app.config['CORS_ORIGINS']}})

    # Importar modelos para que Alembic los vea
    with app.app_context():
        from .models import user, event, indicativo # Asumiendo indicativo.py en app/models
    
    # Registrar blueprints
    from app.routes import main, auth, events
    app.register_blueprint(main.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(events.bp)
    
    return app 