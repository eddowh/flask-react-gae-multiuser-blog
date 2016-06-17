# -*- coding: utf-8 -*-

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
        return {
            'subject': post.subject,
            'content': post.content,
            'created': datetime.strftime(post.created, TIME_FMT),
            'last_modified': datetime.strftime(post.last_modified, TIME_FMT),
        }


@api.resource('/posts/')
class BlogPostsAPI(Resource, PostViewMixin):

    def get(self):
        posts = Post.query().order(-Post.created)
        return [self.get_post_context(p) for p in posts]


@api.resource('/posts/<int:post_id>/')
class BlogPostAPI(Resource, PostViewMixin):

    def _get_key(self, post_id):
        key = ndb.Key('Post', int(post_id),
                      parent=blog_key())
        return key

    def get(self, post_id):
        key = self._get_key(post_id)
        post = key.get()

        if post:
            return self.get_post_context(post)

    def delete(self, post_id):
        key = self._get_key(post_id)
        key.delete()
        return None, 204


@api.resource('/newpost/')
class NewPostAPI(Resource, PostViewMixin):

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
