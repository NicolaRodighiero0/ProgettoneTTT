from flask import Blueprint, request, jsonify, session
from app.models.gym_database import GymDatabaseManager

exercises_bp = Blueprint('exercises', __name__)

@exercises_bp.route('/api/exercises', methods=['GET'])
def get_exercises():
    filters = {
        'muscle_group': request.args.get('muscle_group'),
        'objective': request.args.get('objective'),
        'difficulty': request.args.get('difficulty')
    }
    
    db = GymDatabaseManager()
    db.open_connection()
    exercises = db.get_filtered_exercises(filters)
    db.close_connection()
    return jsonify(exercises)

@exercises_bp.route('/api/exercises', methods=['POST'])
def add_exercise():
    if session.get('role') != 'trainer':
        return jsonify({'error': 'Unauthorized'}), 401
        
    data = request.get_json()
    required_fields = ['name', 'description', 'objective', 'difficulty']
    
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    db = GymDatabaseManager()
    db.open_connection()
    exercise_id = db.add_exercise(data)
    db.close_connection()
    return jsonify({'id': exercise_id}), 201

@exercises_bp.route('/api/exercises/<int:exercise_id>', methods=['PUT'])
def update_exercise(exercise_id):
    if session.get('role') != 'trainer':
        return jsonify({'error': 'Unauthorized'}), 401
        
    data = request.get_json()
    db = GymDatabaseManager()
    db.open_connection()
    success = db.update_exercise(exercise_id, data)
    db.close_connection()
    
    if success:
        return jsonify({'success': True})
    return jsonify({'error': 'Exercise not found'}), 404

@exercises_bp.route('/api/exercises/<int:exercise_id>', methods=['DELETE'])
def delete_exercise(exercise_id):
    if session.get('role') != 'trainer':
        return jsonify({'error': 'Unauthorized'}), 401
        
    db = GymDatabaseManager()
    db.open_connection()
    success = db.delete_exercise(exercise_id)
    db.close_connection()
    
    if success:
        return jsonify({'success': True})
    return jsonify({'error': 'Exercise not found'}), 404

@exercises_bp.route('/api/exercises/search', methods=['GET'])
def search_exercises():
    """Ricerca esercizi con filtri multipli"""
    filters = {
        'muscle_groups': request.args.getlist('muscle_group'),
        'objectives': request.args.getlist('objective'),
        'difficulty': request.args.get('difficulty'),
        'requires_machine': request.args.get('requires_machine', type=bool),
        'text': request.args.get('q')  # ricerca testuale
    }
    
    db = GymDatabaseManager()
    db.open_connection()
    exercises = db.search_exercises(filters)
    db.close_connection()
    
    return jsonify(exercises)