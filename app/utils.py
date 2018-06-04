"""Useful functions"""

from math import ceil
import datetime
from app.models import BorrowLog
now = datetime.datetime.utcnow()


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


def return_book(borrow_id, user_id, book):
    """Return a borrowed book to the library"""

    book_record = BorrowLog.query.get(borrow_id)
    if not book_record:
        return {'message': 'The provided borrow_id was not found. Make sure you have borrowed this book',
                'status_code': 404}
    if book_record.returned:
        return dict(message='This book has already been returned',
                    status_code=409)
    if book_record.user_id != user_id:
        return {
            'message': 'You can only return books that you have borrowed',
            'status_code': 401
        }
    book_record.return_timestamp = now
    book_record.returned = True
    book_record.save()
    book.available += 1
    return {
        'message': 'Book successfully returned on {}'.format(book_record.return_timestamp),
        'status_code': 200
    }
