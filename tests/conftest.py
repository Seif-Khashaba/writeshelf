import pytest
from app import app, db
import os
from dotenv import load_dotenv

load_dotenv()

@pytest.fixture
def test_client():
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    # Use a separate test database
    test_db_uri = os.getenv('TEST_MONGO_URI', 'mongodb://localhost:27017/writeshelf_test')
    app.config['MONGO_URI'] = test_db_uri
    
    with app.test_client() as client:
        yield client
        
    # Clean up test database after tests
    db.client.drop_database('writeshelf_test')

@pytest.fixture
def authenticated_client(test_client):
    test_client.post('/api/signup', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'testpass123'
    })
    
    test_client.post('/api/login', json={
        'username': 'testuser',
        'password': 'testpass123'
    })
    
    return test_client
