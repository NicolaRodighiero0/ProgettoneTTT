from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.gym_database import GymDatabaseManager

notifications_bp = Blueprint('notifications', __name__)

@notifications_bp.route('/api/notifications')
@jwt_required()
def get_notifications():
    """Recupera le notifiche per l'utente corrente"""
    current_user = get_jwt_identity()
    
    db = GymDatabaseManager()
    db.open_connection()
    
    if current_user['role'] == 'trainer':
        # Notifiche per il trainer (es. clienti che completano workout)
        notifications = db.get_trainer_notifications(current_user['id'])
    else:
        # Notifiche per il cliente (es. nuove schede assegnate)
        notifications = db.get_client_notifications(current_user['id'])
        
    db.close_connection()
    return jsonify(notifications)