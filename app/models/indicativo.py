from app.extensions import db
from datetime import datetime

class Indicativo(db.Model):
    __tablename__ = 'indicativos'
    id = db.Column(db.Integer, primary_key=True)
    indicativo = db.Column(db.String(50), nullable=False)
    nombre = db.Column(db.String(100), nullable=True)
    localizacion = db.Column(db.String(200), nullable=True)
    fecha_inicio = db.Column(db.DateTime, nullable=True)
    fecha_fin = db.Column(db.DateTime, nullable=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'indicativo': self.indicativo,
            'nombre': self.nombre,
            'localizacion': self.localizacion,
            'fecha_inicio': self.fecha_inicio.strftime('%Y-%m-%d %H:%M:%S') if self.fecha_inicio else None,
            'fecha_fin': self.fecha_fin.strftime('%Y-%m-%d %H:%M:%S') if self.fecha_fin else None,
            'event_id': self.event_id
        } 