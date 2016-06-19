# -*- coding: utf-8 -*-

from google.appengine.ext import ndb

from blogs.mixins import (
    CommentReplyDeleteMixin, CommentDeleteMixin, PostDeleteMixin
)
from users.models import User


class Post(ndb.Model, PostDeleteMixin):
    author = ndb.KeyProperty(kind=User, required=True)
    subject = ndb.StringProperty(required=True)
    content = ndb.TextProperty(required=True)
    is_draft = ndb.BooleanProperty(default=True)
    created = ndb.DateTimeProperty(auto_now_add=True)
    published = ndb.DateTimeProperty(auto_now_add=True)
    last_modified = ndb.DateTimeProperty(auto_now=True)

    @property
    def tags(self):
        return PostTag.query().filter(PostTag.post == self.key)

    @property
    def comments(self):
        return Comment.query(Comment.post == self.key)

    @property
    def reactions(self):
        return Reaction.query(Reaction.post == self.key)

    def add_tags(self, tags):
        """Associate a post with more tags.

        If tag doesn't exist in DB, create new ones.

        :param tags: tags in the form of array/list of strings
        :type tags: list (str)
        """
        # prefilter and remove duplicates
        tags = set(tags)
        for tag_name in tags:
            tag = Tag.query(Tag.name == tag_name).get()
            # if tag hasn't existed before, create a new tag in the DB
            # this also means that this tag has never been associated with
            # this post (or possibly any post yet) so create new post tag
            # with questions
            if tag is None:
                new_tag = Tag(name=tag_name)
                new_tag.put()
                tag_key = new_tag.key
                new_post_tag = PostTag(post=self.key, tag=tag_key)
                new_post_tag.put()
            else:
                tag_key = tag.key
                # if tag exists, there's a chance you might have associated
                # this post with a tag already, so in that case check for
                # whether tag has already existed, otherwise create!
                post_tag = self.tags.filter(Tag.key == tag_key).get()
                if post_tag is None:
                    new_post_tag = PostTag(post=self.key, tag=tag_key)
                    new_post_tag.put()

    def delete_cascade(self):
        PostDeleteMixin.delete_cascade(self, self)


class Tag(ndb.Model):
    name = ndb.StringProperty(indexed=True)

    @property
    def posts(self):
        return PostTag.query().filter(PostTag.tag == self.key)


class PostTag(ndb.Model):  # many-to-many via 'join table'
    post = ndb.KeyProperty(kind=Post, required=True)
    tag = ndb.KeyProperty(kind=Tag, required=True)


class Reaction(ndb.Model):
    user = ndb.KeyProperty(kind=User, required=True)
    post = ndb.KeyProperty(kind=Post, required=True)
    type = ndb.StringProperty(
        choices=[
            'like',
            'love',
            'amused',
            'surprised',
            'sad',
            'angry'
        ]
    )
    timestamp = ndb.DateTimeProperty(auto_now_add=True)


class Comment(ndb.Model, CommentDeleteMixin):
    user = ndb.KeyProperty(kind=User, required=True)
    post = ndb.KeyProperty(kind=Post, required=True)

    @property
    def replies(self):
        return CommentReply.query(CommentReply.comment == self.key)

    @property
    def likes(self):
        return Like.query(Like.comment == self.key)

    def delete_cascade(self):
        CommentDeleteMixin.delete_cascade(self, self)


class CommentReply(ndb.Model, CommentReplyDeleteMixin):
    user = ndb.KeyProperty(kind=User, required=True)
    comment = ndb.KeyProperty(kind=Comment, required=True)

    @property
    def likes(self):
        return Like.query(Like.reply == self.key)

    def delete_cascade(self):
        CommentReplyDeleteMixin.delete_cascade(self, self)


class Like(ndb.Model):
    user = ndb.KeyProperty(kind=User, required=True)
    comment = ndb.KeyProperty(kind=Comment, default=None)
    reply = ndb.KeyProperty(kind=Comment, default=None)
