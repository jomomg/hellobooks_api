from . import auth

from flask import request, jsonify
from app.models import User, blacklist
from flask_jwt_extended import (create_access_token,
                                get_jwt_identity,
                                jwt_required,
                                get_raw_jwt)


@auth.route('/api/v1/auth/register', methods=['POST'])
def register_user():
    """Registers a new user"""

    if request.method == 'POST':
        email = request.data['email']
        password = request.data['password']
        user = User.get_by_email(email)

        if not user:
            new_user = User()
            new_user.email = email
            new_user.set_password(password)
            new_user.save()

            response = jsonify({'message': 'successful registration'})
            response.status_code = 201
            return response

        else:
            response = jsonify({'message': 'you are already registered'})
            response.status_code = 202
            return response


@auth.route('/api/v1/auth/login', methods=['POST'])
def login_user():
    """Logs a user in"""

    if request.method == 'POST':
        email = request.data['email']
        password = request.data['password']
        user = User.get_by_email(email)

        if user and user.check_password(password):
            access_token = create_access_token(identity=email)
            response = {'message': 'successful login', 'access_token': access_token}
            return jsonify(response), 200

        else:
            response = jsonify({'message': 'invalid email or password'})
            response.status_code = 401
            return response


@auth.route('/api/v1/auth/reset-password', methods=['POST'])
@jwt_required
def reset_password():
    """resets a user's password"""

    email = get_jwt_identity()
    current_user = User().get_by_email(email)
    new_password = request.data['password']

    current_user.set_password(new_password)
    response = jsonify({'message': 'password reset successful'})
    response.status_code = 200
    return response


@auth.route('/api/v1/auth/logout', methods=['POST'])
@jwt_required
def logout():
    """logs a user out by revoking access token"""

    jti = get_raw_jwt()['jti']
    blacklist.add(jti)
    response = jsonify({'message': 'successfully logged out'})
    response.status_code = 200
    return response
