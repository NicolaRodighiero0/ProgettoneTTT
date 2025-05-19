from flask import Blueprint, jsonify
from datetime import datetime
from app.models.gym_database import GymDatabaseManager  # Percorso 

workout_execution_bp = Blueprint('workout_execution', __name__)

@workout_execution_bp.route('/api/workout-sessions/<int:session_id>/timer', methods=['POST'])
def start_exercise_timer(session_id):
    """Gestisce il timer per l'esecuzione degli esercizi"""
    db = GymDatabaseManager()
    db.open_connection()
    
    timer_id = db.create_exercise_timer(
        session_id=session_id,
        start_time=datetime.now()
    )
    
    db.close_connection()
    return jsonify({'timer_id': timer_id})