import os
from flask import Flask, send_from_directory, current_app
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from datetime import datetime

# Blueprint HTML e API
from app.pages         import pages_bp
from app.login         import login_bp, auth_bp
from app.register      import register_bp
from app.home          import home_bp
from app.trainer       import trainer_page_bp, trainer_api_bp
from app.client        import client_bp
from app.exercises     import exercises_bp
from app.workout       import workout_bp
from app.machines      import machines_bp
from app.statistics    import statistics_bp
from app.notifications import notifications_bp

# Blueprint metadata
from app.api_metadata  import metadata_bp
from app.profile       import profile_bp

# DB
from app.models.gym_database import GymDatabaseManager

def format_datetime(value, fmt='%d/%m/%Y %H:%M'):
    """Converte ISO string o datetime in stringa formattata."""
    if value is None:
        return ''
    if isinstance(value, datetime):
        return value.strftime(fmt)
    try:
        return datetime.fromisoformat(str(value)).strftime(fmt)
    except ValueError:
        return value

def service_worker():
    """
    Serve service-worker.js dalla cartella static del Flask app.
    """
    return send_from_directory(current_app.static_folder, 'service-worker.js')

def manifest():
    """
    Serve manifest.json dalla cartella static del Flask app.
    """
    return send_from_directory(current_app.static_folder, 'manifest.json')

def create_app():
    # static_folder punta a <progetto>/app/static
    app = Flask(__name__, static_folder='static')

    # Jinja filter per le date
    app.jinja_env.filters['datetime'] = format_datetime

    # CORS (solo su /api/*)
    cors_origins = os.environ.get('CORS_ORIGINS', '*')
    CORS(app, resources={r"/api/*": {"origins": cors_origins}})

    # Configurazione da file esterno
    app.config.from_pyfile(os.path.join(os.path.dirname(__file__), '..', 'config.py'))

    # JWT
    JWTManager(app)

    # Inizializzazione schema DB
    db = GymDatabaseManager(app.config['DATABASE_PATH'])
    db.open_connection()
    db.create_all_tables()
    db.close_connection()

    # Registrazione dei blueprint
    app.register_blueprint(home_bp)
    app.register_blueprint(pages_bp)
    app.register_blueprint(login_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(register_bp)
    app.register_blueprint(metadata_bp)
    app.register_blueprint(trainer_page_bp)
    app.register_blueprint(trainer_api_bp)
    app.register_blueprint(client_bp)
    app.register_blueprint(exercises_bp)
    app.register_blueprint(workout_bp)
    app.register_blueprint(machines_bp)
    app.register_blueprint(statistics_bp)
    app.register_blueprint(notifications_bp)
    app.register_blueprint(profile_bp)

    # Route per il service worker
    app.add_url_rule(
        '/service-worker.js',
        endpoint='service_worker',
        view_func=service_worker
    )

    # Route per il manifest della PWA
    app.add_url_rule(
        '/manifest.json',
        endpoint='manifest',
        view_func=manifest
    )

    return app
