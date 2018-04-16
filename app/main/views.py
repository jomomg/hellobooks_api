"""Main application views"""

from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Book, User
from . import main


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


@main.route('/')
def home():
    """Return html containing link to documentation"""

    return API_HOME_PAGE


@main.route('/api/v1/books', methods=['POST'])
@jwt_required
def add_book():
    """Add a book to the library"""

    new_book = Book()

    if request.method == 'POST':
        data = request.get_json(force=True)
        new_book.populate(data)
        new_book.save()

        return jsonify(new_book.serialize()), 201


@main.route('/api/v1/books', methods=['GET'])
@jwt_required
def get_all_books():
    """Retrieve all books stored in the library"""

    all_books = Book.get_all()
    if not all_books:
        return jsonify({'message': 'There were no books found'}), 404
    result = []

    if request.method == 'GET':
        for book in all_books:
            book_item = book.serialize()
            result.append(book_item)

        return jsonify(result), 200


@main.route('/api/v1/books/<int:book_id>', methods=['PUT', 'DELETE'])
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
        book.populate(data)

        return jsonify(book.serialize()), 200


@main.route('/api/v1/books/<int:book_id>', methods=['GET'])
@jwt_required
def retrieve_book(book_id):
    """Retrieve a book using its book id"""

    book = Book.get_by_id(book_id)
    if not book:
        return jsonify({'message': 'The requested book was not found'}), 404

    if request.method == 'GET':
        return jsonify(book.serialize()), 200


@main.route('/api/v1/users/books/<int:book_id>', methods=['POST'])
@jwt_required
def borrow_book(book_id):
    """Borrow a book from the library"""

    current_user_email = get_jwt_identity()
    user = User.get_by_email(current_user_email)
    book = Book().get_by_id(book_id)

    if not book:
        return jsonify({'message': 'The requested book was not found'}), 404
    elif not book.is_available():
        return jsonify({'message': 'This book has already been borrowed'}), 409

    if request.method == 'POST':
        borrow_info = user.borrow_book(book)
        return jsonify(borrow_info), 200
