from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.gym_database import GymDatabaseManager

workout_plans_bp = Blueprint('workout_plans', __name__)

@workout_plans_bp.route('/api/workout-plans', methods=['POST'])
@jwt_required()
def create_workout_plan():
    current_user = get_jwt_identity()
    if current_user['role'] != 'trainer':
        return jsonify({'error': 'Unauthorized'}), 403
        
    data = request.get_json()
    required = ['client_id', 'exercises']
    if not all(k in data for k in required):
        return jsonify({'error': 'Missing required fields'}), 400
        
    db = GymDatabaseManager()
    db.open_connection()
    
    # Verifica che il cliente appartenga al trainer
    if not db.verify_trainer_client(current_user['id'], data['client_id']):
        db.close_connection()
        return jsonify({'error': 'Client not found'}), 404
    
    plan_id = db.create_workout_plan(
        client_id=data['client_id'],
        trainer_id=current_user['id'],
        exercises=data['exercises']
    )
    
    db.close_connection()
    return jsonify({'id': plan_id}), 201

@workout_plans_bp.route('/api/workout-plans/<int:plan_id>/execute', methods=['POST'])
@jwt_required()
def start_workout_execution(plan_id):
    """Avvia l'esecuzione di una scheda"""
    current_user = get_jwt_identity()
    
    db = GymDatabaseManager()
    db.open_connection()
    
    # Verifica che la scheda appartenga al cliente
    plan = db.get_workout_plan(plan_id)
    if not plan or plan['client_id'] != current_user['id']:
        db.close_connection()
        return jsonify({'error': 'Workout plan not found'}), 404
    
    # Crea una nuova sessione di allenamento
    session_id = db.create_workout_session(plan_id)
    exercises = db.get_workout_plan_exercises(plan_id)
    
    db.close_connection()
    
    return jsonify({
        'session_id': session_id,
        'exercises': exercises
    })

@workout_plans_bp.route('/api/workout-sessions/<int:session_id>/exercises/<int:exercise_id>', 
                       methods=['POST'])
@jwt_required()
def complete_exercise(session_id, exercise_id):
    """Registra il completamento di un esercizio durante l'allenamento"""
    current_user = get_jwt_identity()
    data = request.get_json()
    
    db = GymDatabaseManager()
    db.open_connection()
    
    # Verifica che la sessione appartenga al cliente
    if not db.verify_workout_session(session_id, current_user['id']):
        db.close_connection()
        return jsonify({'error': 'Session not found'}), 404
    
    # Registra i dati dell'esercizio completato
    db.log_exercise_completion(
        session_id=session_id,
        exercise_id=exercise_id,
        reps=data.get('reps'),
        weight=data.get('weight'),
        duration=data.get('duration'),
        notes=data.get('notes')
    )
    
    db.close_connection()
    return jsonify({'success': True})