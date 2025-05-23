from flask import Blueprint, jsonify, request, render_template_string
from app.models.event import Event
from app import db
from datetime import datetime

bp = Blueprint('events', __name__, url_prefix='/events')

# Página web de administración
@bp.route('/admin')
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
        return jsonify({
            'status': 'success',
            'event': event.to_dict()
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@bp.route('/api', methods=['POST'])
def create_event():
    try:
        data = request.get_json()
        
        # Validar datos requeridos
        if not data or 'nombre' not in data or 'fecha' not in data:
            return jsonify({'status': 'error', 'message': 'Nombre y fecha son requeridos'}), 400
        
        # Convertir fecha string a datetime
        fecha = datetime.strptime(data['fecha'], '%Y-%m-%d %H:%M:%S')
        
        # Crear nuevo evento
        evento = Event(
            nombre=data['nombre'],
            fecha=fecha
        )
        
        db.session.add(evento)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Evento creado exitosamente',
            'event': evento.to_dict()
        }), 201
        
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
            <button type="submit" id="submitBtn">Agregar Evento</button>
            <button type="button" id="cancelBtn" onclick="cancelEdit()" style="display: none;">Cancelar</button>
        </form>
    </div>

    <div class="events-container">
        <h2>Lista de Eventos</h2>
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
            
            const fechaObj = new Date(fecha);
            const fechaInput = fechaObj.toISOString().slice(0, 16);
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