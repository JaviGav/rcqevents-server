from app import db
from datetime import datetime

class Message(db.Model):
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    indicativo_id = db.Column(db.Integer, db.ForeignKey('indicativos.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relaciones
    event = db.relationship('Event', backref=db.backref('messages', lazy=True))
    indicativo = db.relationship('Indicativo', backref=db.backref('messages', lazy=True))
    
    def to_dict(self):
        return {
            'id': self.id,
            'event_id': self.event_id,
            'indicativo_id': self.indicativo_id,
            'indicativo': self.indicativo.indicativo if self.indicativo else None,
            'nombre': self.indicativo.nombre if self.indicativo else None,
            'content': self.content,
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        } 