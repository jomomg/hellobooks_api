from functools import wraps
from flask_jwt_extended.exceptions import (InvalidHeaderError, NoAuthorizationError)

from flask_jwt_extended import verify_jwt_refresh_token_in_request


def verify_refresh_in_request_optional():
    try:
        verify_jwt_refresh_token_in_request()
    except (InvalidHeaderError, NoAuthorizationError):
        pass


def refresh_jwt_optional(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_refresh_in_request_optional()
        return fn(*args, **kwargs)
    return wrapper
