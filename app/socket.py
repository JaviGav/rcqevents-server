from flask_socketio import SocketIO, emit, join_room, leave_room
from app.models.message import Message
from app.models.event import Event
from app.models.indicativo import Indicativo
from datetime import datetime
from app.extensions import db

socketio = SocketIO()

@socketio.on('connect')
def handle_connect():
    print('Cliente conectado')

@socketio.on('disconnect')
def handle_disconnect():
    print('Cliente desconectado')

@socketio.on('join_event')
def handle_join_event(data):
    event_id = data.get('event_id')
    indicativo_id = data.get('indicativo_id')
    
    if not event_id or not indicativo_id:
        emit('error', {'message': 'Se requiere event_id e indicativo_id'})
        return
    # Verificar que el evento existe y está activo
    event = Event.query.get(event_id)
    if not event:
        emit('error', {'message': 'Evento no encontrado'})
        return
    if not event.activo:
        emit('error', {'message': 'El evento está inactivo'})
        return
    # Verificar que el indicativo existe y pertenece al evento
    indicativo = Indicativo.query.filter_by(id=indicativo_id, event_id=event_id).first()
    if not indicativo:
        emit('error', {'message': 'Indicativo no encontrado o no pertenece al evento'})
        return
    # Unirse a la sala del evento y a la sala privada del indicativo
    room = f'event_{event_id}'
    join_room(room)
    join_room(f'indicativo_{indicativo_id}_event_{event_id}')
    # Enviar historial de mensajes
    messages = Message.query.filter_by(event_id=event_id).order_by(Message.timestamp.asc()).all()
    emit('message_history', {'messages': [msg.to_dict() for msg in messages]})
    # Notificar a otros usuarios
    emit('user_joined', {
        'message': f'Indicativo {indicativo.indicativo} se unió al chat',
        'indicativo': indicativo.to_dict()
    }, room=room, include_self=False)

@socketio.on('leave_event')
def handle_leave_event(data):
    event_id = data.get('event_id')
    indicativo_id = data.get('indicativo_id')
    
    if event_id and indicativo_id:
        room = f'event_{event_id}'
        indicativo = Indicativo.query.get(indicativo_id)
        leave_room(room)
        if indicativo:
            emit('user_left', {
                'message': f'Indicativo {indicativo.indicativo} dejó el chat',
                'indicativo': indicativo.to_dict()
            }, room=room)

@socketio.on('send_message')
def handle_send_message(data):
    event_id = data.get('event_id')
    indicativo_id = data.get('indicativo_id')
    content = data.get('content')
    to_indicativo_id = data.get('to_indicativo_id')
    
    if not all([event_id, indicativo_id, content]):
        emit('error', {'message': 'Faltan campos requeridos'})
        return
    # Validar que content sea un JSON y contenga 'type'
    if not isinstance(content, dict):
        emit('error', {'message': 'El campo content debe ser un JSON'})
        return
    if 'type' not in content:
        emit('error', {'message': 'El campo content debe contener la clave "type"'})
        return
    # Verificar que el evento existe y está activo
    event = Event.query.get(event_id)
    if not event:
        emit('error', {'message': 'Evento no encontrado'})
        return
    if not event.activo:
        emit('error', {'message': 'El evento está inactivo'})
        return
    # Verificar que el indicativo existe y pertenece al evento
    indicativo = Indicativo.query.filter_by(id=indicativo_id, event_id=event_id).first()
    if not indicativo:
        emit('error', {'message': 'Indicativo no encontrado o no pertenece al evento'})
        return
    # Si es privado, verificar que el destinatario existe y pertenece al evento
    to_indicativo = None
    if to_indicativo_id:
        to_indicativo = Indicativo.query.filter_by(id=to_indicativo_id, event_id=event_id).first()
        if not to_indicativo:
            emit('error', {'message': 'Indicativo destinatario no encontrado o no pertenece al evento'})
            return
    # Crear y guardar el mensaje
    message = Message(
        event_id=event_id,
        indicativo_id=indicativo_id,
        content=content
    )
    db.session.add(message)
    db.session.commit()
    # Preparar el mensaje para emitir
    msg_dict = message.to_dict()
    msg_dict['to_indicativo_id'] = to_indicativo_id
    # Emitir el mensaje
    if to_indicativo_id:
        # Mensaje privado: solo al emisor y destinatario
        room_emisor = f'indicativo_{indicativo_id}_event_{event_id}'
        room_dest = f'indicativo_{to_indicativo_id}_event_{event_id}'
        emit('new_message', msg_dict, room=room_emisor)
        if to_indicativo_id != str(indicativo_id):
            emit('new_message', msg_dict, room=room_dest)
    else:
        # Mensaje público: a toda la sala del evento
        room = f'event_{event_id}'
        emit('new_message', msg_dict, room=room) 