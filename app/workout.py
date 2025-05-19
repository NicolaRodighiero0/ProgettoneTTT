from flask import Blueprint, request, jsonify, session
from app.models.gym_database import GymDatabaseManager
from datetime import datetime

workout_bp = Blueprint('workout', __name__)

@workout_bp.route('/api/workouts', methods=['POST'])
def create_workout():
    if session.get('role') != 'trainer':
        return jsonify({'error': 'Unauthorized'}), 401
        
    data = request.get_json()
    client_id = data.get('client_id')
    exercises = data.get('exercises')
    
    db = GymDatabaseManager()
    db.open_connection()
    
    workout_id = db.create_workout_plan(
        client_id=client_id,
        trainer_id=session['user_id'],
        exercises=exercises
    )
    
    db.close_connection()
    return jsonify({'id': workout_id}), 201

@workout_bp.route('/api/workouts/<int:workout_id>', methods=['PUT'])
def update_workout(workout_id):
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
        
    data = request.get_json()
    db = GymDatabaseManager()
    db.open_connection()
    
    # Verifica permessi
    workout = db.get_workout(workout_id)
    if not workout or (session['role'] == 'client' and workout['client_id'] != session['user_id']):
        return jsonify({'error': 'Not found'}), 404
        
    db.update_workout_exercise(workout_id, data)
    db.close_connection()
    return jsonify({'success': True})

@workout_bp.route('/api/workouts/history/<int:client_id>')
def get_workout_history(client_id):
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
        
    if session['role'] == 'client' and session['user_id'] != client_id:
        return jsonify({'error': 'Forbidden'}), 403
        
    db = GymDatabaseManager()
    db.open_connection()
    history = db.get_client_workouts(client_id)
    db.close_connection()
    
    return jsonify(history)