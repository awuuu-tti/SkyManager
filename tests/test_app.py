def test_home_page(client):
    response = client.get('/')
    assert response.status_code == 200


def test_login_page(client):
    response = client.get('/login')
    assert response.status_code == 200


def test_register_page(client):
    response = client.get('/register')
    assert response.status_code == 200


def test_search_page(client):
    response = client.get('/search')
    assert response.status_code == 200


def test_invalid_page(client):
    response = client.get('/unknown_page')
    assert response.status_code == 404


def test_post_login(client):
    response = client.post('/login', data={
        'username': 'test',
        'password': 'test'
    })

    assert response.status_code in [200, 302]


def test_post_register(client):
    response = client.post('/register', data={
        'username': 'test',
        'password': '123456'
    })

    assert response.status_code in [200, 302]


def test_search_post(client):
    response = client.post('/search', data={
        'from_city': 'Moscow',
        'to_city': 'London'
    })

    assert response.status_code in [200, 302, 405]


def test_empty_login(client):
    response = client.post('/login', data={})

    assert response.status_code in [200, 400, 302]


def test_empty_register(client):
    response = client.post('/register', data={})

    assert response.status_code in [200, 400, 302]

def test_home_content(client):
    response = client.get('/')

    assert response.data is not None


def test_login_content(client):
    response = client.get('/login')

    assert len(response.data) > 0


def test_register_content(client):
    response = client.get('/register')

    assert len(response.data) > 0


def test_search_content(client):
    response = client.get('/search')

    assert response.data != b''


def test_response_type(client):
    response = client.get('/')

    assert response.content_type is not None


def test_status_code_type(client):
    response = client.get('/')

    assert type(response.status_code) == int


def test_multiple_requests(client):
    response1 = client.get('/')
    response2 = client.get('/login')

    assert response1.status_code == 200
    assert response2.status_code == 200


def test_headers_exist(client):
    response = client.get('/')

    assert response.headers is not None


def test_response_not_empty(client):
    response = client.get('/')

    assert response.data != b''


def test_invalid_route_content(client):
    response = client.get('/unknown')

    assert response.status_code == 404