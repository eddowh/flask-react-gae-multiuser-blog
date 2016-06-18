# -*- coding: utf-8 -*-

from collections import OrderedDict
from datetime import datetime

from flask import Blueprint, g, request
from flask_restful import Api, Resource
from google.appengine.ext import ndb

from settings import ROOT_URL, TIME_FMT
from auth import auth
from users.models import User


api = Api(Blueprint('users', __name__))


def user_key(name='default'):
    return ndb.Key('users', name)


class UserResourceMixin(object):

    def get_user_base_context(self, user):
        return OrderedDict([
            ("username", user.username),
            ("id", user.key.integer_id()),
            ("uri", api.url_for(UserAPI, username=user.username)),
            ("email", user.email),
            ("full_name", user.full_name),
            ("is_active", user.is_active),
            ("is_admin", user.is_admin),
            ("date_joined", datetime.strftime(user.date_joined, TIME_FMT)),
            ("date_updated", datetime.strftime(user.date_updated, TIME_FMT)),
        ])


@api.resource('/')
class UsersAPI(Resource, UserResourceMixin):

    def get(self):
        users = User.query()
        users_resp = []
        for user in users:
            resp = self.get_user_base_context(user)
            resp['uri'] = ROOT_URL + \
                api.url_for(UserAPI, username=user.username)
            users_resp.append(resp)
        return users_resp


@api.resource('/<string:username>/')
class UserAPI(Resource, UserResourceMixin):

    def get(self, username):
        user = User.query(getattr(User, 'username') == username).get()
        if not user:
            return None, 404
        else:
            return self.get_user_base_context(user)

    @auth.login_required
    def put(self, username):
        user = User.query(User.username == username).get()
        if not user:
            return None, 404
        if g.user != user:
            return None, 403

        is_modified = False
        data = request.get_json()

        for field in ['username', 'email']:
            mod_val = data.get(field, getattr(user, field))
            if mod_val and mod_val != getattr(user, field):
                if User.query(getattr(User, field) == mod_val).get() is None:
                    setattr(user, field, mod_val)
                    is_modified = True
                else:
                    return None, 400

        full_name = data.get('full_name')
        if full_name and full_name != user.full_name:
            user.full_name = full_name
            is_modified = True

        if is_modified:
            user.date_updated = datetime.now()
            user.put()
        return (
            None,
            201,
            {'Location': api.url_for(UserAPI, username=user.username)}
        )


@api.resource('/<string:username>/deactivate/')
class UserDeactivateAPI(Resource):

    @auth.login_required
    def put(self, username):
        user = User.query(User.username == username).get()
        if not user:
            return None, 404
        if g.user != user:
            return None, 403

        password = request.get_json().get('password', '')
        if not user.verify_password(password):
            return None, 401
        else:
            user.is_active = False
            user.date_updated = datetime.now()
            user.put()
            return None, 201


@api.resource('/<string:username>/delete/')
class UserDeleteAPI(Resource):

    @auth.login_required
    def post(self, username):
        user = User.query(User.username == username).get()
        if not user:
            return None, 404
        if g.user != user:
            return None, 403
        password = request.get_json().get('password', '')
        if not user.verify_password(password):
            return None, 401
        else:
            user.key.delete()
            return None, 204


@api.resource('/newuser/')
class NewUserAPI(Resource):

    def post(self):
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        full_name = data.get('full_name', '')

        can_be_created = (
            username is not None and
            email is not None and
            password is not None and
            User.query(User.username == username).get() is None and
            User.query(User.email == email).get() is None)
        if can_be_created:
            parent = user_key()
            new_user = User(parent=parent,
                            username=username,
                            email=email,
                            full_name=full_name)
            new_user.hash_password(password)
            new_user.put()
            return (
                None,
                201,
                {'Location': api.url_for(UserAPI, username=new_user.username)}
            )
        else:
            return None, 400  # Bad Request
