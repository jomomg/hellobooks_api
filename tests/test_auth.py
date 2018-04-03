import unittest
import json

from app import create_app
import app.models


class AuthTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.user = {
            'email': 'user@somewhere.com',
            'password': 'user_pass'
        }

    def tearDown(self):
        app.models.users_list = []

    def login_user(self, user_data):
        login = self.client.post('/api/v1/auth/login', data=user_data)
        return login

    def register_user(self, user_data):
        registration = self.client.post('/api/v1/auth/register', data=user_data)
        return registration

    def test_user_registration(self):
        """Test whether the api can register a user"""

        registration = self.register_user(self.user)
        self.assertEqual(registration.status_code, 201)
        registration_msg = json.loads(registration.data)
        self.assertEqual(registration_msg['message'], 'successful registration')

    def test_already_registered_user(self):
        """Test that a user cannot be registered twice"""

        registration = self.register_user(self.user)
        self.assertEqual(registration.status_code, 201)
        second_registration = self.register_user(self.user)
        self.assertEqual(second_registration.status_code, 202)
        result = json.loads(second_registration.data)
        self.assertEqual(result['message'], 'you are already registered')

    def test_user_login(self):
        """Test whether a user can login"""

        registration = self.register_user(self.user)
        self.assertEqual(registration.status_code, 201)
        login = self.login_user(self.user)
        self.assertEqual(login.status_code, 200)
        login_msg = json.loads(login.data)
        self.assertEqual(login_msg['message'], 'successful login')
        self.assertTrue(login_msg['access_token'])

    def test_non_registered_login(self):
        """Test whether a non registered user can login"""

        another_user = {
            'email': 'another@somewhere.com',
            'password': 'user_pass'
        }
        login = self.login_user(another_user)
        self.assertEqual(login.status_code, 401)
        login_msg = json.loads(login.data)
        self.assertEqual(login_msg['message'], 'invalid email or password')

    def test_password_reset(self):
        """Test whether a user can reset their password"""

        registration = self.register_user(self.user)
        self.assertEqual(registration.status_code, 201)
        login = self.login_user(self.user)
        self.assertEqual(login.status_code, 200)
        new_password = {'password': 'new_pass'}
        login_msg = json.loads(login.data)
        access_token = login_msg['access_token']
        reset = self.client.post('/api/v1/auth/reset-password',
                                 data=new_password,
                                 headers={'Authorization': 'Bearer {}'.format(access_token)})
        self.assertEqual(reset.status_code, 200)
        reset_msg = json.loads(reset.data)
        self.assertEqual(reset_msg['message'], 'password reset successful')

    def test_logout(self):
        """Test whether a user can be successfully logged out"""

        registration = self.register_user(self.user)
        self.assertEqual(registration.status_code, 201)
        login = self.login_user(self.user)
        self.assertEqual(login.status_code, 200)
        login_msg = json.loads(login.data)
        access_token = login_msg['access_token']
        logout = self.client.post('/api/v1/auth/logout',
                                  headers={'Authorization': 'Bearer {}'.format(access_token)})
        logout_msg = json.loads(logout.data)
        self.assertEqual(logout.status_code, 200)
        self.assertEqual(logout_msg['message'], 'successfully logged out')


if __name__ == '__main__':
    unittest.main()
