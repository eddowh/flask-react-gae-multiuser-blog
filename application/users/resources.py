# -*- coding: utf-8 -*-

from datetime import datetime

from flask import Blueprint, g, request
from flask_restful import Api, Resource
from google.appengine.ext import ndb

from auth import basic_auth

from users.mixins import UserDeleteMixin, UserResourceMixin
from users.utils import get_user_by_username_or_404
from users.models import User

api = Api(Blueprint('users', __name__))


def user_key(name='default'):
    return ndb.Key('users', name)


@api.resource('/')
class UsersAPI(Resource, UserResourceMixin):

    def get(self):
        users = User.query()
        return [self.get_user_base_context(u) for u in users]


@api.resource('/<string:username>/')
class UserAPI(Resource, UserResourceMixin):

    def get(self, username):
        user = get_user_by_username_or_404(username)
        return self.get_user_base_context(user)

    @basic_auth.login_required
    def put(self, username):
        user = get_user_by_username_or_404(username)
        if g.user != user:
            return None, 403

        is_modified = False
        data = request.get_json()

        # unique fields, hence the query to check
        for field in ['username', 'email']:
            mod_val = data.get(field, getattr(user, field))
            if mod_val and mod_val != getattr(user, field):
                if User.query(getattr(User, field) == mod_val).get() is None:
                    setattr(user, field, mod_val)
                    is_modified = True
                else:
                    return None, 400

        # non-unique fields
        for field in ['full_name', 'bio']:
            mod_val = data.get(field, getattr(user, field))
            if mod_val and mod_val != getattr(user, field):
                setattr(user, field, mod_val)
                is_modified = True

        if is_modified:
            user.last_updated = datetime.now()
            user.put()
        return (
            None,
            201,
            {'Location': api.url_for(UserAPI, username=user.username)}
        )


@api.resource('/<string:username>/password_change/')
class UserPasswordChangeAPI(Resource):

    @basic_auth.login_required
    def put(self, username):
        user = get_user_by_username_or_404(username)
        if g.user != user:
            return None, 403

        old_password = request.get_json().get('old_password', '')
        if not user.verify_password(old_password):
            return None, 401

        # don't commit changes if passwords are the same
        new_password = request.get_json().get('new_password', '')
        if old_password == new_password:
            return None, 204

        else:
            user.hash_password(new_password)
            user.last_updated = datetime.now()
            user.put()
            return None, 201


@api.resource('/<string:username>/deactivate/')
class UserDeactivateAPI(Resource):

    @basic_auth.login_required
    def put(self, username):
        user = get_user_by_username_or_404(username)
        if g.user != user:
            return None, 403

        password = request.get_json().get('password', '')
        if not user.verify_password(password):
            return None, 401
        else:
            user.is_active = False
            user.last_updated = datetime.now()
            user.put()
            return None, 201


@api.resource('/<string:username>/delete/')
class UserDeleteAPI(Resource, UserDeleteMixin):

    @basic_auth.login_required
    def post(self, username):
        user = get_user_by_username_or_404(username)
        if g.user != user:
            return None, 403
        password = request.get_json().get('password', '')
        if not user.verify_password(password):
            return None, 401
        else:
            UserDeleteMixin.delete_cascade(self, user)
            return None, 204


@api.resource('/newuser/')
class NewUserAPI(Resource):

    def post(self):
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        full_name = data.get('full_name', '')
        bio = data.get('bio', '')

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
                            full_name=full_name,
                            bio=bio)
            new_user.hash_password(password)
            new_user.put()
            return (
                None,
                201,
                {'Location': api.url_for(UserAPI, username=new_user.username)}
            )
        else:
            return None, 400  # Bad Request
