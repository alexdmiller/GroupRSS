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

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


# Handlers

class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write('Hello world!')


class FeedsHandler(webapp2.RequestHandler):
  def get(self):
    feeds_query = Feed.all()
    template_values = {
      'feeds': feeds_query.run()
    }
    template = JINJA_ENVIRONMENT.get_template('feeds.html')
    self.response.write(template.render(template_values))

  def post(self):
    feed_url = self.request.get('url')
    feed = Feed.get_by_key_name(feed_url)
    if feed is None:
      feed = Feed(key_name=feed_url,
                  url=feed_url)
      feed.put()

      reader = Reader(feed)
      reader.saveMetadata()
      reader.savePosts()

    self.redirect('/feeds')


class GroupsHandler(webapp2.RequestHandler):
  def get(self):
    groups_query = Group.all()
    template_values = {
      'groups': groups_query.run()
    }
    template = JINJA_ENVIRONMENT.get_template('groups.html')
    self.response.write(template.render(template_values))

  def post(self):
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
      time.sleep(1)
      self.redirect('/group/' + key_name)
    else:
      self.response.write('That group name is already taken.')


class GroupHandler(webapp2.RequestHandler):
  def get(self, group_key_name):
    group = Group.get_by_key_name(group_key_name);
    if group is None:
      self.response.write('No group by that name exists.')
    else:
      template_values = {
        'group_key_name': group_key_name,
        'group': group
      }
      template = JINJA_ENVIRONMENT.get_template('group.html')
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
      group.feed_keys.append(feed.key())
      group.put()

      self.redirect('/group/' + group_key_name)


app = webapp2.WSGIApplication([
    Route('/', MainHandler),
    Route('/feeds', FeedsHandler),
    Route('/groups', GroupsHandler),
    Route(r'/group/<group_key_name>', handler=GroupHandler,
        handler_method='get'),
    Route(r'/group/<group_key_name>/add_feed', handler=GroupHandler,
        handler_method='add_feed_to_group'),
], debug=True)