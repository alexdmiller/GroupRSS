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
import time
from reader import Reader
from models import *
from slugify import slugify
from webapp2 import Route
from google.appengine.api import users

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


class GroupsHandler(webapp2.RequestHandler):
  def get_group_list(self):
    groups_query = Group.all()
    template_values = {
      'groups': groups_query.run()
    }
    template = JINJA_ENVIRONMENT.get_template('templates/groups.html')
    self.response.write(template.render(template_values))

  def create_group(self):
    name = self.request.get('name')
    description = self.request.get('description')
    # TODO: use UniqueSlugify to allow duplicate names
    key_name = slugify(name)
    group = Group.get_by_key_name(key_name)
    if group is None:
      group = Group(key_name=key_name,
                    name=name,
                    description=description)
      group.put()
      time.sleep(0.5)
      self.redirect('/groups/' + key_name)
    else:
      self.response.write('That group name is already taken.')
  
  def get_group(self, group_key_name):
    group = Group.get_by_key_name(group_key_name);
    if group is None:
      self.response.write('No group by that name exists.')
    else:
      # Check for new posts
      for group_feed in group.group_feeds:
        reader = Reader(group_feed.feed)
        reader.savePosts()
      template_values = {
        'group_key_name': group_key_name,
        'group': group,
        'group_posts': group.group_posts.order('-last_modified'),
        'user': users.get_current_user()
      }
      template = JINJA_ENVIRONMENT.get_template('templates/group.html')
      self.response.write(template.render(template_values))

  def add_feed_to_group(self, group_key_name):
    group = Group.get_by_key_name(group_key_name);
    if group is None:
      self.response.write('No group by that name exists.')
    else:
      feed_url = self.request.get('url')
      feed = Feed.get_by_key_name(feed_url)
      if feed is None:
        feed = Feed(key_name=feed_url,
                    url=feed_url)
        feed.put()
        reader = Reader(feed)
        reader.saveMetadata()
        reader.savePosts()

      group_feed = GroupFeed.gql('WHERE group = :1 AND feed = :2', group.key(),
          feed.key()).get()
      if group_feed is None:
        group_feed = GroupFeed(group=group, feed=feed)
        group_feed.put()
        # add currently available posts to group
        for post in feed.posts:
          GroupPost.from_post(group=group, post=post).put()

      self.redirect('/groups/' + group_key_name)

app = webapp2.WSGIApplication([
    Route(r'/groups', handler=GroupsHandler, handler_method='get_group_list',
        methods=['GET']),
    Route(r'/groups', handler=GroupsHandler, handler_method='create_group',
        methods=['POST']),
    Route(r'/groups/<group_key_name>', handler=GroupsHandler,
        handler_method='get_group'),
    Route(r'/groups/<group_key_name>/add_feed', handler=GroupsHandler,
        handler_method='add_feed_to_group'),
], debug=True)
