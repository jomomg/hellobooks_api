"""views.py: Authentication views"""

import re
from flask import request, jsonify
from flask_jwt_extended import (create_access_token,
                                get_jwt_identity,
                                jwt_required,
                                get_raw_jwt)

from app.models import User, blacklist
from . import auth


@auth.route('/api/v1/auth/register', methods=['POST'])
def register_user():
    """Register a new user"""

    if request.method == 'POST':
        email = request.data['email']
        password = request.data['password']
        user = User.get_by_email(email)

        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$', email):
            return jsonify({'message': 'Please enter a valid email address'}), 202

        if not re.match(r'^[a-zA-Z0-9*&#!@^._%+-]', password):
            return jsonify({'message': 'Please enter a valid password'})

        if not user:
            new_user = User()
            new_user.email = email
            new_user.set_password(password)
            new_user.save()

            response = jsonify({'message': 'Successful registration'})
            response.status_code = 201
            return response

        else:
            response = jsonify({'message': 'This account has already been registered'})
            response.status_code = 202
            return response


@auth.route('/api/v1/auth/login', methods=['POST'])
def login_user():
    """Log a user in"""

    if request.method == 'POST':
        email = request.data['email']
        password = request.data['password']
        user = User.get_by_email(email)

        if user and user.check_password(password):
            access_token = create_access_token(identity=email)
            response = {'message': 'Successful login', 'access_token': access_token}
            return jsonify(response), 200

        else:
            response = jsonify({'message': 'Invalid email or password'})
            response.status_code = 401
            return response


@auth.route('/api/v1/auth/reset-password', methods=['POST'])
@jwt_required
def reset_password():
    """Reset a user's password"""

    email = get_jwt_identity()
    current_user = User().get_by_email(email)
    new_password = request.data['password']

    current_user.set_password(new_password)
    response = jsonify({'message': 'Password reset successful'})
    response.status_code = 200
    return response


@auth.route('/api/v1/auth/logout', methods=['POST'])
@jwt_required
def logout():
    """Log a user out by revoking access token"""

    jti = get_raw_jwt()['jti']
    blacklist.add(jti)
    response = jsonify({'message': 'Successfully logged out'})
    response.status_code = 200
    return response
