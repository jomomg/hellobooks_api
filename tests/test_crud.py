"""Contains all book CRUD tests"""

import unittest
import json

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
            'email': 'user@earth.com',
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
            self.client.post('/api/v1/books',
                            data=json.dumps(self.book),
                            headers={'content-type': 'application/json',
                                     'Authorization': 'Bearer {}'.format(access_token)})

        # get paginated results
        paginated = self.client.get(
            '/api/v1/books?limit={}'.format(limit), 
            headers={'Authorization': 'Bearer {}'.format(access_token)}
        )
        paginated_data = json.loads(paginated.data)
        self.assertEqual(paginated.status_code, 200)
        self.assertEqual(paginated_data['previous'], 'None')
        self.assertEqual(paginated_data['next'], '/api/v1/books?page=2&limit={}'.format(limit))
        self.assertEqual(len(paginated_data['results']), limit)
        
        # get the next page
        next_page = self.client.get(
            '/api/v1/books?page=2&limit={}'.format(limit), 
            headers={'Authorization': 'Bearer {}'.format(access_token)}
        )
        next_page_data = json.loads(next_page.data)
        self.assertEqual(next_page.status_code, 200)
        self.assertEqual(next_page_data['previous'], '/api/v1/books?page=1&limit={}'.format(limit))
        self.assertEqual(next_page_data['next'], 'None')
        self.assertEqual(len(next_page_data['results']), total-limit)
        

if __name__ == '__main__':
    unittest.main()
