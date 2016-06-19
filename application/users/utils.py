# -*- coding: utf-8 -*-

from flask_restful import abort

from users.models import User


def get_user_by_username_or_404(username):
    user = User.query(User.username == username).get()
    if user is None:
        abort(404, message="A user with that username does not exist.")
    else:
        return user
