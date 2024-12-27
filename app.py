from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_file
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
import os
from dotenv import load_dotenv
import base64
from io import BytesIO
import bcrypt
from flask_cors import CORS
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash, generate_password_hash
import time
from functools import wraps
import fitz

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-here')
app.config['UPLOAD_FOLDER'] = 'uploads'

# Configure static files
app.static_folder = 'static'
app.static_url_path = '/static'

# MongoDB connection
uri = os.getenv('MONGO_URI')
if not uri:
    raise ValueError("MONGO_URI environment variable is not set")

client = MongoClient(uri)
db = client.writeshelf  # database name

# Initialize MongoDB collections
users = db['users']
books = db['books']
reviews = db['reviews']
follows = db['follows']
activities = db['activities']

# Create text index for books collection
try:
    # Drop existing indexes to ensure clean state
    books.drop_indexes()
    
    # Create compound text index with weights
    books.create_index([
        ('title', 'text'),
        ('author', 'text'),
        ('description', 'text')
    ], weights={
        'title': 10,
        'author': 5,
        'description': 1
    })
    print("Text index created successfully!")
except Exception as e:
    print(f"Error creating text index: {e}")

# Authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function

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

def track_activity(username, activity_type, details=None):
    try:
        print(f"Tracking activity for {username}: {activity_type}")
        print(f"Details: {details}")
        
        activity = {
            'username': username,
            'type': activity_type,
            'details': details or {},
            'timestamp': datetime.utcnow()
        }
        
        result = activities.insert_one(activity)
        print(f"Activity tracked with ID: {result.inserted_id}")
        return True
        
    except Exception as e:
        print(f"Error tracking activity: {str(e)}")
        return False

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('main'))
    return render_template('index.html')

@app.route('/main')
def main():
    if 'username' not in session:
        return redirect(url_for('login_page'))
    return render_template('main.html')

@app.route('/login')
def login_page():
    return render_template('index.html')

@app.route('/book/<book_id>')
def book_page(book_id):
    try:
        if 'username' not in session:
            return redirect(url_for('login_page'))
            
        try:
            book = books.find_one({'_id': ObjectId(book_id)})
            if not book:
                print(f"Book not found: {book_id}")
                return redirect(url_for('main'))
                
            # Convert ObjectId to string for JSON serialization
            book['_id'] = str(book['_id'])
            
            # Track view activity
            activity_details = {
                'book_id': book_id,
                'book_title': book['title']
            }
            track_success = track_activity(session['username'], 'view', activity_details)
            print(f"View activity tracked: {track_success}")
            
            return render_template('book.html', book=book)
            
        except Exception as e:
            print(f"Error loading book page: {str(e)}")
            return redirect(url_for('main'))
            
    except Exception as e:
        print(f"Error loading book page: {str(e)}")
        return redirect(url_for('main'))

@app.route('/read/<book_id>')
def reader_page(book_id):
    try:
        if 'username' not in session:
            return redirect(url_for('login_page'))
            
        try:
            book = books.find_one({'_id': ObjectId(book_id)})
            if not book:
                print(f"Book not found: {book_id}")
                return redirect(url_for('main'))
                
            # Convert ObjectId to string for JSON serialization
            book['_id'] = str(book['_id'])
            
            # Track view activity
            activity_details = {
                'book_id': book_id,
                'book_title': book['title']
            }
            track_success = track_activity(session['username'], 'view', activity_details)
            print(f"View activity tracked: {track_success}")
            
            # Check if it's a PDF book
            if book.get('is_pdf', False):
                return render_template('pdf_reader.html', book=book)
            else:
                return render_template('reader.html', book=book)
            
        except Exception as e:
            print(f"Error loading reader page: {str(e)}")
            return redirect(url_for('main'))
            
    except Exception as e:
        print(f"Error loading reader page: {str(e)}")
        return redirect(url_for('main'))

