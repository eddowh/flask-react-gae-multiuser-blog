# -*- coding: utf-8 -*-

from collections import OrderedDict
from datetime import datetime

from flask import Blueprint, request
from flask_restful import Api, Resource
from google.appengine.ext import ndb

from settings import TIME_FMT
from blogs.models import Post


api = Api(Blueprint('blogs', __name__), catch_all_404s=False)


def blog_key(name='default'):
    return ndb.Key('blogs', name)


class PostViewMixin(object):

    def get_post_context(self, post):
        return OrderedDict([
            ('subject', post.subject),
            ('content', post.content),
            ('created', datetime.strftime(post.created, TIME_FMT)),
            ('last_modified', datetime.strftime(post.last_modified, TIME_FMT)),
        ])


@api.resource('/posts/')
class BlogPostsAPI(Resource, PostViewMixin):

    def get(self):
        posts = Post.query().order(-Post.created)
        return [self.get_post_context(p) for p in posts]


@api.resource('/posts/<int:post_id>/')
class BlogPostAPI(Resource, PostViewMixin):

    def _get_post(self, post_id):
        key = ndb.Key('Post', int(post_id),
                      parent=blog_key())
        return key.get()

    def get(self, post_id):
        post = self._get_post(post_id)
        if post:
            return self.get_post_context(post)

    def put(self, post_id):
        # initialize variables
        post = self._get_post(post_id)
        data = request.get_json()
        is_modified = False

        for field in ['subject', 'content']:
            updated_val = data.get(field)
            if updated_val and updated_val != getattr(post, field):
                setattr(post, field, updated_val)
                is_modified = True

        # only update when changes are detected in subject/content
        # somehow `last_modified` is automatically updated...
        if is_modified:
            post.put()
        return None, 201

    def delete(self, post_id):
        post = self._get_post(post_id)
        post.delete()
        return None, 204


@api.resource('/newpost/')
class NewPostAPI(Resource):

    def post(self):
        data = request.get_json()
        subject = data.get('subject')
        content = data.get('content')

        if subject and content:
            parent = blog_key()
            new_post = Post(parent=parent,
                            subject=data['subject'],
                            content=data['content'])
            new_post.put()
            return {'key': new_post.key.integer_id()}, 201
        else:
            return None, 400  # Bad Request
