from flask import Blueprint, jsonify, request, render_template_string
from app.models.event import Event
from app.models.user import User
from app.extensions import db
from datetime import datetime
from app.routes.auth import token_required
from app.models.indicativo import Indicativo

bp = Blueprint('events', __name__, url_prefix='/events')

# Página web de administración
@bp.route('/')
def admin_page():
    return render_template_string(ADMIN_TEMPLATE)

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
    return render_template_string(EVENT_DETAIL_TEMPLATE, event=event)

@bp.route('/<int:event_id>/control')
def event_control(event_id):
    event = Event.query.get_or_404(event_id)
    indicativos = Indicativo.query.filter_by(event_id=event_id).all()
    return render_template_string(EVENT_CONTROL_TEMPLATE, event=event, indicativos=indicativos)

# Template HTML para la página de administración (parte 1)
ADMIN_TEMPLATE_PART1 = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Administración de Eventos</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .header {
            background-color: #2c3e50;
            color: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        .form-container {
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .events-container {
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .form-group {
            margin-bottom: 15px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        input[type="text"], input[type="datetime-local"] {
            width: 100%;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
        }
        button {
            background-color: #3498db;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            margin-right: 10px;
        }
        button:hover {
            background-color: #2980b9;
        }
        button.delete {
            background-color: #e74c3c;
        }
        button.delete:hover {
            background-color: #c0392b;
        }
        button.edit {
            background-color: #f39c12;
        }
        button.edit:hover {
            background-color: #e67e22;
        }
        button.manage {
            background-color: #27ae60;
        }
        button.manage:hover {
            background-color: #219150;
        }
        button.control {
            background-color: #8e44ad;
        }
        button.control:hover, a.control:hover {
            background-color: #6c3483;
        }
        a.control {
            display: inline-block;
            background-color: #8e44ad;
            color: white !important;
            padding: 10px 20px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            margin-right: 5px;
            text-decoration: none;
            transition: background 0.2s;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        th {
            background-color: #f8f9fa;
            font-weight: bold;
        }
        tr:hover {
            background-color: #f5f5f5;
        }
        .alert {
            padding: 15px;
            margin-bottom: 20px;
            border: 1px solid transparent;
            border-radius: 4px;
        }
        .alert-success {
            color: #155724;
            background-color: #d4edda;
            border-color: #c3e6cb;
        }
        .alert-error {
            color: #721c24;
            background-color: #f8d7da;
            border-color: #f5c6cb;
        }
        .status-badge {
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: bold;
            cursor: pointer;
        }
        .status-active {
            background-color: #27ae60;
            color: white;
        }
        .status-inactive {
            background-color: #e74c3c;
            color: white;
        }
    </style>
</head>
<body>
"""

ADMIN_TEMPLATE = ADMIN_TEMPLATE_PART1 + """
    <div class="header">
        <h1>🎉 Administración de Eventos</h1>
        <p>Gestiona todos tus eventos desde aquí</p>
    </div>

    <div id="alertContainer"></div>

    <div id="eventFormContainer" class="form-container" style="display:none;">
        <h2 id="formTitle">Agregar Nuevo Evento</h2>
        <form id="eventForm">
            <input type="hidden" id="eventId" value="">
            <div class="form-group">
                <label for="nombre">Nombre del Evento:</label>
                <input type="text" id="nombre" name="nombre" required>
            </div>
            <div class="form-group">
                <label for="fecha">Fecha y Hora:</label>
                <input type="datetime-local" id="fecha" name="fecha" required>
            </div>
            <button type="submit" id="submitBtn">Actualizar Evento</button>
            <button type="button" id="cancelBtn" onclick="cancelEdit()">Cancelar</button>
        </form>
    </div>

    <div class="events-container">
        <h2>Lista de Eventos</h2>
        <button id="addEventBtn">Añadir Evento</button>
        <table id="eventsTable">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Nombre</th>
                    <th>Fecha</th>
                    <th>Estado</th>
                    <th>Acciones</th>
                </tr>
            </thead>
            <tbody id="eventsTableBody">
            </tbody>
        </table>
    </div>

    <script>
        let editingEventId = null;

        document.addEventListener('DOMContentLoaded', function() {
            loadEvents();
        });

        document.getElementById('addEventBtn').addEventListener('click', function() {
            document.getElementById('eventForm').reset();
            document.getElementById('eventId').value = '';
            document.getElementById('formTitle').textContent = 'Agregar Nuevo Evento';
            document.getElementById('submitBtn').textContent = 'Agregar Evento';
            document.getElementById('cancelBtn').style.display = 'inline-block';
            document.getElementById('eventFormContainer').style.display = 'block';
            document.getElementById('eventForm').style.display = 'block';
            editingEventId = null;
        });

        document.getElementById('eventForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const nombre = document.getElementById('nombre').value;
            const fecha = document.getElementById('fecha').value;
            
            if (!nombre || !fecha) {
                showAlert('Por favor, complete todos los campos', 'error');
                return;
            }

            const fechaFormatted = new Date(fecha).toISOString().slice(0, 19).replace('T', ' ');

            const eventData = {
                nombre: nombre,
                fecha: fechaFormatted
            };

            if (editingEventId) {
                updateEvent(editingEventId, eventData);
            } else {
                createEvent(eventData);
            }
        });

        function loadEvents() {
            fetch('/events/api')
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        displayEvents(data.events);
                    } else {
                        showAlert('Error al cargar eventos: ' + data.message, 'error');
                    }
                })
                .catch(error => {
                    showAlert('Error de conexión: ' + error.message, 'error');
                });
        }

        function displayEvents(events) {
            const tbody = document.getElementById('eventsTableBody');
            tbody.innerHTML = '';

            events.forEach(event => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${event.id}</td>
                    <td>${event.nombre}</td>
                    <td>${new Date(event.fecha).toLocaleString('es-ES')}</td>
                    <td>
                        <span class="status-badge ${event.activo ? 'status-active' : 'status-inactive'}" 
                              onclick="toggleEvent(${event.id}, ${event.activo})">
                            ${event.activo ? 'Activo' : 'Inactivo'}
                        </span>
                    </td>
                    <td>
                        <a class="control" href="/events/${event.id}/control">Control</a>
                        <button class="manage" onclick="window.location='/events/${event.id}'">Gestionar</button>
                        <button class="edit" onclick="editEvent(${event.id}, '${event.nombre}', '${event.fecha}')">Editar</button>
                        <button class="delete" onclick="deleteEvent(${event.id})">Eliminar</button>
                    </td>
                `;
                tbody.appendChild(row);
            });
        }

        function createEvent(eventData) {
            fetch('/events/api', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(eventData)
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    showAlert('Evento creado exitosamente', 'success');
                    resetForm();
                    loadEvents();
                } else {
                    showAlert('Error al crear evento: ' + data.message, 'error');
                }
            })
            .catch(error => {
                showAlert('Error de conexión: ' + error.message, 'error');
            });
        }

        function editEvent(id, nombre, fecha) {
            editingEventId = id;
            document.getElementById('eventId').value = id;
            document.getElementById('nombre').value = nombre;
            const [datePart, timePart] = fecha.split(' ');
            const fechaInput = datePart + 'T' + timePart.slice(0,5);
            document.getElementById('fecha').value = fechaInput;
            document.getElementById('formTitle').textContent = 'Editar Evento';
            document.getElementById('submitBtn').textContent = 'Actualizar Evento';
            document.getElementById('cancelBtn').style.display = 'inline-block';
            document.getElementById('eventFormContainer').style.display = 'block';
            document.getElementById('eventForm').style.display = 'block';
        }

        function updateEvent(id, eventData) {
            fetch(`/events/api/${id}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(eventData)
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    showAlert('Evento actualizado exitosamente', 'success');
                    resetForm();
                    loadEvents();
                } else {
                    showAlert('Error al actualizar evento: ' + data.message, 'error');
                }
            })
            .catch(error => {
                showAlert('Error de conexión: ' + error.message, 'error');
            });
        }

        function deleteEvent(id) {
            if (confirm('¿Estás seguro de que quieres eliminar este evento?')) {
                fetch(`/events/api/${id}`, {
                    method: 'DELETE'
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        showAlert('Evento eliminado exitosamente', 'success');
                        loadEvents();
                    } else {
                        showAlert('Error al eliminar evento: ' + data.message, 'error');
                    }
                })
                .catch(error => {
                    showAlert('Error de conexión: ' + error.message, 'error');
                });
            }
        }

        function cancelEdit() {
            resetForm();
        }

        function resetForm() {
            editingEventId = null;
            document.getElementById('eventForm').reset();
            document.getElementById('eventId').value = '';
            document.getElementById('formTitle').textContent = 'Agregar Nuevo Evento';
            document.getElementById('submitBtn').textContent = 'Agregar Evento';
            document.getElementById('cancelBtn').style.display = 'none';
            document.getElementById('eventFormContainer').style.display = 'none';
            document.getElementById('eventForm').style.display = 'none';
        }

        function showAlert(message, type) {
            const alertContainer = document.getElementById('alertContainer');
            const alert = document.createElement('div');
            alert.className = `alert alert-${type}`;
            alert.textContent = message;
            
            alertContainer.innerHTML = '';
            alertContainer.appendChild(alert);
            
            setTimeout(() => {
                alert.remove();
            }, 5000);
        }

        function toggleEvent(id, currentStatus) {
            if (confirm(`¿Estás seguro de que quieres ${currentStatus ? 'desactivar' : 'activar'} este evento?`)) {
                fetch(`/events/api/${id}/toggle`, {
                    method: 'POST'
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        showAlert(data.message, 'success');
                        loadEvents();
                    } else {
                        showAlert('Error al cambiar estado: ' + data.message, 'error');
                    }
                })
                .catch(error => {
                    showAlert('Error de conexión: ' + error.message, 'error');
                });
            }
        }
    </script>
