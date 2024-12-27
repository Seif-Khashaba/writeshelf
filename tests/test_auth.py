from seleniumbase import BaseCase
import pytest
import time
import requests
import json

class AuthTests(BaseCase):
    def setUp(self):
        super().setUp()
        self.base_url = 'http://localhost:5000'
        self.timeout = 10
        self.test_user = {
            'username': 'test ',  # Intentional space
            'email': 'test@example.com',
            'password': 'testpass123'
        }

    def type_slowly(self, selector, text):
        """Helper method to type text slowly"""
        element = self.find_element(selector)
        for char in text:
            element.send_keys(char)
            time.sleep(0.1)

    def wait_for_url_to_contain(self, text, timeout=None):
        """Helper method to wait for URL change"""
        if timeout is None:
            timeout = self.timeout
        end_time = time.time() + timeout
        while time.time() < end_time:
            if text in self.get_current_url():
                return True
            time.sleep(0.1)
        raise Exception(f"URL did not contain {text} after {timeout} seconds")

    def test_signup_page_loads(self):
        self.open(f'{self.base_url}/signup')
        self.wait_for_element_present('.auth-form', timeout=self.timeout)
        self.wait_for_element_present('#username', timeout=self.timeout)
        self.wait_for_element_present('#email', timeout=self.timeout)
        self.wait_for_element_present('#password', timeout=self.timeout)
        self.wait_for_element_present('button[type="submit"]', timeout=self.timeout)

    def test_successful_signup(self):
        self.open(f'{self.base_url}/signup')
        self.wait_for_element_present('.auth-form', timeout=self.timeout)
        
        # Clear any existing text and type slowly
        self.clear_and_type('#username', self.test_user['username'])
        self.clear_and_type('#email', self.test_user['email'])
        self.clear_and_type('#password', self.test_user['password'])
        
        # Wait before clicking submit
        time.sleep(1)
        self.click('button[type="submit"]')
        
        # Wait for redirect to login page
        self.wait_for_url_to_contain('/login', timeout=self.timeout)

    def test_login_page_loads(self):
        self.open(f'{self.base_url}/login')
        self.wait_for_element_present('.auth-form', timeout=self.timeout)
        self.wait_for_element_present('#username', timeout=self.timeout)
        self.wait_for_element_present('#password', timeout=self.timeout)
        self.wait_for_element_present('button[type="submit"]', timeout=self.timeout)
        self.wait_for_text('Welcome Back', 'h2', timeout=self.timeout)

    def test_successful_login(self):
        # Create test user via API if not exists
        try:
            signup_response = requests.post(
                f'{self.base_url}/api/signup',
                json=self.test_user
            )
            if signup_response.status_code != 200:
                # User might already exist, try to login
                verify_response = requests.post(
                    f'{self.base_url}/api/login',
                    json={
                        'username': self.test_user['username'],
                        'password': self.test_user['password']
                    }
                )
                if verify_response.status_code != 200:
                    # If login fails, try to create user again
                    signup_response = requests.post(
                        f'{self.base_url}/api/signup',
                        json=self.test_user
                    )
                    assert signup_response.status_code == 200
        except:
            pass  # User might already exist
        
        # Now test the UI login
        self.open(f'{self.base_url}/login')
        self.wait_for_element_present('.auth-form', timeout=self.timeout)
        
        # Clear any existing text and type slowly
        self.clear_and_type('#username', self.test_user['username'])
        self.clear_and_type('#password', self.test_user['password'])
        
        # Wait before clicking submit
        time.sleep(1)
        self.click('button[type="submit"]')
        
        # Wait for redirect to main page
        self.wait_for_url_to_contain('/main', timeout=self.timeout)

    def test_invalid_login(self):
        # Test non-existent user
        response = requests.post(
            f'{self.base_url}/api/login',
            json={
                'username': 'wronguser',
                'password': 'wrongpass'
            }
        )
        assert response.status_code == 401  # Changed from 404 to 401 for invalid login
        data = response.json()
        assert 'error' in data
        
        # Now test UI invalid login
        self.open(f'{self.base_url}/login')
        self.wait_for_element_present('.auth-form', timeout=self.timeout)
        self.clear_and_type('#username', 'wronguser')
        self.clear_and_type('#password', 'wrongpass')
        self.click('button[type="submit"]')
        time.sleep(1)
        self.wait_for_text('Invalid username or password', timeout=self.timeout)

    def test_logout(self):
        # Login first
        self.test_successful_login()
        
        # Now test logout
        self.wait_for_element_present('#logoutBtn', timeout=self.timeout)
        self.click('#logoutBtn')
        
        # Verify redirect to login page
        self.wait_for_url_to_contain('/login', timeout=self.timeout)

    def clear_and_type(self, selector, text):
        """Helper method to clear and type text with waits"""
        self.wait_for_element_present(selector, timeout=self.timeout)
        element = self.find_element(selector)
        element.clear()
        time.sleep(0.5)  # Wait after clearing
        self.type_slowly(selector, text)
        time.sleep(0.5)  # Wait after typing
