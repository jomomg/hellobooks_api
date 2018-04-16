"""Contains all authentication views"""

import re
from flask import request, jsonify
from flask_jwt_extended import (create_access_token,
                                jwt_required,
                                get_raw_jwt)

from app.models import User
from app.app import blacklist
from . import auth


@auth.route('/api/v1/auth/register', methods=['POST'])
def register_user():
    """Register a new user"""

    email = request.data['email']
    password = request.data['password']
    user = User.get_by_email(email)

    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$', email):
        return jsonify({'message': 'Please enter a valid email address'}), 400

    if not re.match(r'^[a-zA-Z0-9*&#!@^._%+-]', password):
        return jsonify({'message': 'Please enter a valid password'}), 400

    if not user:
        new_user = User()
        new_user.email = email
        new_user.set_password(password)
        new_user.save()

        return jsonify({'message': 'Successful registration'}), 201
    else:
        return jsonify({'message': 'This account has already been registered'}), 409


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
            return jsonify({'message': 'Invalid email or password'}), 401


@auth.route('/api/v1/auth/reset-password', methods=['POST'])
def reset_password():
    """Reset a user's password"""

    email = request.data['email']
    user = User().get_by_email(email)
    if not user:
        return jsonify({'message': 'The user specified was not found'}), 404
    new_password = request.data['password']

    user.set_password(new_password)
    return jsonify({'message': 'Password reset successful'}), 200


@auth.route('/api/v1/auth/logout', methods=['POST'])
@jwt_required
def logout():
    """Log a user out by revoking access token"""

    jti = get_raw_jwt()['jti']
    blacklist.add(jti)
    return jsonify({'message': 'Successfully logged out'}), 200
