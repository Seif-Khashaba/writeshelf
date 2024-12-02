from flask import Flask, render_template, request, redirect, url_for, jsonify, session, send_from_directory
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from bson.objectid import ObjectId
from bson.errors import InvalidId
import os
from dotenv import load_dotenv
from datetime import datetime
import bcrypt
from flask_cors import CORS

# Load environment variables
load_dotenv()

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-here')

# MongoDB connection
uri = os.getenv('MONGO_URI')
client = MongoClient(uri, server_api=ServerApi('1'))
db = client.writeshelf  # database name

# Initialize MongoDB collections
users = db.users
books = db.books  # Add books collection

# Test MongoDB connection
try:
    client.admin.command('ping')
    print("Successfully connected to MongoDB!")
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")

# Initialize sample books
def initialize_sample_books():
    if books.count_documents({}) == 0:
        sample_books = [
            {
                "title": "The Shadow's Edge",
                "author": "Elena Martinez",
                "cover_image": "https://picsum.photos/seed/book1/400/600",
                "description": "A thrilling fantasy novel about a young mage discovering her powers in a world of shadows.",
                "genres": ["Fantasy", "Young Adult", "Magic"],
                "rating": 4.5,
                "reviews": [],
                "published_date": "2022-03-15",
                "pages": 384,
                "language": "English",
                "isbn": "978-1234567890"
            },
            {
                "title": "Digital Dreams",
                "author": "James Chen",
                "cover_image": "https://picsum.photos/seed/book2/400/600",
                "description": "A cyberpunk adventure exploring the boundaries between human consciousness and artificial intelligence.",
                "genres": ["Science Fiction", "Cyberpunk", "Thriller"],
                "rating": 4.3,
                "reviews": [],
                "published_date": "2023-01-20",
                "pages": 422,
                "language": "English",
                "isbn": "978-0987654321"
            },
            {
                "title": "The Last Garden",
                "author": "Sarah Williams",
                "cover_image": "https://picsum.photos/seed/book3/400/600",
                "description": "A poetic exploration of nature and humanity in a world struggling with environmental change.",
                "genres": ["Literary Fiction", "Environmental", "Drama"],
                "rating": 4.7,
                "reviews": [],
                "published_date": "2023-05-10",
                "pages": 298,
                "language": "English",
                "isbn": "978-5432109876"
            },
            {
                "title": "Code of Honor",
                "author": "Michael Chang",
                "cover_image": "https://picsum.photos/seed/book4/400/600",
                "description": "A gripping military thriller about loyalty, betrayal, and the cost of keeping secrets.",
                "genres": ["Thriller", "Military", "Action"],
                "rating": 4.4,
                "reviews": [],
                "published_date": "2023-02-28",
                "pages": 456,
                "language": "English",
                "isbn": "978-6789054321"
            },
            {
                "title": "Whispers in Time",
                "author": "Isabella Romano",
                "cover_image": "https://picsum.photos/seed/book5/400/600",
                "description": "A romantic historical fiction weaving together past and present through a mysterious family heirloom.",
                "genres": ["Historical Fiction", "Romance", "Mystery"],
                "rating": 4.6,
                "reviews": [],
                "published_date": "2023-04-15",
                "pages": 368,
                "language": "English",
                "isbn": "978-3456789012"
            }
        ]
        
        # Insert sample books
        books.insert_many(sample_books)
        print("Sample books initialized")

initialize_sample_books()

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/main')
def main():
    if 'username' not in session:
        return redirect(url_for('index'))
    return app.send_static_file('main.html')

