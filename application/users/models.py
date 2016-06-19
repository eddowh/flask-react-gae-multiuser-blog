# -*- coding: utf-8 -*-

from passlib.apps import custom_app_context as pwd_context

from google.appengine.ext import ndb


class User(ndb.Model):
    username = ndb.StringProperty(required=True, indexed=True)
    email = ndb.StringProperty(required=True)
    password_hash = ndb.StringProperty(required=True)
    full_name = ndb.StringProperty()
    bio = ndb.TextProperty()
    is_active = ndb.BooleanProperty(default=True)
    is_admin = ndb.BooleanProperty(default=False)
    joined = ndb.DateTimeProperty(auto_now_add=True)
    # avoid using auto_now because it updates when you're authenticated
    # with flask-httpauth even when nothing has been committed to the DB
    last_updated = ndb.DateTimeProperty(auto_now_add=True)

    def hash_password(self, pwd):
        """Takes a plain password, and stores a hash.

        Called during initial registration or password change.

        :param pwd: password
        :type pwd: str
        """
        self.password_hash = pwd_context.encrypt(pwd)

    def verify_password(self, pwd):
        """Verifies the password against the stored hash.

        :param pwd: password
        :type pwd: str
        :returns: True if password is correct, False otherwise.
        :rtype: bool
        """
        return pwd_context.verify(pwd, self.password_hash)
