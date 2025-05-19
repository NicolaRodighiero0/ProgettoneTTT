import pytest

def test_create_workout_plan(client, test_trainer, test_client_user):
    # Login comee trainer
    client.post('/login', data={
        'username': test_trainer['username'],
        'password': 'password123'
    })
    
    response = client.post('/api/workouts', json={
        'client_id': test_client_user['id'],
        'exercises': [
            {
                'exercise_id': 1,
                'sets': 3,
                'reps': 12,
                'weight': 20,
                'rest_time': 60
            }
        ]
    })
    
    assert response.status_code == 201
    assert 'id' in response.json

def test_get_client_workouts(client, test_client_user):
    # Login come cliente
    client.post('/login', data={
        'username': test_client_user['username'],
        'password': 'password123'
    })
    
    response = client.get(f'/api/workouts/history/{test_client_user["id"]}')
    assert response.status_code == 200
    assert isinstance(response.json, list)