@app.route('/login')
def login_page():
    return app.send_static_file('index.html')

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json() if request.is_json else request.form
        username = data.get('username')
        password = data.get('password')
        
        print(f"Login attempt for username: {username}")
        
        if not username or not password:
            print("Missing username or password")
            return jsonify({'success': False, 'error': 'Username and password are required'}), 400
        
        user = users.find_one({'username': username})
        print(f"Database response - Found user: {user is not None}")
        
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
            print("Password verified successfully")
            session['username'] = username
            redirect_url = url_for('main')
            print(f"Redirecting to: {redirect_url}")
            return jsonify({
                'success': True, 
                'message': 'Login successful',
                'redirect': redirect_url
            })
        
        print("Invalid credentials")
        return jsonify({'success': False, 'error': 'Invalid username or password'}), 401
        
    except Exception as e:
        print(f"Login error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/signup', methods=['POST'])
def signup():
    try:
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        full_name = data.get('full_name')
        gender = data.get('gender')
        country = data.get('country')
        
        if not all([username, email, password, full_name, gender, country]):
            return jsonify({'success': False, 'error': 'All fields are required'}), 400
        
        # Check if username already exists
        if users.find_one({'username': username}):
            return jsonify({'success': False, 'error': 'Username already exists'}), 400
            
        # Check if email already exists
        if users.find_one({'email': email}):
            return jsonify({'success': False, 'error': 'Email already exists'}), 400
        
        # Hash password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        # Create new user
        new_user = {
            'username': username,
            'password': hashed_password,
            'email': email,
            'full_name': full_name,
            'gender': gender,
            'country': country,
            'created_at': datetime.utcnow(),
            'preferences_set': False,
            'genres': []
        }
        
        result = users.insert_one(new_user)
        session['username'] = username
        return jsonify({'success': True, 'message': 'Account created successfully'})
        
    except Exception as e:
        print(f"Signup error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/preferences', methods=['POST'])
def save_preferences():
    if 'username' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'}), 401
    
    try:
        data = request.get_json()
        genres = data.get('genres', [])
        
        if len(genres) < 3:
            return jsonify({'success': False, 'error': 'Please select at least 3 genres'}), 400
        
        # Update user preferences
        result = users.update_one(
            {'username': session['username']},
            {
                '$set': {
                    'genres': genres,
                    'preferences_set': True,
                    'updated_at': datetime.utcnow()
                }
            }
        )
        
        if result.modified_count > 0:
            return jsonify({'success': True, 'message': 'Preferences saved successfully'})
        else:
            return jsonify({'success': False, 'error': 'No changes made'}), 400
            
    except Exception as e:
        print(f"Error saving preferences: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/preferences')
def preferences_page():
    if 'username' not in session:
        return redirect(url_for('index'))
    return app.send_static_file('preferences.html')

@app.route('/api/logout')
def logout():
    session.clear()  # Clear the entire session
    return jsonify({
        'success': True,
        'message': 'Logout successful',
        'redirect': url_for('index')
    })

@app.route('/profile')
def profile():
    if 'username' not in session:
        return redirect(url_for('index'))
    return app.send_static_file('profile.html')

@app.route('/api/profile')
def get_profile():
    if 'username' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'}), 401
    
    try:
        user = users.find_one({'username': session['username']})
        if user:
            # Remove sensitive information
            user.pop('password', None)
            user['_id'] = str(user['_id'])  # Convert ObjectId to string
            return jsonify({
                'success': True,
                'profile': user
            })
        return jsonify({'success': False, 'error': 'User not found'}), 404
    except Exception as e:
        print(f"Error fetching profile: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/profile/update', methods=['POST'])
def update_profile():
    if 'username' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'}), 401
    
    try:
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        bio = data.get('bio')
        
        if not username or not email:
            return jsonify({'success': False, 'error': 'Username and email are required'}), 400
            
        # Check if new username is taken by another user
        if username != session['username']:
            existing_user = users.find_one({'username': username})
            if existing_user:
                return jsonify({'success': False, 'error': 'Username already taken'}), 400
        
        # Update user document
        update_data = {
            'username': username,
            'email': email,
            'bio': bio,
            'updated_at': datetime.utcnow()
        }
        
        result = users.update_one(
            {'username': session['username']},
            {'$set': update_data}
        )
        
        if result.modified_count > 0:
            # Update session with new username
            session['username'] = username
            return jsonify({'success': True, 'message': 'Profile updated successfully'})
        else:
            return jsonify({'success': False, 'error': 'No changes made'}), 400
            
    except Exception as e:
        print(f"Error updating profile: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/book')
def book_page():
    if 'username' not in session:
        return redirect(url_for('index'))
    return send_from_directory('.', 'book.html')

@app.route('/api/books', methods=['GET'])
def get_books():
    try:
        all_books = list(books.find())
        for book in all_books:
            book['_id'] = str(book['_id'])
        return jsonify(all_books)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/books/<book_id>', methods=['GET'])
def get_book(book_id):
    try:
        # Validate ObjectId format
        try:
            book_object_id = ObjectId(book_id)
        except InvalidId:
            return jsonify({'error': 'Invalid book ID format'}), 400
            
        book = books.find_one({'_id': book_object_id})
        if not book:
            return jsonify({'error': 'Book not found'}), 404
            
        book['_id'] = str(book['_id'])
        return jsonify(book)
        
    except Exception as e:
        print(f"Error getting book: {str(e)}")
        return jsonify({'error': 'An error occurred while fetching the book'}), 500

@app.route('/api/books/<book_id>/reviews', methods=['GET', 'POST'])
def handle_reviews(book_id):
    try:
        # Validate ObjectId format
        try:
            book_object_id = ObjectId(book_id)
        except InvalidId:
            return jsonify({'error': 'Invalid book ID format'}), 400
            
        if request.method == 'GET':
            book = books.find_one({'_id': book_object_id})
            if not book:
                return jsonify({'error': 'Book not found'}), 404
            return jsonify(book.get('reviews', []))
            
        elif request.method == 'POST':
            if 'username' not in session:
                return jsonify({'error': 'Unauthorized'}), 401

            data = request.get_json()
            
            if not all(key in data for key in ['rating', 'comment']):
                return jsonify({'error': 'Missing required fields'}), 400
                
            rating = float(data['rating'])
            if rating < 1 or rating > 5:
                return jsonify({'error': 'Rating must be between 1 and 5'}), 400
                
            review = {
                'username': session['username'],
                'rating': rating,
                'comment': data['comment'],
                'date': datetime.utcnow()
            }
            
            result = books.update_one(
                {'_id': book_object_id},
                {
                    '$push': {'reviews': review},
                    '$set': {
                        'rating': {
                            '$avg': '$reviews.rating'
                        }
                    }
                }
            )
            
            if result.modified_count == 0:
                return jsonify({'error': 'Book not found'}), 404
                
            return jsonify({'message': 'Review added successfully'}), 201
            
    except Exception as e:
        print(f"Error handling reviews: {str(e)}")
        return jsonify({'error': 'An error occurred while processing the request'}), 500

if __name__ == '__main__':
    app.run(debug=True)
