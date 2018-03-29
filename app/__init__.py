from flask_api import FlaskAPI
from flask import request, jsonify, abort
from app.models import Book, User, blacklist
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity

from config import app_config


def create_app(config_name):
    """function for creating the application instance"""

    app = FlaskAPI(__name__, instance_relative_config=True)
    app.config.from_object(app_config[config_name])
    app_config[config_name].init_app(app)
    jwt = JWTManager(app)

    @app.route('/api/books', methods=['POST'])
    @jwt_required
    def add_book():
        """Adds a book to the library"""

        new_book = Book()
        # current_user_email = get_jwt_identity()
        # user = User().get_by_email(current_user_email)

        # if not user.is_admin:
        #    return jsonify({'message': 'admin only'}), 403

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

            similar = [book for book in Book().get_all() if book.id == new_book.id]
            if similar:
                return jsonify({'message': 'this book already exists'}), 202
            else:
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

    @app.route('/api/books', methods=['GET'])
    @jwt_required
    def get_all_books():
        """Retrieves all books stored in the library"""

        all_books = Book.get_all()
        result = []

        if request.method == 'GET':
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

    @app.route('/api/books/<int:id>', methods=['PUT', 'DELETE'])
    @jwt_required
    def book_update_delete(id):
        """this function updates or deletes a specific book with a given id"""

        book = Book().get_by_id(id)
        # current_user_email = get_jwt_identity()
        # user = User().get_by_email(current_user_email)

        # if not user.is_admin:
        #    return jsonify({'message': 'admin only'}), 403

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
                'description': book.description
            })

            response.status_code = 200
            return response

    @app.route('/api/books/<int:id>', methods=['GET'])
    @jwt_required
    def retrieve_book(id):
        book = Book().get_by_id(id)
        if not book:
            abort(404)

        if request.method == 'GET':
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

    @app.route('/api/users/books/<int:book_id>', methods=['POST'])
    @jwt_required
    def borrow_book(book_id):
        book = Book().get_by_id(book_id)
        current_user_email = get_jwt_identity()
        user = User.get_by_email(current_user_email)

        if not book:
            abort(404)

        if request.method == 'POST':
            user.borrow_book(book.id)
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

    @jwt.token_in_blacklist_loader
    def check_if_token_in_blacklist(token):
        jti = token['jti']
        return jti in blacklist

    from app.auth import auth
    app.register_blueprint(auth)
    return app
