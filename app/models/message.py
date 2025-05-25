from app.extensions import db
from datetime import datetime
from sqlalchemy.types import TypeDecorator, Text
import json

class JSONEncodedDict(TypeDecorator):
    impl = Text
    def process_bind_param(self, value, dialect):
        if value is None:
            return '{}'
        if isinstance(value, str):
            return value
        return json.dumps(value, ensure_ascii=False)
    def process_result_value(self, value, dialect):
        if value is None:
            return {}
        if isinstance(value, dict):
            return value
        try:
            return json.loads(value)
        except Exception:
            return {}

class Message(db.Model):
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    indicativo_id = db.Column(db.Integer, db.ForeignKey('indicativos.id'), nullable=False)
    content = db.Column(JSONEncodedDict, nullable=False)
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
            'indicativo_color': self.indicativo.color if self.indicativo and self.indicativo.color else None,
            'content': self.content if isinstance(self.content, dict) else {},
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        } 