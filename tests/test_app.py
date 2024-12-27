import pytest
import sys
import os

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, books, users, reviews, follows, activities
from datetime import datetime
from bson import ObjectId
import bcrypt

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
    with app.test_client() as client:
        yield client

@pytest.fixture
def auth_client(client):
    """Client with authenticated user"""
    # Create test user
    password = "testpass123"
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    test_user = {
        'username': 'testuser',
        'password': hashed.decode('utf-8'),  # Store as string in DB
        'email': 'test@example.com',
        'created_at': datetime.utcnow()
    }
    users.delete_many({'username': 'testuser'})  # Clean up any existing test user
    users.insert_one(test_user)

    # Login with test client
    with client.session_transaction() as sess:
        sess['username'] = 'testuser'
    
    return client

@pytest.fixture
def sample_book(auth_client):
    """Create a sample book for testing"""
    book_data = {
        'title': 'Test Book',
        'author': 'testuser',
        'description': 'A test book description',
        'content': 'Test book content',
        'genres': ['Test', 'Fiction'],
        'language': 'English',
        'status': 'published',
        'likes': 0,
        'reviews': [],
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    }
    result = books.insert_one(book_data)
    book_data['_id'] = result.inserted_id
    return book_data

def test_index_redirect_if_not_logged_in(client):
    """Test index page redirects to login if not authenticated"""
    response = client.get('/', follow_redirects=True)
    assert b'WriteShelf - Login' in response.data

def test_index_redirect_if_logged_in(auth_client):
    """Test index page redirects to main if authenticated"""
    response = auth_client.get('/', follow_redirects=True)
    assert b'WriteShelf' in response.data

def test_login(client):
    """Test login functionality"""
    # Create test user first
    password = "testpass123"
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    test_user = {
        'username': 'testuser',
        'password': hashed.decode('utf-8'),  # Store as string in DB
        'email': 'test@example.com',
        'created_at': datetime.utcnow()
    }
    users.delete_many({'username': 'testuser'})
    users.insert_one(test_user)
    
    # Test invalid credentials
    response = client.post('/login', json={
        'username': 'testuser',
        'password': 'wrongpass'
    }, headers={'Content-Type': 'application/json'})
    assert response.status_code == 401
    
    # Test valid credentials
    response = client.post('/login', json={
        'username': 'testuser',
        'password': 'testpass123'
    }, headers={'Content-Type': 'application/json'})
    assert response.status_code == 200

def test_signup(client):
    """Test signup functionality"""
    # Clean up test user if exists
    users.delete_many({'username': 'newuser'})
    
    # Test successful signup
    response = client.post('/signup', json={
        'username': 'newuser',
        'password': 'newpass123',
        'email': 'new@example.com'
    })
    assert response.status_code == 200
    
    # Test duplicate username
    response = client.post('/signup', json={
        'username': 'newuser',
        'password': 'anotherpass',
        'email': 'another@example.com'
    })
    assert response.status_code == 400

def test_book_operations(auth_client, sample_book):
    """Test book-related operations"""
    # Test book creation
    new_book = {
        'title': 'New Test Book',
        'description': 'New test description',
        'content': 'New test content',
        'genres': ['Test'],
        'language': 'English'
    }
    response = auth_client.post('/api/books', json=new_book)
    assert response.status_code == 201
    
    # Test book retrieval
    book_id = str(sample_book['_id'])
    response = auth_client.get(f'/api/books/{book_id}')
    assert response.status_code == 200
    assert response.json['title'] == sample_book['title']

def test_search_functionality(auth_client, sample_book):
    """Test book search functionality"""
    # Test search by title
    response = auth_client.get('/api/books/search?q=Test')
    assert response.status_code == 200
    data = response.json
    assert isinstance(data, list)
    assert len(data) > 0
    assert any(book['title'] == sample_book['title'] for book in data)

def test_review_operations(auth_client, sample_book):
    """Test review-related operations"""
    book_id = str(sample_book['_id'])
    
    # Test adding review
    review_data = {
        'rating': 5,
        'review': 'Great test book!'
    }
    response = auth_client.post(f'/api/books/{book_id}/reviews', json=review_data)
    assert response.status_code in [200, 201]
    
    # Test getting reviews
    response = auth_client.get(f'/api/books/{book_id}/reviews')
    assert response.status_code == 200
    data = response.json
    assert isinstance(data, list)
    if len(data) > 0:
        assert data[0]['review'] == review_data['review']

def test_user_search(auth_client):
    """Test user search functionality"""
    response = auth_client.get('/api/users/search?q=test')
    assert response.status_code == 200
    data = response.json
    assert isinstance(data, list)
    assert len(data) > 0
    assert any(user['username'] == 'testuser' for user in data)

def test_cleanup():
    """Clean up test data"""
    users.delete_many({'username': {'$in': ['testuser', 'newuser', 'otheruser']}})
    books.delete_many({'author': 'testuser'})
    reviews.delete_many({'username': 'testuser'})
    follows.delete_many({'follower': 'testuser'})
    follows.delete_many({'following': 'testuser'})
    activities.delete_many({'username': 'testuser'})
