users_list = []  # list containing all the users
books_list = []  # list containing all the books
borrowing_info = []  # list containing all borrowing information


class Book:
    """class containing all the book information"""

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

    def borrow(self):
        pass

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
