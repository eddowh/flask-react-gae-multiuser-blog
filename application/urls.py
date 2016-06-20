# -*- coding: utf-8 -*-

from settings import ROOT_URL

import blogs.resources
import users.resources


def get_user_uri(username):
    return ROOT_URL + users.resources.api.url_for(
        users.resources.UserAPI, username=username
    )


def get_user_blogpost_reactions_uri(username, post_id):
    return ROOT_URL + blogs.resources.api.url_for(
        blogs.resources.UserBlogPostReactionsAPI,
        username=username, post_id=post_id
    )


def get_user_blogpost_uri(username, post_id):
    return ROOT_URL + blogs.resources.api.url_for(
        blogs.resources.UserBlogPostAPI,
        username=username, post_id=post_id
    )


def get_user_blogposts_uri(username):
    return ROOT_URL + blogs.resources.api.url_for(
        blogs.resources.UserBlogPostsAPI, username=username
    )


def get_user_reactions_uri(username):
    return ROOT_URL + blogs.resources.api.url_for(
        blogs.resources.UserReactionsAPI, username=username
    )
