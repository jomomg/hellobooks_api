"""API endpoints"""

BASE_URL = '/api/v1'


class Main:
    """Main application endpoints"""

    ADD_BOOK = BASE_URL+'/books'
    ALL_BOOKS = BASE_URL+'/books'
    MODIFY_BOOK = BASE_URL+'/books/<int:book_id>'
    DELETE_BOOK = BASE_URL+'/books/<int:book_id>'
    GET_BOOK = BASE_URL+'/books/<int:book_id>'
    BORROW = BASE_URL+'/users/books/<int:book_id>'
    RETURN = BASE_URL+'/users/books/<int:book_id>'
    BORROWING_HISTORY = BASE_URL+'/users/books'
    UNRETURNED = BASE_URL+'/users/books'


class Auth:
    """Authentication endpoints"""

    REGISTER = BASE_URL+'/auth/register'
    LOGIN = BASE_URL+'/auth/login'
    RESET_PASSWORD = BASE_URL+'/auth/reset-password'
    LOGOUT = BASE_URL+'/auth/logout'



