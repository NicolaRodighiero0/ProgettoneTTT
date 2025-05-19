import pytest
from app import create_app
from app.models.gym_database import GymDatabaseManager

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    return app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def db():
    db = GymDatabaseManager(':memory:')
    db.open_connection()
    db.create_all_tables()
    yield db
    db.close_connection()

@pytest.fixture
def test_trainer(db):
    trainer_id = db.insert_user('test_trainer', 'password123', 'trainer')
    return {'id': trainer_id, 'username': 'test_trainer', 'role': 'trainer'}

@pytest.fixture
def test_client_user(db):
    client_id = db.insert_user('test_client', 'password123', 'client')
    return {'id': client_id, 'username': 'test_client', 'role': 'client'}