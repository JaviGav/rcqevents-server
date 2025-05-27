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
    # Usar SQL directo para cargar asignaciones para evitar problemas de esquema
    assignments_data = []
    try:
        from sqlalchemy import text
        assignments = db.session.execute(
            text("SELECT * FROM incident_assignments WHERE incident_id = :incident_id"),
            {"incident_id": incident.id}
        ).fetchall()
        print(f"DEBUG: incident_to_dict - Consultando asignaciones para incident_id={incident.id}, encontradas: {len(assignments)}")
        
        for assignment in assignments:
            # Crear diccionario básico
            assignment_dict = {
                'id': assignment.id,
                'incident_id': assignment.incident_id,
                'indicativo_id': assignment.indicativo_id,
                'estado_asignacion': assignment.estado_asignacion,
                'fecha_creacion_asignacion': assignment.fecha_creacion_asignacion.strftime('%Y-%m-%d %H:%M:%S') if assignment.fecha_creacion_asignacion else None,
            }
            
            # Intentar obtener servicio_nombre si existe la columna
            try:
                assignment_dict['servicio_nombre'] = getattr(assignment, 'servicio_nombre', None)
            except:
                assignment_dict['servicio_nombre'] = None
            
            # Intentar obtener fechas adicionales si existen
            for field in ['fecha_pre_avisado_asig', 'fecha_avisado_asig', 'fecha_en_camino_asig', 'fecha_en_lugar_asig', 'fecha_finalizado_asig']:
                try:
                    value = getattr(assignment, field, None)
                    assignment_dict[field] = value.strftime('%Y-%m-%d %H:%M:%S') if value else None
                except:
                    assignment_dict[field] = None
            
            # Determinar el nombre a mostrar (misma lógica que otros endpoints)
            if assignment_dict['servicio_nombre']:
                assignment_dict['indicativo_nombre'] = assignment_dict['servicio_nombre']
            elif assignment_dict['indicativo_id'] and assignment_dict['indicativo_id'] > 0:
                # Buscar el indicativo para obtener su nombre
                try:
                    indicativo = Indicativo.query.get(assignment_dict['indicativo_id'])
                    if indicativo:
                        assignment_dict['indicativo_nombre'] = f"{indicativo.indicativo} ({indicativo.nombre})" if indicativo.nombre else indicativo.indicativo
                    else:
                        assignment_dict['indicativo_nombre'] = f"ID: {assignment_dict['indicativo_id']}"
                except:
                    assignment_dict['indicativo_nombre'] = f"ID: {assignment_dict['indicativo_id']}"
            else:
                assignment_dict['indicativo_nombre'] = "Asignación sin nombre"
            
            assignments_data.append(assignment_dict)
    except Exception as e:
        print(f"Error al cargar asignaciones para incidente {incident.id}: {e}")
    
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
        'assignments': assignments_data
    }
    return data

