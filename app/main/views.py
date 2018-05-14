"""Main application views"""

from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Book, User, get_paginated
from app.auth.views import admin_required
import datetime
from . import main


@main.route('/')
def home():
    """Return html containing link to documentation"""

    return main.send_static_file('/app/static/index.html')


@main.route('/api/v1/books', methods=['POST'])
@jwt_required
@admin_required
def add_book():
    """Add a book to the library"""

    new_book = Book()
    data = request.get_json(force=True)
    new_book.populate(data)
    new_book.added = datetime.datetime.utcnow()
    new_book.save()
    return jsonify(new_book.serialize()), 201


@main.route('/api/v1/books', methods=['GET'])
@jwt_required
def get_all_books():
    """Retrieve all books stored in the library"""

    limit = request.args.get('limit')
    page = 1 if not request.args.get('page') else request.args.get('page')
    all_books = Book.get_all()
    if not all_books:
        return jsonify({'message': 'There were no books found'}), 404

    result = [book.serialize() for book in all_books]
    if limit:
        paginated = get_paginated(limit, result, '/api/v1/books', page)
        if not paginated:
            return jsonify(message='The requested page was not found'), 404
        return jsonify(paginated), 200
    return jsonify(result), 200


@main.route('/api/v1/books/<int:book_id>', methods=['PUT', 'DELETE'])
@jwt_required
@admin_required
def book_update_delete(book_id):
    """Update or delete a specific book with a given id"""

    book = Book().get_by_id(book_id)
    if not book:
        return jsonify({'message': 'The requested book was not found'}), 404

    if request.method == 'DELETE':
        book.delete()
        return jsonify({'message': 'You have successfully deleted this book'}), 204

    elif request.method == 'PUT':
        data = request.get_json(force=True)
        book.populate(data)
        book.modified = datetime.datetime.utcnow()
        book.save()
        return jsonify(book.serialize()), 200


@main.route('/api/v1/books/<int:book_id>', methods=['GET'])
@jwt_required
def retrieve_book(book_id):
    """Retrieve a book using its book id"""

    book = Book.get_by_id(book_id)
    if not book:
        return jsonify({'message': 'The requested book was not found'}), 404
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
                'message': 'The borrow_id must be included in the request body when returning a book'
            }), 400

        else:
            result = user.return_book(borrow_id, user.id, book)
            return jsonify(message=result['message']), result['status_code']


@main.route('/api/v1/users/books/', methods=['GET'])
@jwt_required
def borrowing_history():
    """Retrieve borrowing history and un-returned books"""

    current_user_email = get_jwt_identity()
    user = User().get_by_email(current_user_email)
    returned = request.args.get('returned')
    limit = request.args.get('limit')
    page = 1 if not request.args.get('page') else request.args.get('page')

    # get un-returned books
    if returned == 'false':
        if not user.get_unreturned():
            return jsonify({'message': 'You do not have any un-returned books'}), 404
        else:
            if limit:
                paginated = get_paginated(limit, user.get_unreturned(), '/api/v1/users/books', page)
                if not paginated:
                    return jsonify(message='The requested page was not found'), 404
                return jsonify(paginated), 200
            
            return jsonify(user.get_unreturned()), 200

    # get borrowing history
    else:
        if not user.get_borrowing_history():
            return jsonify({'message': 'You do not have any borrowing history'}), 404
        else:
            if limit:
                paginated = get_paginated(limit, user.get_borrowing_history(), '/api/v1/users/books', page)
                if not paginated:
                    return jsonify(message='The requested page was not found'), 404
                return jsonify(paginated), 200

            return jsonify(user.get_borrowing_history()), 200
