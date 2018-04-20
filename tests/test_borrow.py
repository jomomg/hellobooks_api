"""Contains all tests related to borrowing of books"""

import unittest
import json
from app.app import create_app, db


class BorrowTestCase(unittest.TestCase):
    """Borrowing tests"""

    def setUp(self):
        """Actions to be performed before each test"""

        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.book = {
            'title': 'Ready Player One',
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
        self.access_token = self.get_access_token(self.user)

    def tearDown(self):
        """Actions to be performed after each test"""

        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def get_access_token(self, user_data):
        """ Logs in a user and returned an access token"""

        self.client.post('/api/v1/auth/register', data=user_data)
        login = self.client.post('/api/v1/auth/login', data=user_data)
        msg = json.loads(login.data)
        return msg['access_token']

    def add_book(self):
        """Add a book"""

        return self.client.post(
            '/api/v1/books',
            data=json.dumps(self.book),
            headers={
                'content-type': 'application/json',
                'Authorization': 'Bearer {}'.format(self.access_token)
            }
        )

    def borrow(self, book_data):
        """Borrow a book"""

        return self.client.post(
            '/api/v1/users/books/{}'.format(book_data['id']),
            headers={
                'content-type': 'application/json',
                'Authorization': 'Bearer {}'.format(self.access_token)
            }
        )

    def return_book(self, book_data, borrow_info):
        """Return a book"""

        return self.client.put(
            '/api/v1/users/books/{}'.format(book_data['id']),
            data=json.dumps({'borrow_id': borrow_info['borrow_id']}),
            headers={
                'content-type': 'application/json',
                'Authorization': 'Bearer {}'.format(self.access_token)
            }
        )

    def test_borrow_book(self):
        """Test whether a user can borrow a book"""

        add_book = self.add_book()
        book_data = json.loads(add_book.data)
        borrow_book = self.borrow(book_data)
        self.assertEqual(borrow_book.status_code, 200)
        self.assertEqual(json.loads(borrow_book.data)['message'],
                         'You have successfully borrowed this book')

    def test_already_borrowed_book(self):
        """Test whether a user can borrow a book that has already been borrowed"""

        add_book = self.add_book()
        book_data = json.loads(add_book.data)
        borrow_once = self.borrow(book_data)
        self.assertEqual(borrow_once.status_code, 200)
        borrow_twice = self.borrow(book_data)
        self.assertEqual(borrow_twice.status_code, 409)

    def test_book_return(self):
        """Test whether a borrowed book can be returned"""

        add_book = self.add_book()
        book_data = json.loads(add_book.data)
        borrow_book = self.borrow(book_data)
        borrow_info = json.loads(borrow_book.data)
        return_book = self.return_book(book_data, borrow_info)
        self.assertEqual(return_book.status_code, 200)
        self.assertEqual(json.loads(return_book.data)['message'],
                         'Book successfully returned')

    def test_not_returned_books(self):
        """Test whether a user's un-returned books can be retrieved"""

        add_book = self.add_book()
        book_data = json.loads(add_book.data)
        borrow_book = self.borrow(book_data)
        self.assertEqual(borrow_book.status_code, 200)
        not_returned = self.client.get(
            '/api/v1/users/books?returned=false',
            headers={
                'Authorization': 'Bearer {}'.format(self.access_token)
            }
        )
        self.assertEqual(not_returned.status_code, 200)
        not_returned_data = json.loads(not_returned.data)
        self.assertIn('Ready Player One', str(not_returned_data))

    def test_borrowing_history(self):
        """Test whether a user can get their borrowing history"""

        add_book = self.add_book()
        book_data = json.loads(add_book.data)
        borrow_book = self.borrow(book_data)
        borrow_info = json.loads(borrow_book.data)
        self.return_book(book_data, borrow_info)
        borrow_history = self.client.get(
            '/api/v1/users/books',
            headers={
                'content-type': 'application/json',
                'Authorization': 'Bearer {}'.format(self.access_token)
            }
        )
        self.assertEqual(borrow_history.status_code, 200)
        borrow_data = json.loads(borrow_history.data)
        self.assertIn('Ready Player One', str(borrow_data))
        self.assertIn('borrow_id', str(borrow_data))
