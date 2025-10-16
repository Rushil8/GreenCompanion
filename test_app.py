import pytest
from app import app

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_home_redirect(client):
    # Should redirect to login if not logged in
    response = client.get('/')
    assert response.status_code == 302  # Redirect

def test_weather_route(client):
    response = client.get('/weather/London')
    assert response.status_code == 200
    assert b"temp" in response.data or b"description" in response.data

def test_upload_get(client):
    response = client.get('/upload')
    assert response.status_code == 200
