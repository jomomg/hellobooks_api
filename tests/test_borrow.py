import unittest
import json
from app import create_app
import app.models


class BorrowTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.book = {
            'book_id': 101,
            'book_title': 'Ready Player One',
            'publisher': 'Random House',
            'publication_year': '2011',
            'edition': '1',
            'category': 'fiction',
            'subcategory': 'science fiction',
            'description': ''
        }

        self.user = {
            'email': 'test@email.com',
            'password': 'my_pass'
        }

    def tearDown(self):
        app.models.books_list = []

    def login_user(self, user_data):
        login = self.client.post('/api/auth/login', data=user_data)
        return login

    def get_access_token(self, login):
        msg = json.loads(login.data)
        return msg['access_token']

    def register_user(self, user_data):
        registration = self.client.post('/api/auth/register', data=user_data)
        return registration

    def test_borrow_book(self):
        """test whether a user can borrow a book"""

        register = self.register_user(self.user)
        self.assertEqual(register.status_code, 201)
        login = self.login_user(self.user)
        access_token = self.get_access_token(login)
        self.assertEqual(login.status_code, 200)

        add_book = self.client.post('/api/books',
                                    data=json.dumps(self.book),
                                    headers={'content-type': 'application/json',
                                             'Authorization': 'Bearer {}'.format(access_token)})
        self.assertEqual(add_book.status_code, 201)

        book_data = json.loads(add_book.data)
        borrow_book = self.client.post('/api/users/books/{}'.format(book_data['book_id']),
                                       headers={'content-type': 'application/json',
                                                'Authorization': 'Bearer {}'.format(access_token)})
        self.assertEqual(borrow_book.status_code, 200)
        self.assertIn('Ready Player One', str(borrow_book.data))
