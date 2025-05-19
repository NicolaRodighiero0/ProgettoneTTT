from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.gym_database import GymDatabaseManager


history_bp = Blueprint('history', __name__)

@history_bp.route('/api/clients/<int:client_id>/workout-history')
@jwt_required()
def get_client_history(client_id):
    """Recupera lo storico completo degli allenamenti di un cliente"""
    current_user = get_jwt_identity()
    
    db = GymDatabaseManager()
    db.open_connection()
    history = db.get_complete_workout_history(client_id)
    db.close_connection()
    
    return jsonify(history)