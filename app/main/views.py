"""Main application views"""

from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Book, User, BorrowLog
from app.decorators import admin_required, allow_pagination
import datetime
from . import main
from app.endpoints import Main
from app.utils import return_book


@main.route(Main.ADD_BOOK, methods=['POST'])
@jwt_required
@admin_required
def add_book():
    """Add a book to the library"""

    new_book = Book()
    data = request.get_json(force=True)
    if not data or not data.get('title'):
        return jsonify(message='You must provide at least the title of the book'), 400
    similar = Book.query.filter_by(isbn=data.get('isbn')).first()
    if similar and similar.isbn:
        similar.available += 1
        similar.save()
        return jsonify(message='You have successfully added this book'), 201
    new_book.populate(data)
    new_book.added = datetime.datetime.utcnow()
    new_book.save()
    return jsonify(message='You have successfully added this book',
                   details=new_book.serialize()), 201


@main.route(Main.ALL_BOOKS, methods=['GET'])
@allow_pagination
def get_all_books():
    """Retrieve all books stored in the library"""

    all_books = Book.get_all()
    if not all_books:
        return jsonify({'message': 'There were no books found'}), 404

    result = [book.serialize() for book in all_books]
    return jsonify(result), 200


@main.route(Main.MODIFY_BOOK, methods=['PUT', 'DELETE'])
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
        similar = Book.query.filter_by(isbn=data.get('isbn')).first()
        if similar and similar.isbn:
            similar.available += 1
            similar.save()
            return jsonify(message='A new copy of this book has been added'), 200
        book.populate(data)
        book.modified = datetime.datetime.utcnow()
        book.save()
        return jsonify(message='You have successfully edited this book',
                       details=book.serialize()), 200


@main.route(Main.GET_BOOK, methods=['GET'])
@jwt_required
def retrieve_book(book_id):
    """Retrieve a book using its book id"""

    book = Book.get_by_id(book_id)
    if not book:
        return jsonify({'message': 'The requested book was not found'}), 404
    return jsonify(book.serialize()), 200


@main.route(Main.BORROW, methods=['POST', 'PUT'])
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
        book_record = BorrowLog.query.filter_by(user_id=user.id, book_id=book.id, returned=False).first()
        if book_record:
            return jsonify(message='You cannot borrow the same book twice'), 403
        borrow_info = user.borrow_book(book)
        return jsonify(message='You have successfully borrowed this book',
                       details=borrow_info), 200

    # return a book
    elif request.method == 'PUT':
        result = return_book(user, book)
        return jsonify(message=result['message']), result['status_code']


@main.route(Main.BORROWING_HISTORY, methods=['GET'])
@jwt_required
@allow_pagination
def borrowing_history():
    """Retrieve borrowing history and un-returned books"""

    current_user_email = get_jwt_identity()
    user = User().get_by_email(current_user_email)
    returned = request.args.get('returned')

    # get un-returned books
    if returned == 'false':
        if not user.get_unreturned():
            return jsonify({'message': 'You do not have any un-returned books'}), 404
        else:
            return jsonify(user.get_unreturned()), 200

    # get borrowing history
    else:
        if not user.get_borrowing_history():
            return jsonify({'message': 'You do not have any borrowing history'}), 404
        else:
            return jsonify(user.get_borrowing_history()), 200


@main.route('/api/v1/users/all/', methods=['GET'])
@jwt_required
@admin_required
@allow_pagination
def all_borrowed_books():
    """Returns all borrowed books"""

    borrowed_books = BorrowLog.query.all()
    results = [book.serialize() for book in borrowed_books]
    return jsonify(results), 200
