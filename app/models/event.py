from app import db
from datetime import datetime

class Event(db.Model):
    __tablename__ = 'events'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200), nullable=False)
    fecha = db.Column(db.DateTime, nullable=False)
    
    # Nueva columna para la clave foránea
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    def to_dict(self):
        event_dict = {
            'id': self.id,
            'nombre': self.nombre,
            'fecha': self.fecha.strftime('%Y-%m-%d %H:%M:%S') if self.fecha else None,
            'user_id': self.user_id
        }
        # Si quieres incluir datos del organizador (User) aquí, puedes hacerlo si la relación está cargada
        # if self.organizer:
        #    event_dict['organizer_name'] = self.organizer.name
        return event_dict 