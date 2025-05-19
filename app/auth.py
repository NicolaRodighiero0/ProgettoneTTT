from functools import wraps
from flask import (
    Blueprint, request, jsonify, render_template,
    redirect, url_for, flash, session, abort
)

from flask_jwt_extended import (
    create_access_token, jwt_required, get_jwt_identity
)
from app.models.gym_database import GymDatabaseManager

# ----------------------------
# Decorator per accesso pagine
# ----------------------------
def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get('logged_in'):
            flash('Devi prima effettuare il login', 'warning')
            return redirect(url_for('login.login_page'))
        return fn(*args, **kwargs)
    return wrapper

def trainer_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if session.get('role') != 'trainer':
            abort(403)
        return fn(*args, **kwargs)
    return wrapper

# ----------------------------
# Blueprint per pagine HTML
# ----------------------------
login_bp = Blueprint('login', __name__)

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
            # Genera token JWT
            access_token = create_access_token(identity={'id': user['id'], 'role': user['role']})
            # Mantieni la sessione per le pagine HTML protette
            session['logged_in'] = True
            session['user_id']   = user['id']
            session['role']      = user['role']
            flash('Login effettuato con successo', 'success')
            return redirect(url_for('home.home'))
        else:
            flash('Username o password non validi', 'danger')
    return render_template('login.html')

@login_bp.route('/logout')
def logout():
    session.clear()
    flash('Logout effettuato con successo', 'success')
    return redirect(url_for('home.home'))

# ----------------------------
# Blueprint per API auth
# ----------------------------
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/login', methods=['POST'])
def login_api():
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')

    db = GymDatabaseManager()
    db.open_connection()
    user = db.authenticate_user(username, password)
    db.close_connection()

    if not user:
        return jsonify({'msg': 'Username o password non validi'}), 401

    token = create_access_token(identity={'id': user['id'], 'role': user['role']})
    return jsonify({'access_token': token}), 200

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def me_api():
    current = get_jwt_identity()
    return jsonify({'user': current}), 200
