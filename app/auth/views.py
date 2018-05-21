"""Contains all authentication views"""

import re
import datetime
from flask import request, jsonify, current_app
from flask_jwt_extended import (create_access_token,
                                jwt_required, get_jwt_identity,
                                get_raw_jwt, jwt_optional)
from werkzeug.security import generate_password_hash
from flask_mail import Message

from app.models import User
from app.app import jwt, mail
from . import auth
from app.endpoints import Auth

blacklist = set()
temp = []


@auth.route(Auth.REGISTER, methods=['POST'])
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
        if email in current_app.config['ADMIN']:
            new_user.is_admin = True
        new_user.save()

        return jsonify({'message': 'Successful registration'}), 201
    else:
        return jsonify({'message': 'This account has already been registered'}), 409


@auth.route(Auth.LOGIN, methods=['POST'])
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


@auth.route(Auth.RESET_PASSWORD, methods=['POST'])
@jwt_optional
def reset_password():
    """Reset a user's password"""

    email = request.data.get('email')
    new_pass = request.data.get('password')
    token_id = get_jwt_identity()

    if token_id:
        user = User.get_by_email(token_id)
        if not user:
            return jsonify(message='The reset code provided is invalid'), 400
        else:
            pass_hash = [item for item in temp if item[0] == user.email][0][1]
            user.password = pass_hash
            user.save()
            revoke_token()
            for record in temp:
                if record[0] == user.email:
                    temp.remove(record)
            return jsonify(message='Your password has been reset'), 200
    else:
        if not email:
            return jsonify(message='You must provide an email to reset the password'), 400
        if not new_pass:
            return jsonify(message='You must provide a new password'), 400

        reset_token = create_access_token(identity=email,
                                          expires_delta=datetime.timedelta(minutes=10))
        temp.append((email, generate_password_hash(new_pass)))
        reset_msg = Message(subject='Password Reset')
        reset_msg.add_recipient(email)
        reset_msg.html = '<p>To reset your password, click on the following link: ' \
                         '<a href={}/api/v1/auth/reset-password?token={}>Reset Password' \
                         '</a>. Keep in mind the link is only valid for ' \
                         '10 minutes</p>'.format(current_app.config['DOMAIN'], reset_token)
        mail.send(reset_msg)
        return jsonify(message='A reset code has been sent to the email you provided.'), 200


@auth.route(Auth.LOGOUT, methods=['POST'])
@jwt_required
def logout():
    """Log a user out by revoking access token"""

    revoke_token()
    return jsonify({'message': 'Successfully logged out'}), 200


@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(token):
    """Callback for checking if a token is blacklisted"""

    jti = token['jti']
    return jti in blacklist


def revoke_token():
    jti = get_raw_jwt()['jti']
    blacklist.add(jti)
    revoked = True
    return revoked
