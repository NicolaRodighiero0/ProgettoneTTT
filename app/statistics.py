from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.gym_database import GymDatabaseManager
from datetime import datetime, timedelta

statistics_bp = Blueprint('statistics', __name__)

@statistics_bp.route('/api/statistics/client/<int:client_id>/progress')
@jwt_required()
def get_client_progress(client_id):
    """Ottiene i progressi del cliente nel tempo"""
    current_user = get_jwt_identity()
    
    # Verifica permessi
    if current_user['role'] == 'client' and current_user['id'] != client_id:
        return jsonify({'error': 'Unauthorized'}), 403
        
    db = GymDatabaseManager()
    db.open_connection()
    
    # Recupera gli ultimi 30 giorni di allenamenti
    progress = db.get_client_progress(
        client_id=client_id,
        start_date=datetime.now() - timedelta(days=30),
        end_date=datetime.now()
    )
    
    db.close_connection()
    return jsonify(progress)

@statistics_bp.route('/api/statistics/exercise/<int:exercise_id>')
@jwt_required()
def get_exercise_stats(exercise_id):
    """Ottiene statistiche specifiche per un esercizio"""
    current_user = get_jwt_identity()
    
    db = GymDatabaseManager()
    db.open_connection()
    
    stats = db.get_exercise_statistics(
        exercise_id=exercise_id,
        client_id=current_user['id'] if current_user['role'] == 'client' else None
    )
    
    db.close_connection()
    return jsonify(stats)