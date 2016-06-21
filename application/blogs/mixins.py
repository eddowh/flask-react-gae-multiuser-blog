# -*- coding: utf-8 -*-

from collections import OrderedDict
from datetime import datetime

from flask_restful import abort
from google.appengine.ext import ndb

import urls
from settings import TIME_FMT


class ReactionResourceMixin(object):

    def get_reaction_context(self, reaction):
        username = reaction.user.get().username
        post_id = reaction.post.get().key.integer_id()
        return OrderedDict([
            ('user', username),
            (
                'user_uri',
                urls.get_user_uri(username)
            ),
            (
                'post_uri',
                urls.get_user_blogpost_uri(username=username, post_id=post_id)
            ),
            ('type', reaction.type),
            ('timestamp', datetime.strftime(reaction.timestamp, TIME_FMT)),
        ])

    def get_reactions_context(self, reactions):
        return [
            self.get_reaction_context(reaction)
            for reaction in reactions
        ]


class CommentResourceMixin(object):

    def get_comment_by_id_or_404(self, comment_id):
        key = ndb.Key('Comment', int(comment_id))
        comment = key.get()
        if comment is None:
            abort(404, status=404,
                  message="A comment with that ID does not exist.")
        else:
            return comment

    def get_comment_context(self, comment):
        username = comment.user.get().username
        post_id = comment.post.get().key.integer_id()
        comment_id = comment.key.integer_id()
        return OrderedDict([
            ('id', comment_id),
            (
                'uri',
                urls.get_user_blogpost_comment_uri(username=username,
                                                   post_id=post_id,
                                                   comment_id=comment_id)
            ),
            ('user', username),
            (
                'user_uri',
                urls.get_user_uri(username)
            ),
            (
                'post_uri',
                urls.get_user_blogpost_uri(username=username, post_id=post_id)
            ),
            ('content', comment.content),
            ('likes_count', comment.likes.count()),
            (
                'likes_uri',
                '',  # TODO
            ),
            ('replies_count', comment.replies.count()),
            (
                'replies_uri',
                '',  # TODO
            ),
            ('created', datetime.strftime(comment.created, TIME_FMT)),
            ('modified', datetime.strftime(comment.modified, TIME_FMT)),
        ])

    def get_comments_context(self, comments):
        return [
            self.get_comment_context(comment)
            for comment in comments
        ]


class PostResourceMixin(ReactionResourceMixin):

    def get_post_by_id_or_404(self, post_id):
        key = ndb.Key('Post', int(post_id))
        post = key.get()
        if post is None:
            abort(404, status=404,
                  message="A post with that ID does not exist.")
        else:
            return post

    def get_post_context(self, post):
        username = post.author.get().username
        post_id = post.key.integer_id()
        return OrderedDict([
            ('author', username),
            ('id', post_id),
            (
                'uri',
                urls.get_user_blogpost_uri(username=username, post_id=post_id)
            ),
            ('subject', post.subject),
            ('content', post.content),
            ('tags', sorted([pt.tag.get().name for pt in post.tags])),
            ('reactions_count', post.reactions.count()),
            (
                'reactions_uri',
                urls.get_user_blogpost_reactions_uri(username=username,
                                                     post_id=post_id)
            ),
            ('comments_count', post.comments.count()),
            (
                'comments_uri',
                urls.get_user_blogpost_comments_uri(username=username,
                                                    post_id=post_id)
            ),
            ('created', datetime.strftime(post.created, TIME_FMT)),
            ('last_modified', datetime.strftime(post.last_modified, TIME_FMT)),
        ])


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
