import pytest

def test_create_exercise(client, test_trainer):
    # Login da trainer
    client.post('/login', data={
        'username': test_trainer['username'],
        'password': 'password123'
    })
    
    response = client.post('/api/exercises', json={
        'name': 'Push-up',
        'description': 'Basic push-up exercise',
        'primary_muscles': ['Pettorali', 'Tricipiti'],
        'secondary_muscles': ['Spalle'],
        'difficulty': 'Medio',
        'objective': 'Tonificazione'
    })
    
    assert response.status_code == 201
    assert 'id' in response.json

def test_get_exercises_list(client):
    response = client.get('/api/exercises')
    assert response.status_code == 200
    assert isinstance(response.json, list)

def test_unauthorized_create_exercise(client, test_client_user):
    # Login come un cliente
    client.post('/login', data={
        'username': test_client_user['username'],
        'password': 'password123'
    })
    
    response = client.post('/api/exercises', json={
        'name': 'Unauthorized Exercise'
    })
    
    assert response.status_code == 403  # Forbidden