@app.route('/api/pdf/<book_id>/<int:page>')
def get_pdf_page(book_id, page):
    try:
        if 'username' not in session:
            return jsonify({'error': 'Unauthorized'}), 401

        book = books.find_one({'_id': ObjectId(book_id)})
        if not book or not book.get('is_pdf'):
            return jsonify({'error': 'Book not found or not a PDF'}), 404

        pdf_path = os.path.join(app.root_path, book['pdf_path'])
        if not os.path.exists(pdf_path):
            return jsonify({'error': 'PDF file not found'}), 404

        doc = fitz.open(pdf_path)
        if page < 0 or page >= doc.page_count:
            return jsonify({'error': 'Invalid page number'}), 400

        # Improved rendering quality with better matrix settings
        zoom = 2.0  # Adjust this value based on display requirements
        mat = fitz.Matrix(zoom, zoom)
        pix = doc[page].get_pixmap(matrix=mat, alpha=False)
        img_data = BytesIO(pix.tobytes('png'))
        img_base64 = base64.b64encode(img_data.getvalue()).decode()

        return jsonify({
            'image': f'data:image/png;base64,{img_base64}',
            'page_number': page + 1,
            'total_pages': doc.page_count,
            'success': True
        })

    except Exception as e:
        print(f"Error rendering PDF page: {e}")
        return jsonify({
            'error': 'Failed to render PDF page',
            'details': str(e),
            'success': False
        }), 500

@app.route('/profile')
def profile():
    if 'username' not in session:
        return redirect(url_for('login_page'))
    return render_template('profile.html')

@app.route('/preferences')
def preferences_page():
    if 'username' not in session:
        return redirect(url_for('login_page'))
    return render_template('preferences.html')

@app.route('/writing')
def writing_page():
    if 'username' not in session:
        return redirect(url_for('login_page'))
    return render_template('writing.html')

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({'error': 'Username and password are required'}), 400

        user = users.find_one({'username': username})
        if not user:
            return jsonify({'error': 'Invalid username or password'}), 401

        # Handle the password check
        try:
            if bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
                session['username'] = username
                return jsonify({'success': True, 'redirect': url_for('main')})
        except Exception as e:
            print(f"Password check error: {str(e)}")
        
        return jsonify({'error': 'Invalid username or password'}), 401
    except Exception as e:
        print(f"Login error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/signup', methods=['POST'])
def signup():
    try:
        data = request.get_json()
        if not data or not all(k in data for k in ['username', 'password', 'email']):
            return jsonify({'error': 'Missing required fields'}), 400

        if users.find_one({'username': data['username']}):
            return jsonify({'error': 'Username already exists'}), 400
        if users.find_one({'email': data['email']}):
            return jsonify({'error': 'Email already exists'}), 400

        # Use bcrypt for password hashing
        hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())
        # Store the hashed password as a string
        hashed_password_str = hashed_password.decode('utf-8')
        
        user = {
            'username': data['username'],
            'password': hashed_password_str,
            'email': data['email'],
            'name': data.get('name', data['username']),
            'bio': '',
            'photo': None,
            'preferences': {'genres': []},
            'stats': {
                'books_count': 0,
                'reviews_given': 0,
                'reviews_received': 0,
                'followers_count': 0,
                'following_count': 0
            },
            'created_at': datetime.utcnow()
        }
        
        users.insert_one(user)
        session['temp_username'] = data['username']
        return jsonify({'success': True, 'redirect': url_for('preferences_page')})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/preferences', methods=['POST'])
def save_preferences():
    try:
        # Check if user is logged in or in signup process
        username = session.get('username') or session.get('temp_username')
        if not username:
            return jsonify({'error': 'No user found'}), 401

        data = request.json
        genres = data.get('genres', [])

        # Update user preferences
        users.update_one(
            {'username': username},
            {'$set': {'preferences.genres': genres}}
        )

        # If this was a new user signup, clear temp session and redirect to login
        if 'temp_username' in session:
            session.pop('temp_username', None)
            return jsonify({'success': True, 'redirect': url_for('login_page')})
        
        # For logged-in users, redirect to main page
        return jsonify({'success': True, 'redirect': url_for('main')})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True, 'redirect': url_for('login_page')})

