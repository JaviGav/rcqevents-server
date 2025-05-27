from app.extensions import db
from datetime import datetime

class IncidentAssignment(db.Model):
    __tablename__ = 'incident_assignments'
    id = db.Column(db.Integer, primary_key=True)
    incident_id = db.Column(db.Integer, db.ForeignKey('incidents.id'), nullable=False)
    indicativo_id = db.Column(db.Integer, db.ForeignKey('indicativos.id'), nullable=True) # Ahora nullable para permitir servicios
    servicio_nombre = db.Column(db.String(100), nullable=True) # Para servicios como CME, GUB, etc.

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
        # Determinar el nombre a mostrar: servicio o indicativo
        if self.servicio_nombre:
            nombre_asignado = self.servicio_nombre
        elif self.indicativo:
            nombre_asignado = f"{self.indicativo.indicativo} ({self.indicativo.nombre})" if self.indicativo.nombre else self.indicativo.indicativo
        elif self.indicativo_id == -1:
            # Caso especial: indicativo_id = -1 significa texto libre, pero servicio_nombre puede ser None por problemas de esquema
            # Intentar recuperar el valor original desde la base de datos
            try:
                from sqlalchemy import text
                from app.extensions import db
                result = db.session.execute(
                    text("SELECT * FROM incident_assignments WHERE id = :assignment_id"),
                    {"assignment_id": self.id}
                ).fetchone()
                
                if result:
                    # Intentar obtener servicio_nombre si la columna existe
                    try:
                        servicio_nombre = getattr(result, 'servicio_nombre', None)
                        if servicio_nombre:
                            nombre_asignado = servicio_nombre
                        else:
                            nombre_asignado = "Asignación personalizada"
                    except:
                        nombre_asignado = "Asignación personalizada"
                else:
                    nombre_asignado = "Texto libre"
            except Exception as e:
                print(f"Error al recuperar nombre de asignación en to_dict: {e}")
                nombre_asignado = "Texto libre"
        else:
            nombre_asignado = "Asignación sin nombre"
            
        return {
            'id': self.id,
            'incident_id': self.incident_id,
            'indicativo_id': self.indicativo_id,
            'servicio_nombre': self.servicio_nombre,
            'indicativo_nombre': nombre_asignado, # Nombre unificado para mostrar
            'estado_asignacion': self.estado_asignacion,
            'fecha_creacion_asignacion': self.fecha_creacion_asignacion.strftime('%Y-%m-%d %H:%M:%S') if self.fecha_creacion_asignacion else None,
            'fecha_pre_avisado_asig': self.fecha_pre_avisado_asig.strftime('%Y-%m-%d %H:%M:%S') if self.fecha_pre_avisado_asig else None,
            'fecha_avisado_asig': self.fecha_avisado_asig.strftime('%Y-%m-%d %H:%M:%S') if self.fecha_avisado_asig else None,
            'fecha_en_camino_asig': self.fecha_en_camino_asig.strftime('%Y-%m-%d %H:%M:%S') if self.fecha_en_camino_asig else None,
            'fecha_en_lugar_asig': self.fecha_en_lugar_asig.strftime('%Y-%m-%d %H:%M:%S') if self.fecha_en_lugar_asig else None,
            'fecha_finalizado_asig': self.fecha_finalizado_asig.strftime('%Y-%m-%d %H:%M:%S') if self.fecha_finalizado_asig else None,
        } 