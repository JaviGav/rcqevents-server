from flask import Blueprint, jsonify, request, current_app
from app.models.user import User
from app.extensions import db
import jwt
from datetime import datetime, timedelta
from functools import wraps

bp = Blueprint('auth', __name__, url_prefix='/auth')

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        try:
            token = token.split(' ')[1]  # Remove 'Bearer ' prefix
            data = jwt.decode(token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            current_user = User.query.get(data['user_id'])
        except:
            return jsonify({'message': 'Token is invalid'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

@bp.route('/register', methods=['POST'])
def register():
    # TODO: Implementar registro de usuarios
    return jsonify({'message': 'Not implemented yet'}), 501

@bp.route('/login', methods=['POST'])
def login():
    # TODO: Implementar login de usuarios
    return jsonify({'message': 'Not implemented yet'}), 501

@bp.route('/me', methods=['GET'])
@token_required
def get_current_user(current_user):
    # TODO: Implementar obtención de usuario actual
    return jsonify({'message': 'Not implemented yet'}), 501 