from flask import Blueprint, request, jsonify, session
from app.models.gym_database import GymDatabaseManager
from datetime import datetime
import re

profile_bp = Blueprint('profile', __name__)

def validate_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    pattern = r'^\+?1?\d{9,15}$'
    return re.match(pattern, phone) is not None

def validate_date(date_str):
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False

@profile_bp.route('/api/profile', methods=['GET'])
def get_profile():
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401

    user_id = session['user_id']
    
    db = GymDatabaseManager()
    db.open_connection()
    profile = db.get_user_profile(user_id)
    db.close_connection()

    if not profile:
        return jsonify({
            'first_name': '',
            'last_name': '',
            'email': '',
            'birth_date': '',
            'phone': '',
            'address': ''
        })

    return jsonify(profile)

@profile_bp.route('/api/profile', methods=['PUT'])
def update_profile():
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json()
    errors = {}

    # Validazione
    if 'email' in data and not validate_email(data['email']):
        errors['email'] = 'Email non valida'

    if 'phone' in data and not validate_phone(data['phone']):
        errors['phone'] = 'Numero di telefono non valido'

    if 'birth_date' in data and not validate_date(data['birth_date']):
        errors['birth_date'] = 'Data non valida (formato richiesto: YYYY-MM-DD)'

    if errors:
        return jsonify({'errors': errors}), 400

    db = GymDatabaseManager()
    db.open_connection()
    
    # Verifica email duplicata
    if 'email' in data:
        existing = db.get_user_by_email(data['email'])
        if existing and existing['id'] != session['user_id']:
            db.close_connection()
            return jsonify({'errors': {'email': 'Email già in uso'}}), 400

    success = db.update_user_profile(session['user_id'], data)
    db.close_connection()

    if success:
        return jsonify({'message': 'Profilo aggiornato con successo'})
    return jsonify({'error': 'Errore nell\'aggiornamento del profilo'}), 500