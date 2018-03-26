from flask_api import FlaskAPI
from flask import request, jsonify, abort
from app.models import Book

from config import app_config


def create_app(config_name):
    """function for creating the application instance"""

    app = FlaskAPI(__name__, instance_relative_config=True)
    app.config.from_object(app_config[config_name])
    app_config[config_name].init_app(app)

    @app.route('/api/books', methods=['POST', 'GET'])
    def books():
        """Adds a book to the library if POST, or retrieves all books if GET is used"""

        new_book = Book()

        if request.method == 'POST':
            data = request.get_json(force=True)
            new_book.id = data.get('book_id')
            new_book.title = data.get('book_title')
            new_book.publisher = data.get('publisher')
            new_book.publication_year = data.get('publication_year')
            new_book.edition = data.get('edition')
            new_book.category = data.get('category')
            new_book.subcategory = data.get('subcategory')
            new_book.description = data.get('description')

            if new_book:
                new_book.save()
                response = jsonify({
                    'book_id': new_book.id,
                    'book_title': new_book.title,
                    'publisher': new_book.publisher,
                    'publication_year': new_book.publication_year,
                    'edition': new_book.edition,
                    'category': new_book.category,
                    'subcategory': new_book.subcategory,
                    'description': new_book.description
                })
                response.status_code = 201
                return response

        else:
            all_books = Book.get_all()
            result = []

            for book in all_books:
                book_item = {
                    'book_id': book.id,
                    'book_title': book.title,
                    'publisher': book.publisher,
                    'publication_year': book.publication_year,
                    'edition': book.edition,
                    'category': book.category,
                    'subcategory': book.subcategory,
                    'description': book.description
                }
                result.append(book_item)

            response = jsonify(result)
            response.status_code = 200
            return response

    @app.route('/api/books/<int:id>', methods=['GET', 'PUT', 'DELETE'])
    def book_specific(id):
        """this function updates, deletes or retrieves a specific book with a given an id"""

        book = Book().get_by_id(id)

        if not book:
            abort(404)

        if request.method == 'DELETE':
            book.delete()
            return {'message': 'success'}, 200

        elif request.method == 'PUT':
            data = request.get_json()
            book.id = data.get('book_id')
            book.title = data.get('book_title')
            book.publisher = data.get('publisher')
            book.publication_year = data.get('publication_year')
            book.edition = data.get('edition')
            book.category = data.get('category')
            book.subcategory = data.get('subcategory')
            book.description = data.get('description')

            book.save()

            response = jsonify({
                'book_id': book.id,
                'book_title': book.title,
                'publisher': book.publisher,
                'publication_year': book.publication_year,
                'edition': book.edition,
                'category': book.category,
                'subcategory': book.subcategory,
                'description': book.description})

            response.status_code = 200
            return response

        elif request.method == 'GET':
            response = jsonify({
                    'book_id': book.id,
                    'book_title': book.title,
                    'publisher': book.publisher,
                    'publication_year': book.publication_year,
                    'edition': book.edition,
                    'category': book.category,
                    'subcategory': book.subcategory,
                    'description': book.description
            })

            response.status_code = 200
            return response

    return app
