from seleniumbase import BaseCase
import os
import pytest
import time
import requests

class BookTests(BaseCase):
    def setUp(self):
        super().setUp()
        self.timeout = 10
        self.base_url = 'http://localhost:5000'
        # Set up test user and login
        self.test_user = {
            'username': 'booktest',
            'email': 'booktest@example.com',
            'password': 'testpass123'
        }
        self.login_test_user()
        
        # Test book data
        self.test_book = {
            'title': 'Test Book',
            'author': 'Test Author',
            'description': 'A test book description',
            'genres': ['Test', 'Fiction']
        }

    def login_test_user(self):
        """Helper method to login test user"""
        try:
            signup_response = requests.post(
                f'{self.base_url}/api/signup',
                json=self.test_user
            )
            if signup_response.status_code != 200:
                # Verify user exists by trying to login
                verify_response = requests.post(
                    f'{self.base_url}/api/login',
                    json={
                        'username': self.test_user['username'],
                        'password': self.test_user['password']
                    }
                )
                assert verify_response.status_code == 200
        except:
            pass  # User might already exist
        
        # Now test the UI login
        self.open(f'{self.base_url}/login')
        self.wait_for_element_present('.form-section', timeout=self.timeout)
        
        # Clear any existing text and type slowly
        self.clear_and_type('#username', self.test_user['username'])
        self.clear_and_type('#password', self.test_user['password'])
        
        # Wait before clicking submit
        time.sleep(1)
        self.click('button[type="submit"]')
        
        # Wait for redirect to main page
        self.wait_for_url_to_contain('/main', timeout=self.timeout)

    def test_main_page_loads(self):
        self.open('http://localhost:5000/main')
        self.wait_for_element_present('.book-grid', timeout=self.timeout)
        self.wait_for_text_visible('WriteShelf', 'nav', timeout=self.timeout)

    def test_add_book(self):
        self.open('http://localhost:5000/main')
        self.wait_for_element_clickable('#addBookBtn', timeout=self.timeout)
        self.click('#addBookBtn')
        
        # Wait for modal to open
        time.sleep(1)
        
        # Fill in book details
        self.clear_and_type('#title', self.test_book['title'])
        self.clear_and_type('#author', self.test_book['author'])
        self.clear_and_type('#description', self.test_book['description'])
        
        # Upload test PDF file
        test_pdf_path = os.path.join(os.path.dirname(__file__), 'test_files', 'test.pdf')
        self.choose_file('#pdfFile', test_pdf_path)
        
        time.sleep(1)  # Wait for file upload
        self.click('button[type="submit"]')
        
        # Wait for success message and book to appear
        self.wait_for_text_visible('Book added successfully', timeout=self.timeout)
        self.wait_for_text_visible(self.test_book['title'], timeout=self.timeout)
        self.wait_for_text_visible(self.test_book['author'], timeout=self.timeout)

    def test_search_books(self):
        # First add a test book
        self.test_add_book()
        time.sleep(1)  # Wait for book to be fully added
        
        # Test search functionality
        self.wait_for_element_present('#searchInput', timeout=self.timeout)
        self.clear_and_type('#searchInput', self.test_book['title'])
        self.wait_for_element_clickable('#searchBtn', timeout=self.timeout)
        self.click('#searchBtn')
        
        # Wait for search results
        time.sleep(1)
        self.wait_for_text_visible(self.test_book['title'], timeout=self.timeout)
        self.wait_for_text_visible(self.test_book['author'], timeout=self.timeout)

    def test_book_details(self):
        # First add a test book
        self.test_add_book()
        time.sleep(1)  # Wait for book to be fully added
        
        # Click on book to view details
        self.wait_for_element_clickable(f'a[data-title="{self.test_book["title"]}"]', timeout=self.timeout)
        self.click(f'a[data-title="{self.test_book["title"]}"]')
        
        # Verify book details page
        self.wait_for_text_visible(self.test_book['title'], 'h1', timeout=self.timeout)
        self.wait_for_text_visible(self.test_book['author'], timeout=self.timeout)
        self.wait_for_text_visible(self.test_book['description'], timeout=self.timeout)

    def test_pdf_reader(self):
        # First add a test book
        self.test_add_book()
        time.sleep(1)  # Wait for book to be fully added
        
        # Navigate to reader page
        self.wait_for_element_clickable(f'a[data-title="{self.test_book["title"]}"]', timeout=self.timeout)
        self.click(f'a[data-title="{self.test_book["title"]}"]')
        
        self.wait_for_element_clickable('#readBtn', timeout=self.timeout)
        self.click('#readBtn')
        
        # Verify PDF reader components
        self.wait_for_element_present('#pdfPage', timeout=self.timeout)
        self.wait_for_element_present('.reader-controls', timeout=self.timeout)
        self.wait_for_element_present('#currentPage', timeout=self.timeout)
        
        # Wait for initial page load
        time.sleep(2)
        
        # Test navigation controls
        self.wait_for_element_clickable('button[onclick="nextPage()"]', timeout=self.timeout)
        self.click('button[onclick="nextPage()"]')
        time.sleep(1)  # Wait for page transition
        
        self.wait_for_element_clickable('button[onclick="previousPage()"]', timeout=self.timeout)
        self.click('button[onclick="previousPage()"]')
        time.sleep(1)  # Wait for page transition

    def clear_and_type(self, selector, text):
        """Helper method to clear and type text with waits"""
        self.wait_for_element_present(selector, timeout=self.timeout)
        element = self.find_element(selector)
        element.clear()
        time.sleep(0.5)  # Wait after clearing
        self.type_slowly(selector, text)
        time.sleep(0.5)  # Wait after typing
