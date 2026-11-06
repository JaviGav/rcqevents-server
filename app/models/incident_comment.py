from app.extensions import db
from datetime import datetime

class IncidentComment(db.Model):
    __tablename__ = 'incident_comments'
    id = db.Column(db.Integer, primary_key=True)
    incident_id = db.Column(db.Integer, db.ForeignKey('incidents.id'), nullable=False)
    texto = db.Column(db.Text, nullable=True)
    imagen_filename = db.Column(db.String(255), nullable=True)  # Nombre del archivo de imagen guardado
    autor = db.Column(db.String(64), nullable=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self, image_url_base=''):
        return {
            'id': self.id,
            'incident_id': self.incident_id,
            'texto': self.texto,
            'imagen_filename': self.imagen_filename,
            'imagen_url': f"{image_url_base}{self.imagen_filename}" if self.imagen_filename else None,
            'autor': self.autor,
            'fecha_creacion': self.fecha_creacion.strftime('%Y-%m-%d %H:%M:%S') if self.fecha_creacion else None,
        }
