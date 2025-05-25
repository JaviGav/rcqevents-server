from app.extensions import db
from datetime import datetime
import pytz

class Event(db.Model):
    __tablename__ = 'events'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200), nullable=False)
    fecha = db.Column(db.DateTime, nullable=False)
    activo = db.Column(db.Boolean, default=True, nullable=False)
    
    # Nueva columna para la clave foránea
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relaciones
    indicativos = db.relationship('Indicativo', backref='evento', lazy=True)
    
    def to_dict(self):
        madrid_tz = pytz.timezone("Europe/Madrid")
        # Convertimos self.fecha (UTC) a la zona horaria de Madrid
        fecha_madrid = madrid_tz.fromutc(self.fecha) if self.fecha else None
        event_dict = {
            'id': self.id,
            'nombre': self.nombre,
            'fecha': (fecha_madrid.strftime('%Y-%m-%d %H:%M:%S') if fecha_madrid else None),
            'user_id': self.user_id,
            'activo': self.activo
        }
        # Si quieres incluir datos del organizador (User) aquí, puedes hacerlo si la relación está cargada
        # if self.organizer:
        #    event_dict['organizer_name'] = self.organizer.name
        return event_dict 