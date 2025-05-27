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
import requests

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
        evento = Event(
            nombre=data['nombre'], 
            fecha=fecha, 
            user_id=1, # (Temporalmente) asigno un user_id fijo
            zona_evento=data.get('zona_evento') # Añadir zona_evento
        )
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
        
        if 'zona_evento' in data: # Añadir manejo para zona_evento
            event.zona_evento = data['zona_evento']
        
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

@bp.route('/<int:event_id>/control')
def event_control(event_id):
    event = Event.query.get_or_404(event_id)
    indicativos_obj = Indicativo.query.filter_by(event_id=event_id).all()
    indicativos_list_of_dicts = [ind.to_dict() for ind in indicativos_obj]
    return render_template('event_control.html', event=event.to_dict(), indicativos=indicativos_list_of_dicts)

@bp.route('/<int:event_id>/callsigns')
def event_callsigns(event_id):
    event = Event.query.get_or_404(event_id)
    indicativos = Indicativo.query.filter_by(event_id=event_id).all()
    return render_template('event_callsigns.html', event=event, indicativos=indicativos)

# --- INCIDENTES ---

def get_address_from_coords(lat, lng):
    if lat is None or lng is None:
        return None
    try:
        # Usar el user-agent es una buena práctica y a veces requerido por Nominatim
        headers = {
            'User-Agent': 'RCQEventsServer/1.0 (contacto@tuemail.com)' # Cambia esto por tu app y email
        }
        url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lng}&zoom=18&addressdetails=1"
        response = requests.get(url, headers=headers, timeout=5) # Timeout de 5 segundos
        response.raise_for_status() # Lanza error para respuestas 4xx/5xx
        data = response.json()
        address = data.get('address')
        if address:
            road = address.get('road', '')
            house_number = address.get('house_number', '')
            city = address.get('city', address.get('town', address.get('village', '')))
            
            display_address = road
            if house_number:
                display_address += f", {house_number}"
            # if city:
            #     display_address += f" - {city}" # Opcional: añadir ciudad
            return display_address if display_address else data.get('display_name')
        return data.get('display_name') # Fallback al display_name completo
    except requests.exceptions.RequestException as e:
        print(f"Error en geocodificación inversa: {e}")
        return None
    except Exception as e:
        print(f"Error inesperado en geocodificación inversa: {e}")
        return None

def update_incident_address(incident):
    """Actualiza la dirección formateada del incidente basándose en sus coordenadas"""
    if incident.lat is not None and incident.lng is not None:
        address = get_address_from_coords(incident.lat, incident.lng)
        incident.direccion_formateada = address
    else:
        incident.direccion_formateada = None

def incident_to_dict(incident, fetch_address=False):
    data = {
        'id': incident.id,
        'incident_number': incident.incident_number,
        'event_id': incident.event_id,
        'estado': incident.estado,
        'reportado_por': incident.reportado_por,
        'tipo': incident.tipo,
        'descripcion': incident.descripcion,
        'lat': incident.lat,
        'lng': incident.lng,
        'direccion_formateada': incident.direccion_formateada,  # Usar la dirección guardada en BD
        'info_ubicacion': incident.info_ubicacion,  # Información adicional de ubicación
        'dorsal': incident.dorsal,
        'patologia': incident.patologia,
        'fecha_creacion': incident.fecha_creacion.strftime('%Y-%m-%d %H:%M:%S') if incident.fecha_creacion else None,
        'fecha_pre_activado': incident.fecha_pre_activado.strftime('%Y-%m-%d %H:%M:%S') if incident.fecha_pre_activado else None,
        'fecha_activado': incident.fecha_activado.strftime('%Y-%m-%d %H:%M:%S') if incident.fecha_activado else None,
        'fecha_stand_by': incident.fecha_stand_by.strftime('%Y-%m-%d %H:%M:%S') if incident.fecha_stand_by else None,
        'fecha_finalizado': incident.fecha_finalizado.strftime('%Y-%m-%d %H:%M:%S') if incident.fecha_finalizado else None,
        'is_deleted': incident.is_deleted,
        'deleted_at': incident.deleted_at.strftime('%Y-%m-%d %H:%M:%S') if incident.deleted_at else None,
        'assignments': [assignment_to_dict(a) for a in incident.assignments]
    }
    return data

def assignment_to_dict(a):
    return a.to_dict()

