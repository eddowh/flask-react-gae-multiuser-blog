# -*- coding: utf-8 -*-

from collections import OrderedDict
from datetime import datetime

from flask import Blueprint, request, g
from flask_restful import Api, Resource
from google.appengine.ext import ndb

from auth import auth
from settings import ROOT_URL, TIME_FMT
from blogs.models import Post
from users.resources import api as users_api, UserAPI


api = Api(Blueprint('blogs', __name__), catch_all_404s=False)


def post_key(name='default'):
    return ndb.Key('posts', name)


class ReactionsResourceMixin(object):

    def get_reaction_context(self, reaction):
        username = reaction.user.get().username
        return OrderedDict([
            ('user', username),
            ('type', reaction.type),
            (
                'user_uri',
                ROOT_URL + users_api.url_for(UserAPI, username=username)
            ),
        ])

    def get_reactions_context(self, reactions):
        return [
            self.get_reaction_context(reaction)
            for reaction in reactions
        ]


class PostResourceMixin(ReactionsResourceMixin):

    def get_post_by_id(self, post_id):
        key = ndb.Key('Post', int(post_id))
        return key.get()

    def get_post_context(self, post):
        post_id = post.key.integer_id()
        return OrderedDict([
            ('id', post_id),
            (
                'uri',
                ROOT_URL + api.url_for(BlogPostAPI, post_id=post_id)
            ),
            ('author', post.author.get().username),
            ('subject', post.subject),
            ('content', post.content),
            ('tags', sorted([pt.tag.get().name for pt in post.tags])),
            ('reactions_count', post.reactions.count()),
            (
                'reactions_uri',
                ROOT_URL + api.url_for(BlogPostReactionsAPI, post_id=post_id)
            ),
            ('created', datetime.strftime(post.created, TIME_FMT)),
            ('last_modified', datetime.strftime(post.last_modified, TIME_FMT)),
        ])


@api.resource('/posts/')
class BlogPostsAPI(Resource, PostResourceMixin):

    def get(self):
        posts = Post.query().order(-Post.created)
        return [self.get_post_context(p) for p in posts]


@api.resource('/posts/<int:post_id>/')
class BlogPostAPI(Resource, PostResourceMixin):

    def get(self, post_id):
        post = self.get_post_by_id(post_id)
        if post:
            return self.get_post_context(post)
        else:
            return None, 404

    def put(self, post_id):
        # initialize variables
        post = self.get_post_by_id(post_id)
        is_modified = False

        data = request.get_json()
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
        post = self.get_post_by_id(post_id)
        post.key.delete()
        return None, 204


@api.resource('/posts/<int:post_id>/reactions/')
class BlogPostReactionsAPI(Resource,
                           PostResourceMixin, ReactionsResourceMixin):

    def get(self, post_id):
        post = self.get_post_by_id(post_id)
        return self.get_reactions_context(post.reactions)


@api.resource('/posts/<int:post_id>/addtags/')
class AddPostTagAPI(Resource):

    def post(self, post_id):
        post = self.get_post_by_id(post_id)
        tags = request.get_json().get('tags', [])
        post.add_tags(tags)


@api.resource('/newpost/')
class NewPostAPI(Resource):

    @auth.login_required
    def post(self):
        data = request.get_json()
        subject = data.get('subject')
        content = data.get('content')
        tags = data.get('tags', [])

        if subject and content:
            new_post = Post(author=g.user.key,
                            subject=subject,
                            content=content)
            # store it in DB
            new_post.put()
            new_post.add_tags(tags)
            new_post_key = new_post.key
            return (
                {'key': new_post_key.integer_id()},
                201,
                {'Location': api.url_for(BlogPostAPI,
                                         post_id=new_post_key.integer_id())},
            )
        else:
            return None, 400  # Bad Request
