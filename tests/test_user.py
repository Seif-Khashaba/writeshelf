from seleniumbase import BaseCase
import pytest
import time
import requests

class UserTests(BaseCase):
    def setUp(self):
        super().setUp()
        self.timeout = 10
        self.base_url = 'http://localhost:5000'
        self.test_user = {
            'username': 'profiletest',
            'email': 'profile@example.com',
            'password': 'testpass123'
        }
        self.login_test_user()

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

    def test_profile_page_loads(self):
        self.open(f'{self.base_url}/profile')
        self.wait_for_element_present('#profileForm', timeout=self.timeout)
        self.wait_for_text_visible(self.test_user['username'], timeout=self.timeout)
        self.wait_for_text_visible(self.test_user['email'], timeout=self.timeout)

    def test_update_profile(self):
        self.open(f'{self.base_url}/profile')
        self.wait_for_element_present('#profileForm', timeout=self.timeout)
        
        # Update profile information
        new_bio = 'This is my test bio'
        self.wait_for_element_present('#bio', timeout=self.timeout)
        self.clear_and_type('#bio', new_bio)
        
        self.wait_for_element_clickable('#updateProfileBtn', timeout=self.timeout)
        self.click('#updateProfileBtn')
        
        # Wait for changes to be saved
        time.sleep(1)
        
        # Verify changes
        self.wait_for_text_visible('Profile updated successfully', timeout=self.timeout)
        self.wait_for_element_present('#bio', timeout=self.timeout)
        self.assert_value('#bio', new_bio)

    def test_change_password(self):
        self.open(f'{self.base_url}/settings')
        self.wait_for_element_present('#changePasswordForm', timeout=self.timeout)
        
        # Change password
        new_password = 'newpass123'
        self.clear_and_type('#currentPassword', self.test_user['password'])
        self.clear_and_type('#newPassword', new_password)
        self.clear_and_type('#confirmPassword', new_password)
        
        self.wait_for_element_clickable('#changePasswordBtn', timeout=self.timeout)
        self.click('#changePasswordBtn')
        
        # Wait for password change
        time.sleep(1)
        
        # Verify password change
        self.wait_for_text_visible('Password changed successfully', timeout=self.timeout)
        
        # Test login with new password
        self.wait_for_element_clickable('#logoutBtn', timeout=self.timeout)
        self.click('#logoutBtn')
        
        self.open(f'{self.base_url}/login')
        self.wait_for_element_present('.form-section', timeout=self.timeout)
        self.clear_and_type('#username', self.test_user['username'])
        self.clear_and_type('#password', new_password)
        self.click('button[type="submit"]')
        
        self.wait_for_url_to_contain('/main', timeout=self.timeout)

    def test_preferences(self):
        self.open(f'{self.base_url}/preferences')
        self.wait_for_element_present('#preferencesForm', timeout=self.timeout)
        
        # Update preferences
        self.wait_for_element_clickable('#darkModeToggle', timeout=self.timeout)
        self.click('#darkModeToggle')
        
        self.wait_for_element_present('#fontSizeSelect', timeout=self.timeout)
        self.select_option_by_text('#fontSizeSelect', 'Large')
        
        self.wait_for_element_clickable('#savePreferencesBtn', timeout=self.timeout)
        self.click('#savePreferencesBtn')
        
        # Wait for preferences to be saved
        time.sleep(1)
        
        # Verify preferences saved
        self.wait_for_text_visible('Preferences saved successfully', timeout=self.timeout)
        self.assert_selected_option('#fontSizeSelect', 'Large')
        
        # Verify dark mode is active (wait for class to be added)
        time.sleep(0.5)
        self.wait_for_element_present('body.dark-theme', timeout=self.timeout)

    def clear_and_type(self, selector, text):
        """Helper method to clear and type text with waits"""
        self.wait_for_element_present(selector, timeout=self.timeout)
        element = self.find_element(selector)
        element.clear()
        time.sleep(0.5)  # Wait after clearing
        self.type_slowly(selector, text)
        time.sleep(0.5)  # Wait after typing