</body>
</html>
"""

EVENT_DETAIL_TEMPLATE = """
<!DOCTYPE html>
<html lang='es'>
<head>
    <meta charset='UTF-8'>
    <meta name='viewport' content='width=device-width, initial-scale=1.0'>
    <title>Detalle de Evento</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; background-color: #f5f5f5; }
        .header { background-color: #2c3e50; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .form-container, .indicativos-container { background-color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input[type='text'], input[type='datetime-local'] { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; font-size: 14px; }
        button { background-color: #3498db; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; font-size: 14px; margin-right: 10px; }
        button:hover { background-color: #2980b9; }
        button.delete { background-color: #e74c3c; }
        button.delete:hover { background-color: #c0392b; }
        button.edit { background-color: #f39c12; }
        button.edit:hover { background-color: #e67e22; }
        button.manage {
            background-color: #27ae60;
        }
        button.manage:hover {
            background-color: #219150;
        }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background-color: #f8f9fa; font-weight: bold; }
        tr:hover { background-color: #f5f5f5; }
        .alert { padding: 15px; margin-bottom: 20px; border: 1px solid transparent; border-radius: 4px; }
        .alert-success { color: #155724; background-color: #d4edda; border-color: #c3e6cb; }
        .alert-error { color: #721c24; background-color: #f8d7da; border-color: #f5c6cb; }
    </style>
</head>
<body>
    <div class='header'>
        <h1>Detalle de Evento</h1>
        <p><b>ID:</b> {{ event.id }}<br>
           <b>Nombre:</b> {{ event.nombre }}<br>
           <b>Fecha:</b> {{ event.fecha }}<br>
        </p>
        <a href='/events/' style='color:white;'>← Volver a Eventos</a>
    </div>
    <div id='alertContainer'></div>
    <div id="indicativoFormContainer" class="form-container" style="display:none;">
        <h2 id='formTitle'>Agregar Indicativo</h2>
        <form id="indicativoForm">
            <input type='hidden' id='indicativoId' value=''>
            <div class='form-group'>
                <label for='indicativo'>Indicativo:</label>
                <input type='text' id='indicativo' name='indicativo' required>
            </div>
            <div class='form-group'>
                <label for='nombre'>Nombre:</label>
                <input type='text' id='nombre' name='nombre'>
            </div>
            <div class='form-group'>
                <label for='localizacion'>Localización:</label>
                <input type='text' id='localizacion' name='localizacion'>
            </div>
            <div class='form-group'>
                <label for='fecha_inicio'>Fecha Inicio:</label>
                <input type='datetime-local' id='fecha_inicio' name='fecha_inicio'>
            </div>
            <div class='form-group'>
                <label for='fecha_fin'>Fecha Fin:</label>
                <input type='datetime-local' id='fecha_fin' name='fecha_fin'>
            </div>
            <button type='submit' id='submitBtn'>Actualizar Indicativo</button>
            <button type='button' id='cancelBtn' onclick='cancelEdit()'>Cancelar</button>
        </form>
    </div>
    <div class='indicativos-container'>
        <h2>Lista de Indicativos</h2>
        <button id="addIndicativoBtn">Añadir Indicativo</button>
        <table id='indicativosTable'>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Indicativo</th>
                    <th>Nombre</th>
                    <th>Localización</th>
                    <th>Fecha Inicio</th>
                    <th>Fecha Fin</th>
                    <th>Acciones</th>
                </tr>
            </thead>
            <tbody id='indicativosTableBody'>
            </tbody>
        </table>
    </div>
    <script>
        let editingIndicativoId = null;
        document.addEventListener('DOMContentLoaded', function() {
            loadIndicativos();
        });
        document.getElementById('addIndicativoBtn').addEventListener('click', function() {
            document.getElementById('indicativoForm').reset();
            document.getElementById('indicativoId').value = '';
            document.getElementById('formTitle').textContent = 'Agregar Nuevo Indicativo';
            document.getElementById('submitBtn').textContent = 'Agregar Indicativo';
            document.getElementById('cancelBtn').style.display = 'inline-block';
            document.getElementById('indicativoFormContainer').style.display = 'block';
            document.getElementById('indicativoForm').style.display = 'block';
            editingIndicativoId = null;
        });
        document.getElementById('indicativoForm').addEventListener('submit', function(e) {
            e.preventDefault();
            const indicativo = document.getElementById('indicativo').value;
            const nombre = document.getElementById('nombre').value;
            const localizacion = document.getElementById('localizacion').value;
            const fecha_inicio = document.getElementById('fecha_inicio').value;
            const fecha_fin = document.getElementById('fecha_fin').value;
            const data = {
                indicativo,
                nombre,
                localizacion,
                fecha_inicio: fecha_inicio ? fecha_inicio.replace('T', ' ') + ':00' : null,
                fecha_fin: fecha_fin ? fecha_fin.replace('T', ' ') + ':00' : null
            };
            if (editingIndicativoId) {
                updateIndicativo(editingIndicativoId, data);
            } else {
                createIndicativo(data);
            }
        });
        function loadIndicativos() {
            fetch(`/events/{{ event.id }}/indicativos/api`)
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        displayIndicativos(data.indicativos);
                    } else {
                        showAlert('Error al cargar indicativos: ' + data.message, 'error');
                    }
                })
                .catch(error => {
                    showAlert('Error de conexión: ' + error.message, 'error');
                });
        }
        function displayIndicativos(indicativos) {
            const tbody = document.getElementById('indicativosTableBody');
            tbody.innerHTML = '';
            indicativos.forEach(indicativo => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${indicativo.id}</td>
                    <td>${indicativo.indicativo || ''}</td>
                    <td>${indicativo.nombre || ''}</td>
                    <td>${indicativo.localizacion || ''}</td>
                    <td>${indicativo.fecha_inicio || ''}</td>
                    <td>${indicativo.fecha_fin || ''}</td>
                    <td>
                        <button class='edit' onclick="editIndicativo(${indicativo.id}, '${indicativo.indicativo || ''}', '${indicativo.nombre || ''}', '${indicativo.localizacion || ''}', '${indicativo.fecha_inicio || ''}', '${indicativo.fecha_fin || ''}')">Editar</button>
                        <button class='delete' onclick='deleteIndicativo(${indicativo.id})'>Eliminar</button>
                    </td>
                `;
                tbody.appendChild(row);
            });
        }
        function createIndicativo(data) {
            fetch(`/events/{{ event.id }}/indicativos/api`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    showAlert('Indicativo creado exitosamente', 'success');
                    resetForm();
                    loadIndicativos();
                } else {
                    showAlert('Error al crear indicativo: ' + data.message, 'error');
                }
            })
            .catch(error => {
                showAlert('Error de conexión: ' + error.message, 'error');
            });
        }
        function editIndicativo(id, indicativo, nombre, localizacion, fecha_inicio, fecha_fin) {
            editingIndicativoId = id;
            document.getElementById('indicativoId').value = id;
            document.getElementById('indicativo').value = indicativo;
            document.getElementById('nombre').value = nombre;
            document.getElementById('localizacion').value = localizacion;
            document.getElementById('fecha_inicio').value = fecha_inicio ? fecha_inicio.replace(' ', 'T').slice(0,16) : '';
            document.getElementById('fecha_fin').value = fecha_fin ? fecha_fin.replace(' ', 'T').slice(0,16) : '';
            document.getElementById('formTitle').textContent = 'Editar Indicativo';
            document.getElementById('submitBtn').textContent = 'Actualizar Indicativo';
            document.getElementById('cancelBtn').style.display = 'inline-block';
            document.getElementById('indicativoFormContainer').style.display = 'block';
            document.getElementById('indicativoForm').style.display = 'block';
        }
        function updateIndicativo(id, data) {
            fetch(`/events/{{ event.id }}/indicativos/api/${id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    showAlert('Indicativo actualizado exitosamente', 'success');
                    resetForm();
                    loadIndicativos();
                } else {
                    showAlert('Error al actualizar indicativo: ' + data.message, 'error');
                }
            })
            .catch(error => {
                showAlert('Error de conexión: ' + error.message, 'error');
            });
        }
        function deleteIndicativo(id) {
            if (confirm('¿Estás seguro de que quieres eliminar este indicativo?')) {
                fetch(`/events/{{ event.id }}/indicativos/api/${id}`, {
                    method: 'DELETE'
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        showAlert('Indicativo eliminado exitosamente', 'success');
                        loadIndicativos();
                    } else {
                        showAlert('Error al eliminar indicativo: ' + data.message, 'error');
                    }
                })
                .catch(error => {
                    showAlert('Error de conexión: ' + error.message, 'error');
                });
            }
        }
        function cancelEdit() {
            resetForm();
        }
        function resetForm() {
            editingIndicativoId = null;
            document.getElementById('indicativoForm').reset();
            document.getElementById('indicativoId').value = '';
            document.getElementById('formTitle').textContent = 'Agregar Nuevo Indicativo';
            document.getElementById('submitBtn').textContent = 'Agregar Indicativo';
            document.getElementById('cancelBtn').style.display = 'none';
            document.getElementById('indicativoFormContainer').style.display = 'none';
            document.getElementById('indicativoForm').style.display = 'none';
        }
        function showAlert(message, type) {
            const alertContainer = document.getElementById('alertContainer');
            const alert = document.createElement('div');
            alert.className = `alert alert-${type}`;
            alert.textContent = message;
            alertContainer.innerHTML = '';
            alertContainer.appendChild(alert);
            setTimeout(() => { alert.remove(); }, 5000);
        }
    </script>
</body>
</html>
"""

# Plantilla básica para control de evento (chat + mapa)
EVENT_CONTROL_TEMPLATE = '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Control de Evento - {{ event.nombre }}</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css" />
    <style>
        body { font-family: Arial, sans-serif; background: #f5f5f5; margin: 0; padding: 0; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header { background: #2c3e50; color: #fff; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .chat-container { display: flex; gap: 20px; }
        .chat-panel { flex: 2; background: #fff; border-radius: 8px; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .map-panel { flex: 1; background: #fff; border-radius: 8px; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); min-width: 350px; }
        #chatHistory { height: 350px; overflow-y: auto; border: 1px solid #eee; margin-bottom: 10px; padding: 10px; background: #fafafa; }
        #map { height: 350px; width: 100%; border-radius: 8px; }
        .message { margin-bottom: 10px; }
        .message .meta { font-size: 12px; color: #888; }
        .message .content { font-size: 15px; }
        .message.location { background: #e3f2fd; border-left: 4px solid #2196f3; padding: 5px 10px; border-radius: 4px; }
        .indicativo-select { margin-bottom: 10px; }
    </style>
</head>
<body>
<div class="container">
    <div class="header">
        <h1>Control de Evento: {{ event.nombre }}</h1>
        <a href="/events/" style="color:white;">← Volver a Eventos</a>
    </div>
    <div class="chat-container">
        <div class="chat-panel">
            <div class="indicativo-select">
                <label for="indicativoSelect"><b>Selecciona tu indicativo:</b></label>
                <select id="indicativoSelect">
                    <option value="">-- Elige un indicativo --</option>
                    {% for ind in indicativos %}
                        <option value="{{ ind.id }}">{{ ind.indicativo }} ({{ ind.nombre or '' }})</option>
                    {% endfor %}
                </select>
            </div>
            <div id="chatHistory"></div>
            <form id="chatForm" style="display:flex; gap:5px;">
                <input type="text" id="chatInput" placeholder="Escribe un mensaje..." style="flex:1; padding:8px;">
                <button type="submit">Enviar</button>
                <button type="button" id="sendLocationBtn">📍</button>
            </form>
        </div>
        <div class="map-panel">
            <h3>Localizaciones</h3>
            <div id="map"></div>
        </div>
    </div>
    <!-- Modal de ubicación manual -->
    <div id="locationModal" style="display:none; position:fixed; top:0; left:0; width:100vw; height:100vh; background:rgba(0,0,0,0.4); z-index:1000; align-items:center; justify-content:center;">
        <div style="background:#fff; border-radius:8px; max-width:500px; width:95vw; margin:40px auto; padding:20px; position:relative;">
            <button id="closeLocationModal" style="position:absolute; top:10px; right:10px; background:#e74c3c; color:#fff; border:none; border-radius:50%; width:32px; height:32px; font-size:18px; cursor:pointer;">&times;</button>
            <h2>Enviar ubicación manualmente</h2>
            <div style="margin-bottom:10px;">
                <label><b>Buscar dirección:</b></label>
                <input type="text" id="addressInput" placeholder="Ej: Plaça Catalunya, Barcelona" style="width:80%;">
                <button type="button" id="searchAddressBtn">Buscar</button>
            </div>
            <div style="margin-bottom:10px;">
                <label><b>Latitud:</b></label>
                <input type="number" id="latInput" step="any" style="width:40%;">
                <label><b>Longitud:</b></label>
                <input type="number" id="lngInput" step="any" style="width:40%;">
            </div>
            <div id="manualMap" style="height:250px; width:100%; margin-bottom:10px; border-radius:8px;"></div>
            <button type="button" id="sendManualLocationBtn" style="background:#8e44ad; color:#fff; padding:10px 20px; border:none; border-radius:4px; cursor:pointer;">Enviar ubicación</button>
        </div>
    </div>
</div>
<script src="https://cdn.socket.io/4.7.5/socket.io.min.js"></script>
<script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>
<script>
const eventId = {{ event.id }};
const indicativoKey = `rcq_indicativo_${eventId}`;
let indicativoId = localStorage.getItem(indicativoKey) || '';
const indicativoSelect = document.getElementById('indicativoSelect');
indicativoSelect.value = indicativoId;
indicativoSelect.addEventListener('change', function() {
    indicativoId = this.value;
    if (indicativoId) localStorage.setItem(indicativoKey, indicativoId);
});
// Socket.IO
let socket = null;
let joined = false;
const chatHistory = document.getElementById('chatHistory');
// --- MAPA DE LOCALIZACIONES: solo última ubicación de cada indicativo ---
const lastLocations = {}; // indicativo_id -> msg
const markerRefs = {}; // indicativo_id -> marker
let selectedMarker = null;

function updateLocationMarkers() {
    // Limpiar marcadores
    Object.values(markerRefs).forEach(m => map.removeLayer(m));
    Object.keys(markerRefs).forEach(k => delete markerRefs[k]);
    // Añadir solo la última ubicación de cada indicativo
    Object.values(lastLocations).forEach(msg => {
        if (msg.content.type === 'location') {
            const marker = L.marker([msg.content.lat, msg.content.lng], {
                icon: (msg.indicativo_id == indicativoId) ? L.icon({
                    iconUrl: 'https://cdn.jsdelivr.net/gh/pointhi/leaflet-color-markers@master/img/marker-icon-violet.png',
                    shadowUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-shadow.png',
                    iconSize: [25, 41], iconAnchor: [12, 41], popupAnchor: [1, -34], shadowSize: [41, 41]
                }) : undefined
            }).addTo(map);
            marker.bindPopup(`<b>${msg.indicativo}</b><br>${msg.timestamp}`);
            markerRefs[msg.indicativo_id] = marker;
        }
    });
}

function appendMessage(msg) {
    const div = document.createElement('div');
    div.className = 'message' + (msg.content.type === 'location' ? ' location' : '');
    div.innerHTML = `<div class="meta"><b>${msg.indicativo || ''}</b> <span>${msg.timestamp}</span></div>`;
    if (msg.content.type === 'text') {
        div.innerHTML += `<div class="content">${msg.content.text}</div>`;
    } else if (msg.content.type === 'location') {
        div.innerHTML += `<div class="content">📍 Ubicación: (${msg.content.lat}, ${msg.content.lng})</div>`;
        // Guardar última ubicación
        lastLocations[msg.indicativo_id] = msg;
        div.style.cursor = 'pointer';
        div.addEventListener('click', function() {
            // Centrar y resaltar marcador
            const marker = markerRefs[msg.indicativo_id];
            if (marker) {
                map.setView([msg.content.lat, msg.content.lng], 15);
                marker.openPopup();
                if (selectedMarker) selectedMarker.setZIndexOffset(0);
                marker.setZIndexOffset(1000);
                selectedMarker = marker;
            }
        });
    }
    chatHistory.appendChild(div);
    chatHistory.scrollTop = chatHistory.scrollHeight;
    updateLocationMarkers();
}

// En historial, reconstruir lastLocations y marcadores
socket.on('message_history', data => {
    chatHistory.innerHTML = '';
    Object.keys(lastLocations).forEach(k => delete lastLocations[k]);
    Object.keys(markerRefs).forEach(k => { map.removeLayer(markerRefs[k]); delete markerRefs[k]; });
    (data.messages || []).forEach(msg => {
        appendMessage(msg);
    });
    updateLocationMarkers();
});
socket.on('new_message', msg => {
    appendMessage(msg);
    // updateLocationMarkers() ya se llama en appendMessage
});

function joinChat() {
    if (!indicativoId) return;
    if (socket) socket.disconnect();
    socket = io();
    socket.emit('join_event', { event_id: eventId, indicativo_id: indicativoId });
    joined = true;
    socket.on('message_history', data => {
        chatHistory.innerHTML = '';
        updateLocationMarkers();
    });
    socket.on('new_message', msg => {
        appendMessage(msg);
        addLocationModal.style.display = 'none';
    });
    socket.on('error', err => {
        alert(err.message);
    });
}
indicativoSelect.addEventListener('change', function() {
    if (this.value) joinChat();
});
if (indicativoId) joinChat();
document.getElementById('chatForm').addEventListener('submit', function(e) {
    e.preventDefault();
    if (!indicativoId) return alert('Selecciona un indicativo');
    const text = document.getElementById('chatInput').value.trim();
    if (!text) return;
    socket.emit('send_message', {
        event_id: eventId,
        indicativo_id: indicativoId,
        content: { type: 'text', text }
    });
    document.getElementById('chatInput').value = '';
});
// --- MODAL UBICACIÓN MANUAL ---
const locationModal = document.getElementById('locationModal');
const closeLocationModal = document.getElementById('closeLocationModal');
const addressInput = document.getElementById('addressInput');
const searchAddressBtn = document.getElementById('searchAddressBtn');
const latInput = document.getElementById('latInput');
const lngInput = document.getElementById('lngInput');
const sendManualLocationBtn = document.getElementById('sendManualLocationBtn');
let manualMap, manualMarker;

function openLocationModal() {
    locationModal.style.display = 'flex';
    // Centrar en Barcelona
    if (!manualMap) {
        manualMap = L.map('manualMap').setView([41.3874, 2.1686], 13);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }).addTo(manualMap);
        manualMap.on('click', function(e) {
            setManualMarker(e.latlng.lat, e.latlng.lng);
        });
    } else {
        manualMap.setView([41.3874, 2.1686], 13);
    }
    if (manualMarker) manualMap.removeLayer(manualMarker);
    latInput.value = '';
    lngInput.value = '';
    addressInput.value = '';
}
function closeLocationModalFn() {
    locationModal.style.display = 'none';
}
function setManualMarker(lat, lng) {
    if (manualMarker) manualMap.removeLayer(manualMarker);
    manualMarker = L.marker([lat, lng]).addTo(manualMap);
    latInput.value = lat;
    lngInput.value = lng;
}
searchAddressBtn.addEventListener('click', function() {
    const address = addressInput.value.trim();
    if (!address) return;
    fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(address)}`)
        .then(r => r.json())
        .then(results => {
            if (results && results.length > 0) {
                const { lat, lon } = results[0];
                setManualMarker(parseFloat(lat), parseFloat(lon));
                manualMap.setView([lat, lon], 16);
            } else {
                alert('Dirección no encontrada');
            }
        });
});
latInput.addEventListener('change', function() {
    const lat = parseFloat(latInput.value);
    const lng = parseFloat(lngInput.value);
    if (!isNaN(lat) && !isNaN(lng)) setManualMarker(lat, lng);
});
lngInput.addEventListener('change', function() {
    const lat = parseFloat(latInput.value);
    const lng = parseFloat(lngInput.value);
    if (!isNaN(lat) && !isNaN(lng)) setManualMarker(lat, lng);
});
closeLocationModal.addEventListener('click', closeLocationModalFn);
sendManualLocationBtn.addEventListener('click', function() {
    const lat = parseFloat(latInput.value);
    const lng = parseFloat(lngInput.value);
    if (isNaN(lat) || isNaN(lng)) return alert('Introduce una latitud y longitud válidas');
    if (!indicativoId) return alert('Selecciona un indicativo');
    socket.emit('send_message', {
        event_id: eventId,
        indicativo_id: indicativoId,
        content: { type: 'location', lat, lng }
    });
    closeLocationModalFn();
});
document.getElementById('sendLocationBtn').addEventListener('click', function() {
    if (!indicativoId) return alert('Selecciona un indicativo');
    // Solo móvil: usar geolocalización
    if (/Mobi|Android/i.test(navigator.userAgent)) {
        if (!navigator.geolocation) return alert('Geolocalización no soportada');
        navigator.geolocation.getCurrentPosition(function(pos) {
            const { latitude, longitude } = pos.coords;
            socket.emit('send_message', {
                event_id: eventId,
                indicativo_id: indicativoId,
                content: { type: 'location', lat: latitude, lng: longitude }
            });
        }, function() {
            alert('No se pudo obtener la ubicación');
        });
    } else {
        openLocationModal();
    }
});
// Cambiar el mapa principal a Barcelona
map.setView([41.3874, 2.1686], 10);
</script>
</body>
</html>
''' 