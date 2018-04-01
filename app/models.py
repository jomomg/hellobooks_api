"""Contains the models used by the application"""

from werkzeug.security import check_password_hash, generate_password_hash
import datetime
from app.app import db


blacklist = set()    # token blacklist


class Book(db.Model):
    """class containing all the book information"""

    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    publisher = db.Column(db.String)
    publication_year = db.Column(db.String)
    edition = db.Column(db.String)
    category = db.Column(db.String)
    subcategory = db.Column(db.String)
    description = db.Column(db.String)
    available = db.Column(db.Integer, default=1)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def get_by_id(book_id):
        return Book.query.get(book_id)

    @staticmethod
    def get_all():
        return Book.query.all()

    def __repr__(self):
        return '<Book: {}>'.format(self.title)


class User(db.Model):
    """class containing all the user information"""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True)
    password = db.Column(db.String)
    is_admin = db.Column(db.String)
    borrowed_books = db.relationship('BorrowLog', backref='user')

    def set_password(self, password):
        """Generate a password hash"""

        self.password = generate_password_hash(password)

    def check_password(self, password):
        """Check if the entered password and the stored password are the same"""

        return check_password_hash(self.password, password)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def borrow_book(self, book_id):
        """Borrow a book"""

        book = Book.get_by_id(book_id)
        now = datetime.datetime.now()
        record = BorrowLog(user_id=self.id,
                           book_id=book.id,
                           borrow_timestamp=now)
        record.save()

    def return_book(self):
        pass

    def borrowing_history(self):
        pass

    @staticmethod
    def get_by_email(email):
        return User.query.filter_by(email=email).first()

    def __repr__(self):
        return '<User: {}>'.format(self.email)


class BorrowLog(db.Model):
    """class containing log of all books borrowed"""

    __tablename__ = 'borrow_log'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)  # user who has borrowed the book
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), primary_key=True)  # book that has been borrowed
    borrow_timestamp = db.Column(db.DateTime)
    returned = db.Column(db.Boolean)
    return_timestamp = db.Column(db.DateTime)

    def save(self):
        db.session.add(self)
        db.session.commit()
