"""Contains all authentication views"""


import datetime
from flask import request, jsonify, current_app
from flask_jwt_extended import (create_access_token,
                                jwt_required, get_jwt_identity,
                                get_raw_jwt, create_refresh_token)
from werkzeug.security import generate_password_hash
from flask_mail import Message

from app.models import User
from app.app import jwt, mail
from . import auth
from app.endpoints import Auth
from app.decorators import admin_required, validate_email_password
from app.jwt_extensions import refresh_jwt_optional

blacklist = set()
temp = []


@auth.route(Auth.REGISTER, methods=['POST'])
@validate_email_password
def register_user():
    """Register a new user"""

    first_name = request.data.get('first_name')
    last_name = request.data.get('last_name')
    email = request.data.get('email')
    password = request.data.get('password')
    confirm_password = request.data.get('confirm_password')

    user = User.get_by_email(email)

    if not email or not password or not confirm_password or not first_name or not last_name:
        return jsonify(
            msg='An email, password, confirm password and first and last name are needed to register'
            ), 400

    if not user:
        new_user = User()
        new_user.email = email
        if password == confirm_password:
            new_user.set_password(password)
        else:
            return jsonify(msg='The passwords you provided do not match'), 400
        if email in current_app.config['ADMIN']:
            new_user.is_admin = True
        new_user.first_name = first_name
        new_user.last_name = last_name
        new_user.save()

        return jsonify({'msg': 'You have successfully registered'}), 201
    else:
        return jsonify({'msg': 'This account has already been registered'}), 409


@auth.route(Auth.REGISTER, methods=['PUT', 'DELETE'])
@jwt_required
@admin_required
def upgrade_downgrade_user():
    """Upgrade or downgrade a user from a normal user to admin"""

    email = request.data.get('email')
    if not email:
        return jsonify(msg='Please provide a user email'), 400
    user = User.get_by_email(email)
    if not user:
        return jsonify(msg='The specified user could not be found'), 404

    if request.method == 'PUT':
        if user.is_admin:
            return jsonify(msg='This user is already an admin'), 409
        else:
            user.is_admin = True
            user.save()
            return jsonify(msg='The user has been upgraded to an admin'), 200

    elif request.method == 'DELETE':
        if not user.is_admin:
            return jsonify(msg='The user does not have admin privileges')
        else:
            user.is_admin = False
            user.save()
            return jsonify(msg='The user has been downgraded')


@auth.route(Auth.LOGIN, methods=['POST'])
def login_user():
    """Log a user in"""

    if request.method == 'POST':
        email = request.data.get('email')
        password = request.data.get('password')
        if not email or not password:
            return jsonify(msg='Please provide an email and a password'), 400
        user = User.get_by_email(email)

        if user and user.check_password(password):
            access_token = create_access_token(identity=email)
            response = {'msg': 'Successful login', 'access_token': access_token}
            return jsonify(response), 200

        else:
            return jsonify({'msg': 'Invalid email or password'}), 401


@auth.route(Auth.RESET_PASSWORD, methods=['POST', 'GET'])
@refresh_jwt_optional
@validate_email_password
def reset_password():
    """Reset a user's password"""

    email = request.data.get('email')
    new_pass = request.data.get('password')
    token_id = get_jwt_identity()

    if token_id:
        user = User.get_by_email(token_id)
        if not user:
            return jsonify(msg='The reset code provided is invalid'), 400
        else:
            pass_hash = [item for item in temp if item[0] == user.email][0][1]
            user.password = pass_hash
            user.save()
            revoke_token()
            for record in temp:
                if record[0] == user.email:
                    temp.remove(record)
            return jsonify(msg='Your password has been reset'), 200
    else:
        if not email:
            return jsonify(msg='You must provide an email to reset the password'), 400
        if not new_pass:
            return jsonify(msg='You must provide a new password'), 400

        reset_token = create_refresh_token(identity=email,
                                           expires_delta=datetime.timedelta(minutes=10))
        temp.append((email, generate_password_hash(new_pass)))
        reset_msg = Message(subject='Password Reset')
        reset_msg.add_recipient(email)
        reset_msg.html = '<p>To reset your password, click on the following link: ' \
                         '<a href={}/api/v1/auth/reset-password?token={}>Reset Password' \
                         '</a>. Keep in mind the link is only valid for ' \
                         '10 minutes</p>'.format(current_app.config['DOMAIN'], reset_token)
        mail.send(reset_msg)
        return jsonify(msg='A reset code has been sent to the email you provided.'), 200


@auth.route(Auth.LOGOUT, methods=['POST'])
@jwt_required
def logout():
    """Log a user out by revoking access token"""

    revoke_token()
    return jsonify({'msg': 'Successfully logged out'}), 200


@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(token):
    """Callback for checking if a token is blacklisted"""

    jti = token['jti']
    return jti in blacklist

@jwt.user_claims_loader
def add_claims_to_token(identity):
    is_admin = False
    user = User.get_by_email(identity)
    if user.is_admin:
        is_admin = True
    return {
        'first_name': user.first_name,
        'last_name': user.last_name,
        'is_admin': is_admin
    }


def revoke_token():
    jti = get_raw_jwt()['jti']
    blacklist.add(jti)
    revoked = True
    return revoked