@bp.route('/<int:event_id>/incidents', methods=['GET'])
def get_incidents(event_id):
    include_deleted_str = request.args.get('include_deleted', 'false').lower()
    include_deleted = include_deleted_str == 'true'

    query = Incident.query.filter_by(event_id=event_id)
    if not include_deleted:
        query = query.filter_by(is_deleted=False)
    
    incidents = query.order_by(Incident.incident_number.asc()).all()
    # No hacemos fetch_address para la lista completa por defecto para evitar muchas llamadas API
    return jsonify({'status': 'success', 'incidents': [incident_to_dict(i, fetch_address=False) for i in incidents]})

@bp.route('/<int:event_id>/incidents', methods=['POST'])
def create_incident(event_id):
    data = request.get_json()
    # Calcular el siguiente incident_number para el evento
    max_num = db.session.query(func.max(Incident.incident_number)).filter_by(event_id=event_id).scalar() or 0
    now = datetime.utcnow()
    nuevo_estado = data.get('estado', 'activo')
    incident = Incident(
        event_id=event_id,
        incident_number=max_num + 1,
        estado=nuevo_estado,
        reportado_por=data.get('reportado_por'),
        tipo=data.get('tipo'),
        descripcion=data.get('descripcion'),
        lat=data.get('lat'),
        lng=data.get('lng'),
        info_ubicacion=data.get('info_ubicacion'),
        dorsal=data.get('dorsal'),
        patologia=data.get('patologia'),
        fecha_creacion=now
    )
    if nuevo_estado == 'pre-incidente': incident.fecha_pre_activado = now
    elif nuevo_estado == 'activo': incident.fecha_activado = now
    elif nuevo_estado == 'stand-by': incident.fecha_stand_by = now
    elif nuevo_estado == 'solucionado': incident.fecha_finalizado = now

    # Actualizar dirección si hay coordenadas
    update_incident_address(incident)

    db.session.add(incident)
    db.session.commit()
    return jsonify({'status': 'success', 'incident': incident_to_dict(incident)})

@bp.route('/<int:event_id>/incidents/<int:incident_id>', methods=['GET'])
def get_incident(event_id, incident_id):
    incident = Incident.query.filter_by(event_id=event_id, id=incident_id).first_or_404()
    # Hacemos fetch_address aquí porque es para un solo incidente (ej. para editar)
    return jsonify({'status': 'success', 'incident': incident_to_dict(incident, fetch_address=True)})

@bp.route('/<int:event_id>/incidents/<int:incident_id>', methods=['PUT'])
def update_incident(event_id, incident_id):
    incident = Incident.query.filter_by(event_id=event_id, id=incident_id).first_or_404()
    data = request.get_json()
    now = datetime.utcnow()

    if 'estado' in data and data['estado'] != incident.estado:
        nuevo_estado = data['estado']
        if nuevo_estado == 'pre-incidente': incident.fecha_pre_activado = now
        elif nuevo_estado == 'activo': incident.fecha_activado = now
        elif nuevo_estado == 'stand-by': incident.fecha_stand_by = now
        elif nuevo_estado == 'solucionado': incident.fecha_finalizado = now
        # Considerar si se deben limpiar otras fechas de estado al cambiar.
        # Por ejemplo, si pasa de 'activo' a 'finalizado', ¿fecha_activado debe permanecer?
        # Por ahora, solo se añade/actualiza la fecha del nuevo estado.
        # El campo incident.estado se actualizará con setattr más abajo.

    # Verificar si las coordenadas van a cambiar
    coords_changed = False
    if 'lat' in data and data['lat'] != incident.lat:
        coords_changed = True
    if 'lng' in data and data['lng'] != incident.lng:
        coords_changed = True

    for field in ['estado', 'reportado_por', 'tipo', 'descripcion', 'lat', 'lng', 'info_ubicacion', 'dorsal', 'patologia']:
        if field in data:
            setattr(incident, field, data[field])
    
    # Actualizar dirección si las coordenadas cambiaron
    if coords_changed:
        update_incident_address(incident)
    
    db.session.commit()
    return jsonify({'status': 'success', 'incident': incident_to_dict(incident)})

@bp.route('/<int:event_id>/incidents/<int:incident_id>', methods=['DELETE'])
def delete_incident(event_id, incident_id):
    incident = Incident.query.filter_by(event_id=event_id, id=incident_id, is_deleted=False).first_or_404()
    # Se marca como eliminado en lugar de borrarlo físicamente
    incident.is_deleted = True
    incident.deleted_at = datetime.utcnow()
    db.session.commit()
    return jsonify({'status': 'success', 'message': 'Incidente marcado como eliminado'})

