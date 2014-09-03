#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import os
import webapp2
import jinja2
from models import *
from webapp2 import Route
from google.appengine.api import users

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class GroupPostHandler(webapp2.RequestHandler):
  def get_comments(self, group_post_id):
    group_post = GroupPost.get(group_post_id)
    if group_post is None:
      self.response.write('Could not find post.')
    else:
      self.response.write(group_post.comments.run())

  def create_comment(self, group_post_id):
    group_post = GroupPost.get(group_post_id)
    if group_post is None:
      self.response.write('Could not find post.')
    else:
      content = self.request.get('content')
      user = users.get_current_user()
      GroupPostComment(group_post=group_post, content=content, user=user).put()
      self.response.write('Comment posted.')

  def mark_read(self, group_post_id):
    group_post = GroupPost.get(group_post_id)
    metadata = UserPostMetadata.get_from_post(users.get_current_user(),
        group_post)
    metadata.read = True
    metadata.put()
    self.response.write('Marekd as read: ' + metadata.key().id_or_name())

app = webapp2.WSGIApplication([
    Route(r'/posts/<group_post_id>/comments',
        handler=GroupPostHandler, handler_method='get_comments',
        methods=['GET']),
    Route(r'/posts/<group_post_id>/comments',
        handler=GroupPostHandler, handler_method='create_comment',
        methods=['POST']),
    Route(r'/posts/<group_post_id>/read',
        handler=GroupPostHandler, handler_method='mark_read',
        methods=['POST'])
], debug=True)
