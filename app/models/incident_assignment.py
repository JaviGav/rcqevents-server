from app.extensions import db
from datetime import datetime

class IncidentAssignment(db.Model):
    __tablename__ = 'incident_assignments'
    id = db.Column(db.Integer, primary_key=True)
    incident_id = db.Column(db.Integer, db.ForeignKey('incidents.id'), nullable=False)
    asignado_a = db.Column(db.String(64), nullable=False)  # puede ser texto libre o indicativo
    estado = db.Column(db.String(32), default='pre-avisado')
    hora_preavisado = db.Column(db.DateTime, default=datetime.utcnow)
    hora_avisado = db.Column(db.DateTime)
    hora_en_camino = db.Column(db.DateTime)
    hora_en_lugar = db.Column(db.DateTime)
    hora_desasignado = db.Column(db.DateTime) 