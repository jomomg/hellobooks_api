import unittest
from app import create_app
import json
import app.models


class CRUDTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

        self.book = {
            'book_id': 123,
            'book_title': 'American Gods',
            'publisher': 'Williams Morrow',
            'publication_year': '2001',
            'edition': '5',
            'category': 'fiction',
            'subcategory': 'fantasy',
            'description': ''
        }

        self.user = {
            'email': 'user@earth.com',
            'password': 'my_pass'
        }

    def tearDown(self):
        app.models.books_list = []
        app.models.users_list = []
        self.app_context.pop()

    def get_access_token(self, user_data):
        """Registers, logs in and returns an access token for authentication"""

        self.client.post('/api/v1/auth/register', data=user_data)
        login = self.client.post('/api/v1/auth/login', data=user_data)
        msg = json.loads(login.data)
        return msg['access_token']

    def test_add_book(self):
        """Test whether the api can add a book"""

        access_token = self.get_access_token(self.user)
        response = self.client.post('/api/v1/books',
                                    data=json.dumps(self.book),
                                    headers={'content-type': 'application/json',
                                             'Authorization': 'Bearer {}'.format(access_token)})
        self.assertEqual(response.status_code, 201)
        self.assertIn('American Gods', str(response.data))

    def test_rejects_similar_books(self):
        """Test that the app does not allow addition of books with similar ids"""

        access_token = self.get_access_token(self.user)
        self.client.post('/api/v1/books',
                         data=json.dumps(self.book),
                         headers={'content-type': 'application/json',
                                  'Authorization': 'Bearer {}'.format(access_token)})
        add_similar_book = self.client.post('/api/v1/books',
                                            data=json.dumps(self.book),
                                            headers={'content-type': 'application/json',
                                                     'Authorization': 'Bearer {}'.format(access_token)})
        self.assertEqual(add_similar_book.status_code, 202)
        json_response = json.loads(add_similar_book.data)
        self.assertEqual(json_response['message'], 'this book already exists')

    def test_get_all_books(self):
        """Test whether the api can retrieve all books"""

        access_token = self.get_access_token(self.user)
        response_post = self.client.post('/api/v1/books',
                                         data=json.dumps(self.book),
                                         headers={'content-type': 'application/json',
                                                  'Authorization': 'Bearer {}'.format(access_token)})
        self.assertEqual(response_post.status_code, 201)
        response_get = self.client.get('/api/v1/books', headers={'Authorization': 'Bearer {}'.format(access_token)})
        self.assertEqual(response_get.status_code, 200)
        self.assertIn('American Gods', str(response_get.data))

    def test_get_book_by_id(self):
        """Test whether the api can retrieve a book by id"""

        access_token = self.get_access_token(self.user)
        response = self.client.post('/api/v1/books',
                                    data=json.dumps(self.book),
                                    headers={'content-type': 'application/json',
                                             'Authorization': 'Bearer {}'.format(access_token)})
        self.assertEqual(response.status_code, 201)
        json_response = json.loads(response.data)
        response_get = self.client.get('/api/v1/books/{}'.format(json_response['book_id']),
                                       headers={'Authorization': 'Bearer {}'.format(access_token)})
        self.assertEqual(response_get.status_code, 200)
        self.assertIn('American Gods', str(response_get.data))

    def test_modify_book(self):
        """Test whether the api can modify book information"""

        access_token = self.get_access_token(self.user)
        response_post = self.client.post('/api/v1/books',
                                         data=json.dumps(self.book),
                                         headers={'content-type': 'application/json',
                                                  'Authorization': 'Bearer {}'.format(access_token)})
        self.assertEqual(response_post.status_code, 201)
        self.book['subcategory'] = 'science fiction'
        response_put = self.client.put('/api/v1/books/123',
                                       data=json.dumps(self.book),
                                       headers={'content-type': 'application/json',
                                                'Authorization': 'Bearer {}'.format(access_token)})
        self.assertEqual(response_put.status_code, 200)
        response_get = self.client.get('/api/v1/books/123', headers={'Authorization': 'Bearer {}'.format(access_token)})
        self.assertIn('science fiction', str(response_get.data))

    def test_delete_book(self):
        """Test whether the api can delete a book"""

        self.book['book_id'] = 345
        access_token = self.get_access_token(self.user)
        response_post = self.client.post('/api/v1/books',
                                         data=json.dumps(self.book),
                                         headers={'content-type': 'application/json',
                                                  'Authorization': 'Bearer {}'.format(access_token)})
        self.assertEqual(response_post.status_code, 201)
        response_delete = self.client.delete('api/v1/books/345',
                                             headers={'Authorization': 'Bearer {}'.format(access_token)})
        self.assertEqual(response_delete.status_code, 200)
        response_get = self.client.get('/api/v1/books/345', headers={'Authorization': 'Bearer {}'.format(access_token)})
        self.assertEqual(response_get.status_code, 404)

if __name__ == '__main__':
    unittest.main()
