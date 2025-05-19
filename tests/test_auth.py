def test_login_success(client, test_trainer):
    response = client.post('/login', data={
        'username': test_trainer['username'],
        'password': 'password123'
    })
    assert response.status_code == 302  # redirect dopo il login

def test_login_failure(client):
    response = client.post('/login', data={
        'username': 'wrong_user',
        'password': 'wrong_password'
    })
    assert response.status_code == 200  # stai ancora sulla pagina di login

def test_logout(client, test_trainer):
    # prima login
    client.post('/login', data={
        'username': test_trainer['username'],
        'password': 'password123'
    })
    
    # dopo logout
    response = client.get('/logout')
    assert response.status_code == 302  # Redirect dopo il logout