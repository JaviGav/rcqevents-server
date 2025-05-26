from app.extensions import db
from datetime import datetime

class IncidentAssignment(db.Model):
    __tablename__ = 'incident_assignments'
    id = db.Column(db.Integer, primary_key=True)
    incident_id = db.Column(db.Integer, db.ForeignKey('incidents.id'), nullable=False)
    indicativo_id = db.Column(db.Integer, db.ForeignKey('indicativos.id'), nullable=False) # Asume que la tabla de Indicativo se llama 'indicativos'

    estado_asignacion = db.Column(db.String(32), default='pre-avisado') # pre-avisado, avisado, en camino, en el lugar, finalizado

    fecha_creacion_asignacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_pre_avisado_asig = db.Column(db.DateTime, nullable=True)
    fecha_avisado_asig = db.Column(db.DateTime, nullable=True)
    fecha_en_camino_asig = db.Column(db.DateTime, nullable=True)
    fecha_en_lugar_asig = db.Column(db.DateTime, nullable=True)
    fecha_finalizado_asig = db.Column(db.DateTime, nullable=True)

    # Relación para acceder al objeto Indicativo desde la asignación
    # El backref en Indicativo se podría llamar 'incident_assignments'
    indicativo = db.relationship('Indicativo', backref=db.backref('incident_assignments', lazy='dynamic'))

    def to_dict(self):
        return {
            'id': self.id,
            'incident_id': self.incident_id,
            'indicativo_id': self.indicativo_id,
            'indicativo_nombre': self.indicativo.indicativo if self.indicativo else None, # Añadir nombre del indicativo
            'estado_asignacion': self.estado_asignacion,
            'fecha_creacion_asignacion': self.fecha_creacion_asignacion.strftime('%Y-%m-%d %H:%M:%S') if self.fecha_creacion_asignacion else None,
            'fecha_pre_avisado_asig': self.fecha_pre_avisado_asig.strftime('%Y-%m-%d %H:%M:%S') if self.fecha_pre_avisado_asig else None,
            'fecha_avisado_asig': self.fecha_avisado_asig.strftime('%Y-%m-%d %H:%M:%S') if self.fecha_avisado_asig else None,
            'fecha_en_camino_asig': self.fecha_en_camino_asig.strftime('%Y-%m-%d %H:%M:%S') if self.fecha_en_camino_asig else None,
            'fecha_en_lugar_asig': self.fecha_en_lugar_asig.strftime('%Y-%m-%d %H:%M:%S') if self.fecha_en_lugar_asig else None,
            'fecha_finalizado_asig': self.fecha_finalizado_asig.strftime('%Y-%m-%d %H:%M:%S') if self.fecha_finalizado_asig else None,
        } 