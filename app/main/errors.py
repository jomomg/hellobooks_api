"""Custom error handlers"""

from flask import jsonify
from . import main


@main.app_errorhandler(400)
def bad_request(e):
    return jsonify(message='The server did not understand the request'), 400


@main.app_errorhandler(404)
def not_found(e):
    return jsonify(message='The requested resource was not found')


@main.app_errorhandler(500)
def internal_server_error(e):
    return jsonify(message='The server experienced an error'), 500
