from flask import Blueprint, jsonify, request, render_template
from app.models.event import Event
from app.models.user import User
from app.extensions import db
from datetime import datetime
from app.routes.auth import token_required
from app.models.indicativo import Indicativo
from app.models.incident import Incident
from app.models.incident_assignment import IncidentAssignment
from sqlalchemy import func

bp = Blueprint('events', __name__, url_prefix='/events')

# Página web de administración
@bp.route('/')
def admin_page():
    return render_template('admin.html')

# API endpoints
@bp.route('/api', methods=['GET'])
def get_events():
    try:
        events = Event.query.all()
        return jsonify({
            'status': 'success',
            'events': [event.to_dict() for event in events]
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@bp.route('/api/<int:event_id>', methods=['GET'])
def get_event(event_id):
    try:
        event = Event.query.get_or_404(event_id)
        organizer = User.query.get(event.user_id)
        event_data = event.to_dict()
        event_data['organizer_name'] = organizer.username if organizer else 'Desconocido'
        return jsonify({
            'status': 'success',
            'event': event_data
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@bp.route('/api', methods=['POST'])
def create_event():
    try:
        data = request.get_json()
        if not data or 'nombre' not in data or 'fecha' not in data:
            return jsonify({'status': 'error', 'message': 'Nombre y fecha son requeridos'}), 400
        fecha_str = data['fecha']
        try:
            fecha = datetime.strptime(fecha_str, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            try:
                fecha = datetime.strptime(fecha_str, '%Y-%m-%dT%H:%M')
            except ValueError:
                return jsonify({'status': 'error', 'message': 'Formato de fecha inválido. Use: YYYY-MM-DD HH:MM:SS o YYYY-MM-DDTHH:MM'}), 400
        # (Temporalmente) asigno un user_id fijo (por ejemplo, 1) para pruebas
        evento = Event(nombre=data['nombre'], fecha=fecha, user_id=1)
        db.session.add(evento)
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'Evento creado exitosamente', 'event': evento.to_dict()}), 201
    except ValueError:
        return jsonify({'status': 'error', 'message': 'Formato de fecha inválido. Use: YYYY-MM-DD HH:MM:SS'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@bp.route('/api/<int:event_id>', methods=['PUT'])
def update_event(event_id):
    try:
        event = Event.query.get_or_404(event_id)
        data = request.get_json()
        
        if not data:
            return jsonify({'status': 'error', 'message': 'No se enviaron datos'}), 400
        
        # Actualizar campos si están presentes
        if 'nombre' in data:
            event.nombre = data['nombre']
        
        if 'fecha' in data:
            event.fecha = datetime.strptime(data['fecha'], '%Y-%m-%d %H:%M:%S')
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Evento actualizado exitosamente',
            'event': event.to_dict()
        })
        
    except ValueError:
        return jsonify({'status': 'error', 'message': 'Formato de fecha inválido. Use: YYYY-MM-DD HH:MM:SS'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@bp.route('/api/<int:event_id>', methods=['DELETE'])
def delete_event(event_id):
    try:
        event = Event.query.get_or_404(event_id)
        db.session.delete(event)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Evento eliminado exitosamente'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@bp.route('/api/<int:event_id>/toggle', methods=['POST'])
def toggle_event(event_id):
    try:
        event = Event.query.get_or_404(event_id)
        event.activo = not event.activo
        db.session.commit()
        return jsonify({
            'status': 'success',
            'message': 'Evento ' + ('activado' if event.activo else 'desactivado') + ' exitosamente',
            'event': event.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

# --- API de Indicativos ---
@bp.route('/<int:event_id>/indicativos/api', methods=['GET'])
def get_indicativos(event_id):
    indicativos = Indicativo.query.filter_by(event_id=event_id).all()
    return jsonify({'status': 'success', 'indicativos': [i.to_dict() for i in indicativos]})

@bp.route('/<int:event_id>/indicativos/api', methods=['POST'])
def create_indicativo(event_id):
    data = request.get_json()
    if not data or 'indicativo' not in data:
        return jsonify({'status': 'error', 'message': 'El campo indicativo es requerido'}), 400
    indicativo = Indicativo(
        indicativo=data['indicativo'],
        nombre=data.get('nombre'),
        localizacion=data.get('localizacion'),
        fecha_inicio=datetime.strptime(data['fecha_inicio'], '%Y-%m-%d %H:%M:%S') if data.get('fecha_inicio') else None,
        fecha_fin=datetime.strptime(data['fecha_fin'], '%Y-%m-%d %H:%M:%S') if data.get('fecha_fin') else None,
        event_id=event_id
    )
    db.session.add(indicativo)
    db.session.commit()
    return jsonify({'status': 'success', 'indicativo': indicativo.to_dict()}), 201

@bp.route('/<int:event_id>/indicativos/api/<int:indicativo_id>', methods=['PUT'])
def update_indicativo(event_id, indicativo_id):
    indicativo = Indicativo.query.filter_by(id=indicativo_id, event_id=event_id).first_or_404()
    data = request.get_json()
    if 'indicativo' in data:
        indicativo.indicativo = data['indicativo']
    if 'nombre' in data:
        indicativo.nombre = data['nombre']
    if 'localizacion' in data:
        indicativo.localizacion = data['localizacion']
    if 'fecha_inicio' in data:
        indicativo.fecha_inicio = datetime.strptime(data['fecha_inicio'], '%Y-%m-%d %H:%M:%S') if data['fecha_inicio'] else None
    if 'fecha_fin' in data:
        indicativo.fecha_fin = datetime.strptime(data['fecha_fin'], '%Y-%m-%d %H:%M:%S') if data['fecha_fin'] else None
    if 'color' in data:
        indicativo.color = data['color']
    db.session.commit()
    return jsonify({'status': 'success', 'indicativo': indicativo.to_dict()})

@bp.route('/<int:event_id>/indicativos/api/<int:indicativo_id>', methods=['DELETE'])
def delete_indicativo(event_id, indicativo_id):
    indicativo = Indicativo.query.filter_by(id=indicativo_id, event_id=event_id).first_or_404()
    db.session.delete(indicativo)
    db.session.commit()
    return jsonify({'status': 'success', 'message': 'Indicativo eliminado'})

@bp.route('/<int:event_id>')
def event_detail(event_id):
    event = Event.query.get_or_404(event_id)
    return render_template('event_detail.html', event=event)

@bp.route('/<int:event_id>/control')
def event_control(event_id):
    event = Event.query.get_or_404(event_id)
    indicativos_obj = Indicativo.query.filter_by(event_id=event_id).all()
    indicativos_list_of_dicts = [ind.to_dict() for ind in indicativos_obj]
    return render_template('event_control.html', event=event, indicativos=indicativos_list_of_dicts)

@bp.route('/<int:event_id>/callsigns')
def event_callsigns(event_id):
    event = Event.query.get_or_404(event_id)
    indicativos = Indicativo.query.filter_by(event_id=event_id).all()
    return render_template('event_callsigns.html', event=event, indicativos=indicativos)

# --- INCIDENTES ---
def incident_to_dict(incident):
    return {
        'id': incident.id,
        'incident_number': incident.incident_number,
        'event_id': incident.event_id,
        'estado': incident.estado,
        'reportado_por': incident.reportado_por,
        'tipo': incident.tipo,
        'descripcion': incident.descripcion,
        'lat': incident.lat,
        'lng': incident.lng,
        'dorsal': incident.dorsal,
        'patologia': incident.patologia,
        'fecha_creacion': incident.fecha_creacion.strftime('%Y-%m-%d %H:%M:%S') if incident.fecha_creacion else None,
        'assignments': [assignment_to_dict(a) for a in incident.assignments]
    }

def assignment_to_dict(a):
    return {
        'id': a.id,
        'asignado_a': a.asignado_a,
        'estado': a.estado,
        'hora_preavisado': a.hora_preavisado.strftime('%Y-%m-%d %H:%M:%S') if a.hora_preavisado else None,
        'hora_avisado': a.hora_avisado.strftime('%Y-%m-%d %H:%M:%S') if a.hora_avisado else None,
        'hora_en_camino': a.hora_en_camino.strftime('%Y-%m-%d %H:%M:%S') if a.hora_en_camino else None,
        'hora_en_lugar': a.hora_en_lugar.strftime('%Y-%m-%d %H:%M:%S') if a.hora_en_lugar else None,
        'hora_desasignado': a.hora_desasignado.strftime('%Y-%m-%d %H:%M:%S') if a.hora_desasignado else None,
    }

@bp.route('/<int:event_id>/incidents', methods=['GET'])
def get_incidents(event_id):
    incidents = Incident.query.filter_by(event_id=event_id).order_by(Incident.incident_number.asc()).all()
    return jsonify({'status': 'success', 'incidents': [incident_to_dict(i) for i in incidents]})

@bp.route('/<int:event_id>/incidents', methods=['POST'])
def create_incident(event_id):
    data = request.get_json()
    # Calcular el siguiente incident_number para el evento
    max_num = db.session.query(func.max(Incident.incident_number)).filter_by(event_id=event_id).scalar() or 0
    incident = Incident(
        event_id=event_id,
        incident_number=max_num + 1,
        estado=data.get('estado', 'activo'),
        reportado_por=data.get('reportado_por'),
        tipo=data.get('tipo'),
        descripcion=data.get('descripcion'),
        lat=data.get('lat'),
        lng=data.get('lng'),
        dorsal=data.get('dorsal'),
        patologia=data.get('patologia')
    )
    db.session.add(incident)
    db.session.commit()
    return jsonify({'status': 'success', 'incident': incident_to_dict(incident)})

@bp.route('/<int:event_id>/incidents/<int:incident_id>', methods=['GET'])
def get_incident(event_id, incident_id):
    incident = Incident.query.filter_by(event_id=event_id, id=incident_id).first_or_404()
    return jsonify({'status': 'success', 'incident': incident_to_dict(incident)})

@bp.route('/<int:event_id>/incidents/<int:incident_id>', methods=['PUT'])
def update_incident(event_id, incident_id):
    incident = Incident.query.filter_by(event_id=event_id, id=incident_id).first_or_404()
    data = request.get_json()
    for field in ['estado', 'reportado_por', 'tipo', 'descripcion', 'lat', 'lng', 'dorsal', 'patologia']:
        if field in data:
            setattr(incident, field, data[field])
    db.session.commit()
    return jsonify({'status': 'success', 'incident': incident_to_dict(incident)})

@bp.route('/<int:event_id>/incidents/<int:incident_id>', methods=['DELETE'])
def delete_incident(event_id, incident_id):
    incident = Incident.query.filter_by(event_id=event_id, id=incident_id).first_or_404()
    db.session.delete(incident)
    db.session.commit()
    return jsonify({'status': 'success'})

# --- ASIGNACIONES ---
@bp.route('/<int:event_id>/incidents/<int:incident_id>/assignments', methods=['POST'])
def add_assignment(event_id, incident_id):
    incident = Incident.query.filter_by(event_id=event_id, id=incident_id).first_or_404()
    data = request.get_json()
    assignment = IncidentAssignment(
        incident_id=incident.id,
        asignado_a=data['asignado_a'],
        estado=data.get('estado', 'pre-avisado')
    )
    db.session.add(assignment)
    db.session.commit()
    return jsonify({'status': 'success', 'incident': incident_to_dict(incident)})

@bp.route('/<int:event_id>/incidents/<int:incident_id>/assignments/<int:assignment_id>', methods=['PUT'])
def update_assignment(event_id, incident_id, assignment_id):
    incident = Incident.query.filter_by(event_id=event_id, id=incident_id).first_or_404()
    assignment = IncidentAssignment.query.filter_by(id=assignment_id, incident_id=incident.id).first_or_404()
    data = request.get_json()
    estado = data.get('estado')
    now = datetime.utcnow()
    if estado and estado != assignment.estado:
        assignment.estado = estado
        if estado == 'pre-avisado':
            assignment.hora_preavisado = now
        elif estado == 'avisado y en camino':
            assignment.hora_avisado = now
            assignment.hora_en_camino = now
        elif estado == 'en el lugar':
            assignment.hora_en_lugar = now
        elif estado == 'desasignado':
            assignment.hora_desasignado = now
    db.session.commit()
    return jsonify({'status': 'success', 'incident': incident_to_dict(incident)})

@bp.route('/<int:event_id>/incidents/<int:incident_id>/assignments/<int:assignment_id>', methods=['DELETE'])
def delete_assignment(event_id, incident_id, assignment_id):
    incident = Incident.query.filter_by(event_id=event_id, id=incident_id).first_or_404()
    assignment = IncidentAssignment.query.filter_by(id=assignment_id, incident_id=incident.id).first_or_404()
    db.session.delete(assignment)
    db.session.commit()
    return jsonify({'status': 'success', 'incident': incident_to_dict(incident)})

# Fin del archivo