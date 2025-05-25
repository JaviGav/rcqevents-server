from flask_socketio import SocketIO, emit, join_room, leave_room
from app import db
from app.models.message import Message
from app.models.event import Event
from datetime import datetime

socketio = SocketIO()

@socketio.on('connect')
def handle_connect():
    print('Cliente conectado')

@socketio.on('disconnect')
def handle_disconnect():
    print('Cliente desconectado')

@socketio.on('join_event')
def handle_join_event(data):
    """Unirse a la sala de chat de un evento específico"""
    event_id = data.get('event_id')
    if not event_id:
        emit('error', {'message': 'Se requiere event_id'})
        return
    
    # Verificar que el evento existe y está activo
    event = Event.query.get(event_id)
    if not event:
        emit('error', {'message': 'Evento no encontrado'})
        return
    if not event.activo:
        emit('error', {'message': 'El evento está inactivo'})
        return
    
    # Unirse a la sala del evento
    room = f'event_{event_id}'
    join_room(room)
    
    # Enviar historial de mensajes
    messages = Message.query.filter_by(event_id=event_id).order_by(Message.timestamp.asc()).all()
    emit('message_history', {'messages': [msg.to_dict() for msg in messages]})
    
    # Notificar a otros usuarios
    emit('user_joined', {'message': f'Usuario se unió al chat'}, room=room, include_self=False)

@socketio.on('leave_event')
def handle_leave_event(data):
    """Salir de la sala de chat de un evento"""
    event_id = data.get('event_id')
    if event_id:
        room = f'event_{event_id}'
        leave_room(room)
        emit('user_left', {'message': f'Usuario dejó el chat'}, room=room)

@socketio.on('send_message')
def handle_send_message(data):
    """Enviar un mensaje a la sala de chat de un evento"""
    event_id = data.get('event_id')
    sender = data.get('sender')
    content = data.get('content')
    
    if not all([event_id, sender, content]):
        emit('error', {'message': 'Faltan campos requeridos'})
        return
    
    # Verificar que el evento existe y está activo
    event = Event.query.get(event_id)
    if not event:
        emit('error', {'message': 'Evento no encontrado'})
        return
    if not event.activo:
        emit('error', {'message': 'El evento está inactivo'})
        return
    
    # Crear y guardar el mensaje
    message = Message(
        event_id=event_id,
        sender=sender,
        content=content
    )
    db.session.add(message)
    db.session.commit()
    
    # Enviar el mensaje a todos en la sala
    room = f'event_{event_id}'
    emit('new_message', message.to_dict(), room=room) 