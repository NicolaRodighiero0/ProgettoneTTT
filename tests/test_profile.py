import pytest

def test_get_profile_unauthorized(client):
    response = client.get('/api/profile')
    assert response.status_code == 401

def test_update_profile(client, test_client_user):
    # Login
    client.post('/login', data={
        'username': test_client_user['username'],
        'password': 'password123'
    })

    # Aggiorna profilo
    profile_data = {
        'first_name': 'Mario',
        'last_name': 'Rossi',
        'email': 'mario.rossi@example.com',
        'birth_date': '1990-01-01',
        'phone': '+391234567890',
        'address': 'Via Roma 1, Milano'
    }
    
    response = client.put('/api/profile', json=profile_data)
    assert response.status_code == 200

    # Verifica dati salvati
    response = client.get('/api/profile')
    assert response.status_code == 200
    data = response.json
    assert data['first_name'] == 'Mario'
    assert data['email'] == 'mario.rossi@example.com'

def test_invalid_profile_data(client, test_client_user):
    # Login
    client.post('/login', data={
        'username': test_client_user['username'],
        'password': 'password123'
    })

    # Test email non valida
    response = client.put('/api/profile', json={
        'email': 'not-an-email'
    })
    assert response.status_code == 400
    assert 'email' in response.json['errors']