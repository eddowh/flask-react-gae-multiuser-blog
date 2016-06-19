# -*- coding: utf-8 -*-

from collections import OrderedDict
from datetime import datetime

from google.appengine.ext import ndb

from settings import TIME_FMT
import urls

from blogs.models import Comment, Post, Reaction
from blogs.mixins import (
    CommentDeleteMixin, PostDeleteMixin
)


class UserResourceMixin(object):

    def get_user_base_context(self, user):
        username = user.username
        return OrderedDict([
            ("username", username),
            ("id", user.key.integer_id()),
            ("uri", urls.get_user_uri(username)),
            ("email", user.email),
            ("full_name", user.full_name),
            ("bio", user.bio),
            ("blogsposts_count", Post.query(Post.author == user.key).count()),
            (
                "blogposts_uri",
                urls.get_posts_uri(username=username)
            ),
            ("is_active", user.is_active),
            ("is_admin", user.is_admin),
            ("joined", datetime.strftime(user.joined, TIME_FMT)),
            ("last_updated", datetime.strftime(user.last_updated, TIME_FMT)),
        ])


class UserDeleteMixin(PostDeleteMixin, CommentDeleteMixin):

    def delete_cascade(self, user):
        # delete comments
        user_comments = Comment.query(Comment.user == user.key)
        CommentDeleteMixin.delete_cascade_multi(self, user_comments)
        # delete posts
        user_posts = Post.query(Post.author == user.key)
        for post in user_posts:
            post.delete_cascade()
        # delete reactions
        user_reactions = Reaction.query(Reaction.user == user.key)
        ndb.delete_multi(user_reactions.fetch(keys_only=True))
        # finally, the user itself
        user.key.delete()
