import unittest
from app import create_app
import json


class CRUDTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context.push()
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

    def tearDown(self):
        self.app_context.pop()

    def test_add_book(self):
        """test whether the api can add a book"""

        response = self.client.post('/api/books/', data=self.book)
        self.assertEqual(response.status_code, 201)
        self.assertIn('American Gods', str(response.data))

    def test_get_book_by_id(self):
        """test whether the api can retrieve a book by id"""

        response = self.client.post('/api/books/', data=self.book)
        self.assertEqual(response.status_code, 201)
        json_response = json.loads(response.data.decode('utf-8'))
        response_get = self.client.get('/api/books/{}'.format(json_response['book-id']))
        self.assertEqual(response_get, 200)
        self.assertIn('American Gods', response_get.data)

    def test_modify_book(self):
        """test whether the api can modify book information"""

        response_post = self.client.post('/api/books/', data=self.book)
        self.assertEqual(response_post.status_code, 201)
        new_book = self.book['subcategory'] = 'science fiction'
        response_put = self.client.put('/api/books/123', data=new_book)
        self.assertEqual(response_put.status_code, 200)
        response_get = self.client.get('/api/books/123')
        self.assertIn('science fiction', str(response_get.data))

    def test_get_all_books(self):
        """test whether the api can retrieve all books"""

        response_post = self.client.post('/api/books/', data=self.book)
        self.assertEqual(response_post.status_code, 201)
        response_get = self.client.get('/api/books/')
        self.assertEqual(response_get.status_code, 200)
        self.assertIn('American Gods', str(response_get))

    def test_delete_book(self):
        """test whether the api can delete a book"""

        response_post = self.client.post('/api/books/', data=self.book)
        self.assertEqual(response_post.status_code, 201)
        response_delete = self.client.delete('api/books/123')
        self.assertEqual(response_delete.status_code, 200)
        response_get = response_get = self.client.get('/api/books/123')
        self.assertEqual(response_get.status_code, 404)

if __name__ == '__main__':
    unittest.main()
