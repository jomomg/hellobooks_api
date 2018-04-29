"""Contains all book CRUD tests"""

import unittest
import json
from flask import current_app

from app.app import create_app, db


class CRUDTestCase(unittest.TestCase):
    """Tests for Creating, Reading, Updating and Deleting a book"""

    def setUp(self):
        """Actions to be performed before each test"""

        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        self.book = {
            'title': 'American Gods',
            'publisher': 'Williams Morrow',
            'publication_year': 2001,
            'edition': 1,
            'category': 'fiction',
            'subcategory': 'fantasy',
            'description': ''
        }

        self.user = {
            'email': current_app.config['ADMIN'],
            'password': 'my_pass'
        }

    def tearDown(self):
        db.session.remove()
        db.drop_all()
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

    def test_generates_unique_ids(self):
        """Test that the app generates unique books ids"""

        access_token = self.get_access_token(self.user)
        add_book = self.client.post('/api/v1/books',
                                    data=json.dumps(self.book),
                                    headers={'content-type': 'application/json',
                                             'Authorization': 'Bearer {}'.format(access_token)})
        add_similar_book = self.client.post('/api/v1/books',
                                            data=json.dumps(self.book),
                                            headers={'content-type': 'application/json',
                                                     'Authorization': 'Bearer {}'.format(access_token)})
        similar_book = json.loads(add_similar_book.data)
        book = json.loads(add_book.data)
        self.assertNotEqual(book['id'], similar_book['id'])

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
        book_data = json.loads(response.data)
        response_get = self.client.get('/api/v1/books/{}'.format(book_data['id']),
                                       headers={'Authorization': 'Bearer {}'.format(access_token)})
        self.assertEqual(response_get.status_code, 200)
        self.assertIn('American Gods', str(response_get.data))

    def test_modify_book(self):
        """Test whether the app can modify book information"""

        access_token = self.get_access_token(self.user)
        response_post = self.client.post('/api/v1/books',
                                         data=json.dumps(self.book),
                                         headers={'content-type': 'application/json',
                                                  'Authorization': 'Bearer {}'.format(access_token)})
        self.assertEqual(response_post.status_code, 201)
        self.book['subcategory'] = 'science fiction'
        book_data = json.loads(response_post.data)
        response_put = self.client.put('/api/v1/books/{}'.format(book_data['id']),
                                       data=json.dumps(self.book),
                                       headers={'content-type': 'application/json',
                                                'Authorization': 'Bearer {}'.format(access_token)})
        self.assertEqual(response_put.status_code, 200)
        response_get = self.client.get('/api/v1/books/{}'.format(book_data['id']),
                                       headers={'Authorization': 'Bearer {}'.format(access_token)})
        self.assertIn('science fiction', str(response_get.data))

    def test_delete_book(self):
        """Test whether the api can delete a book"""

        access_token = self.get_access_token(self.user)
        response_post = self.client.post('/api/v1/books',
                                         data=json.dumps(self.book),
                                         headers={'content-type': 'application/json',
                                                  'Authorization': 'Bearer {}'.format(access_token)})
        self.assertEqual(response_post.status_code, 201)
        book_data = json.loads(response_post.data)
        response_delete = self.client.delete('api/v1/books/{}'.format(book_data['id']),
                                             headers={'Authorization': 'Bearer {}'.format(access_token)})
        self.assertEqual(response_delete.status_code, 204)
        response_get = self.client.get('/api/v1/books/345', headers={'Authorization': 'Bearer {}'.format(access_token)})
        self.assertEqual(response_get.status_code, 404)

    def test_pagination(self):
        """Test whether the app can return paginated results"""

        access_token = self.get_access_token(self.user)
        limit = 3
        total = 5

        # add a lot of books
        for i in range(1, total+1):
            self.book['title'] = 'Book {}'.format(i)
            self.client.post('/api/v1/books', data=json.dumps(self.book),
                             headers={'content-type': 'application/json',
                                      'Authorization': 'Bearer {}'.format(access_token)})

        # get paginated results
        p = self.client.get(
            '/api/v1/books?limit={}'.format(limit), 
            headers={'Authorization': 'Bearer {}'.format(access_token)}
        )
        p_next = json.loads(p.data)['next']
        p_prev = json.loads(p.data)['previous']
        p_results = json.loads(p.data)['results']
        self.assertEqual(p.status_code, 200)
        self.assertEqual(p_prev, 'None')
        self.assertEqual(p_next, '/api/v1/books?page=2&limit={}'.format(limit))
        self.assertEqual(len(p_results), limit)
        
        # get the next page
        np = self.client.get('/api/v1/books?page=2&limit={}'.format(limit),
                             headers={'Authorization': 'Bearer {}'.format(access_token)})
        np_prev = json.loads(np.data)['previous']
        np_next = json.loads(np.data)['next']
        np_results = json.loads(np.data)['results']
        self.assertEqual(np.status_code, 200)
        self.assertEqual(np_prev, '/api/v1/books?page=1&limit={}'.format(limit))
        self.assertEqual(np_next, 'None')
        self.assertEqual(len(np_results), total-limit)

        # previous page
        prev = self.client.get(np_prev, headers={'Authorization': 'Bearer {}'.format(access_token)})
        self.assertEqual(prev.status_code, 200)

        # invalid page number
        invalid = self.client.get('/api/v1/books?page=5&limit={}'.format(limit),
                                  headers={'Authorization': 'Bearer {}'.format(access_token)})
        msg = json.loads(invalid.data)['message']
        self.assertEqual(msg, 'The requested page was not found')
        self.assertEqual(invalid.status_code, 404)


if __name__ == '__main__':
    unittest.main()
