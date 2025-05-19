# app/register.py

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.gym_database import GymDatabaseManager

register_bp = Blueprint('register', __name__)

# Route per la registrazione di un nuovo cliente
@register_bp.route('/register', methods=['GET', 'POST'], endpoint='register')
def register_page():
    """
    Pagina HTML per la registrazione self-service di un nuovo cliente.
    GET: mostra il form
    POST: crea il cliente se username e password sono validi/univoci
    """
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = 'client'

        # Validazione dei campi
        if not username or not password:
            flash('Username e password sono obbligatori', 'warning')
            return render_template('register.html')

        db = GymDatabaseManager()
        db.open_connection()

        # Controllo unicità username
        if db.get_user_by_username(username):
            flash('Username già in uso', 'danger')
            db.close_connection()
            return render_template('register.html')

        # Inserimento del nuovo cliente
        db.insert_user(username=username, password=password, role=role)
        db.close_connection()

        flash('Registrazione completata con successo!', 'success')
        return redirect(url_for('login.login'))

    return render_template('register.html')

# Route per la registrazione di un nuovo cliente tramite API
@register_bp.route('/api/trainer/clients', methods=['POST'], endpoint='create_client_api')
@jwt_required()
def create_client_api():
    """
    POST /api/trainer/clients
    Header: Authorization: Bearer <access_token>
    Body JSON: { "username": "...", "password": "..." }
    Solo un trainer può creare nuovi clienti.
    """
    current = get_jwt_identity()
    if current['role'] != 'trainer':
        return {'error': 'Unauthorized'}, 403

    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')

    # Verifica campi obbligatori
    if not username or not password:
        return {'error': 'Missing required fields'}, 400

    db = GymDatabaseManager()
    db.open_connection()

    # Crea il cliente assegnato al trainer corrente
    client_id = db.insert_user(
        username=username,
        password=password,
        role='client',
        trainer_id=current['id']
    )
    db.close_connection()

    return {'id': client_id}, 201
