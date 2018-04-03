from werkzeug.security import check_password_hash, generate_password_hash
import datetime

users_list = []      # list containing all the users
books_list = []      # list containing all the books
borrowing_info = []  # list containing all borrowing information
blacklist = set()    # token blacklist


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
        self.available = 0

    def save(self):
        books_list.append(self)

    def delete(self):
        books_list.remove(self)

    @staticmethod
    def get_by_id(book_id):
        for book in books_list:
            if book.id == book_id:
                return book
        return None

    @staticmethod
    def get_all():
        return books_list


class User:
    """Class containing all the user information"""

    def __init__(self):
        self.id = None
        self.first_name = None
        self.last_name = None
        self.email = None
        self.password = None
        self.is_admin = False
        self.books_borrowed = []

    def password(self):
        raise AttributeError

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def save(self):
        users_list.append(self)

    def borrow_book(self, book_id):
        book = Book.get_by_id(book_id)
        self.books_borrowed.append(book)
        now = datetime.datetime.now()
        record = BorrowLog(id=book.id,
                           user=self,
                           book=book,
                           borrow_date=now.strftime("%d/%m/%Y"))
        record.save()

    @staticmethod
    def get_by_email(email):
        for user in users_list:
            if user.email == email:
                return user


class BorrowLog:
    """Class containing log of all books borrowed"""

    def __init__(self, id, user, book, borrow_date):
        self.id = id
        self.user = user  # user who has borrowed the book
        self.book = book  # book that has been borrowed
        self.borrow_date = borrow_date

    def save(self):
        borrowing_info.append(self)
