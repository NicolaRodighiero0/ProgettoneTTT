from flask import Flask
from app.home import home_bp
from app.login import login_bp

def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('../config.py')
    
    app.register_blueprint(home_bp)
    app.register_blueprint(login_bp)
    
    return app
