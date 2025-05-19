# app/login.py

# app/login.py

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import check_password_hash
from app.models.gym_database import GymDatabaseManager


login_bp = Blueprint('login', __name__)

@login_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        db = GymDatabaseManager()
        db.open_connection()
        user = db.get_user_by_username(username)   # deve restituire anche user.role e user.id
        db.close_connection()

        if user and check_password_hash(user.password_hash, password):
            # 1) salva l'id
            session['user_id'] = user.id
            # 2) salva il ruolo
            session['user_role'] = user.role
            flash('Login effettuato con successo!', 'success')
            # reindirizza a dashboard in base al ruolo
            if user.role == 'trainer':
                return redirect(url_for('trainer.dashboard'))
            else:
                return redirect(url_for('client.dashboard'))
        else:
            flash('Credenziali non valide', 'danger')

    return render_template('login.html')
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.models.gym_database import GymDatabaseManager

# Blueprint per le pagine HTML (login/logout)
login_bp = Blueprint('login', __name__)
# Blueprint per gli endpoint API di auth
auth_bp  = Blueprint('auth', __name__, url_prefix='/api/auth')

@login_bp.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        db = GymDatabaseManager()
        db.open_connection()
        user = db.authenticate_user(username, password)
        db.close_connection()

        if user:
            # Salvo i dati in sessione
            session['logged_in'] = True
            session['user_id']   = user['id']
            session['role']      = user['role']
            session['username']  = user['username']
            session.permanent    = True  # Persistenza anche dopo chiusura browser

            # Redirect in base al ruolo
            if user['role'] == 'trainer':
                return redirect(url_for('trainer_page.dashboard'))
            else:
                return redirect(url_for('client.dashboard'))

        flash('Username o password non validi', 'danger')

    return render_template('login.html')


@login_bp.route('/logout', endpoint='logout')
def logout():
    session.clear()
    flash('Logout effettuato con successo', 'info')
    # Torno alla pagina di login
    return redirect(url_for('login.login_page'))


# --- ENDPOINT API JWT ---

@auth_bp.route('/login', methods=['POST'])
def login_api():
    """
    POST /api/auth/login
    Request JSON: { "username": "...", "password": "..." }
    Response JSON: { "access_token": "..." }
    """
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')

    db = GymDatabaseManager()
    db.open_connection()
    user = db.authenticate_user(username, password)
    db.close_connection()

    if not user:
        return {'msg': 'Username o password non validi'}, 401

    token = create_access_token(
        identity={'id': user['id'], 'role': user['role']}
    )
    return {'access_token': token}, 200


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def me_api():
    """
    GET /api/auth/me
    Header: Authorization: Bearer <access_token>
    Response JSON: { "user": { "id": ..., "role": ... } }
    """
    current = get_jwt_identity()
    return {'user': current}, 200
