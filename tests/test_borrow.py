"""Contains all tests related to borrowing tests"""

import unittest
import json

from app.app import create_app
import app.models


class BorrowTestCase(unittest.TestCase):
    """Borrowing tests"""

    def setUp(self):
        """Actions to be performed before each test"""

        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.book = {
            'book_id': 101,
            'book_title': 'Ready Player One',
            'publisher': 'Random House',
            'publication_year': 2011,
            'edition': 1,
            'category': 'fiction',
            'subcategory': 'science fiction',
            'description': ''
        }

        self.user = {
            'email': 'test@email.com',
            'password': 'my_pass'
        }

    def tearDown(self):
        """Actions to be performed after each test"""

        app.models.books_list = []

    def get_access_token(self, user_data):
        self.client.post('/api/v1/auth/register', data=user_data)
        login = self.client.post('/api/v1/auth/login', data=user_data)
        msg = json.loads(login.data)
        return msg['access_token']

    def test_borrow_book(self):
        """Test whether a user can borrow a book"""

        access_token = self.get_access_token(self.user)
        add_book = self.client.post('/api/v1/books',
                                    data=json.dumps(self.book),
                                    headers={'content-type': 'application/json',
                                             'Authorization': 'Bearer {}'.format(access_token)})
        self.assertEqual(add_book.status_code, 201)

        book_data = json.loads(add_book.data)
        borrow_book = self.client.post('/api/v1/users/books/{}'.format(book_data['book_id']),
                                       headers={'content-type': 'application/json',
                                                'Authorization': 'Bearer {}'.format(access_token)})
        self.assertEqual(borrow_book.status_code, 200)
        self.assertIn('Ready Player One', str(borrow_book.data))

    def test_already_borrowed_book(self):
        """Test that a user cannot borrow a book that has already been borrowed"""

        access_token = self.get_access_token(self.user)
        add_book = self.client.post('/api/v1/books',
                                    data=json.dumps(self.book),
                                    headers={'content-type': 'application/json',
                                             'Authorization': 'Bearer {}'.format(access_token)})
        self.assertEqual(add_book.status_code, 201)

        book_data = json.loads(add_book.data)
        borrow_once = self.client.post('/api/v1/users/books/{}'.format(book_data['book_id']),
                                       headers={'content-type': 'application/json',
                                                'Authorization': 'Bearer {}'.format(access_token)})
        self.assertEqual(borrow_once.status_code, 200)
        borrow_twice = self.client.post('/api/v1/users/books/{}'.format(book_data['book_id']),
                                       headers={'content-type': 'application/json',
                                                'Authorization': 'Bearer {}'.format(access_token)})
        self.assertEqual(borrow_twice.status_code, 409)
