# -*- coding: utf-8 -*-

from flask import g, make_response, jsonify
from flask_httpauth import HTTPBasicAuth

from users.models import User


auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(username, password):
    user = User.query(User.username == username).get()
    if not user or not user.verify_password(password):
        return False
    # Facebook style, make user active again
    user.is_active = True
    user.put()
    g.user = user
    return True


@auth.error_handler
def unauthorized():
    return make_response(jsonify({
        'error': 'Permission denied'
    }), 401)
