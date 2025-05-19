from flask import Blueprint, request, jsonify, session
from app.models.gym_database import GymDatabaseManager

machines_bp = Blueprint('machines', __name__)

@machines_bp.route('/api/machines', methods=['GET'])
def get_machines():
    db = GymDatabaseManager()
    db.open_connection()
    machines = db.get_all_machines()
    db.close_connection()
    return jsonify(machines)

@machines_bp.route('/api/machines', methods=['POST'])
def add_machine():
    if session.get('role') != 'trainer':
        return jsonify({'error': 'Unauthorized'}), 401
        
    data = request.get_json()
    name = data.get('name')
    
    if not name:
        return jsonify({'error': 'Name is required'}), 400
        
    db = GymDatabaseManager()
    db.open_connection()
    machine_id = db.add_machine(name)
    db.close_connection()
    
    return jsonify({'id': machine_id}), 201