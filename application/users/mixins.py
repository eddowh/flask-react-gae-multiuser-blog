# -*- coding: utf-8 -*-

from google.appengine.ext import ndb

from blogs.models import Comment, Post, Reaction
from blogs.mixins import (
    CommentDeleteMixin, PostDeleteMixin
)


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
