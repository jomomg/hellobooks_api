"""Contains all authentication tests"""

import unittest
import json
import re
from app.app import create_app, db, mail
from app.endpoints import Auth


class AuthTestCase(unittest.TestCase):
    """Authentication test case"""

    def setUp(self):
        """Actions to be performed before each test"""

        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.user = {
            'email': 'user@somewhere.com',
            'password': 'user_pass',
            'confirm password': 'user_pass'
        }

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def login_user(self, user_data):
        """Login helper function"""

        login = self.client.post(Auth.LOGIN, data=user_data)
        return login

    def register_user(self, user_data):
        """Registration helper function"""

        registration = self.client.post(Auth.REGISTER, data=user_data)
        return registration

    def test_user_registration(self):
        """Test whether the api can register a user"""

        registration = self.register_user(self.user)
        self.assertEqual(registration.status_code, 201)
        registration_msg = json.loads(registration.data)
        self.assertEqual(registration_msg['message'], 'You have successfully registered')

    def test_already_registered_user(self):
        """Test that a user cannot be registered twice"""

        self.register_user(self.user)
        second_registration = self.register_user(self.user)
        self.assertEqual(second_registration.status_code, 409)
        result = json.loads(second_registration.data)
        self.assertEqual(result['message'], 'This account has already been registered')

    def test_user_login(self):
        """Test whether a user can login"""

        self.register_user(self.user)
        login = self.login_user(self.user)
        self.assertEqual(login.status_code, 200)
        login_msg = json.loads(login.data)
        self.assertEqual(login_msg['message'], 'Successful login')
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
        self.assertEqual(login_msg['message'], 'Invalid email or password')

    def test_password_reset(self):
        """Test whether a user can reset their password"""

        self.register_user(self.user)
        with mail.record_messages() as outbox:
            rv = self.client.post(Auth.RESET_PASSWORD,
                                  data=dict(email='user@somewhere.com', password='new_pass'))
            self.assertEqual(rv.status_code, 200)
            msg = json.loads(rv.data)['message']
            self.assertEqual(msg, 'A reset code has been sent to the email you provided.')
            self.assertEqual(len(outbox), 1)
            self.assertEqual(outbox[0].subject, 'Password Reset')
            reset_link = re.findall(r'/api/v1/auth/reset-password\?token=[a-zA-Z0-9._-]+', outbox[0].html)[0]
            reset = self.client.post(reset_link)
            self.assertEqual(reset.status_code, 200)
            reset_msg = json.loads(reset.data)['message']
            self.assertEqual(reset_msg, 'Your password has been reset')

        # try login with the old password
        login = self.login_user(self.user)
        self.assertEqual(login.status_code, 401)
        # try login with the new password
        login = self.login_user(dict(email='user@somewhere.com', password='new_pass'))
        self.assertEqual(login.status_code, 200)

    def test_logout(self):
        """Test whether a user can be successfully logged out"""

        self.register_user(self.user)
        login = self.login_user(self.user)
        login_msg = json.loads(login.data)
        access_token = login_msg['access_token']
        logout = self.client.post('/api/v1/auth/logout',
                                  headers={'Authorization': 'Bearer {}'.format(access_token)})
        logout_msg = json.loads(logout.data)
        self.assertEqual(logout.status_code, 200)
        self.assertEqual(logout_msg['message'], 'Successfully logged out')

    def test_register_validation(self):
        """Test whether the app rejects invalid email or password"""

        self.user['email'] = 'useremail.com'
        invalid_email = self.register_user(self.user)
        email_msg = json.loads(invalid_email.data)
        self.assertEqual('Please enter a valid email address', email_msg['message'])
        self.user['password'] = '   '
        self.user['email'] = 'user@email.com'
        invalid_password = self.register_user(self.user)
        pass_msg = json.loads(invalid_password.data)
        self.assertEqual('Please enter a valid password', pass_msg['message'])

    def test_admin_only(self):
        """Test that only an admin can access admin-only endpoints"""

        user = {'email': 'user@email.com',
                'password': 'my_pass',
                'confirm password': 'my_pass'}
        book = {
            'title': 'American Gods', 'publisher': 'Williams Morrow',
            'publication_year': 2001, 'edition': 1, 'category': 'fiction',
            'subcategory': 'fantasy',
            'description': 'A very good book'
        }
        self.client.post('/api/v1/auth/register', data=user)
        login = self.client.post('/api/v1/auth/login', data=user)
        access_token = json.loads(login.data)['access_token']
        rv = self.client.post('/api/v1/books', data=json.dumps(book),
                              headers={'content-type': 'application/json',
                                       'Authorization': 'Bearer {}'.format(access_token)})
        msg = json.loads(rv.data)['message']
        self.assertEqual(rv.status_code, 403)
        self.assertEqual(msg, 'You do not have permission to perform this action')