@app.route('/api/books', methods=['GET'])
def get_books():
    try:
        all_books = list(books.find())
        for book in all_books:
            # Convert ObjectId to string for JSON serialization
            book['_id'] = str(book['_id'])
            if 'author_id' in book:
                book['author_id'] = str(book['author_id'])
            # Ensure published_date is string
            if 'published_date' in book and isinstance(book['published_date'], datetime):
                book['published_date'] = book['published_date'].isoformat()
        return jsonify(all_books)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/books/<book_id>')
def get_book(book_id):
    try:
        try:
            book = books.find_one({'_id': ObjectId(book_id)})
        except Exception as e:
            return jsonify({'error': 'Invalid book ID'}), 400

        if not book:
            return jsonify({'error': 'Book not found'}), 404
        
        # Convert ObjectId fields to strings
        book['_id'] = str(book['_id'])
        if 'author_id' in book:
            book['author_id'] = str(book['author_id'])
            
        # Convert datetime to string
        if 'published_date' in book and isinstance(book['published_date'], datetime):
            book['published_date'] = book['published_date'].isoformat()
            
        return jsonify(book)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/books/<book_id>/reviews', methods=['GET', 'POST'])
def book_reviews(book_id):
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        book = books.find_one({'_id': ObjectId(book_id)})
        if not book:
            return jsonify({'error': 'Book not found'}), 404

        if request.method == 'GET':
            reviews = book.get('reviews', [])
            # Convert ObjectId and datetime objects to strings
            for review in reviews:
                review['created_at'] = review['created_at'].isoformat()
            return jsonify(reviews)

        elif request.method == 'POST':
            data = request.get_json()
            if not data or 'rating' not in data or 'review' not in data:
                return jsonify({'error': 'Missing rating or review'}), 400

            new_review = {
                'reviewer': session['username'],
                'rating': int(data['rating']),
                'review': data['review'],
                'created_at': datetime.now()
            }

            # Add review to book and update average rating
            books.update_one(
                {'_id': ObjectId(book_id)},
                {
                    '$push': {'reviews': new_review},
                    '$set': {
                        'rating': round(
                            sum(r['rating'] for r in book['reviews'] + [new_review]) /
                            (len(book['reviews']) + 1),
                            1  # Round to 1 decimal place
                        )
                    }
                }
            )

            # Convert datetime for JSON response
            new_review['created_at'] = new_review['created_at'].isoformat()
            return jsonify(new_review), 201

    except Exception as e:
        print(f"Error handling reviews: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/books/<book_id>/reviews', methods=['GET', 'POST'])
def handle_reviews(book_id):
    try:
        book = books.find_one({'_id': ObjectId(book_id)})
        if not book:
            return jsonify({'error': 'Book not found'}), 404

        if request.method == 'GET':
            return jsonify(book.get('reviews', []))

        if request.method == 'POST':
            if 'username' not in session:
                return jsonify({'error': 'Unauthorized'}), 401

            data = request.json
            review = {
                'user': session['username'],
                'rating': data['rating'],
                'review': data['review'],
                'date': datetime.now().isoformat()
            }

            # Update book with new review
            books.update_one(
                {'_id': ObjectId(book_id)},
                {
                    '$push': {'reviews': review},
                    '$set': {'rating': calculate_average_rating(book['reviews'] + [review])}
                }
            )

            return jsonify({'success': True}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

def calculate_average_rating(reviews):
    if not reviews:
        return 0
    total = sum(review['rating'] for review in reviews)
    return round(total / len(reviews), 1)

@app.route('/api/user/preferences')
def get_user_preferences():
    try:
        if 'username' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
            
        user = users.find_one({'username': session['username']})
        if not user:
            return jsonify({'error': 'User not found'}), 404
            
        preferences = user.get('preferences', {})
        return jsonify({
            'genres': preferences.get('genres', []),
            'notifications': preferences.get('notifications', True)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/settings')
def settings_page():
    if 'username' not in session:
        return redirect(url_for('login_page'))
    return render_template('settings.html')

@app.route('/api/user/profile', methods=['GET'])
def get_user_profile():
    try:
        if 'username' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
            
        username = session['username']
        user = db.users.find_one({'username': username})
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
            
        # Get user stats
        stats = {
            'followers_count': db.follows.count_documents({'followed': username}),
            'following_count': db.follows.count_documents({'follower': username}),
            'books_count': db.books.count_documents({'author': username}),
            'reviews_count': db.reviews.count_documents({'reviewer': username})
        }
        
        return jsonify({
            'username': user['username'],
            'email': user['email'],
            'name': user.get('name', user['username']),
            'photo': user.get('photo'),
            'bio': user.get('bio', ''),
            'stats': stats
        })
    except Exception as e:
        print("Error getting user profile:", str(e))
        return jsonify({'error': str(e)}), 500

@app.route('/api/user/profile', methods=['PUT'])
def update_user_profile():
    try:
        if 'username' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
            
        data = request.get_json()
        if not data or 'name' not in data:
            return jsonify({'error': 'Name is required'}), 400
            
        result = users.update_one(
            {'username': session['username']},
            {'$set': {'name': data['name']}}
        )
        
        if result.modified_count == 0:
            return jsonify({'error': 'No changes made'}), 400
            
        return jsonify({'message': 'Profile updated successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/user/password', methods=['PUT'])
def change_password():
    try:
        if 'username' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
            
        data = request.get_json()
        if not data or 'current_password' not in data or 'new_password' not in data:
            return jsonify({'error': 'Current and new passwords are required'}), 400
            
        user = users.find_one({'username': session['username']})
        if not user:
            return jsonify({'error': 'User not found'}), 404
            
        # Verify current password
        if not bcrypt.checkpw(data['current_password'].encode('utf-8'), user['password'].encode('utf-8')):
            return jsonify({'error': 'Current password is incorrect'}), 400
            
        # Update password
        hashed_password = bcrypt.hashpw(data['new_password'].encode('utf-8'), bcrypt.gensalt())
        hashed_password_str = hashed_password.decode('utf-8')
        result = users.update_one(
            {'username': session['username']},
            {'$set': {'password': hashed_password_str}}
        )
        
        if result.modified_count == 0:
            return jsonify({'error': 'No changes made'}), 400
            
        return jsonify({'message': 'Password changed successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/user/photo', methods=['POST'])
def update_profile_photo():
    try:
        if 'username' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
            
        if 'photo' not in request.files:
            return jsonify({'error': 'No photo uploaded'}), 400
            
        photo = request.files['photo']
        if photo.filename == '':
            return jsonify({'error': 'No photo selected'}), 400
            
        if not allowed_file(photo.filename):
            return jsonify({'error': 'Invalid file type'}), 400
            
        # Save the file
        filename = secure_filename(f"{session['username']}_{int(time.time())}{os.path.splitext(photo.filename)[1]}")
        photo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Create upload folder if it doesn't exist
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        
        photo.save(photo_path)
        
        # Update user's photo in database
        photo_url = url_for('uploaded_file', filename=filename)
        result = users.update_one(
            {'username': session['username']},
            {'$set': {'photo': photo_url}}
        )
        
        if result.modified_count == 0:
            return jsonify({'error': 'No changes made'}), 400
            
        return jsonify({'message': 'Photo updated successfully', 'photo_url': photo_url})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/search')
def search_page():
    if 'username' not in session:
        return redirect(url_for('login_page'))
    return render_template('search.html')

@app.route('/api/books/search', methods=['GET'])
@login_required
def api_search_books():
    try:
        query = request.args.get('q', '').strip()
        if not query:
            # Return recent books if no query
            books_list = list(books.find().sort('_id', -1).limit(10))
        else:
            # First try exact title match (case-insensitive)
            title_regex = {'title': {'$regex': f'^{query}', '$options': 'i'}}
            exact_matches = list(books.find(title_regex))

            # Then do text search for remaining matches
            text_matches = list(books.find(
                {
                    '$text': {'$search': query},
                    'title': {'$not': {'$regex': f'^{query}', '$options': 'i'}}  # Exclude exact matches
                },
                {'score': {'$meta': 'textScore'}}
            ).sort([('score', {'$meta': 'textScore'})]))

            # Combine results, with exact matches first
            books_list = exact_matches + text_matches
            books_list = books_list[:10]  # Limit to 10 results

        # Format the response
        formatted_books = []
        for book in books_list:
            formatted_book = {
                'id': str(book['_id']),
                'title': book['title'],
                'author_name': book['author'],
                'cover': book.get('cover_image', f"https://picsum.photos/seed/{str(book['_id'])}/400/600"),
                'likes': book.get('likes', 0),
                'reviews': len(book.get('reviews', [])),
                'genres': book.get('genres', [])
            }
            formatted_books.append(formatted_book)

        return jsonify(formatted_books)
    except Exception as e:
        print(f"Search error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/user/timeline/<username>')
def get_user_timeline(username):
    try:
        if 'username' not in session:
            return jsonify({'error': 'Unauthorized'}), 401

        print(f"Fetching timeline for {username}")
        
        # Get user's activities sorted by timestamp
        pipeline = [
            {
                '$match': {
                    'username': username
                }
            },
            {
                '$sort': {
                    'timestamp': -1
                }
            },
            {
                '$limit': 50
            }
        ]
        
        user_activities = list(activities.aggregate(pipeline))
        print(f"Found {len(user_activities)} activities")

        timeline = []
        for activity in user_activities:
            activity['_id'] = str(activity['_id'])
            
            # Convert timestamp to ISO format
            if 'timestamp' in activity:
                activity['timestamp'] = activity['timestamp'].isoformat()

            # Add any additional details based on activity type
            details = activity.get('details', {})
            
            if activity['type'] == 'review':
                # Get book details for the review
                if 'book_id' in details:
                    try:
                        book = books.find_one({'_id': ObjectId(details['book_id'])})
                        if book:
                            details['book_title'] = book['title']
                        else:
                            print(f"Book not found: {details['book_id']}")
                    except Exception as e:
                        print(f"Invalid book ID: {details['book_id']}, {str(e)}")
                    
            elif activity['type'] == 'book':
                # Get book details
                if 'book_id' in details:
                    try:
                        book = books.find_one({'_id': ObjectId(details['book_id'])})
                        if book:
                            details.update({
                                'book_title': book['title'],
                                'description': book.get('description', '')
                            })
                        else:
                            print(f"Book not found: {details['book_id']}")
                    except Exception as e:
                        print(f"Invalid book ID: {details['book_id']}, {str(e)}")
                    
            elif activity['type'] == 'view':
                if 'book_id' in details:
                    try:
                        book = books.find_one({'_id': ObjectId(details['book_id'])})
                        if book:
                            details['book_title'] = book['title']
                        else:
                            print(f"Book not found: {details['book_id']}")
                    except Exception as e:
                        print(f"Invalid book ID: {details['book_id']}, {str(e)}")

            activity['details'] = details
            timeline.append(activity)

        print(f"Processed {len(timeline)} activities")
        return jsonify({
            'success': True,
            'timeline': timeline
        })

    except Exception as e:
        print("Error getting timeline:", str(e))
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/users/<username>/followers')
def get_followers(username):
    try:
        if 'username' not in session:
            return jsonify({'error': 'Unauthorized'}), 401

        # Get all followers for the user
        followers = list(db.follows.find({'followed': username}))
        
        # Get detailed information for each follower
        follower_details = []
        for follow in followers:
            user = db.users.find_one({'username': follow['follower']})
            if user:
                follower_details.append({
                    'username': user['username'],
                    'name': user.get('name', user['username']),
                    'photo': user.get('photo', None),
                    'date': follow.get('date', None)
                })
        
        return jsonify(follower_details)
    except Exception as e:
        print("Error getting followers:", str(e))
        return jsonify({'error': str(e)}), 500

@app.route('/api/users/<username>/following')
def get_following(username):
    try:
        if 'username' not in session:
            return jsonify({'error': 'Unauthorized'}), 401

        # Get all users that this user follows
        following = list(db.follows.find({'follower': username}))
        
        # Get detailed information for each followed user
        following_details = []
        for follow in following:
            user = db.users.find_one({'username': follow['followed']})
            if user:
                following_details.append({
                    'username': user['username'],
                    'name': user.get('name', user['username']),
                    'photo': user.get('photo', None),
                    'date': follow.get('date', None)
                })
        
        return jsonify(following_details)
    except Exception as e:
        print("Error getting following:", str(e))
        return jsonify({'error': str(e)}), 500

@app.route('/api/user/stats/<username>')
def get_user_stats(username):
    try:
        if 'username' not in session:
            print("No username in session")
            return jsonify({'error': 'Unauthorized'}), 401

        current_user = session['username']
        print(f"Session username: {current_user}")
        print(f"Getting stats for user: {username}")

        # Get followers and following counts
        followers_count = follows.count_documents({'followed': username})
        following_count = follows.count_documents({'follower': username})
        print(f"Followers: {followers_count}, Following: {following_count}")
        
        # Get books count (books authored by user)
        books_count = books.count_documents({'author': username})
        print(f"Books authored: {books_count}")
        
        # Get reviews given by user
        reviews_given = reviews.count_documents({'reviewer': username})
        print(f"Reviews given: {reviews_given}")
        
        # Get reviews received (reviews on user's books)
        # First get all books by the user
        user_books = list(books.find({'author': username}))
        # Convert ObjectIds to strings since that's how they're stored in reviews
        user_book_ids = [str(book['_id']) for book in user_books]
        print(f"User's book IDs: {user_book_ids}")
        
        # Count reviews on user's books
        reviews_received = reviews.count_documents({'book_id': {'$in': user_book_ids}})
        print(f"Reviews received: {reviews_received}")
        
        # Get view count
        view_count = activities.count_documents({
            'username': username,
            'type': 'view'
        })
        print(f"Views: {view_count}")
        
        # Get total activities count
        total_activities = activities.count_documents({'username': username})
        print(f"Total activities: {total_activities}")
        
        # Get all activities for debugging
        all_activities = list(activities.find({'username': username}))
        print(f"All activities for {username}:")
        for activity in all_activities:
            print(f"- {activity['type']}: {activity.get('details', {})}")
        
        # Update user stats in database
        users.update_one(
            {'username': username},
            {'$set': {
                'stats': {
                    'followers': followers_count,
                    'following': following_count,
                    'reviews_given': reviews_given,
                    'reviews_received': reviews_received
                }
            }}
        )
        
        stats = {
            'followers_count': followers_count,
            'following_count': following_count,
            'books_count': books_count,
            'reviews_given': reviews_given,
            'reviews_received': reviews_received,
            'total_reviews': reviews_given + reviews_received,
            'views_count': view_count,
            'total_activities': total_activities
        }
        
        print(f"Final stats: {stats}")
        return jsonify(stats)
        
    except Exception as e:
        print("Error getting user stats:", str(e))
        return jsonify({'error': str(e)}), 500

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Missing username or password'}), 400
    
    user = users.find_one({'username': data['username']})
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    if not bcrypt.checkpw(data['password'].encode('utf-8'), user['password'].encode('utf-8')):
        return jsonify({'error': 'Invalid password'}), 401
    
    session['username'] = user['username']
    return jsonify({'message': 'Login successful', 'username': user['username']}), 200

@app.route('/api/signup', methods=['POST'])
def api_signup():
    try:
        data = request.get_json()
        if not all(k in data for k in ['username', 'password', 'email']):
            return jsonify({'error': 'Missing required fields'}), 400

        if users.find_one({'username': data['username']}):
            return jsonify({'error': 'Username already exists'}), 409

        if users.find_one({'email': data['email']}):
            return jsonify({'error': 'Email already exists'}), 409

        hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())
        hashed_password_str = hashed_password.decode('utf-8')
        user = {
            'username': data['username'],
            'password': hashed_password_str,
            'email': data['email'],
            'bio': '',
            'created_at': datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
        }
        
        users.insert_one(user)
        session['username'] = user['username']
        return jsonify({
            'username': user['username'],
            'email': user['email'],
            'message': 'User created successfully'
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/logout', methods=['GET'])
def api_logout():
    session.pop('username', None)
    return jsonify({'message': 'Logout successful'}), 200

@app.route('/api/books', methods=['POST'])
@login_required
def add_book():
    try:
        data = request.get_json()
        required_fields = ['title', 'description', 'content', 'genres']
        
        if not all(field in data for field in required_fields):
            missing_fields = [field for field in required_fields if field not in data]
            return jsonify({'error': f'Missing required fields: {", ".join(missing_fields)}'}), 400
        
        # Create book document
        book = {
            'title': data['title'],
            'author': session['username'],  # Use current user as author
            'description': data['description'],
            'content': data['content'],
            'genres': data['genres'],
            'cover_image': data.get('cover_image'),
            'language': data.get('language', 'English'),
            'status': data.get('status', 'published'),
            'likes': 0,
            'reviews': [],
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        # Insert the book
        result = books.insert_one(book)
        
        # Track activity
        track_activity(
            session['username'],
            'publish_book' if book['status'] == 'published' else 'save_draft',
            {'book_id': str(result.inserted_id), 'title': book['title']}
        )
        
        return jsonify({
            'message': 'Book published successfully' if book['status'] == 'published' else 'Draft saved successfully',
            'id': str(result.inserted_id)
        }), 201
    except Exception as e:
        print(f"Error adding book: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/books/<book_id>', methods=['GET'])
@login_required
def api_get_book(book_id):
    try:
        book = books.find_one({'_id': ObjectId(book_id)})
        if not book:
            return jsonify({'error': 'Book not found'}), 404
        
        book['_id'] = str(book['_id'])
        return jsonify(book), 200
    except Exception as e:
        return jsonify({'error': f'Invalid book ID: {str(e)}'}), 400

@app.route('/api/users/profile', methods=['GET'])
@login_required
def api_get_profile():
    user = users.find_one({'username': session['username']})
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    profile = {
        'username': user['username'],
        'email': user['email'],
        'bio': user.get('bio', ''),
        'created_at': user['created_at']
    }
    return jsonify(profile), 200

@app.route('/api/users/profile', methods=['PUT'])
@login_required
def api_update_profile():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    allowed_fields = ['email', 'bio']
    update_data = {k: v for k, v in data.items() if k in allowed_fields}
    
    if 'email' in update_data:
        existing = users.find_one({
            'email': update_data['email'],
            'username': {'$ne': session['username']}
        })
        if existing:
            return jsonify({'error': 'Email already in use'}), 409
    
    users.update_one(
        {'username': session['username']},
        {'$set': update_data}
    )
    return jsonify({'message': 'Profile updated successfully'}), 200

@app.route('/api/users/search', methods=['GET'])
@login_required
def search_users():
    try:
        query = request.args.get('q', '').strip()
        if not query:
            return jsonify([])

        # Search for users by username, name, or email
        user_list = list(users.find({
            '$or': [
                {'username': {'$regex': query, '$options': 'i'}},
                {'name': {'$regex': query, '$options': 'i'}},
                {'email': {'$regex': query, '$options': 'i'}}
            ]
        }, {
            'password': 0,  # Exclude password from results
            'email': 0     # Exclude email for privacy
        }).limit(10))

        # Format user data
        formatted_users = []
        for user in user_list:
            # Get stats for user
            books_count = books.count_documents({'author': user['username']})
            followers_count = follows.count_documents({'following': user['username']})
            following_count = follows.count_documents({'follower': user['username']})
            
            formatted_user = {
                'username': user['username'],
                'name': user.get('name', user['username']),
                'bio': user.get('bio', ''),
                'photo': user.get('photo'),
                'stats': {
                    'books': books_count,
                    'followers': followers_count,
                    'following': following_count
                },
                'is_following': follows.find_one({
                    'follower': session['username'],
                    'following': user['username']
                }) is not None
            }
            formatted_users.append(formatted_user)

        return jsonify(formatted_users)
    except Exception as e:
        print(f"User search error: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
