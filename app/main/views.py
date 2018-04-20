"""Main application views"""

from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Book, User
from . import main


@main.route('/')
def home():
    """Return html containing link to documentation"""

    return main.send_static_file('/app/static/index.html')


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


@main.route('/api/v1/users/books/<int:book_id>', methods=['POST', 'PUT'])
@jwt_required
def borrow_and_return(book_id):
    """Borrow or return a book from the library"""

    current_user_email = get_jwt_identity()
    user = User.get_by_email(current_user_email)
    book = Book().get_by_id(book_id)

    if not book:
        return jsonify({'message': 'The requested book was not found'}), 404

    # borrow a book
    if request.method == 'POST':
        if not book.is_available():
            return jsonify({'message': 'This book has already been borrowed'}), 409
        borrow_info = user.borrow_book(book)
        return jsonify(borrow_info), 200

    # return a book
    elif request.method == 'PUT':
        borrow_id = request.data.get('borrow_id')
        if not borrow_id:
            return jsonify({
                'message': 'The borrow_id must be included in the request when returning a book'
            }), 400

        else:
            return_msg = user.return_book(borrow_id)
            return jsonify(return_msg), 200


@main.route('/api/v1/users/books/', methods=['GET'])
@jwt_required
def borrowing_history():
    """Retrieve borrowing history and un-returned books"""

    current_user_email = get_jwt_identity()
    user = User().get_by_email(current_user_email)
    returned = request.args.get('returned')

    if returned == 'false':
        if not user.get_unreturned():
            return jsonify({'message': 'There are no un-returned books'}), 404
        else:
            return jsonify(user.get_unreturned()), 200
    else:
        if not user.get_borrowing_history():
            return jsonify({'message': 'No borrowing history yet'}), 404
        else:
            return jsonify(user.get_borrowing_history()), 200