@bp.route('/<int:event_id>/incidents/<int:incident_id>/restore', methods=['POST'])
def restore_incident(event_id, incident_id):
    incident = Incident.query.filter_by(event_id=event_id, id=incident_id, is_deleted=True).first_or_404(
        description='Incidente no encontrado o no está eliminado.'
    )
    incident.is_deleted = False
    incident.deleted_at = None
    db.session.commit()
    return jsonify({'status': 'success', 'message': 'Incidente restaurado', 'incident': incident_to_dict(incident)})

@bp.route('/<int:event_id>/incidents/<int:incident_id>/get_address_only', methods=['GET'])
def get_incident_address_only(event_id, incident_id):
    incident = Incident.query.filter_by(event_id=event_id, id=incident_id, is_deleted=False).first_or_404(
        description='Incidente no encontrado.'
    )
    if incident.lat is not None and incident.lng is not None:
        address = get_address_from_coords(incident.lat, incident.lng)
        if address:
            return jsonify({'status': 'success', 'address': address})
        else:
            return jsonify({'status': 'error', 'message': 'No se pudo obtener la dirección para las coordenadas.'}), 404 # O 200 con mensaje de error
    else:
        return jsonify({'status': 'error', 'message': 'El incidente no tiene coordenadas registradas.'}), 400

# --- ASIGNACIONES DE INCIDENTES ---
@bp.route('/<int:event_id>/incidents/<int:incident_id>/assignments', methods=['POST'])
def create_incident_assignment(event_id, incident_id):
    incident = Incident.query.filter_by(id=incident_id, event_id=event_id).first_or_404()
    data = request.get_json()
    if not data or 'indicativo_id' not in data:
        return jsonify({'status': 'error', 'message': 'indicativo_id es requerido'}), 400

    now = datetime.utcnow()
    nuevo_estado_asignacion = data.get('estado_asignacion', 'pre-avisado')

    assignment = IncidentAssignment(
        incident_id=incident.id,
        indicativo_id=data['indicativo_id'],
        estado_asignacion=nuevo_estado_asignacion,
        fecha_creacion_asignacion=now
    )

    if nuevo_estado_asignacion == 'pre-avisado': assignment.fecha_pre_avisado_asig = now
    elif nuevo_estado_asignacion == 'avisado': assignment.fecha_avisado_asig = now
    elif nuevo_estado_asignacion == 'en camino': assignment.fecha_en_camino_asig = now
    elif nuevo_estado_asignacion == 'en el lugar': assignment.fecha_en_lugar_asig = now
    elif nuevo_estado_asignacion == 'finalizado': assignment.fecha_finalizado_asig = now
    
    db.session.add(assignment)
    db.session.commit()
    return jsonify({'status': 'success', 'message': 'Asignación creada', 'assignment': assignment.to_dict()}), 201

@bp.route('/<int:event_id>/incidents/<int:incident_id>/assignments/<int:assignment_id>', methods=['PUT'])
def update_incident_assignment(event_id, incident_id, assignment_id):
    assignment = IncidentAssignment.query.filter_by(id=assignment_id, incident_id=incident_id).first_or_404()
    data = request.get_json()
    now = datetime.utcnow()

    if 'estado_asignacion' in data and data['estado_asignacion'] != assignment.estado_asignacion:
        nuevo_estado = data['estado_asignacion']
        assignment.estado_asignacion = nuevo_estado
        if nuevo_estado == 'pre-avisado': assignment.fecha_pre_avisado_asig = now
        elif nuevo_estado == 'avisado': assignment.fecha_avisado_asig = now
        elif nuevo_estado == 'en camino': assignment.fecha_en_camino_asig = now
        elif nuevo_estado == 'en el lugar': assignment.fecha_en_lugar_asig = now
        elif nuevo_estado == 'finalizado': assignment.fecha_finalizado_asig = now
        # Considerar limpiar otras fechas si es necesario

    db.session.commit()
    return jsonify({'status': 'success', 'message': 'Asignación actualizada', 'assignment': assignment.to_dict()})

@bp.route('/<int:event_id>/incidents/<int:incident_id>/assignments/<int:assignment_id>', methods=['DELETE'])
def delete_incident_assignment(event_id, incident_id, assignment_id):
    assignment = IncidentAssignment.query.filter_by(id=assignment_id, incident_id=incident_id).first_or_404()
    db.session.delete(assignment)
    db.session.commit()
    return jsonify({'status': 'success', 'message': 'Asignación eliminada'})

# Fin del archivo