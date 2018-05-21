"""Decorators"""

import json
from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity
from app.models import User, get_paginated


def allow_pagination(func):
    """Decorator for paginating results"""

    @wraps(func)
    def paginate(*args, **kwargs):
        limit = request.args.get('limit')
        page = 1 if not request.args.get('page') else request.args.get('page')

        rv = func(*args, **kwargs)[0]
        results = json.loads(rv.data)

        if limit:
            paginated = get_paginated(limit, results, request.path, page)
            if not paginated:
                return jsonify(message='The requested page was not found'), 404
            return jsonify(paginated), 200
        return func(*args, **kwargs)

    return paginate


def admin_required(func):
    """Decorator for protecting admin-only endpoints"""

    @wraps(func)
    def check_admin_status(*args, **kwargs):
        current_user_email = get_jwt_identity()
        user = User.get_by_email(current_user_email)
        if not user.is_admin:
            return jsonify(message='You do not have permission to perform this action'), 403
        return func(*args, **kwargs)
    return check_admin_status
