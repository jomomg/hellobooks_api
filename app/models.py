"""Contains the models used by the application"""

from werkzeug.security import check_password_hash, generate_password_hash
import datetime

users_list = []
books_list = []
borrowing_info = []
# token blacklist
blacklist = set()


class Book:
    """Class containing all the book information"""

    def __init__(self):
        self.id = None
        self.title = None
        self.publisher = None
        self.publication_year = None
        self.edition = None
        self.category = None
        self.subcategory = None
        self.description = None
        self.available = 1

    def save(self, user_books):
        """Save current instance in the books list"""

        user_books.append(self)

    def delete(self, user_books):
        """Delete the current instance in the books list"""

        user_books.remove(self)

    @staticmethod
    def get_by_id(book_id, user_books):
        """Get a book by its id"""

        for book in user_books:
            if book.id == book_id:
                return book
        return None

    @staticmethod
    def get_all(user_books):
        """Get all books in the books list"""

        return user_books

    def serialize(self):
        """Return a JSON object with all the book details"""

        return {
            'book_id': self.id,
            'book_title': self.title,
            'publisher': self.publisher,
            'publication_year': self.publication_year,
            'edition': self.edition,
            'category': self.category,
            'subcategory': self.subcategory,
            'description': self.description
        }


class User:
    """Class containing all the user information"""

    def __init__(self):
        self.id = None
        self.first_name = None
        self.last_name = None
        self.email = None
        self.password = None
        self.is_admin = False
        self.books = []
        self.books_borrowed = []

    def set_password(self, password):
        """Generate a password hash"""

        self.password = generate_password_hash(password)

    def check_password(self, password):
        """Check if the entered password and the stored password are the same"""

        return check_password_hash(self.password, password)

    def save(self):
        """Save current instance in the users list"""

        users_list.append(self)

    def borrow_book(self, book_id, user_books):
        """Borrow a book"""

        book = Book.get_by_id(book_id, user_books)
        self.books_borrowed.append(book)
        now = datetime.datetime.now()
        record = BorrowLog(id=book.id,
                           user=self,
                           book=book,
                           borrow_date=now.strftime("%d/%m/%Y"))
        record.save()

    @staticmethod
    def get_by_email(email):
        """Retrieve a user by their email"""

        for user in users_list:
            if user.email == email:
                return user


class BorrowLog:
    """Class containing log of all books borrowed"""

    def __init__(self, id, user, book, borrow_date):
        self.id = id
        self.user = user
        self.book = book
        self.borrow_date = borrow_date

    def save(self):
        """Save borrowing record"""

        borrowing_info.append(self)
