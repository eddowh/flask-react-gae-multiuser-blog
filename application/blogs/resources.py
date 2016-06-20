# -*- coding: utf-8 -*-

from flask import Blueprint, request, g
from flask_restful import Api, Resource
from google.appengine.ext import ndb

from auth import basic_auth

from users.utils import get_user_by_username_or_404
from blogs.mixins import (
    ReactionsResourceMixin, PostResourceMixin
)
from blogs.models import Post, Reaction


api = Api(Blueprint('blogs', __name__), catch_all_404s=False)


def post_key(name='default'):
    return ndb.Key('posts', name)


# for admin and dev purposes
@api.resource('/posts/')
class BlogPostsAPI(Resource, PostResourceMixin):

    def get(self):
        posts = Post.query().order(-Post.created)
        return [self.get_post_context(p) for p in posts]


@api.resource('/<string:username>/posts/')
class UserBlogPostsAPI(Resource, PostResourceMixin):

    def get(self, username):
        user = get_user_by_username_or_404(username)
        posts = Post.query(Post.author == user.key).order(-Post.created)
        return [self.get_post_context(p) for p in posts]


@api.resource('/<string:username>/reactions/')
class UserReactionsAPI(Resource, ReactionsResourceMixin):

    def get(self, username):
        user = get_user_by_username_or_404(username)
        reactions = Reaction \
            .query(Reaction.user == user.key) \
            .order(-Reaction.timestamp)
        return self.get_reactions_context(reactions)


@api.resource('/<string:username>/posts/<int:post_id>/')
class UserBlogPostAPI(Resource, PostResourceMixin):

    def get(self, username, post_id):
        post = self.get_post_by_id_or_404(post_id)
        print(post)
        return self.get_post_context(post)

    def put(self, username, post_id):
        # initialize variables
        post = self.get_post_by_id_or_404(post_id)
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

    def delete(self, username, post_id):
        post = self.get_post_by_id_or_404(post_id)
        post.key.delete()
        return None, 204


@api.resource('/<string:username>/posts/<int:post_id>/react/')
class UserReactAPI(Resource, PostResourceMixin):

    @basic_auth.login_required
    def post(self, username, post_id):
        post = self.get_post_by_id_or_404(post_id)
        data = request.get_json()

        reaction_type = data.get('type')
        if reaction_type:
            reaction = Reaction(user=g.user.key,
                                post=post.key,
                                type=reaction_type)
            reaction.put()
        return None, 201


@api.resource('/<string:username>/posts/<int:post_id>/reactions/')
class UserBlogPostReactionsAPI(Resource,
                               PostResourceMixin, ReactionsResourceMixin):

    def get(self, username, post_id):
        post = self.get_post_by_id_or_404(post_id)
        return self.get_reactions_context(post.reactions)


@api.resource('/<string:username>/posts/<int:post_id>/addtags/')
class AddPostTagAPI(Resource):

    def post(self, username, post_id):
        post = self.get_post_by_id_or_404(post_id)
        if post is None:
            return None, 404
        tags = request.get_json().get('tags', [])
        if len(tags) > 0:
            post.add_tags(tags)
        return None, 201


@api.resource('/newpost/')
class NewPostAPI(Resource):

    @basic_auth.login_required
    def post(self):
        data = request.get_json()
        subject = data.get('subject')
        content = data.get('content')
        tags = data.get('tags', [])

        user = g.user
        if subject and content:
            new_post = Post(author=user.key,
                            subject=subject,
                            content=content)
            # store it in DB
            new_post.put()
            new_post.add_tags(tags)
            new_post_key = new_post.key
            return (
                {'key': new_post_key.integer_id()},
                201,
                {'Location': api.url_for(UserBlogPostAPI,
                                         username=user.username,
                                         post_id=new_post_key.integer_id())},
            )
        else:
            return None, 400  # Bad Request