def assignment_to_dict(a):
    """Convierte una asignación a diccionario de manera segura"""
    try:
        return a.to_dict()
    except Exception as e:
        print(f"Error al convertir asignación {a.id} a dict: {e}")
        # Fallback manual
        try:
            assignment_dict = {
                'id': a.id,
                'incident_id': a.incident_id,
                'indicativo_id': a.indicativo_id,
                'servicio_nombre': getattr(a, 'servicio_nombre', None),
                'estado_asignacion': a.estado_asignacion,
                'fecha_creacion_asignacion': a.fecha_creacion_asignacion.strftime('%Y-%m-%d %H:%M:%S') if a.fecha_creacion_asignacion else None,
                'fecha_pre_avisado_asig': getattr(a, 'fecha_pre_avisado_asig', None),
                'fecha_avisado_asig': getattr(a, 'fecha_avisado_asig', None),
                'fecha_en_camino_asig': getattr(a, 'fecha_en_camino_asig', None),
                'fecha_en_lugar_asig': getattr(a, 'fecha_en_lugar_asig', None),
                'fecha_finalizado_asig': getattr(a, 'fecha_finalizado_asig', None),
            }
            
            # Determinar el nombre a mostrar
            if assignment_dict['servicio_nombre']:
                assignment_dict['indicativo_nombre'] = assignment_dict['servicio_nombre']
            elif assignment_dict['indicativo_id'] and assignment_dict['indicativo_id'] > 0:
                # Buscar el indicativo para obtener su nombre
                try:
                    indicativo = Indicativo.query.get(assignment_dict['indicativo_id'])
                    if indicativo:
                        assignment_dict['indicativo_nombre'] = f"{indicativo.indicativo} ({indicativo.nombre})" if indicativo.nombre else indicativo.indicativo
                    else:
                        assignment_dict['indicativo_nombre'] = f"ID: {assignment_dict['indicativo_id']}"
                except:
                    assignment_dict['indicativo_nombre'] = f"ID: {assignment_dict['indicativo_id']}"
            else:
                assignment_dict['indicativo_nombre'] = "Asignación sin nombre"
            
            return assignment_dict
        except Exception as e2:
            print(f"Error en fallback manual para asignación: {e2}")
            return {
                'id': getattr(a, 'id', None),
                'incident_id': getattr(a, 'incident_id', None),
                'indicativo_id': getattr(a, 'indicativo_id', None),
                'servicio_nombre': None,
                'indicativo_nombre': 'Error al cargar',
                'estado_asignacion': getattr(a, 'estado_asignacion', 'desconocido'),
                'fecha_creacion_asignacion': None,
                'fecha_pre_avisado_asig': None,
                'fecha_avisado_asig': None,
                'fecha_en_camino_asig': None,
                'fecha_en_lugar_asig': None,
                'fecha_finalizado_asig': None,
            }

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
@bp.route('/<int:event_id>/incidents/<int:incident_id>/assignments', methods=['GET'])
def get_incident_assignments(event_id, incident_id):
    """Obtener todas las asignaciones de un incidente"""
    try:
        # Verificar que el incidente existe y pertenece al evento
        incident = Incident.query.filter_by(id=incident_id, event_id=event_id).first_or_404()
        
        assignments_data = []
        
        # Usar SQL directo para evitar problemas de esquema
        try:
            from sqlalchemy import text
            assignments = db.session.execute(
                text("SELECT * FROM incident_assignments WHERE incident_id = :incident_id"),
                {"incident_id": incident_id}
            ).fetchall()
            print(f"DEBUG: Consultando asignaciones para incident_id={incident_id}, encontradas: {len(assignments)}")
            for assignment in assignments:
                print(f"DEBUG: Asignación encontrada: id={assignment.id}, indicativo_id={assignment.indicativo_id}")
            
            for assignment in assignments:
                # Crear diccionario manualmente para evitar problemas de esquema
                assignment_dict = {
                    'id': assignment.id,
                    'incident_id': assignment.incident_id,
                    'indicativo_id': assignment.indicativo_id,
                    'estado_asignacion': assignment.estado_asignacion,
                    'fecha_creacion_asignacion': assignment.fecha_creacion_asignacion.strftime('%Y-%m-%d %H:%M:%S') if assignment.fecha_creacion_asignacion else None,
                }
                
                # Intentar obtener servicio_nombre si existe la columna
                try:
                    assignment_dict['servicio_nombre'] = getattr(assignment, 'servicio_nombre', None)
                except:
                    assignment_dict['servicio_nombre'] = None
                
                # Intentar obtener fechas adicionales si existen
                for field in ['fecha_pre_avisado_asig', 'fecha_avisado_asig', 'fecha_en_camino_asig', 'fecha_en_lugar_asig', 'fecha_finalizado_asig']:
                    try:
                        value = getattr(assignment, field, None)
                        assignment_dict[field] = value.strftime('%Y-%m-%d %H:%M:%S') if value else None
                    except:
                        assignment_dict[field] = None
                
                # Determinar el nombre a mostrar
                if assignment_dict['servicio_nombre']:
                    assignment_dict['indicativo_nombre'] = assignment_dict['servicio_nombre']
                elif assignment_dict['indicativo_id'] and assignment_dict['indicativo_id'] > 0:
                    # Buscar el indicativo para obtener su nombre
                    try:
                        indicativo = Indicativo.query.get(assignment_dict['indicativo_id'])
                        if indicativo:
                            assignment_dict['indicativo_nombre'] = f"{indicativo.indicativo} ({indicativo.nombre})" if indicativo.nombre else indicativo.indicativo
                        else:
                            assignment_dict['indicativo_nombre'] = f"ID: {assignment_dict['indicativo_id']}"
                    except:
                        assignment_dict['indicativo_nombre'] = f"ID: {assignment_dict['indicativo_id']}"
                else:
                    assignment_dict['indicativo_nombre'] = "Asignación sin nombre"
                
                assignments_data.append(assignment_dict)
                
        except Exception as e:
            print(f"Error al cargar asignaciones: {e}")
            # Si incluso el SQL directo falla, devolver lista vacía
            assignments_data = []
        
        return jsonify({
            'status': 'success',
            'assignments': assignments_data
        })
        
    except Exception as e:
        print(f"Error general en get_incident_assignments: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@bp.route('/<int:event_id>/incidents/<int:incident_id>/assignments', methods=['POST'])
def create_incident_assignment(event_id, incident_id):
    try:
        incident = Incident.query.filter_by(id=incident_id, event_id=event_id).first_or_404()
        data = request.get_json()
        if not data or 'indicativo_id' not in data:
            return jsonify({'status': 'error', 'message': 'indicativo_id es requerido'}), 400

        now = datetime.utcnow()
        nuevo_estado_asignacion = data.get('estado_asignacion', 'pre-avisado')
        
        # Determinar si es un indicativo del evento o texto libre
        indicativo_value = str(data['indicativo_id']).strip()
        
        # Buscar si es un indicativo del evento por nombre (formato: "INDICATIVO (nombre)")
        indicativo_found = None
        for indicativo in Indicativo.query.filter_by(event_id=event_id).all():
            indicativo_display = f"{indicativo.indicativo} ({indicativo.nombre})" if indicativo.nombre else indicativo.indicativo
            if indicativo_display == indicativo_value:
                indicativo_found = indicativo
                break
        
        if indicativo_found:
            # Es un indicativo válido del evento
            indicativo_id = indicativo_found.id
            servicio_nombre = None
        else:
            # Es texto libre (CME, GUB, nombres, etc.)
            indicativo_id = -1  # Valor especial para texto libre
            servicio_nombre = indicativo_value

        # Usar SQL directo para insertar la asignación
        try:
            from sqlalchemy import text
            
            # Verificar qué columnas existen en la tabla
            columns_query = db.session.execute(text("PRAGMA table_info(incident_assignments)")).fetchall()
            existing_columns = [col[1] for col in columns_query]
            
            # Construir la consulta de inserción basada en las columnas existentes
            base_columns = ['incident_id', 'estado_asignacion', 'fecha_creacion_asignacion', 'indicativo_id']
            base_values = [incident.id, nuevo_estado_asignacion, now, indicativo_id]
            
            # Agregar servicio_nombre si la columna existe
            if 'servicio_nombre' in existing_columns and servicio_nombre:
                base_columns.append('servicio_nombre')
                base_values.append(servicio_nombre)
            
            # Agregar fecha de estado específica si la columna existe
            estado_fecha_map = {
                'pre-avisado': 'fecha_pre_avisado_asig',
                'avisado': 'fecha_avisado_asig',
                'en camino': 'fecha_en_camino_asig',
                'en el lugar': 'fecha_en_lugar_asig',
                'finalizado': 'fecha_finalizado_asig'
            }
            
            if nuevo_estado_asignacion in estado_fecha_map:
                fecha_column = estado_fecha_map[nuevo_estado_asignacion]
                if fecha_column in existing_columns:
                    base_columns.append(fecha_column)
                    base_values.append(now)
            
            # Construir y ejecutar la consulta
            columns_str = ', '.join(base_columns)
            placeholders = ', '.join([':param' + str(i) for i in range(len(base_values))])
            
            insert_query = f"INSERT INTO incident_assignments ({columns_str}) VALUES ({placeholders})"
            params = {f'param{i}': value for i, value in enumerate(base_values)}
            
            result = db.session.execute(text(insert_query), params)
            db.session.commit()
            
            # Obtener el ID de la asignación creada
            assignment_id = result.lastrowid
            
            # Crear respuesta manual
            assignment_dict = {
                'id': assignment_id,
                'incident_id': incident.id,
                'indicativo_id': indicativo_id,
                'servicio_nombre': servicio_nombre,
                'estado_asignacion': nuevo_estado_asignacion,
                'fecha_creacion_asignacion': now.strftime('%Y-%m-%d %H:%M:%S'),
            }
            
            # Agregar fechas de estado
            for estado, fecha_col in estado_fecha_map.items():
                if estado == nuevo_estado_asignacion and fecha_col in existing_columns:
                    assignment_dict[fecha_col] = now.strftime('%Y-%m-%d %H:%M:%S')
                else:
                    assignment_dict[fecha_col] = None
            
            # Determinar el nombre a mostrar
            if servicio_nombre:
                # Es texto libre (servicio, nombre, etc.)
                assignment_dict['indicativo_nombre'] = servicio_nombre
            elif indicativo_id and indicativo_id > 0:
                # Es un indicativo real del evento
                try:
                    indicativo = Indicativo.query.get(indicativo_id)
                    if indicativo:
                        assignment_dict['indicativo_nombre'] = f"{indicativo.indicativo} ({indicativo.nombre})" if indicativo.nombre else indicativo.indicativo
                    else:
                        assignment_dict['indicativo_nombre'] = f"ID: {indicativo_id}"
                except:
                    assignment_dict['indicativo_nombre'] = f"ID: {indicativo_id}"
            else:
                assignment_dict['indicativo_nombre'] = "Asignación sin nombre"
            
            return jsonify({'status': 'success', 'message': 'Asignación creada', 'assignment': assignment_dict}), 201
            
        except Exception as e:
            db.session.rollback()
            print(f"Error al crear asignación con SQL directo: {e}")
            return jsonify({'status': 'error', 'message': f'Error al crear asignación: {str(e)}'}), 500
            
    except Exception as e:
        print(f"Error general en create_incident_assignment: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@bp.route('/<int:event_id>/incidents/<int:incident_id>/assignments/<int:assignment_id>', methods=['PUT'])
def update_incident_assignment(event_id, incident_id, assignment_id):
    try:
        data = request.get_json()
        now = datetime.utcnow()

        if 'estado_asignacion' in data:
            nuevo_estado = data['estado_asignacion']
            
            # Usar SQL directo para actualizar
            from sqlalchemy import text
            
            # Verificar qué columnas existen
            columns_query = db.session.execute(text("PRAGMA table_info(incident_assignments)")).fetchall()
            existing_columns = [col[1] for col in columns_query]
            
            # Actualizar estado
            update_parts = ['estado_asignacion = :nuevo_estado']
            params = {'nuevo_estado': nuevo_estado, 'assignment_id': assignment_id, 'incident_id': incident_id}
            
            # Agregar fecha de estado específica si la columna existe
            estado_fecha_map = {
                'pre-avisado': 'fecha_pre_avisado_asig',
                'avisado': 'fecha_avisado_asig',
                'en camino': 'fecha_en_camino_asig',
                'en el lugar': 'fecha_en_lugar_asig',
                'finalizado': 'fecha_finalizado_asig'
            }
            
            if nuevo_estado in estado_fecha_map:
                fecha_column = estado_fecha_map[nuevo_estado]
                if fecha_column in existing_columns:
                    update_parts.append(f'{fecha_column} = :fecha_estado')
                    params['fecha_estado'] = now
            
            update_query = f"UPDATE incident_assignments SET {', '.join(update_parts)} WHERE id = :assignment_id AND incident_id = :incident_id"
            db.session.execute(text(update_query), params)
            db.session.commit()
            
            # Obtener la asignación actualizada usando SQL directo
            assignment_query = db.session.execute(
                text("SELECT * FROM incident_assignments WHERE id = :assignment_id AND incident_id = :incident_id"),
                {'assignment_id': assignment_id, 'incident_id': incident_id}
            ).fetchone()
            
            if assignment_query:
                # Crear diccionario de respuesta
                assignment_dict = {
                    'id': assignment_query.id,
                    'incident_id': assignment_query.incident_id,
                    'indicativo_id': assignment_query.indicativo_id,
                    'estado_asignacion': assignment_query.estado_asignacion,
                    'fecha_creacion_asignacion': assignment_query.fecha_creacion_asignacion.strftime('%Y-%m-%d %H:%M:%S') if assignment_query.fecha_creacion_asignacion else None,
                }
                
                # Agregar campos opcionales
                try:
                    assignment_dict['servicio_nombre'] = getattr(assignment_query, 'servicio_nombre', None)
                except:
                    assignment_dict['servicio_nombre'] = None
                
                # Agregar fechas de estado
                for fecha_col in estado_fecha_map.values():
                    try:
                        value = getattr(assignment_query, fecha_col, None)
                        assignment_dict[fecha_col] = value.strftime('%Y-%m-%d %H:%M:%S') if value else None
                    except:
                        assignment_dict[fecha_col] = None
                
                # Determinar el nombre a mostrar
                if assignment_dict['servicio_nombre']:
                    assignment_dict['indicativo_nombre'] = assignment_dict['servicio_nombre']
                elif assignment_dict['indicativo_id'] and assignment_dict['indicativo_id'] > 0:
                    try:
                        indicativo = Indicativo.query.get(assignment_dict['indicativo_id'])
                        if indicativo:
                            assignment_dict['indicativo_nombre'] = f"{indicativo.indicativo} ({indicativo.nombre})" if indicativo.nombre else indicativo.indicativo
                        else:
                            assignment_dict['indicativo_nombre'] = f"ID: {assignment_dict['indicativo_id']}"
                    except:
                        assignment_dict['indicativo_nombre'] = f"ID: {assignment_dict['indicativo_id']}"
                else:
                    assignment_dict['indicativo_nombre'] = "Asignación sin nombre"
                
                return jsonify({'status': 'success', 'message': 'Asignación actualizada', 'assignment': assignment_dict})
            else:
                return jsonify({'status': 'error', 'message': 'Asignación no encontrada después de actualizar'}), 404
        else:
            return jsonify({'status': 'error', 'message': 'No se proporcionaron datos para actualizar'}), 400
            
    except Exception as e:
        db.session.rollback()
        print(f"Error en update_incident_assignment: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@bp.route('/<int:event_id>/incidents/<int:incident_id>/assignments/<int:assignment_id>', methods=['DELETE'])
def delete_incident_assignment(event_id, incident_id, assignment_id):
    assignment = IncidentAssignment.query.filter_by(id=assignment_id, incident_id=incident_id).first_or_404()
    db.session.delete(assignment)
    db.session.commit()
    return jsonify({'status': 'success', 'message': 'Asignación eliminada'})

# Fin del archivo