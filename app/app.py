"""Main application file"""

from flask_api import FlaskAPI
from flask import request, jsonify
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity

from app.models import Book, User, blacklist
from config import app_config

API_HOME_PAGE = """
<!DOCTYPE html>
<head>
  <title>HelloBooks API</title>
</head>
<body>
  <h1> HelloBooks API v1.0</h1>
  <a href="https://hellobooksapi.docs.apiary.io">
    <h2>See the documentation</h2>
  </a>
</body>
</html>
"""


def create_app(config_name):
    """Function for creating the application instance"""

    app = FlaskAPI(__name__, instance_relative_config=True)
    app.config.from_object(app_config[config_name])
    app_config[config_name].init_app(app)
    app.url_map.strict_slashes = False
    jwt = JWTManager(app)

    @app.route('/')
    def home():
        """Return html containing link to documentation"""

        return API_HOME_PAGE

    @app.route('/api/v1/books', methods=['POST'])
    @jwt_required
    def add_book():
        """Add a book to the library"""

        new_book = Book()

        if request.method == 'POST':
            data = request.get_json(force=True)
            new_book.title = data.get('book_title')
            new_book.publisher = data.get('publisher')
            new_book.publication_year = data.get('publication_year')
            new_book.edition = data.get('edition')
            new_book.category = data.get('category')
            new_book.subcategory = data.get('subcategory')
            new_book.description = data.get('description')

            new_book.save()

            return jsonify(new_book.serialize()), 201

    @app.route('/api/v1/books', methods=['GET'])
    @jwt_required
    def get_all_books():
        """Retrieve all books stored in the library"""

        all_books = Book.get_all()
        if not all_books:
            return jsonify({'message':'There were no books found'}), 404
        result = []

        if request.method == 'GET':
            for book in all_books:
                book_item = book.serialize()
                result.append(book_item)

            response = jsonify(result)
            response.status_code = 200
            return response

    @app.route('/api/v1/books/<int:book_id>', methods=['PUT', 'DELETE'])
    @jwt_required
    def book_update_delete(book_id):
        """Update or delete a specific book with a given id"""

        book = Book().get_by_id(book_id)

        if not book:
            return jsonify({'message': 'The requested book was not found'}), 404

        if request.method == 'DELETE':
            book.delete()
            return jsonify({'message': 'Successfully deleted'}), 204

        elif request.method == 'PUT':
            data = request.get_json(force=True)
            book.title = data.get('book_title')
            book.publisher = data.get('publisher')
            book.publication_year = data.get('publication_year')
            book.edition = data.get('publisher')
            book.category = data.get('category')
            book.subcategory = data.get('subcategory')
            book.description = data.get('description')

            response = jsonify(book.serialize())

            response.status_code = 200
            return response

    @app.route('/api/v1/books/<int:book_id>', methods=['GET'])
    @jwt_required
    def retrieve_book(book_id):
        """Retrieve a book using its book id"""

        book = Book.get_by_id(book_id)

        if not book:
            return jsonify({'message': 'The requested book was not found'}), 404

        if request.method == 'GET':
            response = jsonify(book.serialize())

            response.status_code = 200
            return response

    @app.route('/api/v1/users/books/<int:book_id>', methods=['POST'])
    @jwt_required
    def borrow_book(book_id):
        """Borrow a book from the library"""

        current_user_email = get_jwt_identity()
        user = User.get_by_email(current_user_email)
        book = Book().get_by_id(book_id)

        if not book:
            return jsonify({'message': 'The requested book was not found'}), 404
        elif book.is_borrowed:
            return jsonify({'message': 'This book has already been borrowed'}), 409

        if request.method == 'POST':
            user.borrow_book(book.id)
            response = jsonify({'message': 'You have successfully borrowed this book',
                                'book details': [book.serialize()]})

            response.status_code = 200
            return response

    @jwt.token_in_blacklist_loader
    def check_if_token_in_blacklist(token):
        """Callback for checking if a token is blacklisted"""

        jti = token['jti']
        return jti in blacklist

    from app.auth import auth
    app.register_blueprint(auth)
    return app
