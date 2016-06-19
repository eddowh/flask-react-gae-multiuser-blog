# -*- coding: utf-8 -*-

from google.appengine.ext import ndb


class CommentReplyDeleteMixin(object):

    def delete_cascade(self, reply):
        ndb.delete_multi(reply.likes.fetch(keys_only=True))
        reply.key.delete()

    def delete_cascade_multi(self, replies):
        for reply in replies:
            self.delete_cascade(reply)


class CommentDeleteMixin(CommentReplyDeleteMixin):

    def delete_cascade(self, comment):
        CommentReplyDeleteMixin.delete_cascade_multi(self, comment.replies)
        ndb.delete_multi(comment.likes.fetch(keys_only=True))
        comment.key.delete()

    def delete_cascade_multi(self, comments):
        for comment in comments:
            self.delete_cascade(comment)


class PostDeleteMixin(CommentDeleteMixin):

    def delete_cascade(self, post):
        CommentDeleteMixin.delete_cascade_multi(self, post.comments)
        ndb.delete_multi(post.tags.fetch(keys_only=True))
        ndb.delete_multi(post.reactions.fetch(keys_only=True))
        post.key.delete()

    def delete_cascade_multi(self, posts):
        for post in posts:
            self.delete_cascade(post)
