from flask import Blueprint, jsonify, request
from app.models.event import Event
from app import db
from app.routes.auth import token_required

bp = Blueprint('events', __name__, url_prefix='/events')

@bp.route('/', methods=['GET'])
def get_events():
    # TODO: Implementar obtención de eventos
    return jsonify({'message': 'Not implemented yet'}), 501

@bp.route('/<int:event_id>', methods=['GET'])
def get_event(event_id):
    # TODO: Implementar obtención de evento específico
    return jsonify({'message': 'Not implemented yet'}), 501

@bp.route('/', methods=['POST'])
@token_required
def create_event(current_user):
    # TODO: Implementar creación de eventos
    return jsonify({'message': 'Not implemented yet'}), 501

@bp.route('/<int:event_id>', methods=['PUT'])
@token_required
def update_event(current_user, event_id):
    # TODO: Implementar actualización de eventos
    return jsonify({'message': 'Not implemented yet'}), 501

@bp.route('/<int:event_id>', methods=['DELETE'])
@token_required
def delete_event(current_user, event_id):
    # TODO: Implementar eliminación de eventos
    return jsonify({'message': 'Not implemented yet'}), 501 