from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.models.gym_database import GymDatabaseManager

exercise_metadata_bp = Blueprint('exercise_metadata', __name__)

@exercise_metadata_bp.route('/api/exercises/<int:exercise_id>/muscle-groups', methods=['POST'])
@jwt_required()
def set_muscle_groups(exercise_id):
    """Imposta i gruppi muscolari primari e secondari per un esercizio"""
    data = request.get_json()
    
    db = GymDatabaseManager()
    db.open_connection()
    success = db.set_exercise_muscle_groups(
        exercise_id,
        primary_groups=data.get('primary', []),
        secondary_groups=data.get('secondary', [])
    )
    db.close_connection()
    
    if success:
        return jsonify({'success': True})
    return jsonify({'error': 'Exercise not found'}), 404