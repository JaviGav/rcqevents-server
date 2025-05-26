from app.extensions import db
from datetime import datetime

class Incident(db.Model):
    __tablename__ = 'incidents'
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    incident_number = db.Column(db.Integer, nullable=False)  # autonumérico por evento
    estado = db.Column(db.String(32), default='activo')
    reportado_por = db.Column(db.String(64))
    tipo = db.Column(db.String(64))
    descripcion = db.Column(db.Text)
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)
    dorsal = db.Column(db.String(32))
    patologia = db.Column(db.String(128))
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_pre_activado = db.Column(db.DateTime, nullable=True)
    fecha_activado = db.Column(db.DateTime, nullable=True)
    fecha_stand_by = db.Column(db.DateTime, nullable=True)
    fecha_finalizado = db.Column(db.DateTime, nullable=True)

    __table_args__ = (
        db.UniqueConstraint('event_id', 'incident_number', name='uq_event_incident_number'),
    )

    assignments = db.relationship('IncidentAssignment', backref='incident', lazy=True) 