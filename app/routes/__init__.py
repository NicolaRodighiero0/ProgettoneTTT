import os
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager

# Blueprint HTML e API
from app.routes.pages         import pages_bp
from app.routes.login         import login_bp, auth_bp
from app.routes.register      import register_bp
from app.routes.home          import home_bp
from app.routes.trainer       import trainer_page_bp, trainer_api_bp
from app.routes.client        import client_bp
from app.routes.exercises     import exercises_bp
from app.routes.workout       import workout_bp
from app.routes.machines      import machines_bp
from app.routes.statistics    import statistics_bp
from app.routes.notifications import notifications_bp

# Blueprint metadata
from app.routes.api_metadata  import metadata_bp          # ← import del blueprint

from app.routes.profile       import profile_bp           # ← import del blueprint

from app.models.gym_database import GymDatabaseManager

def create_app():
    app = Flask(__name__, instance_relative_config=False)
    @app.route('/service-worker.js')
    def sw():
        return app.send_static_file('service-worker.js')

    # CORS: limitare le origini solo per /api/*
    cors_origins = os.environ.get('CORS_ORIGINS', '*')
    CORS(app, resources={r"/api/*": {"origins": cors_origins}})

    # Carica la configurazione
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config.py')
    app.config.from_pyfile(config_path)

    # Inizializza JWT
    JWTManager(app)

    # Inizializza il database e crea tabelle se mancanti
    db = GymDatabaseManager(app.config['DATABASE_PATH'])
    db.open_connection()
    db.create_all_tables()
    db.close_connection()

    # Registra tutti i blueprint: prima i metadata, poi le altre API e le pagine
    app.register_blueprint(home_bp)
    app.register_blueprint(pages_bp)
    app.register_blueprint(login_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(register_bp)

    # —————— METADATA ——————
    app.register_blueprint(metadata_bp)              # ← registra metadata_bp

    # —————— TRAINER ——————
    app.register_blueprint(trainer_page_bp)
    app.register_blueprint(trainer_api_bp)

    # —————— CLIENT ——————
    app.register_blueprint(client_bp)

    # —————— ESERCIZI ——————
    app.register_blueprint(exercises_bp)

    # —————— ALTRE API ——————
    app.register_blueprint(workout_bp)
    app.register_blueprint(machines_bp)
    app.register_blueprint(statistics_bp)
    app.register_blueprint(notifications_bp)

    # —————— PROFILO ——————
    app.register_blueprint(profile_bp)               # ← registra profile_bp

    return app
