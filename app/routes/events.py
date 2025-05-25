from flask import Blueprint, jsonify, request, render_template_string
from app.models.event import Event
from app.models.user import User
from app import db
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

    <div class="form-container">
        <h2 id="formTitle">Agregar Nuevo Evento</h2>
        <form id="eventForm" style="display:none;">
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
            <button type="button" id="cancelBtn" onclick="cancelEdit()" style="display: none;">Cancelar</button>
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
            document.getElementById('eventForm').style.display = 'block';
            document.getElementById('formTitle').textContent = 'Agregar Nuevo Evento';
            document.getElementById('submitBtn').textContent = 'Agregar Evento';
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
            // fecha viene como "YYYY-MM-DD HH:MM:SS"
            // Convertimos a "YYYY-MM-DDTHH:MM" para el input
            const [datePart, timePart] = fecha.split(' ');
            const fechaInput = datePart + 'T' + timePart.slice(0,5);
            document.getElementById('fecha').value = fechaInput;
            document.getElementById('formTitle').textContent = 'Editar Evento';
            document.getElementById('submitBtn').textContent = 'Actualizar Evento';
            document.getElementById('cancelBtn').style.display = 'inline-block';
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
    <div class='form-container'>
        <h2 id='formTitle'>Agregar Indicativo</h2>
        <form id='indicativoForm' style="display:none;">
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
            <button type='button' id='cancelBtn' onclick='cancelEdit()' style='display: none;'>Cancelar</button>
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
            document.getElementById('indicativoForm').style.display = 'block';
            document.getElementById('formTitle').textContent = 'Agregar Nuevo Indicativo';
            document.getElementById('submitBtn').textContent = 'Agregar Indicativo';
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