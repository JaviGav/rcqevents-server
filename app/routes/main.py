from flask import Blueprint, jsonify

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return jsonify({
        'status': 'success',
        'message': 'RCQEvents API is running',
        'version': '1.0.0'
    }) 