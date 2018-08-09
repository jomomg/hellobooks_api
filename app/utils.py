"""Useful functions"""

from math import ceil
import datetime
from app.models import BorrowLog


def group(list_obj, group_len):
    """Group objects in a list into lists with length group_len"""

    for i in range(0, len(list_obj), group_len):
        yield list_obj[i:i + group_len]


def get_paginated(limit_param, results, url, page_param):
    """Return paginated results"""

    page = int(page_param)
    limit = int(limit_param)
    page_count = ceil(len(results) / limit)
    paginated = {}
    if page == 1:
        paginated['previous'] = 'None'
    else:
        paginated['previous'] = url + '?page={}&limit={}'.format(page - 1, limit)

    if page < page_count:
        paginated['next'] = url + '?page={}&limit={}'.format(page + 1, limit)
    elif page > page_count:
        return False
    else:
        paginated['next'] = 'None'

    for i, value in enumerate(group(results, limit)):
        if i == (page - 1):
            paginated['results'] = value
            break

    return paginated


def return_book(user, book):
    """Return a borrowed book to the library"""

    book_record = BorrowLog.query.filter_by(user_id=user.id, book_id=book.id, returned=False).first()
    if user.is_admin:
        book_record = BorrowLog.query.filter_by(book_id=book.id, returned=False).first()
    if not book_record:
        return {'message': 'Borrowing record not found. Make sure you have borrowed this book',
                'status_code': 404}
    if book_record.returned:
        return dict(message='This book has already been returned',
                    status_code=409)

    now = datetime.datetime.utcnow()
    book_record.return_timestamp = now
    book_record.returned = True
    book_record.save()
    book.available += 1
    book.save()
    return {
        'message': 'Book successfully returned on {}'.format(book_record.return_timestamp),
        'status_code': 200
    }
