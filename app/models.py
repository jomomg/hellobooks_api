"""Contains the models used by the application"""

from werkzeug.security import check_password_hash, generate_password_hash
from flask import current_app
from math import ceil
import datetime
import uuid
from app.app import db


now = datetime.datetime.utcnow()


def generate_uuid():
    """Generate a unique string id"""

    return str(uuid.uuid4())[:8]


class Book(db.Model):
    """Class containing all the book information"""

    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    publisher = db.Column(db.String)
    publication_year = db.Column(db.String)
    edition = db.Column(db.String)
    category = db.Column(db.String)
    subcategory = db.Column(db.String)
    description = db.Column(db.String)
    added = db.Column(db.DateTime)
    modified = db.Column(db.DateTime)
    available = db.Column(db.Integer, default=1)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def populate(self, dict_obj):
        """Populate attributes with dictionary values"""

        for key in dict_obj:
            setattr(self, key, dict_obj[key])

    def is_available(self):
        """Check if a book is available"""

        if self.available >= 1:
            return True
        else:
            return False

    @staticmethod
    def get_by_id(book_id):
        """Return a book object with a given id"""

        return Book.query.get(book_id)

    @staticmethod
    def get_all():
        return Book.query.all()

    def serialize(self):
        """Returns a dictionary containing book information"""

        return {
            column.key: str(getattr(self, column.key))
            for column in self.__table__.columns
            if column.key != 'available'
        }

    def __repr__(self):
        return '<Book: {}>'.format(self.title)


class User(db.Model):
    """class containing all the user information"""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True)
    password = db.Column(db.String)
    is_admin = db.Column(db.Boolean, default=False)
    borrowed_books = db.relationship('BorrowLog', backref='user')

    def set_password(self, password):
        """Generate a password hash"""

        self.password = generate_password_hash(password)

    def check_password(self, password):
        """Check if the entered password and the stored password are the same"""

        return check_password_hash(self.password, password)

    def save(self):
        """Save to database"""

        db.session.add(self)
        db.session.commit()

    def borrow_book(self, book):
        """Borrow a book"""

        return_time = now + datetime.timedelta(
            days=current_app.config['BOOK_RETURN_PERIOD'])
        record = BorrowLog(
            borrow_id=generate_uuid(),
            user_id=self.id,
            book_id=book.id,
            borrow_timestamp=now,
            expected_return=return_time,
            returned=False
        )
        book.available -= 1
        record.save()
        return {
            'borrow_id': record.borrow_id,
            'borrowed_on': record.borrow_timestamp,
            'expected_return': record.expected_return,
            'message': 'You have successfully borrowed this book'
        }

    def get_unreturned(self):
        """Retrieve all books not yet returned"""

        return [record.book.serialize()
                for record in self.borrowed_books
                if record.user_id == self.id]

    @staticmethod
    def return_book(borrow_id):
        """Return a borrowed book to the library"""

        book_record = BorrowLog.query.get(borrow_id)
        if not book_record:
            return False
        book_record.return_timestamp = now
        book_record.returned = True
        return {
            'message': 'Book successfully returned',
            'return_date': book_record.return_timestamp
        }

    def get_borrowing_history(self):
        """Get the user's borrowing history"""

        if not self.borrowed_books:
            return False
        else:
            return [{
                'borrow_id': record.borrow_id,
                'book_id': record.book_id,
                'title': record.book.title,
                'borrowed_on': record.borrow_timestamp,
                'return_status': record.returned,
                'returned_on': record.return_timestamp
            } for record in self.borrowed_books]

    @staticmethod
    def get_by_email(email):
        return User.query.filter_by(email=email).first()

    def __repr__(self):
        return '<User: {}>'.format(self.email)


class BorrowLog(db.Model):
    """class containing log of all books borrowed"""

    __tablename__ = 'borrow_log'

    borrow_id = db.Column(db.String, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'))
    borrow_timestamp = db.Column(db.DateTime)
    expected_return = db.Column(db.DateTime)
    return_timestamp = db.Column(db.DateTime)
    returned = db.Column(db.Boolean)
    book = db.relationship('Book', backref='book_assoc')

    def save(self):
        db.session.add(self)
        db.session.commit()


def group(list_obj, group_len):
    """Group objects in a list into lists with length group_len"""

    for i in range(0, len(list_obj), group_len):
        yield list_obj[i:i+group_len]


def get_paginated(limit_param, results, url, page_param):
    """Return paginated results"""

    page = int(page_param)
    limit = int(limit_param)
    page_count = ceil(len(results)/limit)
    paginated = {}
    if page == 1:
        paginated['previous'] = 'None'
    else:
        paginated['previous'] = url + '?page={}&limit={}'.format(page-1, limit)
        
    if page < page_count:
        paginated['next'] = url + '?page={}&limit={}'.format(page+1, limit)
    elif page > page_count:
        return False
    else:
        paginated['next'] = 'None'

    for i, value in enumerate(group(results, limit)):
        if i == (page-1):
            paginated['results'] = value
            break

    return paginated
